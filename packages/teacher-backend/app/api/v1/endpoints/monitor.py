"""Screen Monitoring API Endpoints"""

import base64

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.ws_manager import ws_manager
from app.schemas.requests import MonitorStartRequest

router = APIRouter()


@router.post("/monitor/start")
async def start_monitor(req: MonitorStartRequest):
    """Start screen monitoring for specified student"""
    if req.fps not in (1, 2, 3, 5):
        raise HTTPException(400, "fps must be one of: 1, 2, 3, 5")
    if not (10 <= req.quality <= 95):
        raise HTTPException(400, "quality must be between 10 and 95")

    result = await ws_manager.send_screen_monitor_start(
        target_ip=req.student_ip,
        fps=req.fps,
        quality=req.quality,
    )

    if result["delivered"] == 0:
        raise HTTPException(404, f"Student {req.student_ip} is not connected")

    return {
        "ok": True,
        "student_ip": req.student_ip,
        "fps": req.fps,
        "quality": req.quality,
        "delivery": result,
    }


@router.post("/monitor/stop")
async def stop_monitor():
    """Stop current screen monitoring session"""
    result = await ws_manager.send_screen_monitor_stop()
    return {"ok": True, "delivery": result}


@router.get("/monitor/status")
async def monitor_status():
    """Get current monitor session status"""
    return ws_manager.get_monitor_status()


@router.get("/monitor/frame")
async def get_latest_frame():
    """Get latest screen frame (base64 encoded JPEG)

    Frontend polls this endpoint at FPS interval. Returns 204 No Content when no frame available.
    """
    session = ws_manager.monitor_session
    if session.latest_frame is None:
        if session.student_ip:
            print(f"[Monitor] Poll frame — no frame yet (target: {session.student_ip})")
        return Response(status_code=204)

    b64 = base64.b64encode(session.latest_frame).decode("ascii")
    print(f"[Monitor] Returning frame #{session.frame_count} ({len(session.latest_frame)} bytes) "
          f"→ base64 {len(b64)} chars")
    return {
        "frame": b64,
        "ts": session.latest_frame_ts,
        "frame_count": session.frame_count,
        "format": "jpeg",
        "encoding": "base64",
    }
