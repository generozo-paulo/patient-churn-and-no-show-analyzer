import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.schemas import AppointmentSchedulingPayload
from src.no_show_engine import PatientNoShowEngine

st.set_page_config(page_title="Hospital No-Show & Churn Predictive Engine", layout="wide", page_icon="🏥")

st.title("🏥 Patient Churn & No-Show Predictive Engine")
st.markdown("""
Motor de Machine Learning e Econometria em Saúde para predição precoce de absenteísmo ambulatorial (*No-Show*),
otimização de alocação de capacidade clínica e estratégias de *Safe Overbooking* com cálculo dinâmico de ROI.
""")

tabs = st.tabs(["📊 Simulador Clínico Individual", "📈 Coorte Ambulatorial (1.500 Consultas)", "💰 Análise de ROI & Overbooking"])

with tabs[0]:
    st.subheader("Predição de No-Show em Tempo Real por Consulta")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Parâmetros da Consulta")
        lead_time = st.slider("Lead Time (Dias até a consulta)", 1, 90, 21)
        specialty = st.selectbox("Especialidade Médica", ["CARDIOLOGIA", "ONCOLOGIA", "ORTOPEDIA", "OFTALMOLOGIA"])
        prev_no_shows = st.slider("Faltas anteriores nos últimos 12 meses", 0, 5, 2)
        dist_km = st.slider("Distância do Paciente até a Clínica (km)", 1.0, 60.0, 18.5, 0.5)
        cost = st.number_input("Custo da Consulta Ambulatorial (R$)", value=250.0, step=25.0)

        payload = AppointmentSchedulingPayload(
            appointment_id="APT-SIM-001",
            patient_id="PAC-SIM-882",
            lead_time_days=lead_time,
            specialty=specialty,
            previous_no_shows_count=prev_no_shows,
            distance_to_clinic_km=dist_km,
            appointment_cost_brl=cost
        )
        
        result = PatientNoShowEngine.predict_appointment(payload)
        
    with col2:
        st.markdown("### Avaliação de Risco & Recomendação Clínica")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric("Probabilidade de No-Show", f"{result.no_show_probability * 100:.1f}%")
        with metric_col2:
            st.metric("Tier de Risco", result.risk_tier)
        with metric_col3:
            st.metric("Perda Financeira Esperada", f"R$ {result.expected_revenue_loss_brl:.2f}")
            
        gauge_color = "#ef4444" if result.risk_tier == "HIGH" else "#f59e0b" if result.risk_tier == "MEDIUM" else "#10b981"
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = result.no_show_probability * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score de Absenteísmo (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': gauge_color},
                'steps': [
                    {'range': [0, 28], 'color': "rgba(16, 185, 129, 0.2)"},
                    {'range': [28, 55], 'color': "rgba(245, 158, 11, 0.2)"},
                    {'range': [55, 100], 'color': "rgba(239, 68, 68, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 55
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.info(f"**Ação Operacional Recomendada:** `{result.recommended_action}` | **ROI Líquido da Intervenção:** R$ {result.net_roi_intervention_brl:.2f}")

with tabs[1]:
    st.subheader("Análise Populacional Sintética de Absenteísmo")
    df = PatientNoShowEngine.generate_synthetic_appointments(1500)
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig_spec = px.histogram(df, x="specialty", color="actual_no_show", barmode="group",
                                title="Faltas Efetivas vs Comparecimento por Especialidade",
                                labels={"actual_no_show": "No-Show (1=Falta, 0=Presente)", "specialty": "Especialidade"})
        st.plotly_chart(fig_spec, use_container_width=True)
    with col_b:
        fig_lead = px.box(df, x="actual_no_show", y="lead_time_days", color="actual_no_show",
                          title="Lead Time (Dias) vs Ocorrência de No-Show",
                          labels={"actual_no_show": "No-Show"})
        st.plotly_chart(fig_lead, use_container_width=True)
        
    st.dataframe(df.head(10), use_container_width=True)

with tabs[2]:
    st.subheader("Modelagem Econômica de Recuperação de Receita & Overbooking")
    total_appointments = len(df)
    total_no_shows = df["actual_no_show"].sum()
    gross_loss = total_no_shows * 250.0
    recovered_conservative = gross_loss * 0.45
    intervention_costs = total_appointments * 4.5
    net_savings = recovered_conservative - intervention_costs
    roi_pct = (net_savings / intervention_costs) * 100 if intervention_costs > 0 else 0
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total de Agendamentos", f"{total_appointments:,}")
    with col_m2:
        st.metric("Taxa Global de No-Show", f"{(total_no_shows/total_appointments)*100:.1f}%")
    with col_m3:
        st.metric("Receita Recuperada", f"R$ {recovered_conservative:,.2f}")
    with col_m4:
        st.metric("ROI Operacional", f"{roi_pct:.1f}%")
        
    df_econ = pd.DataFrame({
        "Fluxo": ["Prejuízo Bruto por No-Show", "Receita Salva (Intervenção + Overbooking)", "Custo Operacional de Contato", "Resultado Líquido Positivo"],
        "Valor (R$)": [gross_loss, recovered_conservative, intervention_costs, net_savings]
    })
    fig_econ = px.bar(df_econ, x="Fluxo", y="Valor (R$)", color="Fluxo",
                      title="Demonstrativo de Impacto Econômico Hospitalar",
                      text_auto='.2s')
    st.plotly_chart(fig_econ, use_container_width=True)
