# Especificação Contratual (SDD) - Patient Churn & No-Show Predictive Analytics

## 1. Escopo & Objetivos
Pipeline de Machine Learning e Econometria em Saúde para predição de faltas em consultas ambulatoriais e exames de imagem (**No-Show**) e abandono de tratamento/churn de pacientes em clínicas de especialidades.
Calcula o ROI de intervenções preventivas automatizadas (lembretes via WhatsApp/SMS, overbooking inteligente controlado e reescalonamento dinâmico).

## 2. Contratos de Entrada (Pydantic)

### 2.1 Agendamento Ambulatorial (`AppointmentSchedulingPayload`)
- `appointment_id`: str
- `patient_id`: str
- `lead_time_days`: int = Field(ge=0, le=180) # dias entre agendamento e consulta
- `specialty`: Literal["CARDIOLOGIA", "ONCOLOGIA", "ORTOPEDIA", "OFTALMOLOGIA"]
- `previous_no_shows_count`: int = Field(ge=0)
- `distance_to_clinic_km`: float = Field(ge=0.0)
- `appointment_cost_brl`: float = 250.0

## 3. Contratos de Saída (Pydantic)

### 3.1 Previsão de No-Show (`NoShowPredictionResult`)
- `appointment_id`: str
- `no_show_probability`: float = Field(ge=0.0, le=1.0)
- `risk_tier`: Literal["LOW", "MEDIUM", "HIGH"]
- `expected_revenue_loss_brl`: float
- `recommended_action`: Literal["STANDARD_CONFIRMATION", "ACTIVE_CALL_AND_WHATSAPP", "CONTROLLED_OVERBOOKING_SLOT"]
- `net_roi_intervention_brl`: float
