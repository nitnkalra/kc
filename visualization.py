import pandas as pd
import matplotlib.pyplot as plt

from config import (
    SEASON_FOLDER,
    BG_COLOR,
    ACCENT_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    GRID_COLOR,
    CHART_FIGSIZE,
    CHART_DPI,
    # File names
    PRESENTER_DETAILS_FILE,
    ALL_SESSIONS_FILE,
    PARTICIPANT_HISTORY_FILE,
    SESSION_SUMMARY_FILE,
    SESSION_SUMMARY_SHEET,
    EMPLOYEE_MASTER_FILE,
    # Output
    OUTPUT_FOLDER,
    FEEDBACK_TREND_PNG,
    SESSION_COUNT_PNG,
    EMPLOYEES_VS_PARTICIPANTS_PNG,
)


def generate_feedback_trend_png():
    """Generate feedback chart — Total vs Positive feedback per session date."""

    output_folder = SEASON_FOLDER / OUTPUT_FOLDER
    output_folder.mkdir(exist_ok=True)

    # Load session summary and presenter details
    session_summary = pd.read_excel(
        output_folder / SESSION_SUMMARY_FILE,
        sheet_name=SESSION_SUMMARY_SHEET
    )
    presenter_details = pd.read_excel(
        SEASON_FOLDER / PRESENTER_DETAILS_FILE
    )
    presenter_details = presenter_details.rename(columns=str.strip)
    session_summary = session_summary.rename(columns=str.strip)

    presenter_details["Session_ID"] = (
        presenter_details["Session_ID"].astype(str).str.strip()
    )
    session_summary["Session_ID"] = (
        session_summary["Session_ID"].astype(str).str.strip()
    )

    # Merge to get session dates
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
    n = len(merged)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    x_positions = list(range(n))

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

    # Data labels — i is 0-based after reset_index(drop=True)
    for i, row in merged.iterrows():
        ax.text(
            i, row["Feedback_Count"] + 0.3,
            str(int(row["Feedback_Count"])),
            ha="center", va="bottom",
            color=ACCENT_COLOR, fontsize=10, fontweight="bold"
        )
        ax.text(
            i, row["Positive_Feedback_Count"] - 0.3,
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

    ax.set_xticks(x_positions)
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
    output_path = output_folder / FEEDBACK_TREND_PNG
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

    output_folder = SEASON_FOLDER / OUTPUT_FOLDER
    output_folder.mkdir(exist_ok=True)

    # Load all session details (all-time data)
    all_sessions = pd.read_excel(
        SEASON_FOLDER.parent / ALL_SESSIONS_FILE
    )
    all_sessions = all_sessions.rename(columns=str.strip)
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
    monthly_counts = (
        monthly_counts
        .sort_values("Month")
        .reset_index(drop=True)
    )

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
    output_path = output_folder / SESSION_COUNT_PNG
    fig.savefig(
        output_path,
        dpi=CHART_DPI,
        facecolor=BG_COLOR,
        bbox_inches="tight"
    )
    plt.close(fig)

    return output_path


def generate_employees_vs_participants_png():
    """
    Generate all-time Employees vs Participants line chart per month.

    - Participants: unique attendees per month, read from
      all_participant_history.xlsx (Session_Date, Email).
      Appended by processor.py each season run.
    - Employees: total headcount from the current season's
      employee_master (used as the organisation baseline).
    """

    base_folder = SEASON_FOLDER.parent  # kc/ root
    output_folder = SEASON_FOLDER / OUTPUT_FOLDER
    output_folder.mkdir(exist_ok=True)

    # --- Baseline: total employees from current season ---
    employee_master = pd.read_excel(
        SEASON_FOLDER / EMPLOYEE_MASTER_FILE
    )
    employee_master = employee_master.rename(columns=str.strip)
    total_employees = len(employee_master)

    # --- Load participant history ---
    history_file = base_folder / PARTICIPANT_HISTORY_FILE

    if not history_file.exists():
        return None

    participant_history = pd.read_excel(history_file)
    participant_history = participant_history.rename(columns=str.strip)
    participant_history["Session_Date"] = pd.to_datetime(
        participant_history["Session_Date"],
        errors="coerce",
    )
    participant_history["Month"] = (
        participant_history["Session_Date"]
        .dt.to_period("M")
    )

    # Unique participants per month
    df = (
        participant_history
        .groupby("Month")["Email"]
        .nunique()
        .reset_index(name="Participants")
    )
    df["Employees"] = total_employees
    df = df.sort_values("Month").reset_index(drop=True)

    if df.empty:
        return None

    # Include year in label — data spans multiple years
    df["Month_Label"] = df["Month"].dt.strftime("%b %Y")
    x_pos = list(range(len(df)))

    # --- Plot ---
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # Area fills
    ax.fill_between(
        x_pos,
        df["Employees"].values,
        alpha=0.12,
        color=SECONDARY_COLOR,
    )
    ax.fill_between(
        x_pos,
        df["Participants"].values,
        alpha=0.25,
        color=ACCENT_COLOR,
    )

    # Lines
    ax.plot(
        x_pos,
        df["Participants"].values,
        color=ACCENT_COLOR,
        marker="o",
        markersize=9,
        linewidth=2.5,
        label="Participants",
    )
    ax.plot(
        x_pos,
        df["Employees"].values,
        color=SECONDARY_COLOR,
        marker="o",
        markersize=9,
        linewidth=2.5,
        label="Employees",
    )

    # Data labels — i is 0-based after reset_index(drop=True)
    for i, row in df.iterrows():
        ax.text(
            i, row["Participants"] + 0.5,
            str(int(row["Participants"])),
            ha="center", va="bottom",
            color=ACCENT_COLOR, fontsize=10, fontweight="bold",
        )
        ax.text(
            i, row["Employees"] - 0.5,
            str(int(row["Employees"])),
            ha="center", va="top",
            color=SECONDARY_COLOR, fontsize=10, fontweight="bold",
        )

    # Styling
    ax.set_title(
        "Employees vs Participants",
        color=ACCENT_COLOR,
        fontsize=18,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Month", color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Count", color=TEXT_COLOR, fontsize=12)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df["Month_Label"].values)
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
        labelcolor=TEXT_COLOR,
    )

    ax.set_ylim(bottom=0)
    plt.tight_layout()

    output_path = output_folder / EMPLOYEES_VS_PARTICIPANTS_PNG
    fig.savefig(
        output_path,
        dpi=CHART_DPI,
        facecolor=BG_COLOR,
        bbox_inches="tight",
    )
    plt.close(fig)

    return output_path


if __name__ == "__main__":
    saved1 = generate_feedback_trend_png()
    print(f"Saved: {saved1}")
    saved2 = generate_session_count_png()
    print(f"Saved: {saved2}")
    saved3 = generate_employees_vs_participants_png()
    print(f"Saved: {saved3}")
