"""HTTP API：供 Electron 前端和外部教学软件调用"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.protocol import MsgType, FilterMode

from .db import get_db
from .ws_server import ws_manager
from .scanner import scan_ip_range
from .config import WS_PORT


router = APIRouter(prefix="/api")


class SetFilterRequest(BaseModel):
    mode: str
    targets: Optional[List[str]] = None


class RuleCreateRequest(BaseModel):
    domain: str


class SettingUpdateRequest(BaseModel):
    key: str
    value: str


class TestMessageRequest(BaseModel):
    message: str
    targets: Optional[List[str]] = None


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/server_info")
async def server_info():
    """返回教师端 IP 和 WebSocket 地址"""
    local_ip = ws_manager._get_local_ip()
    return {
        "ip": local_ip,
        "ws_url": f"ws://{local_ip}:{WS_PORT}/ws",
        "ws_port": WS_PORT,
    }


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


@router.get("/scan")
async def scan_network(subnet: str = Query(..., description="网段，如 192.168.1.0/24")):
    ips = await scan_ip_range(subnet)
    return {"ok": True, "subnet": subnet, "ips": ips}


@router.get("/rules")
async def list_rules():
    db = get_db()
    whitelist = await db.fetchall("SELECT * FROM whitelist_rules ORDER BY domain")
    blacklist = await db.fetchall("SELECT * FROM blacklist_rules ORDER BY domain")
    return {"whitelist": whitelist, "blacklist": blacklist}


@router.post("/rules/{list_type}")
async def add_rule(list_type: str, req: RuleCreateRequest):
    if list_type not in ("whitelist", "blacklist"):
        raise HTTPException(status_code=400, detail="Invalid list type")
    table = f"{list_type}_rules"
    db = get_db()
    await db.execute(
        f"INSERT OR IGNORE INTO {table} (domain) VALUES (?)", (req.domain,)
    )
    await ws_manager.push_rules()
    return {"ok": True}


@router.delete("/rules/{list_type}/{rule_id}")
async def delete_rule(list_type: str, rule_id: int):
    if list_type not in ("whitelist", "blacklist"):
        raise HTTPException(status_code=400, detail="Invalid list type")
    table = f"{list_type}_rules"
    db = get_db()
    await db.execute(f"DELETE FROM {table} WHERE id = ?", (rule_id,))
    await ws_manager.push_rules()
    return {"ok": True}


@router.post("/rules/{list_type}/{rule_id}/toggle")
async def toggle_rule(list_type: str, rule_id: int):
    if list_type not in ("whitelist", "blacklist"):
        raise HTTPException(status_code=400, detail="Invalid list type")
    table = f"{list_type}_rules"
    db = get_db()
    row = await db.fetchone(f"SELECT enabled FROM {table} WHERE id = ?", (rule_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Rule not found")
    new_state = 0 if row["enabled"] else 1
    await db.execute(f"UPDATE {table} SET enabled = ? WHERE id = ?", (new_state, rule_id))
    await ws_manager.push_rules()
    return {"ok": True, "enabled": bool(new_state)}


@router.get("/browsing/{ip}")
async def get_browsing(ip: str, limit: int = 100):
    db = get_db()
    rows = await db.fetchall(
        "SELECT domain, ts FROM browsing_logs WHERE ip = ? ORDER BY ts DESC LIMIT ?",
        (ip, limit),
    )
    return {"ip": ip, "logs": rows}


@router.get("/settings")
async def get_settings():
    db = get_db()
    return await db.get_settings()


@router.post("/settings")
async def update_setting(req: SettingUpdateRequest):
    db = get_db()
    await db.set_setting(req.key, req.value)
    # 设置变更后重新下发规则
    if req.key in ("filter_mode", "lan_subnets", "upstream_dns"):
        await ws_manager.push_rules()
    return {"ok": True}


@router.post("/test/send")
async def send_test_message(req: TestMessageRequest):
    """向学生端发送测试消息"""
    await ws_manager.send_test_message(req.message, targets=req.targets or None)
    return {
        "ok": True,
        "message": req.message,
        "targets": req.targets or "all",
    }


async def _build_rules_payload() -> dict:
    db = get_db()
    whitelist = await db.fetchall(
        "SELECT domain FROM whitelist_rules WHERE enabled = 1"
    )
    blacklist = await db.fetchall(
        "SELECT domain FROM blacklist_rules WHERE enabled = 1"
    )
    return {
        "whitelist": [r["domain"] for r in whitelist],
        "blacklist": [r["domain"] for r in blacklist],
    }
