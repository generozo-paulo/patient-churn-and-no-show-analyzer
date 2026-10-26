from pydantic import BaseModel, Field
from typing import Literal

class AppointmentSchedulingPayload(BaseModel):
    appointment_id: str
    patient_id: str
    lead_time_days: int = Field(ge=0, le=180)
    specialty: Literal["CARDIOLOGIA", "ONCOLOGIA", "ORTOPEDIA", "OFTALMOLOGIA"]
    previous_no_shows_count: int = Field(ge=0)
    distance_to_clinic_km: float = Field(ge=0.0)
    appointment_cost_brl: float = 250.0

class NoShowPredictionResult(BaseModel):
    appointment_id: str
    no_show_probability: float = Field(ge=0.0, le=1.0)
    risk_tier: Literal["LOW", "MEDIUM", "HIGH"]
    expected_revenue_loss_brl: float
    recommended_action: Literal["STANDARD_CONFIRMATION", "ACTIVE_CALL_AND_WHATSAPP", "CONTROLLED_OVERBOOKING_SLOT"]
    net_roi_intervention_brl: float
