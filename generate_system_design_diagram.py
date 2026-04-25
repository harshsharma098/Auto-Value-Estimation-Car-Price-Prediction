"""
Generate Fig. 3.1 style system design diagram for Auto Value Estimation.
Run: python3 generate_system_design_diagram.py
Output: system_design_fig_3_1.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parent / "system_design_fig_3_1.png"

# Layer colors (similar to reference: blue, rose, green, orange)
C_DATA = "#3b82f6"
C_PROC = "#ec4899"
C_SVC = "#22c55e"
C_PRES = "#f97316"
C_TEXT = "#0f172a"
C_WHITE = "#ffffff"


def add_round_box(ax, xy, w, h, fc, label, sublabels=None, fontsize=11):
    x, y = xy
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        facecolor=fc,
        edgecolor="#1e293b",
        linewidth=1.5,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h - 0.35, label, ha="center", va="top", fontsize=fontsize, fontweight="bold", color=C_WHITE)
    if sublabels:
        yy = y + h - 0.85
        for line in sublabels:
            ax.text(x + w / 2, yy, line, ha="center", va="top", fontsize=8.5, color=C_WHITE, alpha=0.95)
            yy -= 0.38


def main():
    fig, ax = plt.subplots(figsize=(14, 9), dpi=150)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("#f8fafc")

    ax.text(
        7,
        9.45,
        "Auto Value Estimation — System Architecture (Layered)",
        ha="center",
        va="top",
        fontsize=15,
        fontweight="bold",
        color=C_TEXT,
    )
    ax.text(
        7,
        8.85,
        "Research-to-product: file-based data, ML pipeline, Flask API, React client",
        ha="center",
        va="top",
        fontsize=9.5,
        color="#64748b",
    )

    # --- Layout: left column stacked layers, right: presentation + users ---
    # Data layer (top left)
    add_round_box(
        ax,
        (0.4, 6.5),
        5.5,
        1.6,
        C_DATA,
        "Data layer",
        [
            "• Cleaned dataset (CSV)",
            "• Market reference JSON (ex-showroom)",
            "• Trained model artifact (.joblib)",
        ],
    )

    # Processing layer
    add_round_box(
        ax,
        (0.4, 4.25),
        5.5,
        1.95,
        C_PROC,
        "Processing layer",
        [
            "• Preprocess: impute, One-Hot, scale",
            "• Regressor: XGBoost / LGBM / RF",
            "• Inference: cohort, depreciation, blend, EV & km",
        ],
    )

    # Service layer
    add_round_box(
        ax,
        (0.4, 2.15),
        5.5,
        1.75,
        C_SVC,
        "Service layer",
        [
            "• Flask REST API + CORS",
            "• /api/options, /api/predict, …",
            "• Validation & business rules",
        ],
    )

    # Presentation layer (right, spans middle)
    add_round_box(
        ax,
        (7.0, 3.2),
        5.2,
        3.3,
        C_PRES,
        "Presentation layer",
        [
            "• React + TypeScript + Vite",
            "• CarEstimationForm, Navbar",
            "• Pages: Home, Estimate Value, …",
        ],
    )

    # End users
    ax.add_patch(
        FancyBboxPatch(
            (10.2, 0.45),
            2.6,
            1.1,
            boxstyle="round,pad=0.02,rounding_size=0.02",
            facecolor="#e2e8f0",
            edgecolor="#64748b",
            linewidth=1.2,
        )
    )
    ax.text(11.5, 1.2, "End users", ha="center", va="center", fontsize=12, fontweight="bold", color=C_TEXT)
    ax.text(11.5, 0.75, "(browser)", ha="center", va="center", fontsize=8, color="#475569")

    # Arrows: data -> processing -> service
    for y1, y2 in [(6.5, 6.2), (4.25, 4.0), (2.15, 1.9)]:
        arr = FancyArrowPatch(
            (3.15, y1 - 0.05),
            (3.15, y2 + 0.1),
            arrowstyle="->",
            mutation_scale=18,
            color="#334155",
            linewidth=1.8,
        )
        ax.add_patch(arr)

    # Processing / service to presentation (horizontal)
    arr_p = FancyArrowPatch(
        (5.9, 5.5),
        (7.0, 5.5),
        arrowstyle="->",
        mutation_scale=20,
        color="#334155",
        linewidth=1.8,
    )
    ax.add_patch(arr_p)
    arr_p2 = FancyArrowPatch(
        (5.9, 3.5),
        (7.0, 3.8),
        arrowstyle="->",
        mutation_scale=20,
        color="#334155",
        linewidth=1.8,
    )
    ax.add_patch(arr_p2)

    # Data to processing vertical already done. Service to presentation: bottom arrow
    arr_s = FancyArrowPatch(
        (5.4, 2.15),
        (7.0, 3.1),
        arrowstyle="->",
        mutation_scale=18,
        color="#334155",
        linewidth=1.8,
        connectionstyle="arc3,rad=0.0",
    )
    ax.add_patch(arr_s)

    # Presentation to users (down)
    arr_u = FancyArrowPatch(
        (11.5, 3.2),
        (11.5, 1.55),
        arrowstyle="->",
        mutation_scale=20,
        color="#334155",
        linewidth=1.8,
    )
    ax.add_patch(arr_u)

    # Bidirectional hint service <-> presentation (dashed) — optional small note
    ax.text(
        6.2,
        0.5,
        "JSON over HTTP  •  CORS enabled for local dev",
        ha="left",
        fontsize=8.5,
        color="#64748b",
        style="italic",
    )

    # Legend note
    ax.text(
        0.4,
        0.15,
        "Fig. 3.1 — System design: modular layers. No mobile app in v1; web client only. No cloud DB in reference build.",
        ha="left",
        fontsize=7.5,
        color="#94a3b8",
    )

    plt.tight_layout()
    plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none", pad_inches=0.25)
    plt.close()
    print("Saved:", OUT)


if __name__ == "__main__":
    main()
