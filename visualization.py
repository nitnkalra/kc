import numpy as np
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
    KC_ROOT,
    SEASON,
    SEASON_FOLDER,
    ATTENDANCE_FILE,
    BOT_EMAIL,
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
    SEASON_PARTICIPATION_PNG_PATH,
    SEASON_PARTICIPATION_HBAR_PNG_PATH,
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


def _derive_session_dates(all_time: bool = False) -> dict:
    """
    Build {Session_ID: Date} mapping by reading KC bot timestamps from
    each session's attendance.xlsx.

    Args:
        all_time: If True, derive dates for ALL sessions across all seasons.
                  If False (default), only current season.

    Returns dict of session_id → pd.Timestamp.
    """
    all_sessions = pd.read_excel(ALL_SESSIONS_PATH)
    all_sessions = all_sessions.rename(columns=str.strip)
    all_sessions["Season"] = all_sessions["Season"].astype(str).str.strip()

    if not all_time:
        all_sessions = all_sessions[
            all_sessions["Season"].str.lower() == SEASON.lower()
        ]

    dates = {}
    for _, row in all_sessions.iterrows():
        sid = str(row["Session_ID"]).strip()
        season = str(row["Season"]).strip()
        season_folder = KC_ROOT / season
        att_file = season_folder / sid / ATTENDANCE_FILE
        if not att_file.exists():
            continue
        att = pd.read_excel(att_file)
        att = att.rename(columns=str.strip)
        att["Email"] = att["Email"].astype(str).str.lower().str.strip()
        bot = att[att["Email"] == BOT_EMAIL]
        if bot.empty:
            continue
        try:
            dates[sid] = pd.to_datetime(bot.iloc[0]["First Join"])
        except (ValueError, TypeError, KeyError):
            continue
    return dates


def _load_season_participation_data() -> "pd.DataFrame | None":
    """
    Load and prepare season participation data — shared by all 9 chart variants.

    Returns DataFrame with columns: Session_ID, Topic, Date, Attendees, Rate, Label
    Sorted by Date. Rate is integer (rounded, no decimals).
    Returns None if data is empty or total_employees is 0.
    """
    total_employees = _load_total_employees()
    if total_employees == 0:
        return None

    session_summary = pd.read_excel(
        SESSION_SUMMARY_PATH, sheet_name=SESSION_SUMMARY_SHEET
    )
    session_summary = session_summary.rename(columns=str.strip)

    if session_summary.empty:
        return None

    # Derive dates from attendance KC bot timestamps
    session_dates = _derive_session_dates()
    session_summary["Session_ID"] = (
        session_summary["Session_ID"].astype(str).str.strip()
    )
    session_summary["Date"] = session_summary["Session_ID"].map(session_dates)
    merged = session_summary.dropna(subset=["Date"]).copy()
    merged["Date"] = pd.to_datetime(merged["Date"])
    merged = merged.sort_values("Date").reset_index(drop=True)

    merged["Rate"] = (merged["Attendees"] / total_employees * 100).apply(
        lambda v: int(round(v))
    )

    # Date-only label — avoids topic overlap on x-axis
    merged["Label"] = merged["Date"].dt.strftime("%d %b")

    return merged


# ---------------------------------------------------------------------------
# 1. Feedback trend — Total vs Positive per session
# ---------------------------------------------------------------------------

def generate_feedback_trend_png():
    """Line chart: total and positive feedback count per session."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    session_summary = pd.read_excel(
        SESSION_SUMMARY_PATH, sheet_name=SESSION_SUMMARY_SHEET
    )
    session_summary = session_summary.rename(columns=str.strip)
    session_summary["Session_ID"] = (
        session_summary["Session_ID"].astype(str).str.strip()
    )

    # Derive dates from attendance KC bot timestamps
    session_dates = _derive_session_dates()
    session_summary["Date"] = session_summary["Session_ID"].map(session_dates)
    merged = session_summary.copy()
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

    # Derive dates from attendance KC bot timestamps (all-time)
    session_dates = _derive_session_dates(all_time=True)
    all_sessions = pd.DataFrame(
        [(sid, dt) for sid, dt in session_dates.items()],
        columns=["Session_ID", "Date"],
    )
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
# 5. Participation rate % — per session (all-time)
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
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7, axis="y")
    ax.set_ylim(bottom=0, top=110)
    plt.tight_layout()

    fig.savefig(PARTICIPATION_RATE_PNG_PATH, dpi=CHART_DPI,
                facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return PARTICIPATION_RATE_PNG_PATH


# ---------------------------------------------------------------------------
# 6. Season Participation % — progress-bar style (current season only)
# ---------------------------------------------------------------------------

def generate_season_participation_png():
    """
    Compact progress-bar style bar chart: participation % for CURRENT SEASON.

    Design (optimized for online posting):
      - figsize (8, 5)
      - Narrow bars (0.35 width) — cleaner look
      - Integer % labels (no decimals) — bold inside filled bar
      - Background bar at 100% = GRID_COLOR, foreground = ACCENT_COLOR
      - No legend, no trend line — clean and minimal
    """

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    merged = _load_season_participation_data()
    if merged is None:
        return None

    n = len(merged)
    x = list(range(n))

    # --- Auto-scale: CHART_FIGSIZE as base, grows for many bars ---
    fig_w = max(CHART_FIGSIZE[0], n * 0.7)
    fig_h = CHART_FIGSIZE[1]
    bar_width = max(0.35, min(0.5, 6.0 / max(n, 1)))
    label_fs = max(7, min(10, 120 // max(n, 1)))
    xtick_fs = max(7, min(9, 100 // max(n, 1)))

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    _style_axes(ax, fig)

    # Background bars — represent 100% capacity (clearly light/pale)
    ax.bar(
        x, [100] * len(x),
        color=GRID_COLOR, width=bar_width,
        edgecolor=ACCENT_COLOR, linewidth=0.8,
        zorder=2,
    )

    # Foreground bars — actual participation % (solid accent color)
    bars = ax.bar(
        x, merged["Rate"].values,
        color=ACCENT_COLOR, width=bar_width,
        edgecolor=ACCENT_COLOR, linewidth=1.2,
        zorder=3,
    )

    # Bold integer % label inside the filled bar
    for i, bar in enumerate(bars):
        height = bar.get_height()
        rate_val = merged.iloc[i]["Rate"]

        # Position label inside bar if tall enough, else just above
        label_y = height * 0.5 if height > 18 else height + 2
        label_color = "white" if height > 18 else ACCENT_COLOR
        label_va = "center" if height > 18 else "bottom"

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            label_y,
            f"{rate_val}%",
            ha="center", va=label_va,
            color=label_color, fontsize=label_fs, fontweight="bold",
            zorder=6,
        )

    ax.set_title(
        "Season Participation",
        color=ACCENT_COLOR, fontsize=15, fontweight="bold", pad=14,
    )
    ax.set_xlabel("Session", color=TEXT_COLOR, fontsize=11)
    ax.set_ylabel("Participation %", color=TEXT_COLOR, fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(merged["Label"].values, fontsize=xtick_fs)
    if n > 8:
        plt.xticks(rotation=45, ha="right")
    ax.set_ylim(bottom=0, top=105)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.grid(True, color=GRID_COLOR, linewidth=0.4, alpha=0.5, axis="y")
    plt.tight_layout()

    fig.savefig(
        SEASON_PARTICIPATION_PNG_PATH, dpi=CHART_DPI,
        facecolor=BG_COLOR, bbox_inches="tight",
    )
    plt.close(fig)
    return SEASON_PARTICIPATION_PNG_PATH


# ---------------------------------------------------------------------------
# 7. Season Participation — HORIZONTAL BAR (dashboard style)
# ---------------------------------------------------------------------------

def generate_season_participation_hbar_png():
    """Horizontal bar chart — sessions top-to-bottom, bars left-to-right."""

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    merged = _load_season_participation_data()
    if merged is None:
        return None

    n = len(merged)

    # --- Auto-scale: CHART_FIGSIZE as base, grows for many bars ---
    fig_h = max(CHART_FIGSIZE[1], n * 0.4)
    fig_w = CHART_FIGSIZE[0]
    bar_h = max(0.3, min(0.5, 5.0 / max(n, 1)))
    label_fs = max(7, min(12, 120 // max(n, 1)))
    ytick_fs = max(7, min(9, 100 // max(n, 1)))

    # Reverse so earliest session is at top
    labels = merged["Label"].str.replace("\n", " \u2014 ", regex=False).values[::-1]
    rates = merged["Rate"].values[::-1]
    y = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    _style_axes(ax, fig)

    # Background bars (100%)
    ax.barh(y, [100] * len(y), color=GRID_COLOR, height=bar_h, zorder=2)
    # Foreground bars (actual %)
    ax.barh(y, rates, color=ACCENT_COLOR, height=bar_h, zorder=3)

    # % label at end of each bar
    for i, rate in enumerate(rates):
        ax.text(
            rate + 1, i, f"{rate}%",
            ha="left", va="center",
            color=ACCENT_COLOR, fontsize=label_fs, fontweight="bold",
        )

    ax.set_title(
        "Season Participation",
        color=ACCENT_COLOR, fontsize=15, fontweight="bold", pad=14,
    )
    ax.set_xlabel("Participation %", color=TEXT_COLOR, fontsize=11)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=ytick_fs)
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(True, color=GRID_COLOR, linewidth=0.4, alpha=0.5, axis="x")
    plt.tight_layout()

    fig.savefig(
        SEASON_PARTICIPATION_HBAR_PNG_PATH, dpi=CHART_DPI,
        facecolor=BG_COLOR, bbox_inches="tight",
    )
    plt.close(fig)
    return SEASON_PARTICIPATION_HBAR_PNG_PATH


# ---------------------------------------------------------------------------
# Runner — generate all charts
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    print(f"Saved: {generate_feedback_trend_png()}")
    print(f"Saved: {generate_session_count_png()}")
    print(f"Saved: {generate_employees_vs_participants_png()}")
    print(f"Saved: {generate_employees_vs_participants_monthly_png()}")
    print(f"Saved: {generate_participation_rate_png()}")
    print(f"Saved: {generate_season_participation_png()}")
    print(f"Saved: {generate_season_participation_hbar_png()}")
