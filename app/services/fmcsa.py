import httpx

from app.config import FMCSA_WEB_KEY

FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services"


async def verify_carrier(mc_number: str) -> dict:
    mc_clean = mc_number.strip().upper().replace("MC-", "").replace("MC", "").strip()

    if not mc_clean.isdigit():
        return {"verified": False, "rejection_reason": "Invalid MC number format"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        url = f"{FMCSA_BASE}/carriers/docket-number/{mc_clean}"
        resp = await client.get(url, params={"webKey": FMCSA_WEB_KEY})

        if resp.status_code != 200:
            return {"verified": False, "rejection_reason": "Could not reach FMCSA"}

        data = resp.json()
        content = data.get("content")

        if not content:
            return {"verified": False, "rejection_reason": "MC number not found in FMCSA database"}

        carrier = None
        if isinstance(content, list) and content:
            carrier = content[0].get("carrier", content[0])
        elif isinstance(content, dict):
            carrier = content.get("carrier", content)

        if not carrier:
            return {"verified": False, "rejection_reason": "MC number not found in FMCSA database"}

        allowed = carrier.get("allowedToOperate", "N")
        if allowed != "Y":
            return {
                "verified": False,
                "carrier_name": carrier.get("legalName"),
                "rejection_reason": "Carrier is not authorized to operate",
            }

        safety = carrier.get("safetyRating", "")
        if safety == "Unsatisfactory":
            return {
                "verified": False,
                "carrier_name": carrier.get("legalName"),
                "rejection_reason": "Carrier has an Unsatisfactory safety rating",
            }

        bipd_on_file = carrier.get("bipdInsuranceOnFile", "N")
        if bipd_on_file != "Y":
            return {
                "verified": False,
                "carrier_name": carrier.get("legalName"),
                "rejection_reason": "Required liability insurance not on file with FMCSA",
            }

        common_auth = carrier.get("commonAuthorityStatus", "")
        contract_auth = carrier.get("contractAuthorityStatus", "")
        if common_auth != "A" and contract_auth != "A":
            return {
                "verified": False,
                "carrier_name": carrier.get("legalName"),
                "rejection_reason": "Carrier does not have active operating authority",
            }

        return {
            "verified": True,
            "carrier_name": carrier.get("legalName"),
            "dot_number": str(carrier.get("dotNumber", "")),
            "allowed_to_operate": allowed,
            "authority_status": carrier.get("commonAuthorityStatus", "Unknown"),
            "insurance_on_file": bipd_on_file == "Y",
            "safety_rating": safety or "None",
            "total_drivers": carrier.get("totalDrivers"),
            "total_power_units": carrier.get("totalPowerUnits"),
        }
