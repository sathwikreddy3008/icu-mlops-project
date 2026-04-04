import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="ICU · Risk Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🩺"
)

API_URL = "https://icu-mlops-project.onrender.com/predict"

# ══════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700&family=Bebas+Neue&display=swap" rel="stylesheet">

<style>
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main {
    background: #0c0f18 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #dde4f0 !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
#MainMenu, footer { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.block-container {
    padding: 0 2.5rem 5rem !important;
    max-width: 1300px !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0c0f18; }
::-webkit-scrollbar-thumb { background: #252d3d; border-radius: 4px; }

/* ── TOP BAR ── */
.topbar {
    position: sticky; top: 0; z-index: 999;
    background: rgba(12,15,24,0.95);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid #1b2235;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 2.5rem; height: 62px;
    margin: 0 -2.5rem 3rem;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.brand-mark {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #e53e3e, #fc8181);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    box-shadow: 0 0 18px rgba(229,62,62,0.45);
}
.brand-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 21px; letter-spacing: 2.5px; color: #fff;
}
.brand-sub {
    font-size: 10.5px; color: #3d4f6a;
    letter-spacing: 1.5px; text-transform: uppercase; margin-top: 1px;
}
.topbar-right { display: flex; align-items: center; gap: 14px; }
.chip {
    background: #131926; border: 1px solid #1e2a3d;
    border-radius: 7px; padding: 5px 13px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 600; color: #546a8a;
    letter-spacing: 0.8px;
}
.live-dot {
    display: flex; align-items: center; gap: 7px;
    font-size: 12px; font-weight: 700; color: #48bb78;
}
.pulse { width: 7px; height: 7px; background: #48bb78;
    border-radius: 50%; animation: glow 2s ease-in-out infinite; }
@keyframes glow {
    0%,100% { box-shadow: 0 0 0 0 rgba(72,187,120,.5); }
    50%      { box-shadow: 0 0 0 5px rgba(72,187,120,0); }
}

/* ── SECTION HEADER ── */
.sh {
    display: flex; align-items: center; gap: 11px;
    margin-bottom: 1.1rem;
}
.sh-icon {
    width: 30px; height: 30px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
}
.ic-b { background: rgba(66,153,225,.13); }
.ic-t { background: rgba(56,178,172,.13); }
.ic-p { background: rgba(159,122,234,.13); }
.ic-r { background: rgba(229,62,62,.13); }
.sh-label {
    font-size: 11.5px; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase; color: #8899b5;
}
.sh-rule { flex: 1; height: 1px;
    background: linear-gradient(90deg, #1e2a3d 0%, transparent 100%); }

/* ── INPUT SECTION BACKGROUND ── */
/* We style the stHorizontalBlock (row of columns) container */
[data-testid="stHorizontalBlock"] {
    background: #131926 !important;
    border: 1px solid #1b2437 !important;
    border-radius: 14px !important;
    padding: 1.4rem 1.6rem !important;
    margin-bottom: 0 !important;
    gap: 1.5rem !important;
}

/* left-accent bar per section — injected via pseudo on wrapper */
.accent-blue  [data-testid="stHorizontalBlock"] { border-left: 3px solid #4299e1 !important; }
.accent-teal  [data-testid="stHorizontalBlock"] { border-left: 3px solid #38b2ac !important; }
.accent-purple[data-testid="stHorizontalBlock"] { border-left: 3px solid #9f7aea !important; }

/* ── NUMBER INPUTS ── */
[data-testid="stNumberInput"] input {
    background: #0c0f18 !important;
    border: 1px solid #242f44 !important;
    color: #e2e8f0 !important;
    border-radius: 9px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 15px !important; font-weight: 500 !important;
    padding: 10px 12px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: #4299e1 !important;
    box-shadow: 0 0 0 3px rgba(66,153,225,.14) !important;
    outline: none !important;
}
[data-testid="stNumberInput"] button {
    background: #1a2030 !important;
    border-color: #242f44 !important;
    color: #6b7fa0 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #0c0f18 !important;
    border: 1px solid #242f44 !important;
    color: #e2e8f0 !important;
    border-radius: 9px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11.5px !important; font-weight: 700 !important;
    color: #6b7fa0 !important;
    letter-spacing: 0.8px !important; text-transform: uppercase !important;
    margin-bottom: 5px !important;
}

/* ── PREDICT BUTTON ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #e53e3e 0%, #c53030 100%) !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13.5px !important; font-weight: 800 !important;
    letter-spacing: 2.5px !important; text-transform: uppercase !important;
    border: none !important; border-radius: 12px !important;
    padding: 1rem 2rem !important; width: 100% !important;
    transition: all .22s ease !important;
    box-shadow: 0 4px 22px rgba(229,62,62,.32) !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(229,62,62,.48) !important;
}

/* ── RESULT CARDS ── */
.res-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.res-card {
    background: #131926; border: 1px solid #1b2437;
    border-radius: 16px; padding: 2rem 2.5rem;
    text-align: center; position: relative; overflow: hidden;
}
.res-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.res-card.rp::before { background: linear-gradient(90deg, transparent, #4299e1, transparent); }
.res-card.rv::before { background: linear-gradient(90deg, transparent, #9f7aea, transparent); }
.res-eyebrow {
    font-size: 10px; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase; color: #3d4f6a; margin-bottom: 1rem;
}
.res-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 88px; line-height: .95; letter-spacing: -1px;
}
.res-sub { font-size: 12px; color: #546a8a; margin-top: 10px; letter-spacing: .3px; }
.clr-blue  { color: #63b3ed; }
.clr-red   { color: #fc8181; }
.clr-green { color: #68d391; }
.clr-amber { color: #f6ad55; }
.badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 22px; border-radius: 40px;
    font-size: 14px; font-weight: 700; letter-spacing: .5px;
    margin: 12px 0 8px;
}
.bdg-r { background: rgba(229,62,62,.13); border: 1px solid rgba(229,62,62,.38); color: #fc8181; }
.bdg-g { background: rgba(72,187,120,.10); border: 1px solid rgba(72,187,120,.30); color: #68d391; }

/* ── VITAL CARDS ── */
.vital-grid {
    display: grid; grid-template-columns: repeat(6,1fr);
    gap: 12px; margin-bottom: 20px;
}
.vcard {
    background: #131926; border: 1px solid #1b2437;
    border-radius: 13px; padding: 1.1rem 1rem;
    text-align: center; position: relative;
    transition: border-color .2s;
}
.vcard:hover { border-color: #2a3a55; }
.vcard-label {
    font-size: 10px; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase; color: #3d4f6a;
    margin-bottom: 6px;
}
.vcard-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 26px; font-weight: 700; line-height: 1;
}
.vcard-unit { font-size: 12px; color: #546a8a; margin-top: 3px; }
.vcard-bar {
    position: absolute; bottom: 0; left: 0;
    height: 3px; border-radius: 0 0 13px 13px;
    width: 100%;
}
.bar-red    { background: linear-gradient(90deg, #e53e3e, #fc8181); }
.bar-green  { background: linear-gradient(90deg, #38a169, #68d391); }
.bar-amber  { background: linear-gradient(90deg, #c05621, #f6ad55); }
.bar-blue   { background: linear-gradient(90deg, #2b6cb0, #63b3ed); }

/* ── GAUGE WRAPPER ── */
.gauge-wrap {
    background: #131926; border: 1px solid #1b2437;
    border-radius: 16px; padding: .5rem;
    margin-bottom: 20px;
}

/* ── ALERT PILLS ── */
.alert-box {
    background: #131926; border: 1px solid #1b2437;
    border-radius: 14px; padding: 1.2rem 1.4rem;
    display: flex; flex-wrap: wrap; gap: 10px;
    margin-bottom: 20px;
}
.ap {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 15px; border-radius: 8px;
    font-size: 13px; font-weight: 600;
    animation: fade .35s ease both;
}
@keyframes fade {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.ap-r { background: rgba(229,62,62,.09); border: 1px solid rgba(229,62,62,.32); color: #fc8181; }
.ap-a { background: rgba(237,137,54,.09); border: 1px solid rgba(237,137,54,.30); color: #fbd38d; }
.ap-g { background: rgba(72,187,120,.08); border: 1px solid rgba(72,187,120,.28); color: #68d391; }

/* ── TABLE ── */
[data-testid="stDataFrame"] {
    background: #131926 !important;
    border: 1px solid #1b2437 !important;
    border-radius: 13px !important; overflow: hidden !important;
}

/* ── DIVIDER ── */
.gap { margin-bottom: 2rem; }

/* ── FOOTER ── */
.foot {
    text-align: center; padding: 2rem 0 0;
    font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;
    color: #1e2a3d; border-top: 1px solid #131926; margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════
def generate_alerts(data, prob):
    a = []
    if prob > 0.7:
        a.append(("🚨", "CRITICAL — Immediate intervention required", "r"))
    if data["mean_spo2"] < 90:
        a.append(("🫁", f"LOW SpO₂ · {data['mean_spo2']}% — Hypoxemia", "a"))
    if data["mean_heart_rate"] > 110:
        a.append(("❤️", f"TACHYCARDIA · {data['mean_heart_rate']} bpm", "a"))
    if data["mean_systolic_bp"] > 140:
        a.append(("🩸", f"HYPERTENSION · SBP {data['mean_systolic_bp']} mmHg", "a"))
    if data["mean_temperature"] > 38:
        a.append(("🌡️", f"FEVER · {data['mean_temperature']}°C", "a"))
    return a


# ══════════════════════════════════════════
#  TOP NAV
# ══════════════════════════════════════════
now_str = datetime.now().strftime("%d %b %Y  %H:%M")
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="brand-mark">🩺</div>
    <div>
      <div class="brand-name">ICU Risk Monitoring Dashboard</div>
      <div class="brand-sub">Clinical Decision Support · XGBoost v2</div>
    </div>
  </div>
  <div class="topbar-right">
    <div class="chip">ROC-AUC 0.91</div>
    <div class="chip">{now_str}</div>
    <div class="live-dot"><div class="pulse"></div> Live</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════
#  SECTION 1 — DEMOGRAPHICS
# ══════════════════════════════════════════
st.markdown("""
<div class="sh">
  <div class="sh-icon ic-b">👤</div>
  <div class="sh-label">Patient Demographics</div>
  <div class="sh-rule"></div>
</div>""", unsafe_allow_html=True)

with st.container():
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: age = st.number_input("Age (yrs)", 0, 120, 65)
    with c2: LOS = st.number_input("Stay (days)", 0.0, 30.0, 3.5, step=0.5)
    with c3: num_diagnoses = st.number_input("Diagnoses", 0, 20, 5)
    with c4: unique_diseases = st.number_input("Unique Diseases", 0, 20, 4)
    with c5: num_meds = st.number_input("Medications", 0, 50, 8)

st.markdown('<div class="gap"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
#  SECTION 2 — VITALS
# ══════════════════════════════════════════
st.markdown("""
<div class="sh">
  <div class="sh-icon ic-t">💓</div>
  <div class="sh-label">Vital Signs</div>
  <div class="sh-rule"></div>
</div>""", unsafe_allow_html=True)

with st.container():
    v1,v2,v3 = st.columns(3)
    with v1: spo2 = st.number_input("SpO₂ (%)", 70, 100, 92)
    with v2: hr   = st.number_input("Heart Rate (bpm)", 40, 180, 95)
    with v3: temp = st.number_input("Temperature (°C)", 30.0, 45.0, 38.0, step=0.1)

st.markdown('<div class="gap"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
#  SECTION 3 — CLINICAL
# ══════════════════════════════════════════
st.markdown("""
<div class="sh">
  <div class="sh-icon ic-p">⚕️</div>
  <div class="sh-label">Clinical Parameters</div>
  <div class="sh-rule"></div>
</div>""", unsafe_allow_html=True)

with st.container():
    p1,p2,p3,p4 = st.columns(4)
    with p1: systolic_bp = st.number_input("Systolic BP (mmHg)", 60, 200, 110)
    with p2: resp_rate   = st.number_input("Resp. Rate (/min)", 10, 40, 22)
    with p3: vasopressor_flag = st.selectbox("Vasopressor?", [0,1], format_func=lambda x: "Yes" if x else "No")
    with p4: antibiotic_flag  = st.selectbox("Antibiotics?",  [0,1], format_func=lambda x: "Yes" if x else "No")

st.markdown('<div class="gap"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════
data = {
    "age": age, "LOS": LOS,
    "num_diagnoses": num_diagnoses, "unique_diseases": unique_diseases, "num_meds": num_meds,
    "vasopressor_flag": vasopressor_flag, "antibiotic_flag": antibiotic_flag,
    "mean_temperature": temp, "max_temperature": temp+1, "min_temperature": temp-1,
    "trend": 0.5, "rolling_mean": temp,
    "mean_spo2": spo2, "min_spo2": spo2-4, "spo2_low_flag": int(spo2 < 90),
    "max_systolic_bp": systolic_bp+10, "min_systolic_bp": systolic_bp-10, "mean_systolic_bp": systolic_bp,
    "mean_resp_rate": resp_rate, "max_resp_rate": resp_rate+5, "std_resp_rate": 3,
    "mean_heart_rate": hr, "min_heart_rate": hr-20, "std_heart_rate": 5,
}


# ══════════════════════════════════════════
#  PREDICT BUTTON
# ══════════════════════════════════════════
st.markdown("""
<div class="sh">
  <div class="sh-icon ic-r">⚡</div>
  <div class="sh-label">Run Analysis</div>
  <div class="sh-rule"></div>
</div>""", unsafe_allow_html=True)

if st.button("ANALYSE PATIENT RISK  →", use_container_width=True):

    with st.spinner(
    "Running XGBoost inference...\n"
    "\nIf you encounter an API error, please try again — the service may still be initializing."
    ):
        try:
            res    = requests.post(API_URL, json=data, timeout=60)
            result = res.json()
            prob   = result["risk_probability"]
            pred   = result["prediction"]
        except Exception as e:
            st.error(f"API Error: {e}")
            st.stop()

    pct = int(prob * 100)

    # ── VITAL SNAPSHOT CARDS ──
    st.markdown('<div class="gap"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sh">
      <div class="sh-icon ic-t">💊</div>
      <div class="sh-label">Vital Snapshot</div>
      <div class="sh-rule"></div>
    </div>""", unsafe_allow_html=True)

    def bc(val, lo, hi):
        if val < lo: return "bar-red"
        if val > hi: return "bar-amber"
        return "bar-green"

    spo2_b = "bar-red"   if spo2 < 90 else "bar-green"
    hr_b   = "bar-red"   if hr > 110  else "bar-green"
    tmp_b  = "bar-amber" if temp > 38 else "bar-green"
    sbp_b  = "bar-amber" if systolic_bp > 140 else "bar-green"

    st.markdown(f"""
    <div class="vital-grid">
      <div class="vcard">
        <div class="vcard-label">SpO₂</div>
        <div class="vcard-val {'clr-red' if spo2<90 else 'clr-green'}">{spo2}</div>
        <div class="vcard-unit">%</div>
        <div class="vcard-bar {spo2_b}"></div>
      </div>
      <div class="vcard">
        <div class="vcard-label">Heart Rate</div>
        <div class="vcard-val {'clr-red' if hr>110 else 'clr-green'}">{hr}</div>
        <div class="vcard-unit">bpm</div>
        <div class="vcard-bar {hr_b}"></div>
      </div>
      <div class="vcard">
        <div class="vcard-label">Temperature</div>
        <div class="vcard-val {'clr-amber' if temp>38 else 'clr-green'}">{temp}</div>
        <div class="vcard-unit">°C</div>
        <div class="vcard-bar {tmp_b}"></div>
      </div>
      <div class="vcard">
        <div class="vcard-label">Systolic BP</div>
        <div class="vcard-val {'clr-amber' if systolic_bp>140 else 'clr-green'}">{systolic_bp}</div>
        <div class="vcard-unit">mmHg</div>
        <div class="vcard-bar {sbp_b}"></div>
      </div>
      <div class="vcard">
        <div class="vcard-label">Resp Rate</div>
        <div class="vcard-val clr-blue">{resp_rate}</div>
        <div class="vcard-unit">/min</div>
        <div class="vcard-bar bar-blue"></div>
      </div>
      <div class="vcard">
        <div class="vcard-label">Stay</div>
        <div class="vcard-val clr-blue">{LOS}</div>
        <div class="vcard-unit">days</div>
        <div class="vcard-bar bar-blue"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RESULT CARDS + GAUGE ──
    st.markdown("""
    <div class="sh">
      <div class="sh-icon ic-r">🎯</div>
      <div class="sh-label">Prediction Results</div>
      <div class="sh-rule"></div>
    </div>""", unsafe_allow_html=True)

    pct_clr = "clr-red" if pct >= 70 else "clr-amber" if pct >= 40 else "clr-green"
    verdict = "⚠️ HIGH RISK" if pred == 1 else "✅ LOW RISK"
    bdg_cls = "bdg-r" if pred == 1 else "bdg-g"
    vrd_sub = "Immediate escalation required" if pred == 1 else "Continue standard monitoring"

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(f"""
        <div class="res-card rp" style="height:100%">
          <div class="res-eyebrow">Mortality Risk Probability</div>
          <div class="res-num {pct_clr}">{pct}<span style="font-size:40px">%</span></div>
          <div class="res-sub">XGBoost · MIMIC-III · 70+ clinical features</div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown(f"""
        <div class="res-card rv" style="height:100%">
          <div class="res-eyebrow">Clinical Verdict</div>
          <div style="margin:1rem 0">
            <span class="badge {bdg_cls}">{verdict}</span>
          </div>
          <div class="res-sub">{vrd_sub}</div>
          <div style="margin-top:1.5rem; display:flex; gap:24px; justify-content:center; text-align:left">
            <div>
              <div style="font-size:10px;color:#3d4f6a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px">Vasopressor</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{"Active" if vasopressor_flag else "None"}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#3d4f6a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px">Antibiotics</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{"Active" if antibiotic_flag else "None"}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#3d4f6a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px">Diagnoses</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{num_diagnoses}</div>
            </div>
            <div>
              <div style="font-size:10px;color:#3d4f6a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px">Medications</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:14px;color:#e2e8f0;font-weight:600">{num_meds}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── GAUGE ──
    bar_color = "#fc8181" if pct >= 70 else "#f6ad55" if pct >= 40 else "#68d391"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={'suffix': '%', 'font': {'size': 44, 'color': bar_color, 'family': 'JetBrains Mono'}},
        title={'text': "RISK PROBABILITY GAUGE", 'font': {'size': 11, 'color': '#3d4f6a', 'family': 'DM Sans'}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': '#252d3d',
                'tickfont': {'color': '#3d4f6a', 'size': 10, 'family': 'JetBrains Mono'},
                'nticks': 6,
            },
            'bar': {'color': bar_color, 'thickness': 0.20},
            'bgcolor': '#0c0f18',
            'borderwidth': 0,
            'steps': [
                {'range': [0,  40], 'color': 'rgba(104,211,145,.07)'},
                {'range': [40, 70], 'color': 'rgba(246,173,85,.07)'},
                {'range': [70,100], 'color': 'rgba(252,129,129,.09)'},
            ],
            'threshold': {
                'line': {'color': bar_color, 'width': 3},
                'thickness': 0.75,
                'value': pct,
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(19,25,38,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=30, r=30, t=50, b=20),
        height=230,
    )

    st.markdown('<div class="gauge-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── ALERTS ──
    st.markdown("""
    <div class="sh">
      <div class="sh-icon ic-r">🔔</div>
      <div class="sh-label">Clinical Alerts</div>
      <div class="sh-rule"></div>
    </div>""", unsafe_allow_html=True)

    alerts = generate_alerts(data, prob)
    pills = ""
    if alerts:
        for i, (icon, msg, col) in enumerate(alerts):
            pills += f'<div class="ap ap-{col}" style="animation-delay:{i*0.07}s">{icon}&nbsp; {msg}</div>'
    else:
        pills = '<div class="ap ap-g">✅&nbsp; All vitals within normal limits — patient stable</div>'

    st.markdown(f'<div class="alert-box">{pills}</div>', unsafe_allow_html=True)

    # ── HISTORY TABLE ──
    st.markdown("""
    <div class="sh">
      <div class="sh-icon ic-b">📋</div>
      <div class="sh-label">Prediction History</div>
      <div class="sh-rule"></div>
    </div>""", unsafe_allow_html=True)

    history_file = "data/patient_history.csv"
    record = data.copy()
    record.update({"probability": round(prob, 4), "prediction": pred,
                   "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    df_new = pd.DataFrame([record])
    if os.path.exists(history_file):
        df_all = pd.concat([pd.read_csv(history_file), df_new], ignore_index=True)
    else:
        df_all = df_new
    os.makedirs("data", exist_ok=True)
    df_all.to_csv(history_file, index=False)

    cols = ["time","age","LOS","mean_heart_rate","mean_spo2","mean_systolic_bp","mean_temperature","probability","prediction"]
    show = df_all[cols].tail(8).copy()
    show.columns = ["Time","Age","Stay","HR","SpO₂","SBP","Temp","Risk %","Class"]
    show["Class"]  = show["Class"].map({1: "🔴 HIGH", 0: "🟢 LOW"})
    show["Risk %"] = show["Risk %"].apply(lambda x: f"{float(x)*100:.1f}%")
    st.dataframe(show, use_container_width=True, hide_index=True)


# ── FOOTER ──
st.markdown("""
<div class="foot">
  ICU Risk Intelligence &nbsp;·&nbsp; XGBoost · FastAPI · Streamlit &nbsp;·&nbsp; MIMIC-III Dataset &nbsp;·&nbsp; ROC-AUC 0.91
</div>""", unsafe_allow_html=True)