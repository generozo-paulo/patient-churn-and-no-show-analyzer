import numpy as np
import pandas as pd
from typing import List, Tuple
from src.schemas import AppointmentSchedulingPayload, NoShowPredictionResult

class PatientNoShowEngine:
    """
    Motor analítico de Machine Learning e Econometria em Saúde para predição de No-Show e ROI.
    """

    @staticmethod
    def generate_synthetic_appointments(n_appointments: int = 1500, random_state: int = 42) -> pd.DataFrame:
        """Gera base histórica ambulatorial com características comportamentais de agendamento."""
        np.random.seed(random_state)
        records = []
        specialties = ["CARDIOLOGIA", "ONCOLOGIA", "ORTOPEDIA", "OFTALMOLOGIA"]

        for i in range(n_appointments):
            lead_time = int(np.random.exponential(scale=18.0) + 1)
            prev_no_shows = int(np.random.poisson(lam=0.6))
            dist_km = float(np.random.exponential(scale=12.0) + 1.5)
            spec = str(np.random.choice(specialties, p=[0.35, 0.20, 0.25, 0.20]))
            cost = 250.0

            # Mecanismo de probabilidade de No-Show (regressão logística comportamental)
            z = -1.8 + (0.04 * lead_time) + (0.65 * prev_no_shows) + (0.03 * dist_km) - (0.4 if spec == "ONCOLOGIA" else 0.0)
            prob = 1.0 / (1.0 + np.exp(-z))
            actual_no_show = 1 if (np.random.rand() < prob) else 0

            records.append({
                "appointment_id": f"APT-{i+1:06d}",
                "patient_id": f"PAC-{np.random.randint(1000, 9999)}",
                "lead_time_days": lead_time,
                "specialty": spec,
                "previous_no_shows_count": prev_no_shows,
                "distance_to_clinic_km": round(dist_km, 1),
                "appointment_cost_brl": cost,
                "actual_no_show": actual_no_show
            })

        return pd.DataFrame(records)

    @staticmethod
    def predict_appointment(payload: AppointmentSchedulingPayload) -> NoShowPredictionResult:
        z = -1.8 + (0.04 * payload.lead_time_days) + (0.65 * payload.previous_no_shows_count) + (0.03 * payload.distance_to_clinic_km)
        if payload.specialty == "ONCOLOGIA":
            z -= 0.40 # consultas oncológicas têm menor evasão

        prob = float(1.0 / (1.0 + np.exp(-z)))
        expected_loss = float(prob * payload.appointment_cost_brl)

        if prob >= 0.55:
            risk = "HIGH"
            action = "CONTROLLED_OVERBOOKING_SLOT"
            # Custo da intervenção ativa (WhatsApp + Overbooking) ~R$ 15, com recuperação esperada de 65% do valor da consulta
            recovered_revenue = payload.appointment_cost_brl * 0.65
            net_roi = recovered_revenue - 15.0
        elif prob >= 0.28:
            risk = "MEDIUM"
            action = "ACTIVE_CALL_AND_WHATSAPP"
            recovered_revenue = payload.appointment_cost_brl * 0.40
            net_roi = recovered_revenue - 8.0
        else:
            risk = "LOW"
            action = "STANDARD_CONFIRMATION"
            net_roi = 0.0

        return NoShowPredictionResult(
            appointment_id=payload.appointment_id,
            no_show_probability=round(prob, 4),
            risk_tier=risk,
            expected_revenue_loss_brl=round(expected_loss, 2),
            recommended_action=action,
            net_roi_intervention_brl=round(net_roi, 2)
        )
