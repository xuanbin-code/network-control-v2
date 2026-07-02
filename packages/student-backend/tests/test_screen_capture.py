"""ScreenCaptureService 单元测试

测试目标：
- start / stop 生命周期与状态管理
- fps 与 quality 参数边界裁剪
- 截图、缩放、编码、发送主循环
- 捕获异常与发送异常时的容错行为

运行方式（需在 virtualenv 中安装 pytest、pytest-asyncio）：
    cd packages/student-backend
    ..\.venv\Scripts\python -m pytest tests/test_screen_capture.py -v
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.screen_capture import ScreenCaptureService


@pytest.fixture
def ws_client():
    """模拟 WebSocket 客户端"""
    return AsyncMock()


@pytest.fixture
def service(ws_client):
    """ScreenCaptureService 实例"""
    return ScreenCaptureService(ws_client)


class TestInit:
    def test_initial_state(self, service):
        """初始化后应处于停止状态，使用默认参数"""
        assert service.is_running is False
        assert service._capture_task is None
        assert service._interval == 0.5
        assert service._quality == 50
        assert service._frame_count == 0


class TestStart:
    @pytest.mark.asyncio
    async def test_start_creates_task_and_sets_running(self, service):
        """start 后应创建后台任务并置 running 为 True"""
        await service.start()
        assert service.is_running is True
        assert service._capture_task is not None
        assert service._capture_task.done() is False
        await service.stop()

    @pytest.mark.asyncio
    async def test_start_clamps_fps_and_quality(self, service):
        """fps 与 quality 应被限制在合法范围内"""
        await service.start(fps=0, quality=5)
        assert service._interval == 1.0  # fps 下限为 1
        assert service._quality == 10    # quality 下限为 10
        await service.stop()

        await service.start(fps=20, quality=100)
        assert service._interval == pytest.approx(0.1)  # fps 上限为 10
        assert service._quality == 95                     # quality 上限为 95
        await service.stop()

    @pytest.mark.asyncio
    async def test_start_restarts_when_already_running(self, service):
        """重复 start 应先停止旧任务再启动新任务"""
        await service.start()
        old_task = service._capture_task
        await service.start()
        assert service._capture_task is not old_task
        assert service.is_running is True
        assert old_task.cancelled() is True
        await service.stop()


class TestStop:
    @pytest.mark.asyncio
    async def test_stop_cancels_task(self, service):
        """stop 应取消后台任务并清理状态"""
        await service.start()
        task = service._capture_task
        await service.stop()
        assert service.is_running is False
        assert task.cancelled() is True
        assert service._capture_task is None

    @pytest.mark.asyncio
    async def test_stop_is_idempotent(self, service):
        """停止已停止的服务不应报错"""
        await service.stop()
        assert service.is_running is False
        assert service._capture_task is None


def _build_mss_mocks(mock_mss, width: int, height: int):
    """构造 mss 与 PIL 的 mock 对象，返回 (raw, sct, img)"""
    raw = MagicMock()
    raw.width = width
    raw.height = height
    raw.bgra = b"\x00" * width * height * 4

    sct = MagicMock()
    sct.monitors = [raw]
    sct.grab.return_value = raw
    # 支持 with mss.mss() as sct:
    sct.__enter__ = MagicMock(return_value=sct)
    sct.__exit__ = MagicMock(return_value=False)
    mock_mss.mss.return_value = sct

    img = MagicMock()
    img.width = width
    img.height = height
    return raw, sct, img


class TestCaptureLoop:
    @pytest.mark.asyncio
    @patch("app.services.screen_capture.mss")
    @patch("app.services.screen_capture.Image")
    async def test_capture_loop_sends_one_frame(self, mock_image, mock_mss, service):
        """主循环应成功捕获一帧并通过 WebSocket 发送"""
        _raw, _sct, img = _build_mss_mocks(mock_mss, 1920, 1080)
        mock_image.frombytes.return_value = img

        async def _sleep(_delay):
            # 第一次 interval sleep 时退出循环
            service._running = False

        with patch("app.services.screen_capture.asyncio.sleep", side_effect=_sleep):
            await service.start()
            await service._capture_task  # 等待循环自然结束

        assert service._frame_count == 1
        service._ws_client.send_bytes.assert_awaited_once()
        img.save.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.screen_capture.mss")
    @patch("app.services.screen_capture.Image")
    async def test_capture_loop_resizes_wide_image(self, mock_image, mock_mss, service):
        """宽度超过 1920 时应按比例缩放"""
        _raw, _sct, img = _build_mss_mocks(mock_mss, 3840, 2160)
        img.resize.return_value = img
        mock_image.frombytes.return_value = img

        async def _sleep(_delay):
            service._running = False

        with patch("app.services.screen_capture.asyncio.sleep", side_effect=_sleep):
            await service.start()
            await service._capture_task

        img.resize.assert_called_once()
        new_size = img.resize.call_args[0][0]
        assert new_size[0] == 1920
        assert new_size[1] == 1080  # 3840x2160 等比缩放后高度

    @pytest.mark.asyncio
    @patch("app.services.screen_capture.mss")
    async def test_capture_loop_handles_capture_error(self, mock_mss, service):
        """截图异常时不应崩溃，应进入错误恢复睡眠"""
        sct = MagicMock()
        sct.grab.side_effect = RuntimeError("capture failed")
        mock_mss.mss.return_value = sct

        sleep_calls = []

        async def _sleep(delay):
            sleep_calls.append(delay)
            # 经历一次异常恢复睡眠（1.0s）后退出
            if len(sleep_calls) >= 2:
                service._running = False

        with patch("app.services.screen_capture.asyncio.sleep", side_effect=_sleep):
            await service.start()
            await service._capture_task

        assert service._frame_count == 0
        service._ws_client.send_bytes.assert_not_awaited()
        assert 1.0 in sleep_calls  # 错误恢复睡眠

    @pytest.mark.asyncio
    @patch("app.services.screen_capture.mss")
    @patch("app.services.screen_capture.Image")
    async def test_capture_loop_handles_send_error(self, mock_image, mock_mss, service):
        """发送失败时不应崩溃，应记录错误并继续"""
        _raw, _sct, img = _build_mss_mocks(mock_mss, 1920, 1080)
        mock_image.frombytes.return_value = img
        service._ws_client.send_bytes.side_effect = RuntimeError("send failed")

        sleep_calls = []

        async def _sleep(delay):
            sleep_calls.append(delay)
            if len(sleep_calls) >= 2:
                service._running = False

        with patch("app.services.screen_capture.asyncio.sleep", side_effect=_sleep):
            await service.start()
            await service._capture_task

        assert service._frame_count == 0
        service._ws_client.send_bytes.assert_awaited()
        assert 1.0 in sleep_calls  # 错误恢复睡眠

    @pytest.mark.asyncio
    async def test_is_running_reflects_state(self, service):
        """is_running 应在 start/stop 后正确反映状态"""
        assert service.is_running is False
        await service.start()
        assert service.is_running is True
        await service.stop()
        assert service.is_running is False
