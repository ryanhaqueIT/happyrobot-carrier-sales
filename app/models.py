from pydantic import BaseModel
from typing import Optional


class Load(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None


class LoadSearchResponse(BaseModel):
    loads: list[Load]
    count: int


class VerifyMCRequest(BaseModel):
    mc_number: str


class CarrierVerification(BaseModel):
    verified: bool
    carrier_name: Optional[str] = None
    dot_number: Optional[str] = None
    allowed_to_operate: Optional[str] = None
    authority_status: Optional[str] = None
    insurance_on_file: Optional[bool] = None
    safety_rating: Optional[str] = None
    total_drivers: Optional[int] = None
    total_power_units: Optional[int] = None
    rejection_reason: Optional[str] = None


class NegotiationEntry(BaseModel):
    call_id: str
    round_number: int
    carrier_offer: Optional[float] = None
    agent_offer: Optional[float] = None
    accepted: bool = False


class CallRecord(BaseModel):
    call_id: str
    session_id: Optional[str] = None
    carrier_name: Optional[str] = None
    mc_number: Optional[str] = None
    equipment_type: Optional[str] = None
    load_id: Optional[str] = None
    offered_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    negotiation_rounds: int = 0
    call_duration: Optional[float] = None
    transcript: Optional[str] = None


class MetricsSummary(BaseModel):
    total_calls: int
    booked: int
    declined: int
    not_qualified: int
    no_match: int
    transferred: int
    dropped: int
    booking_rate: float
    avg_agreed_rate: Optional[float]
    avg_negotiation_rounds: float
    sentiment_positive: int
    sentiment_neutral: int
    sentiment_negative: int
    recent_calls: list[dict]
