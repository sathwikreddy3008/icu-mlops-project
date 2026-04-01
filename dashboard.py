#dashboard.py
import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="ICU Monitor", layout="wide")

# -----------------------------------
# CUSTOM UI
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

.alert-blink {
    animation: blink 1s infinite;
    font-weight: bold;
    font-size: 18px;
}

@keyframes blink {
  50% { opacity: 0.3; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# ALERT LOGIC
# -----------------------------------
def generate_alerts(data, probability):
    alerts = []

    if probability > 0.7:
        alerts.append(("CRITICAL RISK", "🚨", "red"))
    elif probability > 0.4:
        alerts.append(("MEDIUM RISK", "⚠️", "orange"))

    if data["mean_spo2"] < 90:
        alerts.append(("LOW SPO2", "🫁", "red"))

    if data["mean_heart_rate"] > 110:
        alerts.append(("HIGH HEART RATE", "❤️", "orange"))

    if data["mean_heart_rate"] < 50:
        alerts.append(("LOW HEART RATE", "💓", "red"))

    if data["mean_systolic_bp"] > 140:
        alerts.append(("HIGH BP", "🩸", "orange"))

    if data["mean_systolic_bp"] < 90:
        alerts.append(("LOW BP", "🩸", "red"))

    if data["mean_temperature"] > 38:
        alerts.append(("FEVER", "🌡️", "orange"))

    if data["mean_temperature"] < 36:
        alerts.append(("HYPOTHERMIA", "❄️", "red"))

    return alerts


# -----------------------------------
# MAIN APP
# -----------------------------------
def main():

    st.markdown('<div class="main-title">ICU Monitoring Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">AI-powered patient risk system</div>', unsafe_allow_html=True)

    st.divider()

    # -----------------------------------
    # INPUTS
    # -----------------------------------
    st.header("Patient Input")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", 0, 120, 65, key="age")
        LOS = st.number_input("LOS", 0.0, 30.0, 3.5, key="los")

    with col2:
        num_diagnoses = st.number_input("Diagnoses", 0, 20, 5, key="diag")
        num_meds = st.number_input("Medications", 0, 50, 8, key="meds")

    with col3:
        mean_spo2 = st.number_input("SPO2", 70, 100, 92, key="spo2")
        mean_hr = st.number_input("Heart Rate", 40, 180, 95, key="hr")

    # -----------------------------------
    # DATA
    # -----------------------------------
    data = {
        "age": age,
        "LOS": LOS,
        "num_diagnoses": num_diagnoses,
        "unique_diseases": num_diagnoses,
        "num_meds": num_meds,
        "vasopressor_flag": 0,
        "antibiotic_flag": 0,
        "mean_temperature": 38,
        "max_temperature": 39,
        "min_temperature": 37,
        "trend": 0.5,
        "rolling_mean": 38,
        "mean_spo2": mean_spo2,
        "min_spo2": mean_spo2 - 4,
        "spo2_low_flag": int(mean_spo2 < 90),
        "max_systolic_bp": 130,
        "min_systolic_bp": 90,
        "mean_systolic_bp": 110,
        "mean_resp_rate": 22,
        "max_resp_rate": 28,
        "std_resp_rate": 3,
        "mean_heart_rate": mean_hr,
        "min_heart_rate": mean_hr - 20,
        "std_heart_rate": 5
    }

    st.divider()

    # -----------------------------------
    # PREDICT
    # -----------------------------------
    if st.button("Predict ICU Risk", use_container_width=True):

        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json=data,
                timeout=10
            )

            if response.status_code != 200:
                st.error(response.text)
                return

            result = response.json()

            prediction = result.get("prediction", 0)
            probability = result.get("risk_probability", 0)

        except Exception as e:
            st.error(f"API Error: {e}")
            return

        # -----------------------------------
        # KPI
        # -----------------------------------
        c1, c2, c3 = st.columns(3)
        c1.metric("Age", age)
        c2.metric("LOS", LOS)
        c3.metric("Risk %", f"{probability:.2f}")

        # -----------------------------------
        # ALERTS
        # -----------------------------------
        alerts = generate_alerts(data, probability)

        st.subheader("🚨 ICU Alerts")

        if alerts:
            for alert, icon, color in alerts:
                if color == "red":
                    st.markdown(f"<div class='alert-blink'>{icon} {alert}</div>", unsafe_allow_html=True)
                else:
                    st.warning(f"{icon} {alert}")
        else:
            st.success("✅ Patient Stable")

        # -----------------------------------
        # RESULT
        # -----------------------------------
        if prediction == 1:
            st.error(f"🚨 HIGH RISK ({probability:.2f})")
        else:
            st.success(f"✅ LOW RISK ({probability:.2f})")

        # -----------------------------------
        # TABS
        # -----------------------------------
        tab1, tab2, tab3 = st.tabs(["Risk Meter", "Charts", "History"])

        # -----------------------------------
        # GAUGE
        # -----------------------------------
        with tab1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probability * 100,
                title={'text': "ICU Risk"},
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
        # CHART
        # -----------------------------------
        with tab2:
            st.subheader("Heart Rate Trend")
            st.line_chart([mean_hr - 20, mean_hr, mean_hr + 5])

        # -----------------------------------
        # HISTORY (FIXED DUPLICATE ISSUE)
        # -----------------------------------
        with tab3:
            history_file = "data/patient_history.csv"

            record = data.copy()
            record["prediction"] = prediction
            record["probability"] = probability
            record["time"] = datetime.now()

            df_new = pd.DataFrame([record])

            if os.path.exists(history_file):
                df_old = pd.read_csv(history_file)
                df_all = pd.concat([df_old, df_new], ignore_index=True)
            else:
                df_all = df_new

            os.makedirs("data", exist_ok=True)
            df_all.to_csv(history_file, index=False)

            st.dataframe(df_all.tail(10))


# -----------------------------------
# RUN
# -----------------------------------
if __name__ == "__main__":
    main()