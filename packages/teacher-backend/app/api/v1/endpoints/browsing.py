"""浏览记录查询"""

from fastapi import APIRouter

from app.db import get_db

router = APIRouter()


@router.get("/browsing/{ip}")
async def get_browsing(ip: str, limit: int = 100):
    db = get_db()
    rows = await db.fetchall(
        "SELECT domain, ts FROM browsing_logs WHERE ip = ? ORDER BY ts DESC LIMIT ?",
        (ip, limit),
    )
    return {"ip": ip, "logs": rows}
