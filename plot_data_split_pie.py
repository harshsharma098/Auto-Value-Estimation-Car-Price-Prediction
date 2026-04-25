"""
Train / validation / test split pie chart + R² per split (model fit on train only).
Uses the same dataset and features as car_price_model_advanced.py.
Split: 70% train, 15% validation, 15% test — random_state=42.

Run: python3 plot_data_split_pie.py
Or: imported from plot_model_metrics.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from car_price_model_advanced import DEFAULT_FEATURES, TARGET, build_preprocessor, get_model

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "car_dataset_india_cleaned.csv"
PIE_PATH = ROOT / "model_data_split_pie.png"
SPLIT_JSON = ROOT / "data_split_summary.json"

# Same split convention as typical ML workflow (documented; production joblib uses full data)
RANDOM_STATE = 42
TEST_FRACTION = 0.15  # test set
VAL_FRACTION_OF_REMAINDER = 0.15 / 0.85  # val = 15% of all rows from the 85% remainder → 70 train / 15 val / 15 test


def generate_split_pie(model_name: str = "xgb"):
    df = pd.read_csv(DATA_PATH)
    if "Battery_Charge_Level" not in df.columns:
        df["Battery_Charge_Level"] = np.nan
    df["Battery_Charge_Level"] = df["Battery_Charge_Level"].fillna(0)

    X = df[DEFAULT_FEATURES].copy()
    y = df[TARGET].copy()
    n_total = len(X)

    X_trval, X_test, y_trval, y_test = train_test_split(
        X, y, test_size=TEST_FRACTION, random_state=RANDOM_STATE
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trval, y_trval, test_size=VAL_FRACTION_OF_REMAINDER, random_state=RANDOM_STATE
    )

    n_train, n_val, n_test = len(X_train), len(X_val), len(X_test)
    pct_train = 100.0 * n_train / n_total
    pct_val = 100.0 * n_val / n_total
    pct_test = 100.0 * n_test / n_total

    pre = build_preprocessor(X_train)
    model = get_model(model_name)
    pipe = Pipeline([("preprocessor", pre), ("model", model)])
    pipe.fit(X_train, y_train)

    pred_train = pipe.predict(X_train)
    pred_val = pipe.predict(X_val)
    pred_test = pipe.predict(X_test)

    r2_train = float(r2_score(y_train, pred_train))
    r2_val = float(r2_score(y_val, pred_val))
    r2_test = float(r2_score(y_test, pred_test))

    summary = {
        "random_state": RANDOM_STATE,
        "total_rows": int(n_total),
        "train_rows": int(n_train),
        "validation_rows": int(n_val),
        "test_rows": int(n_test),
        "train_pct": round(pct_train, 2),
        "validation_pct": round(pct_val, 2),
        "test_pct": round(pct_test, 2),
        "r2_train": r2_train,
        "r2_validation": r2_val,
        "r2_test": r2_test,
        "note": "Pipeline fit on training split only; R² on val/test reflects generalization. Saved model_advanced.joblib is fit on full data.",
    }
    with open(SPLIT_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    # --- Pie chart ---
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
            "font.size": 10,
            "figure.facecolor": "#f8fafc",
        }
    )

    sizes = [n_train, n_val, n_test]
    labels = [
        f"Training\n{n_train:,} rows ({pct_train:.1f}%)",
        f"Validation\n{n_val:,} rows ({pct_val:.1f}%)",
        f"Testing\n{n_test:,} rows ({pct_test:.1f}%)",
    ]
    colors = ["#3b82f6", "#f59e0b", "#10b981"]
    explode = (0.02, 0.02, 0.02)

    fig, ax = plt.subplots(figsize=(9, 7), facecolor="#f8fafc")
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        pctdistance=0.72,
        shadow=False,
        startangle=90,
        wedgeprops={"edgecolor": "#1e293b", "linewidth": 0.8},
        textprops={"fontsize": 10, "color": "#0f172a"},
    )
    for aut in autotexts:
        aut.set_fontweight("bold")
        aut.set_color("#0f172a")
        aut.set_fontsize(11)

    ax.set_title(
        "Dataset partition — Training / Validation / Testing\n"
        "Auto Value Estimation · car_dataset_india_cleaned.csv",
        fontsize=13,
        fontweight="bold",
        color="#0f172a",
        pad=16,
    )

    metrics_txt = (
        f"R² (model fit on training split only)\n"
        f"  Train:      {r2_train:.4f}\n"
        f"  Validation: {r2_val:.4f}\n"
        f"  Test:       {r2_test:.4f}"
    )
    fig.text(
        0.5,
        0.06,
        metrics_txt,
        ha="center",
        va="bottom",
        fontsize=10,
        family="monospace",
        color="#334155",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#cbd5e1", linewidth=1),
    )
    fig.text(
        0.5,
        0.015,
        "Split: 70% / 15% / 15% · random_state=42 · same features as car_price_model_advanced.py",
        ha="center",
        fontsize=8,
        color="#64748b",
    )

    plt.savefig(PIE_PATH, dpi=175, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    print(f"Saved split pie: {PIE_PATH}")
    print(f"Saved summary: {SPLIT_JSON}")
    print(f"  R² train={r2_train:.4f}  val={r2_val:.4f}  test={r2_test:.4f}")
    return summary


def main():
    generate_split_pie()


if __name__ == "__main__":
    main()
