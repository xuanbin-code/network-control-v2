"""HTTP API：供 Electron 前端和外部教学软件调用"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from shared.protocol import MsgType, FilterMode

from .db import get_db
from .ws_server import ws_manager


router = APIRouter(prefix="/api")


class SetFilterRequest(BaseModel):
    mode: str
    targets: Optional[List[str]] = None


class RuleCreateRequest(BaseModel):
    domain: str


class SettingUpdateRequest(BaseModel):
    key: str
    value: str


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/machines")
async def list_machines():
    db = get_db()
    rows = await db.fetchall("SELECT * FROM machines ORDER BY ip")
    return {"machines": rows}


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
        # 全部
        await db.execute("UPDATE machines SET mode = ?", (req.mode,))
    else:
        for ip in targets:
            await db.execute(
                "UPDATE machines SET mode = ? WHERE ip = ?", (req.mode, ip)
            )

    await ws_manager.broadcast({
        "type": MsgType.SET_FILTER,
        "payload": {"mode": req.mode},
    }, targets=targets or None)

    return {"ok": True, "mode": req.mode, "targets": targets}


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
    await ws_manager.broadcast({
        "type": MsgType.UPDATE_RULES,
        "payload": await _build_rules_payload(),
    })
    return {"ok": True}


@router.delete("/rules/{list_type}/{rule_id}")
async def delete_rule(list_type: str, rule_id: int):
    if list_type not in ("whitelist", "blacklist"):
        raise HTTPException(status_code=400, detail="Invalid list type")
    table = f"{list_type}_rules"
    db = get_db()
    await db.execute(f"DELETE FROM {table} WHERE id = ?", (rule_id,))
    await ws_manager.broadcast({
        "type": MsgType.UPDATE_RULES,
        "payload": await _build_rules_payload(),
    })
    return {"ok": True}


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
    return {"ok": True}


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
