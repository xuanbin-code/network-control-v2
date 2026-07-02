"""Screen Capture Service: periodically capture screenshots and send to teacher via WebSocket binary frames"""

import asyncio
import logging
from io import BytesIO

import mss
from PIL import Image

logger = logging.getLogger("screen_capture")


class ScreenCaptureService:
    """Manage screen capture and binary frame transmission"""

    def __init__(self, ws_client):
        self._ws_client = ws_client
        self._running = False
        self._capture_task: asyncio.Task | None = None
        self._interval = 0.5        # 默认 2 FPS
        self._quality = 50          # JPEG 质量
        self._frame_count = 0

    async def start(self, fps: int = 2, quality: int = 50):
        """Start screen capture loop.

        Args:
            fps: Frames per second (1-10)
            quality: JPEG compression quality (10-95)
        """
        if self._running:
            await self.stop()

        self._interval = 1.0 / max(1, min(fps, 10))
        self._quality = max(10, min(quality, 95))
        self._frame_count = 0
        self._running = True
        self._capture_task = asyncio.create_task(self._capture_loop())
        logger.info(f"Screen capture started: fps={fps}, quality={quality}, interval={self._interval:.0f}ms")

    async def stop(self):
        """Stop screen capture loop"""
        self._running = False
        if self._capture_task:
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass
            self._capture_task = None
        logger.info(f"Screen capture stopped, {self._frame_count} frames sent total")

    async def _capture_loop(self):
        """Main loop: capture → encode → send binary frame"""
        loop = asyncio.get_running_loop()

        while self._running:
            try:
                # 在默认线程池中执行阻塞的截图操作（mss 是同步阻塞 API）
                with mss.mss() as sct:
                    monitor = sct.monitors[0]  # 虚拟桌面（包含所有显示器）
                    raw = await loop.run_in_executor(None, sct.grab, monitor)

                # BGRA 像素 → PIL Image（在默认线程池中转换）
                img = await loop.run_in_executor(
                    None,
                    lambda: Image.frombytes("RGB", (raw.width, raw.height), raw.bgra, "raw", "BGRX"),
                )

                # 限制最大宽度 1920px，避免 4K 屏幕帧过大
                if img.width > 1920:
                    ratio = 1920.0 / img.width
                    new_size = (1920, int(img.height * ratio))
                    img = await loop.run_in_executor(None, img.resize, new_size, Image.LANCZOS)

                # JPEG 编码到内存缓冲区
                buf = BytesIO()
                await loop.run_in_executor(None, lambda: img.save(buf, "JPEG", quality=self._quality))
                jpeg_bytes = buf.getvalue()

                # 通过 WebSocket 二进制帧发送
                await self._ws_client.send_bytes(jpeg_bytes)
                self._frame_count += 1
                if self._frame_count <= 3 or self._frame_count % 10 == 0:
                    logger.info(f"Sent frame #{self._frame_count} ({len(jpeg_bytes)} bytes)")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Screen capture error: {e}")
                await asyncio.sleep(1.0)

            await asyncio.sleep(self._interval)

    @property
    def is_running(self) -> bool:
        return self._running
