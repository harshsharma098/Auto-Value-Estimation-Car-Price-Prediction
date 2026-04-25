import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import subprocess, sys
from pathlib import Path
import matplotlib.pyplot as plt

st.set_page_config(page_title="Car Price Predictor", layout="wide")

DATA_DEFAULT = "./car_dataset_india_cleaned.csv"
MODEL_PATH = "./model_advanced.joblib"
METRICS_PATH = "./model_advanced_metrics.json"

st.title("🚗 Car Price Predictor (Cleaned Dataset Version)")

# Load Dataset
df = pd.read_csv(DATA_DEFAULT)
st.subheader("📘 Dataset Preview")
st.dataframe(df.head(10), use_container_width=True)

# ===========================
# TRAINING SECTION (EXPANDER)
# ===========================
with st.expander("⚙️ Train / Retrain Model"):
    st.write("Use this panel to train or tune the prediction model.")

    model_type = st.selectbox("Model Type", ["xgb", "lgb", "rf"])
    tune = st.checkbox("Enable Hyperparameter Tuning")
    n_iter = st.slider("Tuning Iterations", 5, 50, 20)

    if st.button("Train Model"):
        cmd = [
            sys.executable,
            "car_price_model_advanced.py",
            "train",
            "--data", DATA_DEFAULT,
            "--out", MODEL_PATH,
            "--model", model_type,
            "--n-iter", str(n_iter)
        ]

        if tune:
            cmd.append("--tune")

        with st.spinner("Training in progress..."):
            process = subprocess.run(cmd, capture_output=True, text=True)

        st.text(process.stdout)
        st.success("Training Complete! Model Saved.")

        # Reload metrics
        if Path(METRICS_PATH).exists():
            with open(METRICS_PATH, "r") as f:
                metrics = json.load(f)

            st.subheader("📊 Updated Model Accuracy")
            col1, col2, col3 = st.columns(3)
            col1.metric("MAE", f"{metrics['MAE']:.2f}")
            col2.metric("RMSE", f"{metrics['RMSE']:.2f}")
            col3.metric("R² Score", f"{metrics['R2']:.4f}")

# ===========================
# METRICS SECTION (Always visible if model exists)
# ===========================
if Path(METRICS_PATH).exists():
    with open(METRICS_PATH, "r") as f:
        m = json.load(f)

    st.subheader("📈 Current Model Performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("MAE", f"{m['MAE']:.2f}")
    col2.metric("RMSE", f"{m['RMSE']:.2f}")
    col3.metric("R²", f"{m['R2']:.4f}")

else:
    st.warning("⚠ No trained model found. Please train from the 'Train / Retrain' panel.")

# ===========================
# PREDICTION SECTION
# ===========================
st.subheader("🔮 Predict Car Price")

if Path(MODEL_PATH).exists():
    pipe = joblib.load(MODEL_PATH)
    st.success("Model Loaded Successfully!")

    # User input fields
    brand = st.selectbox("Brand", sorted(df["Brand"].unique()))
    model = st.selectbox("Model", sorted(df["Model"].unique()))
    year = st.number_input("Year", 2000, 2025, 2020)

    fuel = st.selectbox("Fuel Type", df["Fuel_Type_Clean"].unique())
    trans = st.selectbox("Transmission", df["Transmission_Clean"].unique())

    mileage = st.number_input("Mileage", 5.0, 80.0, 18.0)
    engine = st.number_input("Engine CC", 0, 4000, 1500)
    seats = st.number_input("Seating Capacity", 2, 9, 5)
    service = st.number_input("Service Cost", 500, 30000, 10000)

    age = pd.Timestamp.now().year - year

    if st.button("Predict Price"):
        row = {
            "Brand": brand,
            "Model": model,
            "Year": year,
            "Fuel_Type_Clean": fuel,
            "Transmission_Clean": trans,
            "Mileage_Clean": mileage,
            "Engine_CC_Clean": engine,
            "Seating_Capacity_Clean": seats,
            "Service_Cost_Clean": service,
            "Age": age
        }

        pred = pipe.predict(pd.DataFrame([row]))[0]
        st.success(f"💰 Estimated Price: ₹ {int(pred):,}")

else:
    st.error("❌ Model not found. Please train the model first.")
