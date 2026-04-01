ICU Risk Prediction System

An end-to-end Machine Learning + MLOps project to predict ICU patient risk using real-world clinical data.

---

## Overview

This project predicts the probability of ICU patient mortality using clinical features such as vitals, diagnoses, and medications. It integrates data engineering, machine learning, API deployment, and an interactive dashboard.

---

##  Features

- Built using MIMIC-III clinical dataset  
- Feature engineering with 70+ clinical features  
- XGBoost model (ROC-AUC ~0.91)  
- FastAPI backend for real-time prediction  
- Streamlit dashboard for visualization  
- Clinical alert system (High BP, Low SPO2, etc.)  
- Risk gauge and patient monitoring  
- History tracking of predictions  

---

##  Tech Stack

- Python  
- Pandas  
- Scikit-learn  
- XGBoost  
- FastAPI  
- Streamlit  
- MLflow  
- Plotly  

---

##  How to Run

### 1. Clone repository

```bash
git clone https://github.com/sathwikreddy3008/icu-mlops-project.git
cd icu-mlops-project


### 2. Install dependencies

pip install -r requirements.txt


### 3. Run backend (FastAPI)

uvicorn app:app --reload

### 4. Run dashboard (Streamlit)

Streamlit run dashboard.py

----

## Project structure

icu-mlops-project/
│
├── src/
│   ├── ingestion/
│   ├── features/
│   ├── pipelines/
│   ├── models/
│
├── app.py
├── dashboard.py
├── requirements.txt
├── models/
└── README.md