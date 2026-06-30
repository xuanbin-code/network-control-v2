"""学生机管理"""

from fastapi import APIRouter

from app.db import get_db

router = APIRouter()


@router.get("/machines")
async def list_machines():
    db = get_db()
    rows = await db.fetchall("SELECT * FROM machines ORDER BY online DESC, ip")
    return {"machines": rows}


@router.get("/status")
async def get_status():
    db = get_db()
    rows = await db.fetchall("SELECT * FROM machines ORDER BY online DESC, ip")
    return {"ok": True, "agents": rows}
