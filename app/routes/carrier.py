from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.models import VerifyMCRequest, CarrierVerification
from app.services.fmcsa import verify_carrier

router = APIRouter(tags=["Carrier"])


@router.post("/verify-mc", response_model=CarrierVerification)
async def verify_mc(body: VerifyMCRequest, _key: str = Depends(require_api_key)):
    result = await verify_carrier(body.mc_number)
    return result
