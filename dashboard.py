import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

# -----------------------------------
# CONFIG
# -----------------------------------
st.set_page_config(page_title="ICU Monitor", layout="wide")

API_URL = "https://icu-mlops-project.onrender.com/predict"

# -----------------------------------
# STYLE
# -----------------------------------
st.markdown("""
<style>
body {
    background-color: #0b0f1a;
}
.main-title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    color: #00ffcc;
}
.sub-text {
    text-align: center;
    color: #888;
}
.stButton>button {
    background-color: #00ffcc;
    color: black;
    font-weight: bold;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# ALERT LOGIC
# -----------------------------------
def generate_alerts(data, probability):
    alerts = []

    if probability > 0.7:
        alerts.append("🚨 CRITICAL RISK")

    if data["mean_spo2"] < 90:
        alerts.append("🫁 LOW SPO2")

    if data["mean_heart_rate"] > 110:
        alerts.append("❤️ HIGH HEART RATE")

    if data["mean_systolic_bp"] > 140:
        alerts.append("🩸 HIGH BP")

    if data["mean_temperature"] > 38:
        alerts.append("🌡️ FEVER")

    return alerts


# -----------------------------------
# UI
# -----------------------------------
st.markdown('<div class="main-title">ICU Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">AI-powered patient risk system</div>', unsafe_allow_html=True)

st.divider()

# -----------------------------------
# INPUTS
# -----------------------------------
st.header("Patient Input")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 0, 120, 65)
    LOS = st.number_input("Length of Stay", 0.0, 30.0, 3.5)

with col2:
    num_diagnoses = st.number_input("Diagnoses", 0, 20, 5)
    unique_diseases = st.number_input("Unique Diseases", 0, 20, 4)

with col3:
    num_meds = st.number_input("Medications", 0, 50, 8)

# -----------------------------------
# VITALS
# -----------------------------------
st.subheader("Vitals")

col4, col5, col6 = st.columns(3)

with col4:
    spo2 = st.number_input("SPO2", 70, 100, 92)

with col5:
    hr = st.number_input("Heart Rate", 40, 180, 95)

with col6:
    temp = st.number_input("Temperature (°C)", 30.0, 45.0, 38.0)

# -----------------------------------
# CLINICAL
# -----------------------------------
st.subheader("Clinical Parameters")

col7, col8, col9 = st.columns(3)

with col7:
    systolic_bp = st.number_input("Systolic BP", 60, 200, 110)

with col8:
    resp_rate = st.number_input("Respiratory Rate", 10, 40, 22)

with col9:
    vasopressor_flag = st.selectbox("Vasopressor Used?", [0, 1])

col10, col11 = st.columns(2)

with col10:
    antibiotic_flag = st.selectbox("Antibiotics Used?", [0, 1])

# -----------------------------------
# DATA PREP
# -----------------------------------
data = {
    "age": age,
    "LOS": LOS,
    "num_diagnoses": num_diagnoses,
    "unique_diseases": unique_diseases,
    "num_meds": num_meds,
    "vasopressor_flag": vasopressor_flag,
    "antibiotic_flag": antibiotic_flag,

    "mean_temperature": temp,
    "max_temperature": temp + 1,
    "min_temperature": temp - 1,

    "trend": 0.5,
    "rolling_mean": temp,

    "mean_spo2": spo2,
    "min_spo2": spo2 - 4,
    "spo2_low_flag": int(spo2 < 90),

    "max_systolic_bp": systolic_bp + 10,
    "min_systolic_bp": systolic_bp - 10,
    "mean_systolic_bp": systolic_bp,

    "mean_resp_rate": resp_rate,
    "max_resp_rate": resp_rate + 5,
    "std_resp_rate": 3,

    "mean_heart_rate": hr,
    "min_heart_rate": hr - 20,
    "std_heart_rate": 5
}

st.divider()

# -----------------------------------
# PREDICT
# -----------------------------------
if st.button("🚀 Predict ICU Risk", use_container_width=True):

    #st.info("⏳ Waking server... please wait")

    try:
        res = requests.post(API_URL, json=data, timeout=60)
        result = res.json()

        prob = result["risk_probability"]
        pred = result["prediction"]

    except Exception as e:
        st.error(f"API Error: {e}")
        st.stop()

    # -----------------------------------
    # RESULTS
    # -----------------------------------
    colA, colB = st.columns(2)

    with colA:
        st.metric("Risk Probability", f"{prob:.2f}")

    with colB:
        if pred == 1:
            st.error("🚨 HIGH RISK")
        else:
            st.success("✅ LOW RISK")

    # -----------------------------------
    # ALERTS
    # -----------------------------------
    st.subheader("🚨 Alerts")

    alerts = generate_alerts(data, prob)

    if alerts:
        for a in alerts:
            st.warning(a)
    else:
        st.success("Patient Stable")

    # -----------------------------------
    # GAUGE
    # -----------------------------------
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        title={'text': "Risk %"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 40], 'color': "green"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "red"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------
    # HISTORY
    # -----------------------------------
    history_file = "data/patient_history.csv"

    record = data.copy()
    record["prediction"] = pred
    record["probability"] = prob
    record["time"] = datetime.now()

    df_new = pd.DataFrame([record])

    if os.path.exists(history_file):
        df_old = pd.read_csv(history_file)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    os.makedirs("data", exist_ok=True)
    df_all.to_csv(history_file, index=False)

    st.subheader(" Recent Patients")
    st.dataframe(df_all.tail(10))