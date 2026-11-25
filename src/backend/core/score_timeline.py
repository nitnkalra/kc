"""
score_timeline.py
-----------------
Builds Score_Timeline.xlsx — per-employee cumulative score tracking.

Receives the history DataFrame directly from process_season() in-memory —
no intermediate Session_History.xlsx file needed.

Sheet layout
------------
  Timeline      → Full chronological history, one row per (Employee, Session).
  session_01    → All employees' score breakdown for session_01.
  session_02    → Same for session_02  (includes consecutive-bonus rows).
  …             → One sheet per session in all_session_details.

Per-session sheet columns
--------------------------
  Employee | Attendance_Points | Feedback_Points | Presentation_Points
  Volunteer_Points | Consecutive_Bonus | Session_Total | Cumulative_After_Session

  Consecutive_Bonus appears on the second session's sheet because the bonus
  is triggered when the employee completes the pair (i.e. attends session_02).

  Cumulative_After_Session = employee's running total AFTER this session.
  Sorted alphabetically by Employee name — NOT a leaderboard.
"""

import pandas as pd

from config import (
    ALL_SESSIONS_PATH,
    SEASON,
    SEASON_FOLDER,
    ATTENDANCE_FILE,
    BOT_EMAIL,
    SCORE_TIMELINE_PATH,
    OUTPUT_FOLDER,
    SESSION_TYPE_COLUMN,
)

# Point columns coming from the history DataFrame
POINT_COLS = [
    "Attendance_Points",
    "Feedback_Points",
    "Presentation_Points",
    "Volunteer_Points",
    "Consecutive_Bonus",
]

_ARROW = "\u2192"   # → (used in consecutive-bonus Session_IDs)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _resolve_session_date(
    session_id: str,
    date_map: dict,
) -> "pd.Timestamp | None":
    """
    Return the session date for a given Session_ID.

    Consecutive-bonus rows ("session_01 → session_02") are assigned
    the SECOND session's date — that is when the bonus was triggered.
    """
    sid = session_id.strip()
    if _ARROW in sid:
        second = sid.split(_ARROW)[1].strip()
        return date_map.get(second)
    return date_map.get(sid)


def _resolve_session_type(
    session_id: str,
    type_map: dict,
) -> str:
    """
    Return the session type label for a given Session_ID.

    Consecutive-bonus rows ("session_01 → session_02") → empty string
    (not tied to a single session type).
    """
    sid = session_id.strip()
    if _ARROW in sid:
        return ""
    return type_map.get(sid, "regular")


def _build_session_sheet(
    timeline: pd.DataFrame,
    session_date: "pd.Timestamp",
) -> pd.DataFrame:
    """
    Build the per-session score breakdown for one session.

    Filters timeline rows whose Session_Date matches session_date.
    Uses .dt.date comparison (Python datetime.date objects) to avoid
    silent failures from datetime64 precision / dtype mismatches
    across pandas versions.

    Sorted alphabetically by Employee name — not a leaderboard.
    Employees with Session_Total == 0 are kept (they were present).
    """
    # Convert both sides to datetime.date for a precision-safe comparison
    target_date = pd.Timestamp(session_date).date()
    session_rows = timeline[timeline["Session_Date"].dt.date == target_date]

    if session_rows.empty:
        return pd.DataFrame()

    # Sum point breakdown columns per employee
    pts = (
        session_rows
        .groupby("Employee", as_index=False)
        [POINT_COLS]
        .sum()
    )
    pts["Session_Total"] = pts[POINT_COLS].sum(axis=1)

    # Cumulative total after this session = max Cumulative_Total on this date
    cum = (
        session_rows
        .groupby("Employee", as_index=False)["Cumulative_Total"]
        .max()
        .rename(columns={"Cumulative_Total": "Cumulative_After_Session"})
    )

    return (
        pts.merge(cum, on="Employee", how="left")
        .sort_values("Employee")          # alphabetical — not a leaderboard
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def build_score_timeline(history: pd.DataFrame, logger) -> pd.DataFrame:
    """
    Build Score_Timeline.xlsx from the history DataFrame returned by
    process_season(). No disk read needed.

    Args:
        history: Raw per-activity DataFrame from process_season().
        logger:  Logger instance.

    Returns:
        Full Timeline DataFrame (also written to Score_Timeline.xlsx).
    """
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    # --- Work on a clean copy ---
    df = history.copy()
    df["Session_ID"] = df["Session_ID"].astype(str).str.strip()

    # --- Derive session dates from attendance KC bot timestamps ---
    all_sessions = pd.read_excel(ALL_SESSIONS_PATH)
    all_sessions = all_sessions.rename(columns=str.strip)
    all_sessions["Season"] = all_sessions["Season"].astype(str).str.strip()
    all_sessions["Session_ID"] = (
        all_sessions["Session_ID"].astype(str).str.strip()
    )
    current_sessions = all_sessions[
        all_sessions["Season"].str.lower() == SEASON.lower()
    ]

    date_map: dict = {}
    for _, row in current_sessions.iterrows():
        sid = str(row["Session_ID"]).strip()
        att_file = SEASON_FOLDER / sid / ATTENDANCE_FILE
        if not att_file.exists():
            continue
        att = pd.read_excel(att_file)
        att = att.rename(columns=str.strip)
        att["Email"] = att["Email"].astype(str).str.lower().str.strip()
        bot = att[att["Email"] == BOT_EMAIL]
        if bot.empty:
            continue
        try:
            date_map[sid] = pd.to_datetime(
                bot.iloc[0]["First Join"]
            ).normalize()
        except (ValueError, TypeError, KeyError):
            continue

    # --- Build session_id → session_type map ---
    # If Session_Type column is missing from all_session_details, default to "regular"
    if SESSION_TYPE_COLUMN in current_sessions.columns:
        type_map: dict = {
            str(r["Session_ID"]).strip():
            str(r.get(SESSION_TYPE_COLUMN, "")).strip().lower() or "regular"
            for _, r in current_sessions.iterrows()
        }
    else:
        type_map = {sid: "regular" for sid in date_map}

    # --- Assign a date to every history row ---
    df["Session_Date"] = df["Session_ID"].apply(
        lambda sid: _resolve_session_date(sid, date_map)
    )
    # Normalize here too — ensures consistent midnight timestamps
    df["Session_Date"] = pd.to_datetime(
        df["Session_Date"], errors="coerce"
    ).dt.normalize()

    unresolved = df["Session_Date"].isna().sum()
    if unresolved:
        logger.warning(
            f"Score_Timeline: {unresolved} row(s) could not be mapped "
            "to a session date and will be excluded."
        )
    df = df.dropna(subset=["Session_Date"])

    # --- Collapse to one row per (Employee, Session_ID, Session_Date) ---
    timeline = (
        df
        .groupby(
            ["Employee", "Session_ID", "Session_Date"],
            sort=False,
        )
        [POINT_COLS]
        .sum()
        .reset_index()
    )

    timeline["Session_Total"] = timeline[POINT_COLS].sum(axis=1)

    timeline = (
        timeline
        .sort_values(["Employee", "Session_Date"])
        .reset_index(drop=True)
    )

    timeline["Cumulative_Total"] = (
        timeline
        .groupby("Employee")["Session_Total"]
        .cumsum()
    )

    # --- Add Session_Type column ---
    timeline["Session_Type"] = timeline["Session_ID"].apply(
        lambda sid: _resolve_session_type(sid, type_map)
    )

    timeline = timeline[[
        "Employee",
        "Session_ID",
        "Session_Type",
        "Session_Date",
        "Attendance_Points",
        "Feedback_Points",
        "Presentation_Points",
        "Volunteer_Points",
        "Consecutive_Bonus",
        "Session_Total",
        "Cumulative_Total",
    ]]

    # --- Write multi-sheet Excel ---
    with pd.ExcelWriter(SCORE_TIMELINE_PATH, engine="openpyxl") as writer:

        # Sheet 1: Full cumulative timeline — all employees, all sessions
        timeline.to_excel(writer, sheet_name="Timeline", index=False)

        # Per-session sheets — score breakdown per employee, sorted by name
        sheets_written = 0
        for sid, s_date in sorted(date_map.items(), key=lambda x: x[1]):

            session_df = _build_session_sheet(timeline, s_date)

            if session_df.empty:
                logger.warning(
                    f"Score_Timeline: no data found for {sid} "
                    f"({s_date.date()}) — sheet skipped."
                )
                continue

            # Excel sheet names are limited to 31 characters
            session_df.to_excel(
                writer, sheet_name=sid[:31], index=False
            )
            sheets_written += 1

    logger.info(
        f"Score_Timeline.xlsx saved — "
        f"'Timeline' sheet ({len(timeline)} rows, "
        f"{timeline['Employee'].nunique()} employees) "
        f"+ {sheets_written} per-session sheet(s)"
    )

    return timeline
