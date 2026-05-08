from fastapi import APIRouter, Depends, Query

from app.auth import require_api_key
from app.models import CarrierVerification
from app.services.fmcsa import verify_carrier

router = APIRouter(tags=["Carrier"])


@router.get("/verify-mc", response_model=CarrierVerification)
async def verify_mc(
    mc_number: str = Query(..., description="MC number, digits only"),
    _key: str = Depends(require_api_key),
):
    result = await verify_carrier(mc_number)
    return result
