"""网络控制：模式切换、单台控制"""

from fastapi import APIRouter, HTTPException, Query

from shared.protocol import FilterMode

from app.db import get_db
from app.schemas import SetFilterRequest
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.post("/network/set")
async def set_network(req: SetFilterRequest):
    if req.mode not in (
        FilterMode.NORMAL,
        FilterMode.WHITELIST,
        FilterMode.BLACKLIST,
        FilterMode.DISCONNECT,
    ):
        raise HTTPException(status_code=400, detail="Invalid mode")

    db = get_db()
    targets = req.targets or []
    if not targets:
        await db.execute("UPDATE machines SET mode = ?", (req.mode,))
    else:
        for ip in targets:
            await db.execute(
                "UPDATE machines SET mode = ? WHERE ip = ?", (req.mode, ip)
            )

    await ws_manager.set_filter(req.mode, targets=targets or None)

    return {"ok": True, "mode": req.mode, "targets": targets}


# 兼容原 Network_Control 的 HTTP 控制接口
@router.get("/network/enable")
@router.post("/network/enable")
async def enable_network():
    await ws_manager.set_filter(FilterMode.NORMAL)
    db = get_db()
    await db.execute("UPDATE machines SET mode = ?", (FilterMode.NORMAL,))
    return {"ok": True, "action": "enable", "message": "已下发『全部允许上网』指令"}


@router.get("/network/disable")
@router.post("/network/disable")
async def disable_network():
    await ws_manager.set_filter(FilterMode.DISCONNECT)
    db = get_db()
    await db.execute("UPDATE machines SET mode = ?", (FilterMode.DISCONNECT,))
    return {"ok": True, "action": "disable", "message": "已下发『禁止上网』指令"}


@router.get("/network/enable_ip")
@router.post("/network/enable_ip")
async def enable_ip(ip: str = Query(..., description="学生端 IP")):
    ip = ip.strip()
    if not ip:
        raise HTTPException(status_code=400, detail="missing ip")
    await ws_manager.set_filter(FilterMode.NORMAL, targets=[ip])
    db = get_db()
    await db.execute("UPDATE machines SET mode = ? WHERE ip = ?", (FilterMode.NORMAL, ip))
    return {"ok": True, "action": "enable_ip", "ip": ip,
            "message": f"已下发『允许上网』指令: {ip}"}


@router.get("/network/disable_ip")
@router.post("/network/disable_ip")
async def disable_ip(ip: str = Query(..., description="学生端 IP")):
    ip = ip.strip()
    if not ip:
        raise HTTPException(status_code=400, detail="missing ip")
    await ws_manager.set_filter(FilterMode.DISCONNECT, targets=[ip])
    db = get_db()
    await db.execute("UPDATE machines SET mode = ? WHERE ip = ?", (FilterMode.DISCONNECT, ip))
    return {"ok": True, "action": "disable_ip", "ip": ip,
            "message": f"已下发『禁止上网』指令: {ip}"}
