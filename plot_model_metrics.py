"""
Evaluate trained model on the full dataset and plot MAE, MSE, RMSE, R².
Single horizontal row: three clear panels, no overlapping labels.

Also generates train/validation/test pie chart (see plot_data_split_pie.py).

Run from project root: python3 plot_model_metrics.py
"""

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, root_mean_squared_error

from car_price_model_advanced import DEFAULT_FEATURES, TARGET

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model_advanced.joblib"
DATA_PATH = ROOT / "car_dataset_india_cleaned.csv"
METRICS_JSON = ROOT / "model_advanced_metrics.json"
PLOT_PATH = ROOT / "model_metrics_plot.png"


def _style():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.edgecolor": "#94a3b8",
            "axes.linewidth": 1.0,
            "figure.facecolor": "#f8fafc",
            "axes.facecolor": "#ffffff",
            "grid.color": "#e2e8f0",
            "grid.linestyle": "-",
            "grid.linewidth": 0.8,
        }
    )


def main():
    if not MODEL_PATH.exists():
        raise SystemExit(f"Missing {MODEL_PATH}. Train first: python car_price_model_advanced.py train ...")

    if PLOT_PATH.exists():
        PLOT_PATH.unlink()

    df = pd.read_csv(DATA_PATH)
    if "Battery_Charge_Level" not in df.columns:
        df["Battery_Charge_Level"] = np.nan
    df["Battery_Charge_Level"] = df["Battery_Charge_Level"].fillna(0)

    X = df[DEFAULT_FEATURES].copy()
    y = df[TARGET].copy()

    pipe = joblib.load(MODEL_PATH)
    preds = pipe.predict(X)

    mae = float(mean_absolute_error(y, preds))
    mse = float(mean_squared_error(y, preds))
    rmse = float(root_mean_squared_error(y, preds))
    r2 = float(r2_score(y, preds))

    print("Model evaluation (full training set — same as training script fit):")
    print(f"  MAE  = ₹ {mae:,.2f}")
    print(f"  MSE  = {mse:,.2f}  (₹²)")
    print(f"  RMSE = ₹ {rmse:,.2f}")
    print(f"  R²   = {r2:.6f}")

    out_metrics = {"MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2}
    with open(METRICS_JSON, "w") as f:
        json.dump(out_metrics, f, indent=2)
    print(f"\nUpdated {METRICS_JSON}")

    _style()

    # Wide figure, constrained_layout avoids title/label overlap
    fig, axes = plt.subplots(
        1, 3, figsize=(15.5, 5.9), sharey=False, constrained_layout=True
    )
    fig.patch.set_facecolor("#f8fafc")

    fig.suptitle(
        "Regression metrics — Car price model (Auto Value Estimation)",
        fontsize=14,
        fontweight="bold",
        color="#0f172a",
    )
    fig.supxlabel(
        "In-sample metrics on full training data",
        fontsize=9,
        color="#64748b",
        y=0.02,
    )

    # --- Panel 1: MAE & RMSE (lakhs of ₹) ---
    ax0 = axes[0]
    labels = ["MAE", "RMSE"]
    vals_lakh = [mae / 1e5, rmse / 1e5]
    colors = ["#2563eb", "#7c3aed"]
    xpos = np.arange(len(labels))
    bars = ax0.bar(xpos, vals_lakh, width=0.52, color=colors, edgecolor="#1e293b", linewidth=0.5, zorder=2)
    ax0.set_xticks(xpos)
    ax0.set_xticklabels(labels, fontsize=11, fontweight="semibold")
    ax0.set_ylabel("Error (lakhs of ₹)", color="#334155", labelpad=10)
    ax0.set_title("Mean absolute & root mean\nsquared error", fontsize=11, pad=14, color="#0f172a")
    ymax = max(vals_lakh) * 1.32
    ax0.set_ylim(0, ymax)
    ax0.yaxis.grid(True, zorder=0)
    ax0.set_axisbelow(True)
    for b, rupees in zip(bars, [mae, rmse]):
        h = b.get_height()
        ax0.text(
            b.get_x() + b.get_width() / 2,
            h + ymax * 0.02,
            f"₹ {rupees:,.0f}",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="semibold",
            color="#0f172a",
        )
    ax0.text(
        0.5,
        -0.18,
        "Lower is better · values in Indian rupees",
        transform=ax0.transAxes,
        ha="center",
        fontsize=8,
        color="#64748b",
    )

    # --- Panel 2: MSE (billions ₹²) — value below axis, no overlap with title ---
    ax1 = axes[1]
    mse_bn = mse / 1e9
    ax1.bar([0], [mse_bn], width=0.45, color="#dc2626", edgecolor="#7f1d1d", linewidth=0.5, zorder=2)
    ax1.set_xticks([0])
    ax1.set_xticklabels(["MSE"], fontsize=11, fontweight="semibold")
    ax1.set_ylabel("MSE (billions of ₹²)", color="#334155", labelpad=10)
    ax1.set_title("Mean squared error", fontsize=11, pad=14, color="#0f172a")
    ax1.set_ylim(0, max(mse_bn * 1.35, 0.8))
    ax1.yaxis.grid(True, zorder=0)
    ax1.set_axisbelow(True)
    # Exact value under the chart (axes coords) — avoids overlapping the title
    ax1.text(
        0.5,
        -0.22,
        f"Scaled bar: {mse_bn:.2f} billion ₹²\nExact MSE: {mse:,.0f} ₹²",
        transform=ax1.transAxes,
        ha="center",
        va="top",
        fontsize=8.5,
        color="#334155",
        linespacing=1.35,
    )

    # --- Panel 3: R² vertical bar (0–1) ---
    ax2 = axes[2]
    ax2.bar([0], [r2], width=0.45, color="#059669", edgecolor="#065f46", linewidth=0.5, zorder=2)
    ax2.set_xticks([0])
    ax2.set_xticklabels(["R²"], fontsize=11, fontweight="semibold")
    ax2.set_ylabel("R² score (0–1)", color="#334155", labelpad=10)
    ax2.set_title("Coefficient of determination", fontsize=11, pad=16, color="#0f172a")
    ax2.set_ylim(0, 1.05)
    ax2.axhline(1.0, color="#cbd5e1", linestyle=":", linewidth=0.8, zorder=0)
    ax2.yaxis.grid(True, zorder=0)
    ax2.set_axisbelow(True)
    # Value below the bar (avoids crowding the subplot title)
    ax2.text(
        0.5,
        -0.2,
        f"R² = {r2:.4f}\n({100 * r2:.2f}% variance explained)",
        transform=ax2.transAxes,
        ha="center",
        va="top",
        fontsize=9.5,
        fontweight="semibold",
        color="#064e3b",
        linespacing=1.25,
    )
    ax2.text(
        0.5,
        -0.34,
        "Higher is better · max = 1.0",
        transform=ax2.transAxes,
        ha="center",
        fontsize=8,
        color="#64748b",
    )

    plt.savefig(PLOT_PATH, dpi=175, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved plot: {PLOT_PATH}")

    try:
        from plot_data_split_pie import generate_split_pie

        generate_split_pie()
    except Exception as e:
        print(f"Could not generate train/val/test pie chart: {e}")


if __name__ == "__main__":
    main()
