from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.auth import require_api_key
from app.models import LoadSearchResponse, Load
from app.services.loads import search_loads, get_load_by_id

router = APIRouter(tags=["Loads"])


@router.get("/loads", response_model=LoadSearchResponse)
async def list_loads(
    origin: Optional[str] = Query(None, description="Filter by origin city/state"),
    destination: Optional[str] = Query(None, description="Filter by destination city/state"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    min_rate: Optional[float] = Query(None, description="Minimum loadboard rate"),
    max_rate: Optional[float] = Query(None, description="Maximum loadboard rate"),
    _key: str = Depends(require_api_key),
):
    results = search_loads(origin, destination, equipment_type, min_rate, max_rate)
    return {"loads": results, "count": len(results)}


@router.get("/loads/{load_id}", response_model=Load)
async def get_load(load_id: str, _key: str = Depends(require_api_key)):
    load = get_load_by_id(load_id)
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load
