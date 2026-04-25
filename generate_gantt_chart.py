"""
Generate Gantt chart image (Table 1.2) from project schedule.
Run: python3 generate_gantt_chart.py
Output: gantt_chart_table_1_2.png
"""

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Table 1.2 — Task, Start, End, Duration (dates as DD/MM/YYYY)
ROWS = [
    ("Research Proposal", "01/03/2025", "18/03/2025", "2 weeks"),
    ("Literature Review", "18/03/2025", "21/04/2025", "5 weeks"),
    ("Data Collection and Preprocessing", "21/07/2025", "11/08/2025", "3 weeks"),
    ("Model Development", "11/08/2025", "01/10/2025", "7 weeks"),
    ("Model Training and Evaluation", "01/10/2025", "28/10/2025", "4 weeks"),
    ("Results Analysis and Interpretation", "09/01/2026", "07/02/2026", "4 weeks"),
    ("Paper Writing and Revision", "07/02/2026", "20/03/2026", "6 weeks"),
    ("Final Review and Submission", "20/03/2026", "09/04/2026", "3 weeks"),
]

FMT = "%d/%m/%Y"
COLORS = [
    "#1d4ed8", "#5b21b6", "#0d9488", "#a21caf", "#c2410c", "#15803d", "#a16207", "#991b1b"
]


def main():
    fig, ax = plt.subplots(figsize=(15, 7.2), facecolor="white")

    for i, (name, s, e, dur) in enumerate(ROWS):
        start = datetime.strptime(s, FMT)
        end = datetime.strptime(e, FMT)
        y = len(ROWS) - 1 - i
        start_num = mdates.date2num(start)
        end_num = mdates.date2num(end)
        width = end_num - start_num
        ax.barh(
            y,
            width,
            left=start_num,
            height=0.68,
            color=COLORS[i % len(COLORS)],
            edgecolor="white",
            linewidth=0.9,
        )
        # Duration label inside bar (center)
        ax.text(
            start_num + width * 0.5,
            y,
            dur,
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white",
        )

    ax.set_yticks(range(len(ROWS)))
    ax.set_yticklabels([r[0] for r in reversed(ROWS)], fontsize=9.5)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8.5)
    ax.set_xlabel("Calendar timeline", fontsize=10, fontweight="600")
    ax.set_title("Table 1.2: Gantt Chart\nAuto Value Estimation — Project Schedule", fontsize=12, fontweight="bold", pad=14)
    ax.set_xlim(mdates.date2num(datetime(2025, 2, 10)), mdates.date2num(datetime(2026, 4, 25)))
    ax.grid(axis="x", linestyle="--", alpha=0.4, which="major")
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.text(
        0.5,
        0.02,
        "Durations match Table 1.2 (start/end dates as DD/MM/YYYY). Gaps on the timeline reflect breaks between phases as in the table.",
        ha="center",
        fontsize=7.5,
        color="#64748b",
    )

    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    out = __file__.replace("generate_gantt_chart.py", "gantt_chart_table_1_2.png")
    plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()
    print("Saved:", out)


if __name__ == "__main__":
    main()
