"""局域网扫描"""

from fastapi import APIRouter, Query

from app.services.scanner import scan_ip_range

router = APIRouter()


@router.get("/scan")
async def scan_network(subnet: str = Query(..., description="网段，如 192.168.1.0/24")):
    ips = await scan_ip_range(subnet)
    return {"ok": True, "subnet": subnet, "ips": ips}
