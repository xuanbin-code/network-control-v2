"""锁屏与黑屏安静服务

包含两类全屏覆盖窗口：
1. LockScreen：网线拔出锁屏，需密码或网线恢复才能解锁，60 秒未解锁自动关机。
2. BlackScreenQuiet：教师端下发的黑屏安静控制，支持倒计时自动解除或持续黑屏，
   并内置本地 TCP 进程间通信（IPC）接口，供教师端远程调用解除。

迁移并扩展自原 Network_Control 项目的 lock_screen.py。
"""

import hashlib
import os
import socket
import socketserver
import subprocess
import sys
import threading
import traceback
from typing import cast

# 设置 stdout 编码为 utf-8，避免中文乱码
# type: ignore 用于消除部分 IDE 对 sys.stdout.reconfigure 的类型误报
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
except Exception:
    pass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

DEFAULT_BLACK_SCREEN_SECONDS = 30
DEFAULT_BLACK_SCREEN_IPC_HOST = "127.0.0.1"
DEFAULT_BLACK_SCREEN_IPC_PORT = 8779

IPC_COMMAND_UNLOCK = "UNLOCK"
IPC_COMMAND_STATUS = "STATUS"
IPC_RESPONSE_OK = "OK\n"
IPC_RESPONSE_ERROR = "ERROR\n"
IPC_RESPONSE_LOCKED = "LOCKED\n"


def _resolve_asset_path(filename: str) -> str | None:
    """在开发目录和 PyInstaller 打包目录中定位资源文件。"""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "assets", filename),
        os.path.join(here, "assets", filename),
        os.path.join(here, filename),
    ]
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        candidates.insert(0, os.path.join(base, "assets", filename))
        candidates.insert(1, os.path.join(base, filename))

    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


class _IpcCommandHandler(socketserver.StreamRequestHandler):
    """黑屏安静 IPC 命令处理器。"""

    def handle(self):
        try:
            raw = self.rfile.readline()
            if not raw:
                return
            command = raw.strip().decode("utf-8", errors="ignore").upper()
            server = cast(BlackScreenIpcServer, self.server)

            if command == IPC_COMMAND_UNLOCK:
                print(f"[BlackScreenIpc] 收到 UNLOCK 命令，来源: {self.client_address}")
                if server.unlock_callback:
                    try:
                        # 先发送响应并强制刷新，再触发关闭窗口的回调
                        self.wfile.write(IPC_RESPONSE_OK.encode())
                        self.wfile.flush()
                        server.unlock_callback()
                    except Exception as e:
                        print(f"[BlackScreenIpc] 执行 UNLOCK 回调异常: {e}")
                        self.wfile.write(IPC_RESPONSE_ERROR.encode())
                        self.wfile.flush()
                else:
                    self.wfile.write(IPC_RESPONSE_ERROR.encode())
                    self.wfile.flush()
            elif command == IPC_COMMAND_STATUS:
                locked = "yes" if server.is_locked_callback and server.is_locked_callback() else "no"
                self.wfile.write(f"{locked}\n".encode())
                self.wfile.flush()
            else:
                self.wfile.write(IPC_RESPONSE_ERROR.encode())
                self.wfile.flush()
        except Exception as e:
            print(f"[BlackScreenIpc] 处理命令异常: {e}")


class BlackScreenIpcServer(socketserver.ThreadingTCPServer):
    """黑屏安静本地 TCP IPC 服务器。

    教师端或其他进程可向该服务器发送 UNLOCK 命令远程解除黑屏。
    """

    allow_reuse_address = True
    daemon_threads = True

    def __init__(
        self,
        host: str,
        port: int,
        unlock_callback,
        is_locked_callback=None,
    ):
        super().__init__((host, port), _IpcCommandHandler)
        self.host = host
        self.port = self.server_address[1]
        self.unlock_callback = unlock_callback
        self.is_locked_callback = is_locked_callback
        self._thread: threading.Thread | None = None

    def start(self):
        """在后台线程中启动 IPC 服务器。"""
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()
        print(f"[BlackScreenIpc] 已启动，监听 {self.host}:{self.port}")

    def stop(self):
        """停止 IPC 服务器。"""
        self.shutdown()
        self.server_close()
        print("[BlackScreenIpc] 已停止。")


def find_available_port(host: str = DEFAULT_BLACK_SCREEN_IPC_HOST, start: int = DEFAULT_BLACK_SCREEN_IPC_PORT) -> int:
    """从 start 端口开始查找一个可用的 TCP 端口。"""
    port = start
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            result = sock.connect_ex((host, port))
            if result != 0:
                return port
        port += 1
    raise RuntimeError("无法找到可用的 IPC 端口")


def send_unlock_command(
    host: str = DEFAULT_BLACK_SCREEN_IPC_HOST,
    port: int = DEFAULT_BLACK_SCREEN_IPC_PORT,
    timeout: float = 2.0,
) -> bool:
    """向指定 IPC 服务器发送解除黑屏命令。

    Returns:
        是否成功发送并收到 OK 响应。
    """
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall(f"{IPC_COMMAND_UNLOCK}\n".encode())
            response = sock.recv(64).decode("utf-8", errors="ignore").strip()
            print(f"[send_unlock_command] 收到响应: {response}")
            return response == "OK"
    except Exception as e:
        print(f"[send_unlock_command] 发送解除命令失败: {e}")
        return False


class LockScreen(QWidget):
    """网线拔出锁屏 - 全屏覆盖，需密码或网线恢复才能解锁

    60 秒内未解锁则关机。
    """

    def __init__(self, password_hash: str):
        super().__init__()
        self.password_hash = password_hash
        self.remaining = 60
        self._network_back = False
        self._shutdown_done = False

        self._build_ui()
        self._start_timer()
        self._start_network_monitor()

    def _build_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setStyleSheet("QWidget { background-color: #000080; }")
        self.showFullScreen()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        def lbl(text, size, color="white", bold=False):
            w = QLabel(text)
            w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            f = QFont("微软雅黑", size)
            if bold:
                f.setBold(True)
            w.setFont(f)
            w.setStyleSheet(f"color: {color}; background: transparent;")
            return w

        layout.addStretch(2)
        layout.addWidget(lbl("！  网 线 已 被 拔 出  ！", 40, "#FFFFFF", True))
        layout.addSpacing(10)

        self._countdown_lbl = lbl(
            "请在 60 秒内恢复网线，或输入解锁密码，否则计算机将自动关机",
            15, "#FFFF00"
        )
        self._countdown_lbl.setWordWrap(True)
        layout.addWidget(self._countdown_lbl)

        layout.addSpacing(20)
        layout.addWidget(lbl("网线已被拔出，请输入解锁密码：", 18))

        self._pwd = QLineEdit()
        self._pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self._pwd.setFixedSize(320, 46)
        self._pwd.setFont(QFont("微软雅黑", 15))
        self._pwd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pwd.setStyleSheet(
            "background: white; color: black; border-radius: 4px; padding: 4px;"
        )
        self._pwd.returnPressed.connect(self._verify)
        layout.addWidget(self._pwd, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("确认解锁")
        btn.setFixedSize(200, 46)
        btn.setFont(QFont("微软雅黑", 14))
        btn.setStyleSheet(
            "background: #4CAF50; color: white; border-radius: 4px;"
        )
        btn.clicked.connect(self._verify)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._err_lbl = lbl("", 13, "#FF6666")
        layout.addWidget(self._err_lbl)

        layout.addStretch(2)

    def _start_timer(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self):
        if self._network_back:
            self._timer.stop()
            QApplication.quit()
            return

        self.remaining -= 1
        self._countdown_lbl.setText(
            f"请在 {self.remaining} 秒内恢复网线，或输入解锁密码，否则计算机将自动关机"
        )

        if self.remaining <= 0 and not self._shutdown_done:
            self._shutdown_done = True
            self._timer.stop()
            subprocess.run(["shutdown", "/s", "/t", "0"])

    def _verify(self):
        pwd = self._pwd.text()
        if hashlib.sha256(pwd.encode()).hexdigest() == self.password_hash:
            self._timer.stop()
            QApplication.quit()
        else:
            self._err_lbl.setText("密码错误，请重试")
            self._pwd.clear()
            self._pwd.setFocus()

    def _start_network_monitor(self):
        def monitor():
            import time
            time.sleep(4)
            while not self._network_back:
                time.sleep(3)
                try:
                    r = subprocess.run(
                        ['powershell', '-Command',
                         '(Get-NetAdapter | Where-Object {'
                         '$_.Status -eq "Up" -and $_.Name -notmatch "Loopback"}).Count'],
                        capture_output=True, text=True, timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    s = r.stdout.strip()
                    if s.isdigit() and int(s) > 0:
                        self._network_back = True
                except Exception:
                    pass

        threading.Thread(target=monitor, daemon=True).start()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_F4):
            return
        super().keyPressEvent(event)


class BlackScreenQuiet(QWidget):
    """教师端下发的黑屏安静窗口

    - 全屏黑屏、置顶、无边框
    - 显示小猫提醒图和 "请保持安静" 文字
    - 支持倒计时自动解除，也支持持续黑屏（需手动或教师端远程解除）
    - 内置本地 TCP IPC 服务器，接收 UNLOCK 命令远程解除
    - 支持按钮点击或 ESC 提前解除
    """

    def __init__(
        self,
        countdown_seconds: int | None = DEFAULT_BLACK_SCREEN_SECONDS,
        ipc_host: str = DEFAULT_BLACK_SCREEN_IPC_HOST,
        ipc_port: int | None = DEFAULT_BLACK_SCREEN_IPC_PORT,
    ):
        super().__init__()
        # countdown_seconds <= 0 或 None 表示持续黑屏，无自动倒计时
        if countdown_seconds is None or countdown_seconds <= 0:
            self.countdown_seconds = 0
            self.remaining_seconds = 0
            self._infinite = True
        else:
            self.countdown_seconds = countdown_seconds
            self.remaining_seconds = countdown_seconds
            self._infinite = False

        self._ipc_host = ipc_host
        self._ipc_port = ipc_port
        self._ipc_server: BlackScreenIpcServer | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._build_ui()
        self._start_ipc_server()

    def _build_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("QWidget { background-color: #000000; }")
        self.showFullScreen()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # 倒计时显示（持续黑屏时显示固定提示）
        self.countdown_label = QLabel(self._format_time(self.remaining_seconds))
        self.countdown_label.setFont(QFont("微软雅黑", 48, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet("QLabel { color: #ffffff; }")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.countdown_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 小猫提醒图
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_cat_image()
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 请保持安静
        self.quiet_label = QLabel("请保持安静")
        self.quiet_label.setFont(QFont("微软雅黑", 32, QFont.Weight.Bold))
        self.quiet_label.setStyleSheet("QLabel { color: #ffffff; }")
        self.quiet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.quiet_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 提示文字
        if self._infinite:
            tip_text = "教师端已下发黑屏安静，解除前请保持安静"
        else:
            tip_text = "黑屏安静测试中，倒计时结束后自动解除"
        self.tip_label = QLabel(tip_text)
        self.tip_label.setFont(QFont("微软雅黑", 14))
        self.tip_label.setStyleSheet("QLabel { color: #aaaaaa; }")
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tip_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # IPC 状态提示
        self.ipc_label = QLabel("")
        self.ipc_label.setFont(QFont("微软雅黑", 11))
        self.ipc_label.setStyleSheet("QLabel { color: #888888; }")
        self.ipc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ipc_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 测试 IPC 解除按钮
        self.test_ipc_btn = QPushButton("测试远程解除 (IPC)")
        self.test_ipc_btn.setFixedSize(220, 44)
        self.test_ipc_btn.setFont(QFont("微软雅黑", 12))
        self.test_ipc_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #2c5aa0;"
            "  color: #ffffff;"
            "  border: 2px solid #4a7fc9;"
            "  border-radius: 6px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #3a6fb8;"
            "  border: 2px solid #6a9fd9;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #1e457a;"
            "}"
        )
        self.test_ipc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_ipc_btn.clicked.connect(self._test_ipc_unlock)
        layout.addWidget(self.test_ipc_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 退出按钮
        self.exit_btn = QPushButton("解除黑屏安静 / 结束测试")
        self.exit_btn.setFixedSize(280, 60)
        self.exit_btn.setFont(QFont("微软雅黑", 14))
        self.exit_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #333333;"
            "  color: #ffffff;"
            "  border: 2px solid #555555;"
            "  border-radius: 8px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #444444;"
            "  border: 2px solid #777777;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #222222;"
            "}"
        )
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self._exit_test)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 启动倒计时（仅非持续模式）
        if not self._infinite:
            self._timer.start(1000)

    def _start_ipc_server(self):
        """启动本地 TCP IPC 服务器，用于接收远程解除命令。"""
        try:
            port = self._ipc_port
            if port is None:
                port = find_available_port(self._ipc_host)
            self._ipc_server = BlackScreenIpcServer(
                host=self._ipc_host,
                port=port,
                unlock_callback=self._schedule_exit,
                is_locked_callback=lambda: self.isVisible(),
            )
            self._ipc_server.start()
            self.ipc_label.setText(f"IPC 监听: {self._ipc_host}:{self._ipc_server.port}")
        except Exception as e:
            print(f"[BlackScreenQuiet] 启动 IPC 服务器失败: {e}")
            self.ipc_label.setText(f"IPC 未启动: {e}")

    def _schedule_exit(self):
        """线程安全地安排主线程关闭窗口（供 IPC 服务器回调使用）。"""
        QTimer.singleShot(0, self._exit_test)

    def _test_ipc_unlock(self):
        """点击测试按钮，模拟教师端通过 IPC 发送解除命令。"""
        if self._ipc_server is None:
            print("[BlackScreenQuiet] IPC 服务器未启动，无法测试远程解除。")
            return
        port = self._ipc_server.port
        print(f"[BlackScreenQuiet] 测试按钮触发 IPC 解除命令到 127.0.0.1:{port}")
        threading.Thread(
            target=send_unlock_command,
            kwargs={"host": self._ipc_host, "port": port},
            daemon=True,
        ).start()

    def _load_cat_image(self):
        """加载小猫图片并按屏幕高度等比例缩放。"""
        image_path = _resolve_asset_path("cat_quite_img.png")
        if not image_path:
            self.image_label.setText("[未找到小猫图片]")
            self.image_label.setStyleSheet("QLabel { color: #ff6666; font-size: 16px; }")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setText("[小猫图片加载失败]")
            self.image_label.setStyleSheet("QLabel { color: #ff6666; font-size: 16px; }")
            return

        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            max_height = int(available.height() * 0.40)
            max_width = int(available.width() * 0.75)
            scaled = pixmap.scaled(
                max_width,
                max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setPixmap(pixmap)

    def _format_time(self, seconds: int) -> str:
        if self._infinite:
            return "持续黑屏中"
        return f"{seconds} 秒"

    def _tick(self):
        if self._infinite:
            return
        self.remaining_seconds -= 1
        self.countdown_label.setText(self._format_time(self.remaining_seconds))
        if self.remaining_seconds <= 0:
            self._timer.stop()
            print("[BlackScreenQuiet] 倒计时结束，自动解除黑屏安静。")
            self._exit_test()

    def _exit_test(self):
        self._timer.stop()
        if self._ipc_server is not None:
            self._ipc_server.stop()
            self._ipc_server = None
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._exit_test()
        else:
            super().keyPressEvent(event)


class FocusReminderWindow(QWidget):
    """专注提示窗 - 访问被拦截网页时弹出全屏提示

    - 全屏、无边框、置顶
    - 显示"请专心学习，不要访问无关网页"
    - 倒计时自动关闭，或按 ESC / 点击按钮立即关闭
    """

    DEFAULT_MESSAGE = "请专心学习，不要访问无关网页"

    def __init__(self, countdown_seconds: int = 8, message: str = ""):
        super().__init__()
        self.remaining_seconds = max(1, countdown_seconds)
        self.message = message or self.DEFAULT_MESSAGE

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._build_ui()

    def _build_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("QWidget { background-color: #1a1a2e; }")
        self.showFullScreen()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24)

        # 提示图标/emoji
        icon_label = QLabel("🚫")
        icon_label.setFont(QFont("Segoe UI Emoji", 72))
        icon_label.setStyleSheet("QLabel { color: #ffffff; background: transparent; }")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 主提示文字
        msg_label = QLabel(self.message)
        msg_label.setFont(QFont("微软雅黑", 32, QFont.Weight.Bold))
        msg_label.setStyleSheet("QLabel { color: #ffffff; background: transparent; }")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 副标题
        sub_label = QLabel("当前网页与课堂内容无关，已被网络管理系统拦截")
        sub_label.setFont(QFont("微软雅黑", 16))
        sub_label.setStyleSheet("QLabel { color: #a0a0a0; background: transparent; }")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setWordWrap(True)
        layout.addWidget(sub_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 倒计时
        self._countdown_label = QLabel(f"{self.remaining_seconds} 秒后自动关闭")
        self._countdown_label.setFont(QFont("微软雅黑", 18))
        self._countdown_label.setStyleSheet("QLabel { color: #f0c040; background: transparent; }")
        self._countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._countdown_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 立即关闭按钮
        close_btn = QPushButton("我知道了")
        close_btn.setFixedSize(220, 56)
        close_btn.setFont(QFont("微软雅黑", 14))
        close_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #2c5aa0;"
            "  color: #ffffff;"
            "  border: 2px solid #4a7fc9;"
            "  border-radius: 8px;"
            "}"
            "QPushButton:hover { background-color: #3a6fb8; }"
            "QPushButton:pressed { background-color: #1e457a; }"
        )
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self._exit)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._timer.start(1000)

    def _tick(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self._exit()
        else:
            self._countdown_label.setText(f"{self.remaining_seconds} 秒后自动关闭")

    def _exit(self):
        self._timer.stop()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self._exit()
        else:
            super().keyPressEvent(event)


def run_focus_reminder(countdown_seconds: int = 8, message: str = ""):
    """启动专注提示窗（阻塞当前线程）。"""
    app = QApplication(sys.argv[:1])
    screens = app.screens()
    if not screens:
        print("[run_focus_reminder] 错误：未检测到可用屏幕")
        sys.exit(1)
    window = FocusReminderWindow(countdown_seconds=countdown_seconds, message=message)
    window.show()
    sys.exit(app.exec())


def run_lock_screen(password_hash: str):
    """启动网线拔出锁屏窗口（阻塞当前线程）。"""
    app = QApplication(sys.argv[:1])
    screen = LockScreen(password_hash)
    screen.show()
    sys.exit(app.exec())


def run_black_screen_quiet(
    countdown_seconds: int | None = DEFAULT_BLACK_SCREEN_SECONDS,
    ipc_host: str = DEFAULT_BLACK_SCREEN_IPC_HOST,
    ipc_port: int | None = DEFAULT_BLACK_SCREEN_IPC_PORT,
):
    """启动黑屏安静窗口（阻塞当前线程）。

    Args:
        countdown_seconds: 倒计时秒数。默认 30 秒；传入 0 或 None 表示持续黑屏，
                          不会自动解除，需通过按钮、ESC 或 IPC UNLOCK 命令退出。
        ipc_host: IPC 服务器监听地址，默认 127.0.0.1。
        ipc_port: IPC 服务器监听端口，默认 8779；传 None 则自动查找可用端口。
    """
    app = QApplication(sys.argv[:1])

    screens = app.screens()
    if not screens:
        print("[run_black_screen_quiet] 错误：未检测到可用屏幕，无法显示黑屏窗口。")
        sys.exit(1)

    infinite = countdown_seconds is None or countdown_seconds <= 0
    mode_text = "持续黑屏" if infinite else f"倒计时 {countdown_seconds} 秒"
    print(f"[run_black_screen_quiet] 检测到 {len(screens)} 个屏幕，启动黑屏安静窗口（{mode_text}）。")
    window = BlackScreenQuiet(
        countdown_seconds=countdown_seconds,
        ipc_host=ipc_host,
        ipc_port=ipc_port,
    )
    window.show()
    sys.exit(app.exec())


def main():
    """命令行入口，便于单独测试黑屏安静窗口或专注提示窗。

    用法：
        python -m app.services.lock_screen                  # 默认 30 秒黑屏倒计时
        python -m app.services.lock_screen 0                # 持续黑屏
        python -m app.services.lock_screen 60               # 60 秒黑屏倒计时
        python -m app.services.lock_screen --focus-reminder            # 8 秒专注提示窗
        python -m app.services.lock_screen --focus-reminder 10         # 10 秒专注提示窗
    """
    try:
        args = sys.argv[1:]

        # 专注提示窗模式
        if args and args[0] == "--focus-reminder":
            seconds = 8
            if len(args) > 1:
                try:
                    seconds = int(args[1])
                except ValueError:
                    print(f"[main] 警告：无法解析专注提示倒计时 '{args[1]}'，使用默认值 8。")
            run_focus_reminder(countdown_seconds=seconds)
            return

        # 黑屏安静模式（默认）
        countdown = DEFAULT_BLACK_SCREEN_SECONDS
        if args:
            try:
                value = int(args[0])
                countdown = value
            except ValueError:
                print(f"[main] 警告：无法解析倒计时参数 '{args[0]}'，已使用默认值 {DEFAULT_BLACK_SCREEN_SECONDS}。")
        run_black_screen_quiet(countdown)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[main] 运行异常: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
