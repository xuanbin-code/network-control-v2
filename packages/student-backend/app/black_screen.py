"""黑屏安静测试窗口

供前端测试组调用，全屏黑屏覆盖，支持倒计时自动解除或持续黑屏，
并内置本地 TCP IPC 接口，可远程发送 UNLOCK 命令解除。
"""

import os
import socket
import socketserver
import subprocess
import sys
import threading
import traceback
from typing import cast

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

DEFAULT_BLACK_SCREEN_SECONDS = 30
DEFAULT_BLACK_SCREEN_IPC_HOST = "127.0.0.1"
DEFAULT_BLACK_SCREEN_IPC_PORT = 8779

IPC_COMMAND_UNLOCK = "UNLOCK"
IPC_COMMAND_STATUS = "STATUS"
IPC_RESPONSE_OK = "OK\n"
IPC_RESPONSE_ERROR = "ERROR\n"


class _IpcCommandHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            raw = self.rfile.readline()
            if not raw:
                return
            command = raw.strip().decode("utf-8", errors="ignore").upper()
            server = cast(BlackScreenIpcServer, self.server)

            if command == IPC_COMMAND_UNLOCK:
                if server.unlock_callback:
                    try:
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
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, host: str, port: int, unlock_callback, is_locked_callback=None):
        super().__init__((host, port), _IpcCommandHandler)
        self.host = host
        self.port = self.server_address[1]
        self.unlock_callback = unlock_callback
        self.is_locked_callback = is_locked_callback
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)
        self._thread.start()
        print(f"[BlackScreenIpc] 已启动，监听 {self.host}:{self.port}")

    def stop(self):
        self.shutdown()
        self.server_close()
        print("[BlackScreenIpc] 已停止。")


def send_unlock_command(
    host: str = DEFAULT_BLACK_SCREEN_IPC_HOST,
    port: int = DEFAULT_BLACK_SCREEN_IPC_PORT,
    timeout: float = 2.0,
) -> bool:
    """向指定 IPC 服务器发送解除黑屏命令。"""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall(f"{IPC_COMMAND_UNLOCK}\n".encode())
            response = sock.recv(64).decode("utf-8", errors="ignore").strip()
            print(f"[send_unlock_command] 收到响应: {response}")
            return response == "OK"
    except Exception as e:
        print(f"[send_unlock_command] 发送解除命令失败: {e}")
        return False


class BlackScreenQuiet(QWidget):
    """黑屏安静测试窗口"""

    def __init__(
        self,
        countdown_seconds: int | None = DEFAULT_BLACK_SCREEN_SECONDS,
        ipc_host: str = DEFAULT_BLACK_SCREEN_IPC_HOST,
        ipc_port: int | None = DEFAULT_BLACK_SCREEN_IPC_PORT,
    ):
        super().__init__()
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
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("QWidget { background-color: #000000; }")
        self.showFullScreen()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self.countdown_label = QLabel(self._format_time(self.remaining_seconds))
        self.countdown_label.setFont(QFont("微软雅黑", 48, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet("QLabel { color: #ffffff; }")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.countdown_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.quiet_label = QLabel("请保持安静")
        self.quiet_label.setFont(QFont("微软雅黑", 32, QFont.Weight.Bold))
        self.quiet_label.setStyleSheet("QLabel { color: #ffffff; }")
        self.quiet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.quiet_label, alignment=Qt.AlignmentFlag.AlignCenter)

        if self._infinite:
            tip_text = "教师端已下发黑屏安静，解除前请保持安静"
        else:
            tip_text = "黑屏安静测试中，倒计时结束后自动解除"
        self.tip_label = QLabel(tip_text)
        self.tip_label.setFont(QFont("微软雅黑", 14))
        self.tip_label.setStyleSheet("QLabel { color: #aaaaaa; }")
        self.tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tip_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.ipc_label = QLabel("")
        self.ipc_label.setFont(QFont("微软雅黑", 11))
        self.ipc_label.setStyleSheet("QLabel { color: #888888; }")
        self.ipc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.ipc_label, alignment=Qt.AlignmentFlag.AlignCenter)

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

        if not self._infinite:
            self._timer.start(1000)

    def _start_ipc_server(self):
        try:
            port = self._ipc_port
            if port is None:
                port = self._find_available_port(self._ipc_host)
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

    @staticmethod
    def _find_available_port(host: str = DEFAULT_BLACK_SCREEN_IPC_HOST, start: int = DEFAULT_BLACK_SCREEN_IPC_PORT) -> int:
        port = start
        while port < 65535:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.2)
                if sock.connect_ex((host, port)) != 0:
                    return port
            port += 1
        raise RuntimeError("无法找到可用的 IPC 端口")

    def _schedule_exit(self):
        QTimer.singleShot(0, self._exit_test)

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


def run_black_screen_quiet(
    countdown_seconds: int | None = DEFAULT_BLACK_SCREEN_SECONDS,
    ipc_host: str = DEFAULT_BLACK_SCREEN_IPC_HOST,
    ipc_port: int | None = DEFAULT_BLACK_SCREEN_IPC_PORT,
):
    """启动黑屏安静窗口（阻塞当前线程）。"""
    app = QApplication(sys.argv[:1])
    screens = app.screens()
    if not screens:
        print("[run_black_screen_quiet] 错误：未检测到可用屏幕。")
        sys.exit(1)

    infinite = countdown_seconds is None or countdown_seconds <= 0
    mode_text = "持续黑屏" if infinite else f"倒计时 {countdown_seconds} 秒"
    print(f"[run_black_screen_quiet] 启动黑屏安静窗口（{mode_text}）。")
    window = BlackScreenQuiet(
        countdown_seconds=countdown_seconds,
        ipc_host=ipc_host,
        ipc_port=ipc_port,
    )
    window.show()
    sys.exit(app.exec())


def main():
    """命令行入口。"""
    try:
        countdown = DEFAULT_BLACK_SCREEN_SECONDS
        if len(sys.argv) > 1:
            try:
                value = int(sys.argv[1])
                countdown = value
            except ValueError:
                print(f"[main] 警告：无法解析倒计时参数 '{sys.argv[1]}'，已使用默认值 {DEFAULT_BLACK_SCREEN_SECONDS}。")
        run_black_screen_quiet(countdown)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[main] 运行异常: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
