"""黑白名单规则管理"""

from fastapi import APIRouter, HTTPException

from app.db import get_db
from app.schemas import RuleCreateRequest
from app.services.ws_manager import ws_manager

router = APIRouter()


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
