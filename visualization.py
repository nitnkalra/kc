import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.dates import DateFormatter

from config import (
    SEASON_FOLDER,
    BG_COLOR,
    ACCENT_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    GRID_COLOR,
    CHART_FIGSIZE,
    CHART_DPI,
)


def generate_feedback_trend_png():
    """Generate feedback chart — Total vs Positive feedback per session date."""

    output_folder = SEASON_FOLDER / "outputs"
    output_folder.mkdir(exist_ok=True)

    # Load session summary for feedback counts
    session_summary = pd.read_excel(
        output_folder / "Session_Summary.xlsx",
        sheet_name="Session_Summary"
    )

    # Load presenter details for session dates
    presenter_details = pd.read_excel(
        SEASON_FOLDER / "presenter_details.xlsx"
    )
    presenter_details.columns = presenter_details.columns.str.strip()
    presenter_details["Session_ID"] = (
        presenter_details["Session_ID"].astype(str).str.strip()
    )
    session_summary["Session_ID"] = (
        session_summary["Session_ID"].astype(str).str.strip()
    )

    # Merge to get dates
    merged = session_summary.merge(
        presenter_details[["Session_ID", "Date"]],
        on="Session_ID",
        how="left"
    )
    merged["Date"] = pd.to_datetime(merged["Date"])

    # Only include sessions where feedback was actually collected
    merged = merged[merged["Feedback_Count"] > 0]
    merged = merged.sort_values("Date").reset_index(drop=True)

    if merged.empty:
        return None

    # Use session labels on x-axis (prevents matplotlib date auto-range)
    merged["Label"] = merged["Date"].dt.strftime("%d %b %Y")

    # --- Plot ---
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x_positions = range(len(merged))

    # Lines
    ax.plot(
        x_positions,
        merged["Feedback_Count"].values,
        color=ACCENT_COLOR,
        marker="o",
        markersize=10,
        linewidth=2.5,
        label="Total Feedback"
    )
    ax.plot(
        x_positions,
        merged["Positive_Feedback_Count"].values,
        color=SECONDARY_COLOR,
        marker="s",
        markersize=9,
        linewidth=2.5,
        label="Positive Feedback"
    )

    # Data labels
    for i, row in merged.iterrows():
        ax.text(
            list(x_positions)[i], row["Feedback_Count"] + 0.3,
            str(int(row["Feedback_Count"])),
            ha="center", va="bottom",
            color=ACCENT_COLOR, fontsize=10, fontweight="bold"
        )
        ax.text(
            list(x_positions)[i], row["Positive_Feedback_Count"] - 0.3,
            str(int(row["Positive_Feedback_Count"])),
            ha="center", va="top",
            color=SECONDARY_COLOR, fontsize=10, fontweight="bold"
        )

    # Styling
    ax.set_title(
        "Feedback \u2014 Per Session",
        color=ACCENT_COLOR,
        fontsize=18,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Session Date", color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Count", color=TEXT_COLOR, fontsize=12)

    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(merged["Label"].values)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    plt.xticks(rotation=45, ha="right")

    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)

    ax.legend(
        loc="upper left",
        fontsize=11,
        facecolor=BG_COLOR,
        edgecolor=ACCENT_COLOR,
        labelcolor=TEXT_COLOR
    )

    ax.set_ylim(bottom=0)
    plt.tight_layout()

    # Save PNG
    output_path = output_folder / "feedback_trend.png"
    fig.savefig(
        output_path,
        dpi=CHART_DPI,
        facecolor=BG_COLOR,
        bbox_inches="tight"
    )
    plt.close(fig)

    return output_path


def generate_session_count_png():
    """Generate monthly session count bar chart from all_session_details.xlsx."""

    output_folder = SEASON_FOLDER / "outputs"
    output_folder.mkdir(exist_ok=True)

    # Load all session details (all-time data)
    all_sessions = pd.read_excel(
        SEASON_FOLDER / "all_session_details.xlsx"
    )
    all_sessions.columns = all_sessions.columns.str.strip()
    all_sessions["Date"] = pd.to_datetime(all_sessions["Date"])

    # Group by month
    all_sessions["Month"] = all_sessions["Date"].dt.to_period("M")
    monthly_counts = (
        all_sessions
        .groupby("Month")
        .size()
        .reset_index(name="Session_Count")
    )
    monthly_counts["Month_Label"] = (
        monthly_counts["Month"].dt.strftime("%b %Y")
    )
    monthly_counts = monthly_counts.sort_values("Month").reset_index(drop=True)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.bar(
        monthly_counts["Month_Label"],
        monthly_counts["Session_Count"],
        color=ACCENT_COLOR,
        alpha=0.85,
        width=0.6,
        edgecolor=ACCENT_COLOR,
        linewidth=0.5
    )

    # Data labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.1,
            str(int(height)),
            ha="center",
            va="bottom",
            color=ACCENT_COLOR,
            fontsize=11,
            fontweight="bold"
        )

    ax.set_title(
        "Sessions Delivered \u2014 Monthly",
        color=ACCENT_COLOR,
        fontsize=18,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Month", color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Session Count", color=TEXT_COLOR, fontsize=12)

    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    plt.xticks(rotation=45, ha="right")

    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7, axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)

    ax.set_ylim(bottom=0)
    plt.tight_layout()

    # Save PNG
    output_path = output_folder / "session_count.png"
    fig.savefig(
        output_path,
        dpi=CHART_DPI,
        facecolor=BG_COLOR,
        bbox_inches="tight"
    )
    plt.close(fig)

    return output_path


if __name__ == "__main__":
    saved1 = generate_feedback_trend_png()
    print(f"Saved: {saved1}")
    saved2 = generate_session_count_png()
    print(f"Saved: {saved2}")
