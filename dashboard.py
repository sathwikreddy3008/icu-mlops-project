import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="ICU · Risk Monitor",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="⚕️"
)

API_URL = "https://icu-mlops-project.onrender.com/predict"

# ─── THEME VIA URL PARAM (No JS required) ────────────
try:
    if "set_dark" in st.query_params:
        st.session_state.dark = (st.query_params["set_dark"] == "1")
        st.query_params.clear()
except Exception:
    pass

if "dark" not in st.session_state:
    st.session_state.dark = True

dark      = st.session_state.dark
next_dark = "0" if dark else "1"

# ─── DESIGN TOKENS ────────────────────────────────────────────────────────────
if dark:
    bg,bg2,bg3        = "#181818","#222222","#2b2b2b"
    bdr,bdr2          = "#2e2e2e","#393939"
    txt,txt2,txt3     = "#e3e3e3","#888888","#4e4e4e"
    acc,asoft         = "#c8906a","rgba(200,144,106,.13)"
    red,rsoft         = "#ce5f5f","rgba(206,95,95,.13)"
    grn,gsoft         = "#5aaa74","rgba(90,170,116,.13)"
    amb,amsoft        = "#be8828","rgba(190,136,40,.13)"
    shd               = "0 1px 3px rgba(0,0,0,.55),0 4px 16px rgba(0,0,0,.32)"
    gs1,gs2,gs3       = "rgba(90,170,116,.08)","rgba(190,136,40,.08)","rgba(206,95,95,.10)"
    gtick             = "#404040"
    pbg,ovl           = "#1d1d1d","rgba(0,0,0,.62)"
    sw_bg             = "#c8906a"          
    knob_side         = "right:3px"        
else:
    bg,bg2,bg3        = "#eeebe3","#faf7f1","#e5e1d6"
    bdr,bdr2          = "#d8d2c5","#c4bdb0"
    txt,txt2,txt3     = "#1c1c1c","#5c5c5c","#9e9e9e"
    acc,asoft         = "#7a4a1e","rgba(122,74,30,.08)"
    red,rsoft         = "#982828","rgba(152,40,40,.08)"
    grn,gsoft         = "#235936","rgba(35,89,54,.08)"
    amb,amsoft        = "#774d00","rgba(119,77,0,.08)"
    shd               = "0 1px 2px rgba(0,0,0,.06),0 4px 12px rgba(0,0,0,.07)"
    gs1,gs2,gs3       = "rgba(35,89,54,.07)","rgba(119,77,0,.07)","rgba(152,40,40,.09)"
    gtick             = "#c4c4c4"
    pbg,ovl           = "#faf7f1","rgba(0,0,0,.28)"
    sw_bg             = bdr
    knob_side         = "left:3px"

# ─── PANEL: PRE-RENDER RECENT HISTORY ────────────────────────────────────────
hfile = "data/patient_history.csv"
phist = ""
if os.path.exists(hfile):
    try:
        df_h = pd.read_csv(hfile).tail(3)
        for _, r in df_h.iterrows():
            rp   = f"{float(r['probability'])*100:.0f}%"
            cls  = "High" if int(r['prediction'])==1 else "Low"
            clr  = red  if int(r['prediction'])==1 else grn
            bgc  = rsoft if int(r['prediction'])==1 else gsoft
            t    = str(r.get('time',''));  ts = t[11:16] if len(t)>=16 else "—"
            ag   = int(r.get('age',0))
            phist += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:9px 0;border-bottom:1px solid {bdr}">'
                f'<div><div style="font-size:13.5px;font-weight:500;color:{txt}">{rp} risk</div>'
                f'<div style="font-size:11px;color:{txt3};margin-top:1px">Age {ag} · {ts}</div></div>'
                f'<div style="font-size:11.5px;font-weight:600;color:{clr};background:{bgc};'
                f'border:1px solid {clr};border-radius:20px;padding:3px 10px">{cls}</div></div>'
            )
    except Exception:
        pass

if not phist:
    phist = f'<p style="font-size:12px;color:{txt3}">No predictions yet.</p>'

now = datetime.now().strftime("%d %b %Y")

# ─── ONE BIG INJECT: CSS + PURE CSS TOGGLE PANEL + NAV ───────────────────────
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600&family=DM+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],section.main{{
  background:{bg}!important;font-family:'Instrument Sans',sans-serif!important;color:{txt}!important}}
[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer,
[data-testid="stSidebar"]{{display:none!important}}
.block-container{{padding:2rem 2.5rem 6rem!important;max-width:860px!important;margin:0 auto!important}}

/* ── NAV ── */
.icn{{display:flex;align-items:center;justify-content:space-between;
  padding:0 0 1.25rem;margin-bottom:2.75rem;border-bottom:1px solid {bdr}}}
.icn-l{{display:flex;align-items:center;gap:12px}}
.icn-mark{{width:33px;height:33px;background:{bg3};border:1px solid {bdr};border-radius:9px;
  display:flex;align-items:center;justify-content:center;color:{txt}}}
.icn-brand{{font-family:'Lora',serif;font-size:16px;font-weight:500;color:{txt};letter-spacing:-.2px}}
.icn-sub{{font-size:11px;color:{txt3};margin-top:1px}}
.icn-r{{display:flex;align-items:center;gap:8px}}
.chip{{font-family:'DM Mono',monospace;font-size:10.5px;color:{txt3};
  background:{bg3};border:1px solid {bdr};border-radius:20px;padding:4px 11px;white-space:nowrap}}
.livebdg{{display:flex;align-items:center;gap:5px;font-size:11px;font-weight:600;color:{grn};
  background:{gsoft};border:1px solid {grn};border-radius:20px;padding:4px 10px}}
.ldot{{width:5px;height:5px;background:{grn};border-radius:50%;
  animation:livep 2.5s ease-in-out infinite}}
@keyframes livep{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}

/* Menu Trigger */
.hbg{{width:33px;height:33px;background:{bg3};border:1px solid {bdr};border-radius:8px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:4.5px;cursor:pointer;transition:background .15s,border-color .15s;flex-shrink:0}}
.hbg:hover{{background:{bdr};border-color:{bdr2}}}
.hl{{width:13px;height:1.5px;background:{txt2};border-radius:2px;transition:background .15s}}
.hbg:hover .hl{{background:{txt}}}

/* ── PANEL TOGGLE LOGIC (PURE CSS) ── */
#panel-toggle:checked ~ .pnl{{transform:translateX(0)}}
#panel-toggle:checked ~ .ovl{{opacity:1;pointer-events:all}}

.ovl{{position:fixed;inset:0;z-index:998;background:{ovl};
  opacity:0;pointer-events:none;transition:opacity .25s}}
.pnl{{position:fixed;top:0;right:0;bottom:0;z-index:999;width:286px;
  background:{pbg};border-left:1px solid {bdr};
  box-shadow:-6px 0 30px rgba(0,0,0,{'0.42' if dark else '0.12'});
  transform:translateX(100%);transition:transform .28s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;overflow-y:auto}}
.pnl-h{{padding:1.5rem 1.5rem 1.25rem;border-bottom:1px solid {bdr};
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;background:{pbg};z-index:1}}
.pnl-title{{font-family:'Lora',serif;font-size:16px;font-weight:500;color:{txt}}}
.pnl-x{{width:28px;height:28px;background:{bg3};border:1px solid {bdr};
  border-radius:7px;display:flex;align-items:center;justify-content:center;
  cursor:pointer;font-size:13px;color:{txt2};transition:background .15s}}
.pnl-x:hover{{background:{bdr};color:{txt}}}
.psec{{padding:1.25rem 1.5rem;border-bottom:1px solid {bdr}}}
.psec-lbl{{font-size:10px;font-weight:600;color:{txt3};letter-spacing:2px;
  text-transform:uppercase;margin-bottom:1rem}}

/* Theme Row */
.trow{{display:flex;align-items:center;justify-content:space-between;
  cursor:pointer;padding:4px 0;user-select:none}}
.trow-t{{font-size:14px;font-weight:500;color:{txt}}}
.trow-s{{font-size:11.5px;color:{txt3};margin-top:2px}}
.pswitch{{width:44px;height:25px;background:{sw_bg};border-radius:13px;position:relative;
  border:1px solid {bdr2};flex-shrink:0;transition:background .2s}}
.pknob{{position:absolute;top:3px;{knob_side};width:17px;height:17px;
  background:#fff;border-radius:50%;box-shadow:0 1px 3px rgba(0,0,0,.25)}}
.pstat{{background:{bg3};border:1px solid {bdr};border-radius:10px;
  padding:.8rem 1rem;margin-bottom:8px}}
.pstat-l{{font-size:10px;font-weight:600;color:{txt3};letter-spacing:1.5px;
  text-transform:uppercase;margin-bottom:3px}}
.pstat-v{{font-family:'DM Mono',monospace;font-size:14px;font-weight:500;color:{txt}}}

/* ── HERO ── */
.hero{{margin-bottom:2rem}}
.hero-t{{font-family:'Lora',serif;font-size:34px;font-weight:500;color:{txt};
  letter-spacing:-.5px;line-height:1.18;margin-bottom:.5rem}}
.hero-d{{font-size:14px;color:{txt2};line-height:1.65;max-width:520px}}

/* ── SECTION LABEL ── */
.sec{{display:flex;align-items:center;margin-bottom:0.4rem;margin-top:1.5rem}}
.sec-l{{font-size:10.5px;font-weight:600;color:{txt3};letter-spacing:2px;
  text-transform:uppercase;padding-right:14px;white-space:nowrap}}
.sec-r{{flex:1;height:1px;background:{bdr}}}

/* ── CARDS & NATIVE COLUMNS STYLING ── */
.card, [data-testid="stHorizontalBlock"] {{
  background:{bg2}!important;
  border:1px solid {bdr}!important;
  border-radius:14px!important;
  padding:1.2rem 1.5rem!important;
  box-shadow:{shd}!important;
  transition:border-color .18s!important;
  margin-top:0.2rem!important;
  margin-bottom:0.5rem!important;
  gap:1rem!important;
}}
.card:hover, [data-testid="stHorizontalBlock"]:hover {{
  border-color:{bdr2}!important;
}}
.element-container{{margin-bottom:0!important;}}

/* ── INPUTS & SELECTBOXES (FIXED UI WITH HOVER) ── */

/* 1. Reset sneaky dark backgrounds injected by Streamlit in nested divs */
[data-testid="stNumberInput"] div[data-baseweb="input"],
[data-testid="stNumberInput"] div[data-baseweb="base-input"],
[data-testid="stNumberInput"] input {{
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
}}

/* 2. Style the master outer wrapper to serve as our pristine input box */
[data-testid="stNumberInput"] > div > div, 
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
  background-color: {bg3} !important; 
  border: 1px solid {bdr} !important;
  color: {txt} !important;
  border-radius: 9px !important; 
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
}}

/* 3. Hover state (Smooth outline) */
[data-testid="stNumberInput"] > div > div:hover,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {{
  border-color: {txt3} !important;
}}

/* 4. Focus state (Active selection) */
[data-testid="stNumberInput"] > div > div:focus-within,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {{
  border-color: {acc} !important;
  box-shadow: 0 0 0 2px {asoft} !important;
  background-color: {bg2} !important;
}}

/* 5. Clean up text styling */
[data-testid="stNumberInput"] input {{
  color: {txt} !important;
  caret-color: {txt} !important; 
  padding: 9px 12px !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 14px !important; 
  font-weight: 500 !important;
}}

/* 6. Clean up the + / - buttons */
[data-testid="stNumberInput"] button {{
  background-color: transparent !important; 
  border: none !important;
  color: {txt3} !important; 
  border-radius: 7px !important;
}}
[data-testid="stNumberInput"] button:hover {{
  background-color: {bdr} !important; 
  color: {txt} !important;
}}

/* Selectbox specific text and icon */
[data-testid="stSelectbox"] span {{ color:{txt}!important; font-family:'DM Mono',monospace!important; font-size:14px!important;}}
[data-testid="stSelectbox"] svg {{ fill:{txt2}!important; }}

/* Labels */
label[data-testid="stWidgetLabel"] p{{
  font-family:'Instrument Sans',sans-serif!important;font-size:12px!important;
  font-weight:500!important;color:{txt2}!important;margin-bottom:5px!important}}

/* ── NATIVE HTML TABLE STYLING ── */
.htable {{ width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }}
.htable th {{ font-family: 'Instrument Sans', sans-serif; color: {txt3}; font-weight: 600; padding: 12px 8px; border-bottom: 1px solid {bdr}; text-transform: uppercase; font-size: 10px; letter-spacing: 1px; }}
.htable td {{ padding: 12px 8px; border-bottom: 1px solid {bdr2}; color: {txt}; font-family: 'DM Mono', monospace; }}
.htable tr:last-child td {{ border-bottom: none; }}

/* Miscellaneous elements */
[data-testid="stButton"]>button{{
  background:{txt}!important;color:{bg}!important;
  font-family:'Instrument Sans',sans-serif!important;
  font-size:13.5px!important;font-weight:600!important;border:none!important;
  border-radius:11px!important;padding:.85rem 2rem!important;width:100%!important;
  transition:opacity .18s,transform .15s!important;box-shadow:none!important;cursor:pointer!important}}
[data-testid="stButton"]>button:hover{{opacity:.84!important;transform:translateY(-1px)!important}}
[data-testid="stButton"]>button:active{{transform:translateY(0)!important}}
.divider{{height:1px;background:{bdr};margin:2.25rem 0}}
.rhero{{background:{bg2};border:1px solid {bdr};border-radius:16px;
  padding:2.25rem 2.5rem;margin-bottom:1rem;box-shadow:{shd};
  display:flex;align-items:flex-start;justify-content:space-between;gap:2rem}}
.eyebrow{{font-size:10px;font-weight:600;color:{txt3};letter-spacing:2px; text-transform:uppercase;margin-bottom:.55rem}}
.bignum{{font-family:'Lora',serif;font-size:68px;font-weight:600; line-height:1;letter-spacing:-2px}}
.num-sub{{font-size:12px;color:{txt3};margin-top:.45rem}}
.verdict{{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;
  border-radius:40px;font-size:13.5px;font-weight:600;margin-bottom:.85rem}}
.vhi{{background:{rsoft};border:1px solid {red};color:{red}}}
.vlo{{background:{gsoft};border:1px solid {grn};color:{grn}}}
.vmeta{{font-size:12px;color:{txt3};line-height:1.8;text-align:right}}
.vgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:1rem}}
.vc{{background:{bg2};border:1px solid {bdr};border-radius:12px;
  padding:1.1rem 1.1rem .9rem;box-shadow:{shd};transition:border-color .18s}}
.vc:hover{{border-color:{bdr2}}}
.vc-n{{font-size:10px;font-weight:600;color:{txt3};letter-spacing:1.5px; text-transform:uppercase;margin-bottom:.4rem}}
.vc-v{{font-family:'Lora',serif;font-size:34px;font-weight:500; line-height:1;margin-bottom:2px}}
.vc-u{{font-size:11px;color:{txt3};margin-bottom:.65rem}}
.bb{{height:2.5px;background:{bg3};border-radius:3px;overflow:hidden}}
.bf{{height:100%;border-radius:3px;transition:width .5s ease}}
.strip{{display:flex;gap:8px;margin-bottom:1rem;flex-wrap:wrap}}
.ic{{flex:1;min-width:90px;background:{bg2};border:1px solid {bdr};
  border-radius:10px;padding:.85rem 1rem;box-shadow:{shd}}}
.ic-l{{font-size:10px;font-weight:600;color:{txt3};letter-spacing:1.5px; text-transform:uppercase;margin-bottom:3px}}
.ic-v{{font-family:'DM Mono',monospace;font-size:14px;font-weight:500;color:{txt}}}
.alerts{{display:flex;flex-wrap:wrap;gap:7px;padding:1.1rem 1.25rem;
  background:{bg2};border:1px solid {bdr};border-radius:12px; margin-bottom:1rem;box-shadow:{shd}}}
.pill{{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;
  border-radius:7px;font-size:12.5px;font-weight:500;animation:pillIn .28s ease both}}
@keyframes pillIn{{from{{opacity:0;transform:translateY(3px)}}to{{opacity:1;transform:translateY(0)}}}}
.pr{{background:{rsoft};border:1px solid {red};color:{red}}}
.pa{{background:{amsoft};border:1px solid {amb};color:{amb}}}
.pg{{background:{gsoft};border:1px solid {grn};color:{grn}}}
.gwrap{{background:{bg2};border:1px solid {bdr};border-radius:14px;
  padding:.4rem .4rem 0;box-shadow:{shd};margin-bottom:1rem;overflow:hidden}}
.foot{{text-align:center;font-size:11px;color:{txt3};padding-top:2.5rem;
  border-top:1px solid {bdr};margin-top:2.5rem;letter-spacing:.3px}}
</style>

<input type="checkbox" id="panel-toggle" style="display:none">

<label class="ovl" for="panel-toggle"></label>

<div class="pnl">
  <div class="pnl-h">
    <div class="pnl-title">Settings</div>
    <label class="pnl-x" for="panel-toggle">&#10005;</label>
  </div>

  <div class="psec">
    <div class="psec-lbl">Appearance</div>
    <a href="?set_dark={next_dark}" target="_self" style="text-decoration:none; color:inherit;">
      <div class="trow">
        <div>
          <div class="trow-t">{'Dark mode' if dark else 'Light mode'}</div>
          <div class="trow-s">Tap to switch</div>
        </div>
        <div class="pswitch"><div class="pknob"></div></div>
      </div>
    </a>
  </div>

  <div class="psec">
    <div class="psec-lbl">Recent Predictions</div>
    {phist}
  </div>

  <div class="psec">
    <div class="psec-lbl">Model Info</div>
    <div class="pstat"><div class="pstat-l">Algorithm</div><div class="pstat-v">XGBoost v2</div></div>
    <div class="pstat"><div class="pstat-l">Dataset</div><div class="pstat-v">MIMIC-III</div></div>
    <div class="pstat"><div class="pstat-l">ROC-AUC</div><div class="pstat-v">0.91</div></div>
    <div class="pstat"><div class="pstat-l">Features</div><div class="pstat-v">70+ clinical signals</div></div>
  </div>

  <div class="psec" style="border-bottom:none">
    <div class="psec-lbl">Notice</div>
    <div style="font-size:12px;color:{txt3};line-height:1.7">
      For clinical decision support only. Does not replace physician judgement.
      Always validate with clinical expertise and patient context.
    </div>
  </div>
</div>

<div class="icn">
  <div class="icn-l">
    <div class="icn-mark">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
    </div>
    <div>
      <div class="icn-brand">ICU Risk Monitor</div>
      <div class="icn-sub">Clinical Decision Support</div>
    </div>
  </div>
  <div class="icn-r">
    <div class="livebdg"><div class="ldot"></div>Live</div>
    <span class="chip">{now}</span>
    <label class="hbg" for="panel-toggle">
      <div class="hl"></div><div class="hl"></div><div class="hl"></div>
    </label>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── PAGE HERO (UPDATED COPY) ─────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-t">Predictive Risk Analysis</div>
  <div class="hero-d">Enter clinical parameters to compute ICU mortality risk using our validated XGBoost model trained on MIMIC-III.</div>
</div>
""", unsafe_allow_html=True)


# ─── REAL-TIME VITALS ─────────────────────────────────────────
st.markdown('<div class="sec"><div class="sec-l">Real-Time Vitals</div><div class="sec-r"></div></div>', unsafe_allow_html=True)
v1, v2, v3, v4, v5 = st.columns(5)
with v1: spo2        = st.number_input("SpO₂ (%)", 70, 100, 92)
with v2: hr          = st.number_input("Heart Rate (bpm)", 40, 180, 95)
with v3: temp        = st.number_input("Temp. (°C)", 30.0, 45.0, 38.0, step=0.1)
with v4: systolic_bp = st.number_input("Systolic BP (mmHg)", 60, 200, 110)
with v5: resp_rate   = st.number_input("Resp. Rate (/min)", 10, 40, 22)


# ─── PATIENT PROFILE ─────────────────────────────────
st.markdown('<div class="sec"><div class="sec-l">Patient Profile</div><div class="sec-r"></div></div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: age             = st.number_input("Age (yrs)", 0, 120, 65)
with c2: LOS             = st.number_input("ICU Stay (days)", 0.0, 30.0, 3.5, step=0.5)
with c3: num_diagnoses   = st.number_input("Diagnoses", 0, 20, 5)
with c4: unique_diseases = st.number_input("Unique Diseases", 0, 20, 4)
with c5: num_meds        = st.number_input("Medications", 0, 50, 8)


# ─── ACTIVE INTERVENTIONS ─────────────────────────────────────────────────────
st.markdown('<div class="sec"><div class="sec-l">Active Interventions</div><div class="sec-r"></div></div>', unsafe_allow_html=True)
i1, i2, i3, i4 = st.columns(4)
with i1: vasopressor_flag = st.selectbox("Vasopressors", [0,1], format_func=lambda x:"Active" if x else "None")
with i2: antibiotic_flag  = st.selectbox("Antibiotics",  [0,1], format_func=lambda x:"Active" if x else "None")


# ─── PAYLOAD ──────────────────────────────────────────────────────────────────
data = {
    "age": age, "LOS": LOS,
    "num_diagnoses": num_diagnoses, "unique_diseases": unique_diseases, "num_meds": num_meds,
    "vasopressor_flag": vasopressor_flag, "antibiotic_flag": antibiotic_flag,
    "mean_temperature": temp, "max_temperature": temp+1, "min_temperature": temp-1,
    "trend": 0.5, "rolling_mean": temp,
    "mean_spo2": spo2, "min_spo2": spo2-4, "spo2_low_flag": int(spo2<90),
    "max_systolic_bp": systolic_bp+10, "min_systolic_bp": systolic_bp-10,
    "mean_systolic_bp": systolic_bp,
    "mean_resp_rate": resp_rate, "max_resp_rate": resp_rate+5, "std_resp_rate": 3,
    "mean_heart_rate": hr, "min_heart_rate": hr-20, "std_heart_rate": 5,
}

# ─── ANALYSE BUTTON ────────────────────────────────────────────
st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
if st.button("Compute Risk Score →", use_container_width=True, key="analyse"):
    with st.spinner("Running inference…  \n*First request may take a moment to initialize.*"):
        try:
            res    = requests.post(API_URL, json=data, timeout=100)
            result = res.json()
            prob   = result["risk_probability"]
            pred   = result["prediction"]
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

    pct = int(prob * 100)
    pcc = red if pct>=70 else (amb if pct>=40 else grn)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec"><div class="sec-l">Results</div><div class="sec-r"></div></div>',
                unsafe_allow_html=True)

    vt = "High Risk" if pred==1 else "Low Risk"
    vc = "vhi"       if pred==1 else "vlo"
    vi = "&#9888;"   if pred==1 else "&#10003;"
    vs = "Immediate escalation recommended" if pred==1 else "Continue standard monitoring"

    st.markdown(f"""
<div class="rhero">
  <div>
    <div class="eyebrow">Mortality Risk Probability</div>
    <div class="bignum" style="color:{pcc}">{pct}%</div>
    <div class="num-sub">XGBoost · MIMIC-III · 70+ features</div>
  </div>
  <div style="text-align:right">
    <div class="verdict {vc}">{vi}&nbsp;&nbsp;{vt}</div>
    <div class="vmeta">
      <span>{vs}</span>
      <span style="display:block;margin-top:4px">
        Vasopressor: {"Active" if vasopressor_flag else "None"}&nbsp;·&nbsp;
        Antibiotics: {"Active" if antibiotic_flag else "None"}
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── GAUGE ──
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=pct,
        number={'suffix':'%','font':{'size':36,'color':pcc,'family':'DM Mono'}},
        title={'text':"Risk Score",'font':{'size':10,'color':gtick,'family':'Instrument Sans'}},
        gauge={
            'axis':{'range':[0,100],'tickwidth':1,'tickcolor':bdr,
                    'tickfont':{'color':gtick,'size':10,'family':'DM Mono'},'nticks':6},
            'bar':{'color':pcc,'thickness':0.16},
            'bgcolor':'rgba(0,0,0,0)','borderwidth':0,
            'steps':[{'range':[0,40],'color':gs1},{'range':[40,70],'color':gs2},
                     {'range':[70,100],'color':gs3}],
            'threshold':{'line':{'color':pcc,'width':2},'thickness':0.75,'value':pct}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                      font_color=txt,margin=dict(l=30,r=30,t=36,b=8),height=185)
    st.markdown('<div class="gwrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── VITALS ──
    st.markdown('<div class="sec" style="margin-top:.5rem">'
                '<div class="sec-l">Vital Snapshot</div><div class="sec-r"></div></div>',
                unsafe_allow_html=True)
    sc = red if spo2<90 else grn;        sw_ = int((spo2-70)/30*100)
    hc = red if hr>110 else grn;         hw_ = int((hr-40)/140*100)
    tc = amb if temp>38 else grn;        tw_ = int((temp-30)/15*100)
    bc = amb if systolic_bp>140 else grn; bw_ = int((systolic_bp-60)/140*100)
    rw_ = int((resp_rate-10)/30*100);   lw_ = int(LOS/30*100)

    st.markdown(f"""
<div class="vgrid">
  <div class="vc"><div class="vc-n">SpO&#8322;</div>
    <div class="vc-v" style="color:{sc}">{spo2}</div><div class="vc-u">percent</div>
    <div class="bb"><div class="bf" style="width:{sw_}%;background:{sc}"></div></div></div>
  <div class="vc"><div class="vc-n">Heart Rate</div>
    <div class="vc-v" style="color:{hc}">{hr}</div><div class="vc-u">bpm</div>
    <div class="bb"><div class="bf" style="width:{hw_}%;background:{hc}"></div></div></div>
  <div class="vc"><div class="vc-n">Temperature</div>
    <div class="vc-v" style="color:{tc}">{temp}</div><div class="vc-u">&#176;C</div>
    <div class="bb"><div class="bf" style="width:{tw_}%;background:{tc}"></div></div></div>
  <div class="vc"><div class="vc-n">Systolic BP</div>
    <div class="vc-v" style="color:{bc}">{systolic_bp}</div><div class="vc-u">mmHg</div>
    <div class="bb"><div class="bf" style="width:{bw_}%;background:{bc}"></div></div></div>
  <div class="vc"><div class="vc-n">Resp. Rate</div>
    <div class="vc-v" style="color:{txt}">{resp_rate}</div><div class="vc-u">per min</div>
    <div class="bb"><div class="bf" style="width:{rw_}%;background:{acc}"></div></div></div>
  <div class="vc"><div class="vc-n">ICU Stay</div>
    <div class="vc-v" style="color:{txt}">{LOS}</div><div class="vc-u">days</div>
    <div class="bb"><div class="bf" style="width:{lw_}%;background:{acc}"></div></div></div>
</div>
""", unsafe_allow_html=True)

    # ── INFO STRIP ──
    st.markdown(f"""
<div class="strip">
  <div class="ic"><div class="ic-l">Age</div><div class="ic-v">{age} yrs</div></div>
  <div class="ic"><div class="ic-l">Diagnoses</div><div class="ic-v">{num_diagnoses}</div></div>
  <div class="ic"><div class="ic-l">Unique Diseases</div><div class="ic-v">{unique_diseases}</div></div>
  <div class="ic"><div class="ic-l">Medications</div><div class="ic-v">{num_meds}</div></div>
  <div class="ic"><div class="ic-l">Vasopressor</div><div class="ic-v">{"Active" if vasopressor_flag else "None"}</div></div>
  <div class="ic"><div class="ic-l">Antibiotics</div><div class="ic-v">{"Active" if antibiotic_flag else "None"}</div></div>
</div>
""", unsafe_allow_html=True)

    # ── ALERTS ──
    st.markdown('<div class="sec" style="margin-top:.5rem">'
                '<div class="sec-l">Clinical Alerts</div><div class="sec-r"></div></div>',
                unsafe_allow_html=True)
    alts = []
    if prob>0.7:          alts.append(("&#128308;","Critical risk — immediate escalation required","r"))
    if spo2<90:           alts.append(("&#129754;",f"Hypoxemia · SpO&#8322; {spo2}% below threshold","a"))
    if hr>110:            alts.append(("&#128150;",f"Tachycardia · {hr} bpm","a"))
    if systolic_bp>140:   alts.append(("&#129978;",f"Hypertension · SBP {systolic_bp} mmHg","a"))
    if temp>38:           alts.append(("&#127777;",f"Fever · {temp}&#176;C","a"))

    pills = "".join(
        f'<div class="pill p{c}" style="animation-delay:{i*.07}s">{ic}&ensp;{m}</div>'
        for i,(ic,m,c) in enumerate(alts)
    ) if alts else f'<div class="pill pg">&#10003;&ensp;All vitals within normal range — patient stable</div>'
    st.markdown(f'<div class="alerts">{pills}</div>', unsafe_allow_html=True)

    # ── HISTORY TABLE ──
    st.markdown('<div class="sec" style="margin-top:1.5rem">'
                '<div class="sec-l">Prediction History</div><div class="sec-r"></div></div>',
                unsafe_allow_html=True)
    record = data.copy()
    record.update({"probability":round(prob,4),"prediction":pred,
                   "time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    df_new = pd.DataFrame([record])
    if os.path.exists(hfile):
        df_all = pd.concat([pd.read_csv(hfile), df_new], ignore_index=True)
    else:
        df_all = df_new
    os.makedirs("data", exist_ok=True)
    df_all.to_csv(hfile, index=False)

    cols_show = ["time","age","LOS","mean_heart_rate","mean_spo2",
                 "mean_systolic_bp","mean_temperature","probability","prediction"]
    show = df_all[cols_show].tail(8).copy()
    show.columns = ["Time","Age","Stay","HR","SpO₂","SBP","Temp","Risk","Class"]
    show["Class"] = show["Class"].apply(lambda x: f'<span style="color:{red};font-weight:600;">High</span>' if x==1 else f'<span style="color:{grn};font-weight:600;">Low</span>')
    show["Risk"]  = show["Risk"].apply(lambda x: f"{float(x)*100:.1f}%")
    
    table_html = show.to_html(index=False, escape=False, classes="htable", border=0)
    st.markdown(f'<div class="card" style="padding: 1rem 1.5rem;">{table_html}</div>', unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="foot">ICU Risk Monitor · XGBoost · FastAPI · Streamlit · MIMIC-III</div>',
    unsafe_allow_html=True
)