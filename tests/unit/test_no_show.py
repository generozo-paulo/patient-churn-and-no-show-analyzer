import pytest
import pandas as pd
from src.schemas import AppointmentSchedulingPayload, NoShowPredictionResult
from src.no_show_engine import PatientNoShowEngine

def test_predict_appointment_contract():
    payload = AppointmentSchedulingPayload(
        appointment_id="APT-TEST-001",
        patient_id="PAC-TEST-001",
        lead_time_days=45,
        specialty="ORTOPEDIA",
        previous_no_shows_count=3,
        distance_to_clinic_km=25.0,
        appointment_cost_brl=250.0
    )
    result = PatientNoShowEngine.predict_appointment(payload)
    assert isinstance(result, NoShowPredictionResult)
    assert 0.0 <= result.no_show_probability <= 1.0
    assert result.risk_tier in ["LOW", "MEDIUM", "HIGH"]
    assert result.expected_revenue_loss_brl > 0.0
    assert result.recommended_action in ["STANDARD_CONFIRMATION", "ACTIVE_CALL_AND_WHATSAPP", "CONTROLLED_OVERBOOKING_SLOT"]

def test_generate_synthetic_appointments():
    df = PatientNoShowEngine.generate_synthetic_appointments(100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    assert "actual_no_show" in df.columns
    assert "lead_time_days" in df.columns
    assert "specialty" in df.columns

def test_oncology_protective_effect():
    payload_orto = AppointmentSchedulingPayload(
        appointment_id="APT-01",
        patient_id="PAC-01",
        lead_time_days=15,
        specialty="ORTOPEDIA",
        previous_no_shows_count=1,
        distance_to_clinic_km=10.0
    )
    payload_onco = AppointmentSchedulingPayload(
        appointment_id="APT-02",
        patient_id="PAC-02",
        lead_time_days=15,
        specialty="ONCOLOGIA",
        previous_no_shows_count=1,
        distance_to_clinic_km=10.0
    )
    res_orto = PatientNoShowEngine.predict_appointment(payload_orto)
    res_onco = PatientNoShowEngine.predict_appointment(payload_onco)
    assert res_onco.no_show_probability < res_orto.no_show_probability
