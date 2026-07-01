import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config import (
    BG_COLOR,
    ACCENT_COLOR,
    SECONDARY_COLOR,
    TEXT_COLOR,
    GRID_COLOR,
    CHART_FIGSIZE,
    CHART_DPI,
    # Input paths
    PRESENTER_DETAILS_PATH,
    ALL_SESSIONS_PATH,
    PARTICIPANT_HISTORY_PATH,
    EMPLOYEE_MASTER_PATH,
    # Output paths
    OUTPUT_FOLDER,
    SESSION_SUMMARY_PATH,
    SESSION_SUMMARY_SHEET,
    FEEDBACK_TREND_PNG_PATH,
    SESSION_COUNT_PNG_PATH,
    EMPLOYEES_VS_PARTICIPANTS_PNG_PATH,
    EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH,
    PARTICIPATION_RATE_PNG_PATH,
)


# ---------------------------------------------------------------------------
# Private helpers — shared across functions
# ---------------------------------------------------------------------------

def _load_participant_counts() -> "pd.DataFrame | None":
    """
    Load all_participant_history.xlsx and return unique participant count
    per session date.  Returns None if the file does not exist / is empty.
    """
    if not PARTICIPANT_HISTORY_PATH.exists():
        return None

    df = pd.read_excel(PARTICIPANT_HISTORY_PATH)
    df = df.rename(columns=str.strip)
    df["Session_Date"] = pd.to_datetime(df["Session_Date"], errors="coerce")
    df = df.dropna(subset=["Session_Date"])

    if df.empty:
        return None

    return (
        df.groupby("Session_Date")["Email"]
        .nunique()
        .reset_index(name="Participants")
        .sort_values("Session_Date")
        .reset_index(drop=True)
    )


def _load_total_employees() -> int:
    """Return total headcount from employee_master.xlsx."""
    emp = pd.read_excel(EMPLOYEE_MASTER_PATH)
    emp = emp.rename(columns=str.strip)
    return len(emp)


def _style_axes(ax, fig):
    """Apply common dark-theme styling to axes."""
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)


# ---------------------------------------------------------------------------
# 1. Feedback trend — Total vs Positive per session
# ---------------------------------------------------------------------------

def generate_feedback_trend_png():
    """Line chart: total and positive feedback count per session."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    session_summary = pd.read_excel(
        SESSION_SUMMARY_PATH, sheet_name=SESSION_SUMMARY_SHEET
    )
    presenter = pd.read_excel(PRESENTER_DETAILS_PATH)
    session_summary = session_summary.rename(columns=str.strip)
    presenter       = presenter.rename(columns=str.strip)

    session_summary["Session_ID"] = (
        session_summary["Session_ID"].astype(str).str.strip()
    )
    presenter["Session_ID"] = presenter["Session_ID"].astype(str).str.strip()

    merged = session_summary.merge(
        presenter[["Session_ID", "Date"]], on="Session_ID", how="left"
    )
    merged["Date"] = pd.to_datetime(merged["Date"])
    merged = (
        merged[merged["Feedback_Count"] > 0]
        .sort_values("Date")
        .reset_index(drop=True)
    )

    if merged.empty:
        return None

    merged["Label"] = merged["Date"].dt.strftime("%d %b %Y")
    x = list(range(len(merged)))

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    _style_axes(ax, fig)

    ax.plot(x, merged["Feedback_Count"].values,
            color=ACCENT_COLOR, marker="o", markersize=10,
            linewidth=2.5, label="Total Feedback")
    ax.plot(x, merged["Positive_Feedback_Count"].values,
            color=SECONDARY_COLOR, marker="s", markersize=9,
            linewidth=2.5, label="Positive Feedback")

    for i, row in merged.iterrows():
        ax.text(i, row["Feedback_Count"] + 0.3,
                str(int(row["Feedback_Count"])),
                ha="center", va="bottom",
                color=ACCENT_COLOR, fontsize=10, fontweight="bold")
        ax.text(i, row["Positive_Feedback_Count"] - 0.3,
                str(int(row["Positive_Feedback_Count"])),
                ha="center", va="top",
                color=SECONDARY_COLOR, fontsize=10, fontweight="bold")

    ax.set_title("Feedback \u2014 Per Session",
                 color=ACCENT_COLOR, fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Session Date", color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Count",        color=TEXT_COLOR, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(merged["Label"].values)
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    ax.legend(loc="upper left", fontsize=11,
              facecolor=BG_COLOR, edgecolor=ACCENT_COLOR, labelcolor=TEXT_COLOR)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fig.savefig(FEEDBACK_TREND_PNG_PATH, dpi=CHART_DPI,
                facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return FEEDBACK_TREND_PNG_PATH


# ---------------------------------------------------------------------------
# 2. Session count — Monthly bar chart (all-time)
# ---------------------------------------------------------------------------

def generate_session_count_png():
    """Bar chart: number of sessions delivered per month (all-time)."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    all_sessions = pd.read_excel(ALL_SESSIONS_PATH)
    all_sessions = all_sessions.rename(columns=str.strip)
    all_sessions["Date"]  = pd.to_datetime(all_sessions["Date"])
    all_sessions["Month"] = all_sessions["Date"].dt.to_period("M")

    monthly = (
        all_sessions.groupby("Month").size()
        .reset_index(name="Session_Count")
    )
    monthly["Month_Label"] = monthly["Month"].dt.strftime("%b %Y")
    monthly = monthly.sort_values("Month").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    _style_axes(ax, fig)

    bars = ax.bar(monthly["Month_Label"], monthly["Session_Count"],
                  color=ACCENT_COLOR, alpha=0.85, width=0.6,
                  edgecolor=ACCENT_COLOR, linewidth=0.5)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1, str(int(h)),
                ha="center", va="bottom",
                color=ACCENT_COLOR, fontsize=11, fontweight="bold")

    ax.set_title("Sessions Delivered \u2014 Monthly",
                 color=ACCENT_COLOR, fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Month",         color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Session Count", color=TEXT_COLOR, fontsize=12)
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7, axis="y")
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fig.savefig(SESSION_COUNT_PNG_PATH, dpi=CHART_DPI,
                facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return SESSION_COUNT_PNG_PATH


# ---------------------------------------------------------------------------
# 3. Employees vs Participants — PER SESSION
# ---------------------------------------------------------------------------

def generate_employees_vs_participants_png():
    """Dual-line chart: unique attendees per session vs total headcount."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    total_employees = _load_total_employees()
    counts = _load_participant_counts()
    if counts is None:
        return None

    counts["Employees"]     = total_employees
    counts["Session_Label"] = counts["Session_Date"].dt.strftime("%d %b '%y")
    x = list(range(len(counts)))

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    _style_axes(ax, fig)

    ax.fill_between(x, counts["Employees"].values,    alpha=0.10, color=SECONDARY_COLOR)
    ax.fill_between(x, counts["Participants"].values, alpha=0.22, color=ACCENT_COLOR)

    ax.plot(x, counts["Participants"].values,
            color=ACCENT_COLOR, marker="o", markersize=8,
            linewidth=2.5, label="Participants (per session)")
    ax.plot(x, counts["Employees"].values,
            color=SECONDARY_COLOR, marker=None,
            linewidth=2, linestyle="--", label=f"Employees ({total_employees})")

    for i, row in counts.iterrows():
        ax.text(i, row["Participants"] + 0.4, str(int(row["Participants"])),
                ha="center", va="bottom",
                color=ACCENT_COLOR, fontsize=9, fontweight="bold")

    ax.set_title("Employees vs Participants \u2014 Per Session",
                 color=ACCENT_COLOR, fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Session Date", color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Headcount",    color=TEXT_COLOR, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(counts["Session_Label"].values)
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    ax.legend(loc="upper left", fontsize=11,
              facecolor=BG_COLOR, edgecolor=ACCENT_COLOR, labelcolor=TEXT_COLOR)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fig.savefig(EMPLOYEES_VS_PARTICIPANTS_PNG_PATH, dpi=CHART_DPI,
                facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return EMPLOYEES_VS_PARTICIPANTS_PNG_PATH


# ---------------------------------------------------------------------------
# 4. Employees vs Participants — MONTHLY
# ---------------------------------------------------------------------------

def generate_employees_vs_participants_monthly_png():
    """Dual-line chart: unique attendees per month vs total headcount."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    total_employees = _load_total_employees()

    if not PARTICIPANT_HISTORY_PATH.exists():
        return None

    raw = pd.read_excel(PARTICIPANT_HISTORY_PATH)
    raw = raw.rename(columns=str.strip)
    raw["Session_Date"] = pd.to_datetime(raw["Session_Date"], errors="coerce")
    raw = raw.dropna(subset=["Session_Date"])
    raw["Month"] = raw["Session_Date"].dt.to_period("M")

    monthly = (
        raw.groupby("Month")["Email"].nunique()
        .reset_index(name="Participants")
        .sort_values("Month")
        .reset_index(drop=True)
    )
    monthly["Employees"]   = total_employees
    monthly["Month_Label"] = monthly["Month"].dt.strftime("%b %Y")
    x = list(range(len(monthly)))

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    _style_axes(ax, fig)

    ax.fill_between(x, monthly["Employees"].values,    alpha=0.10, color=SECONDARY_COLOR)
    ax.fill_between(x, monthly["Participants"].values, alpha=0.22, color=ACCENT_COLOR)

    ax.plot(x, monthly["Participants"].values,
            color=ACCENT_COLOR, marker="o", markersize=9,
            linewidth=2.5, label="Participants (per month)")
    ax.plot(x, monthly["Employees"].values,
            color=SECONDARY_COLOR, marker=None,
            linewidth=2, linestyle="--", label=f"Employees ({total_employees})")

    for i, row in monthly.iterrows():
        ax.text(i, row["Participants"] + 0.4, str(int(row["Participants"])),
                ha="center", va="bottom",
                color=ACCENT_COLOR, fontsize=10, fontweight="bold")
        ax.text(i, row["Employees"] - 0.5, str(int(row["Employees"])),
                ha="center", va="top",
                color=SECONDARY_COLOR, fontsize=10, fontweight="bold")

    ax.set_title("Employees vs Participants \u2014 Monthly",
                 color=ACCENT_COLOR, fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Month",    color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Headcount",color=TEXT_COLOR, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(monthly["Month_Label"].values)
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    ax.legend(loc="upper left", fontsize=11,
              facecolor=BG_COLOR, edgecolor=ACCENT_COLOR, labelcolor=TEXT_COLOR)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    fig.savefig(EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH, dpi=CHART_DPI,
                facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH


# ---------------------------------------------------------------------------
# 5. Participation rate % — per session
# ---------------------------------------------------------------------------

def generate_participation_rate_png():
    """Color-coded bar chart: attendance rate % per session."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    total_employees = _load_total_employees()
    if total_employees == 0:
        return None

    counts = _load_participant_counts()
    if counts is None:
        return None

    counts["Rate"]          = (counts["Participants"] / total_employees * 100).round(1)
    counts["Session_Label"] = counts["Session_Date"].dt.strftime("%d %b '%y")
    x = list(range(len(counts)))

    def _color(rate: float) -> str:
        if rate >= 75:
            return "#4ADE80"
        if rate >= 50:
            return ACCENT_COLOR
        if rate >= 25:
            return "#FB923C"
        return "#F87171"

    colors = [_color(r) for r in counts["Rate"]]

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
    _style_axes(ax, fig)

    ax.bar(x, counts["Rate"].values, color=colors, width=0.6, alpha=0.85)

    for ref, lbl in [(25, "25%"), (50, "50%"), (75, "75%")]:
        ax.axhline(ref, color=GRID_COLOR, linewidth=1.2, linestyle="--", alpha=0.8)
        ax.text(len(x) - 0.5, ref + 0.8, lbl,
                color=TEXT_COLOR, fontsize=9, ha="right", alpha=0.7)

    for i, row in counts.iterrows():
        ax.text(i, row["Rate"] + 0.8, f"{row['Rate']}%",
                ha="center", va="bottom",
                color=TEXT_COLOR, fontsize=9, fontweight="bold")

    legend_patches = [
        mpatches.Patch(color="#4ADE80",    label="\u2265 75%  High"),
        mpatches.Patch(color=ACCENT_COLOR, label="\u2265 50%  Moderate"),
        mpatches.Patch(color="#FB923C",    label="\u2265 25%  Low"),
        mpatches.Patch(color="#F87171",    label="< 25%   Very low"),
    ]
    ax.legend(handles=legend_patches, loc="upper left", fontsize=10,
              facecolor=BG_COLOR, edgecolor=ACCENT_COLOR, labelcolor=TEXT_COLOR)

    ax.set_title("Participation Rate \u2014 Per Session",
                 color=ACCENT_COLOR, fontsize=18, fontweight="bold", pad=15)
    ax.set_xlabel("Session Date",      color=TEXT_COLOR, fontsize=12)
    ax.set_ylabel("Participation %",   color=TEXT_COLOR, fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(counts["Session_Label"].values)
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.5, axis="y")
    ax.set_ylim(bottom=0, top=110)
    plt.tight_layout()

    fig.savefig(PARTICIPATION_RATE_PNG_PATH, dpi=CHART_DPI,
                facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return PARTICIPATION_RATE_PNG_PATH


if __name__ == "__main__":
    print(f"Saved: {generate_feedback_trend_png()}")
    print(f"Saved: {generate_session_count_png()}")
    print(f"Saved: {generate_employees_vs_participants_png()}")
    print(f"Saved: {generate_employees_vs_participants_monthly_png()}")
    print(f"Saved: {generate_participation_rate_png()}")
