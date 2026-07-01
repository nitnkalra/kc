import json
import pandas as pd
from datetime import timedelta

from config import (
    # Paths
    SEASON_FOLDER,
    EMPLOYEE_MASTER_PATH,
    PRESENTER_DETAILS_PATH,
    VOLUNTEER_PATH,
    PARTICIPANT_HISTORY_PATH,
    ATTENDANCE_FILE,
    FEEDBACK_FILE,
    OUTPUT_FOLDER,
    LEADERBOARD_JSON_PATH,
    LEADERBOARD_EXCEL_PATH,
    SESSION_SUMMARY_PATH,
    # Sheet names
    SESSION_SUMMARY_SHEET,
    FEEDBACK_INSIGHTS_SHEET,
    # Scoring
    FEEDBACK_POINTS,
    PRESENTATION_POINTS,
    JOIN_BUFFER_MINUTES,
    LEAVE_BUFFER_MINUTES,
    FEEDBACK_RATING_COLUMN,
    POSITIVE_RATINGS,
    FEEDBACK_CATEGORY_COLUMN,
    CONSECUTIVE_SESSION_BONUS,
    VOLUNTEER_ROLE_POINTS,
    VOLUNTEER_TRACKER_SHEET,
    VOLUNTEER_DETAILS_SHEET,
    # Bot
    BOT_EMAIL,
)

from src.scoring import get_attendance_points


# ---------------------------------------------------------------------------
# Volunteer name resolver
# ---------------------------------------------------------------------------

def _resolve_volunteer_email(
    name: str,
    name_to_email: dict,
    logger,
) -> "str | None":
    """
    Resolve a volunteer name (possibly short or partial) to their canonical email.

    Resolution order:
        1. Exact match       — "nitin kalra"  maps directly.
        2. First-token match — "nitin"        matches "nitin kalra" (first word).
        3. Starts-with match — "nitin k"      matches "nitin kalra".
        4. Substring match   — "kalra"        matches "nitin kalra" (any part).

    If multiple candidates match, the longest (most specific) full name wins.
    A warning is logged when the match is ambiguous.
    Returns None when no match is found at all.
    """
    key = name.strip().lower()

    # 1. Exact match
    if key in name_to_email:
        return name_to_email[key]

    # 2 / 3 / 4. Partial matching — collect all full names that fit
    candidates = [
        full_name for full_name in name_to_email
        if key in full_name.split()           # whole-word token match
        or full_name.startswith(key + " ")    # starts-with (handles "nitin k")
        or key in full_name                   # substring fallback
    ]

    if not candidates:
        return None

    # Prefer the longest (most specific) match to minimise false positives
    candidates.sort(key=len, reverse=True)

    if len(candidates) > 1:
        logger.warning(
            f"Volunteer name '{name}' matched multiple entries: "
            f"{candidates} — using '{candidates[0]}'."
        )

    return name_to_email[candidates[0]]


# ---------------------------------------------------------------------------
# Volunteer points helper
# ---------------------------------------------------------------------------

def _append_volunteer_rows(
    history_rows: list,
    presenter_details: pd.DataFrame,
    email_to_name: dict,
    logger,
) -> None:
    """
    Read kc_volunteer_team.xlsx and append one history row
    per volunteer activity per session.

    Display name resolution priority (ensures no duplicate rows in leaderboard):
        1. employee_master  — canonical source, used everywhere else in pipeline
        2. volunteer_details full name — fallback if volunteer not in employee_master
        3. raw tracker name — last resort (should never reach this in practice)
    """
    if not VOLUNTEER_PATH.exists():
        logger.warning(
            f"Volunteer file not found: {VOLUNTEER_PATH.name}"
            " — skipping volunteer points."
        )
        return

    try:
        tracker = pd.read_excel(
            VOLUNTEER_PATH,
            sheet_name=VOLUNTEER_TRACKER_SHEET,
        )
        tracker = tracker.rename(columns=str.strip)

        details = pd.read_excel(
            VOLUNTEER_PATH,
            sheet_name=VOLUNTEER_DETAILS_SHEET,
        )
        details = details.rename(columns=str.strip)

    except Exception as e:
        logger.error(f"Error loading volunteer file: {e}")
        return

    # name (lowercase) → email  — for resolving short/partial tracker names
    name_to_email = {
        str(r.get("Volunteer_name", "")).strip().lower():
        str(r.get("Volunteer_email", "")).strip().lower()
        for _, r in details.iterrows()
        if pd.notna(r.get("Volunteer_name"))
        and pd.notna(r.get("Volunteer_email"))
    }

    # email → full name from volunteer_details — secondary display_name fallback.
    # Prevents duplicate leaderboard rows when a volunteer is not in employee_master.
    vol_email_to_name = {
        str(r.get("Volunteer_email", "")).strip().lower():
        str(r.get("Volunteer_name", "")).strip()
        for _, r in details.iterrows()
        if pd.notna(r.get("Volunteer_email"))
        and pd.notna(r.get("Volunteer_name"))
    }

    # session_id → topic
    session_topics = {
        str(r["Session_ID"]).strip(): str(r["Topic"]).strip()
        for _, r in presenter_details.iterrows()
    }

    for _, row in tracker.iterrows():

        session_id = str(row.get("Session_ID", "")).strip()
        topic = session_topics.get(
            session_id,
            str(row.get("Session_name", "")).strip(),
        )

        for col, points in VOLUNTEER_ROLE_POINTS.items():

            if col not in tracker.columns:
                continue

            cell = str(row.get(col, "")).strip()
            if not cell or cell.lower() in ("nan", "none", ""):
                continue

            for name in [n.strip() for n in cell.split(",")]:
                if not name:
                    continue

                # Resolve name → email with partial/short-name support
                email = _resolve_volunteer_email(name, name_to_email, logger)

                if email is None:
                    logger.warning(
                        f"Volunteer '{name}' not found in "
                        f"{VOLUNTEER_DETAILS_SHEET} — skipped."
                    )
                    continue

                # Display name resolution — 3-level priority:
                # 1. employee_master  (same source as attendance rows → no duplicates)
                # 2. volunteer_details full name (if not in employee_master)
                # 3. raw tracker name (last resort)
                display_name = (
                    email_to_name.get(email)
                    or vol_email_to_name.get(email)
                    or name
                )

                history_rows.append([
                    session_id, topic, display_name,
                    0, 0, 0, 0,      # Attendance_%, Att_Pts, Feedback_Pts, Pres_Pts
                    points,          # Volunteer_Points
                    0,               # Consecutive_Bonus
                    points,          # Total_Points
                ])


# ---------------------------------------------------------------------------
# Consecutive session bonus helper
# ---------------------------------------------------------------------------

def _append_consecutive_bonus_rows(
    history_rows: list,
    presenter_details: pd.DataFrame,
) -> None:
    """
    Award CONSECUTIVE_SESSION_BONUS per consecutive session pair attended.

    session_01 + session_02 → +5
    session_02 + session_03 → +5  (another +5, not cumulative per pair)

    Excluded from consecutive bonus eligibility:
      - Pure volunteer rows  (Att%=0, PresPts=0, VolPts>0) — volunteer only, not attended
      - Presenter rows       (PresPts>0) — presenting ≠ attending as a participant

    Host scenario:
      If a host also appears in attendance.xlsx (physically present), their
      attendance row IS counted. Volunteer row is skipped. So a host who
      attends consecutive sessions correctly earns the bonus.
    """
    sessions = presenter_details.copy()
    sessions["Date"] = pd.to_datetime(sessions["Date"], errors="coerce")
    sessions = sessions.dropna(subset=["Date"]).sort_values("Date")

    session_order = (
        sessions["Session_ID"].astype(str).str.strip().tolist()
    )

    if len(session_order) < 2:
        return

    valid_sids = set(session_order)

    attended: dict = {}

    for row in history_rows:
        sid = row[0]
        if sid not in valid_sids:
            continue

        # Skip pure volunteer rows — volunteering alone does not count as attending
        if row[3] == 0 and row[6] == 0 and row[7] > 0:
            continue

        # Skip presenter rows — presenting ≠ attending as a participant
        if row[6] > 0:
            continue

        emp = row[2]
        if emp not in attended:
            attended[emp] = set()
        attended[emp].add(sid)

    for employee, sids in attended.items():
        for i in range(len(session_order) - 1):
            s1, s2 = session_order[i], session_order[i + 1]
            if s1 in sids and s2 in sids:
                history_rows.append([
                    f"{s1} \u2192 {s2}",
                    "Consecutive Attendance Bonus",
                    employee,
                    0, 0, 0, 0,
                    0,
                    CONSECUTIVE_SESSION_BONUS,
                    CONSECUTIVE_SESSION_BONUS,
                ])


# ---------------------------------------------------------------------------
# Main season processor
# ---------------------------------------------------------------------------

def process_season(logger) -> pd.DataFrame:
    """
    Process all sessions in SEASON_FOLDER and write output files.

    Reads:  employee_master, presenter_details, per-session attendance/feedback,
            kc_volunteer_team (optional)
    Writes: Leaderboard.xlsx, Session_Summary.xlsx,
            leaderboard.json, all_participant_history.xlsx (appended)

    Returns:
        history (pd.DataFrame) — raw per-activity rows, passed directly to
        build_score_timeline() so no intermediate file is needed on disk.
    """
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    # --- Employee master ---
    employee_master = pd.read_excel(EMPLOYEE_MASTER_PATH)
    employee_master = employee_master.rename(columns=str.strip)
    employee_master["Email"] = (
        employee_master["Email"].astype(str).str.lower().str.strip()
    )

    # Build email → display name map
    name_col = next(
        (c for c in employee_master.columns if "name" in c.lower()),
        next(
            (c for c in employee_master.columns if c.lower() != "email"),
            None,
        ),
    )
    email_to_name: dict = {}
    if name_col:
        for _, r in employee_master.iterrows():
            em = str(r.get("Email", "")).lower().strip()
            nm = r.get(name_col)
            if em and pd.notna(nm):
                nm = str(nm).strip()
                if nm:
                    email_to_name[em] = nm

    logger.info("Input files loaded successfully")

    # --- Presenter details ---
    presenter_details = pd.read_excel(PRESENTER_DETAILS_PATH)
    presenter_details = presenter_details.rename(columns=str.strip)

    history_rows: list = []
    feedback_category_counter: dict = {}
    session_summary_rows: list = []
    participant_history_rows: list = []

    # Tracks emails already warned about — avoids repeating the same
    # warning across multiple sessions for the same unknown email.
    unknown_emails_warned: set = set()

    # --- Process each session ---
    for _, session in presenter_details.iterrows():

        session_id = str(session["Session_ID"]).strip()
        topic      = str(session["Topic"]).strip()

        session_folder  = SEASON_FOLDER / session_id
        attendance_file = session_folder / ATTENDANCE_FILE
        feedback_file   = session_folder / FEEDBACK_FILE

        if not attendance_file.exists():
            logger.error(f"Attendance missing: {session_id}")
            continue

        try:
            start_dt = pd.to_datetime(
                f"{session['Date']} {session['Start Time']}"
            )
            end_dt = pd.to_datetime(
                f"{session['Date']} {session['End Time']}"
            )
        except Exception as e:
            logger.error(f"{session_id} datetime error: {e}")
            continue

        ideal_start   = start_dt + timedelta(minutes=JOIN_BUFFER_MINUTES)
        ideal_end     = end_dt   - timedelta(minutes=LEAVE_BUFFER_MINUTES)
        ideal_seconds = max((ideal_end - ideal_start).total_seconds(), 1)

        attendance = pd.read_excel(attendance_file)
        attendance = attendance.rename(columns=str.strip)
        attendance["Email"] = (
            attendance["Email"].astype(str).str.lower().str.strip()
        )

        feedback_emails         = set()
        positive_feedback_count = 0
        feedback_count          = 0

        if feedback_file.exists():
            feedback = pd.read_excel(feedback_file)
            feedback = feedback.rename(columns=str.strip)
            feedback["Email"] = (
                feedback["Email"].astype(str).str.lower().str.strip()
            )
            feedback_emails = set(feedback["Email"])
            feedback_count  = len(feedback)

            # Rating column — config constant first, fuzzy fallback
            rating_col = (
                FEEDBACK_RATING_COLUMN
                if FEEDBACK_RATING_COLUMN in feedback.columns
                else next(
                    (c for c in feedback.columns
                     if "rate" in c.lower() and "session" in c.lower()),
                    None,
                )
            )
            if rating_col:
                positive_feedback_count = (
                    feedback[rating_col]
                    .astype(str).str.lower().str.strip()
                    .isin(POSITIVE_RATINGS)
                    .sum()
                )

            # Category column — config constant first, fuzzy fallback
            like_col = (
                FEEDBACK_CATEGORY_COLUMN
                if FEEDBACK_CATEGORY_COLUMN in feedback.columns
                else next(
                    (c for c in feedback.columns
                     if "like" in c.lower() and "session" in c.lower()),
                    None,
                )
            )
            if like_col:
                for value in feedback[like_col].dropna():
                    feedback_category_counter[value] = (
                        feedback_category_counter.get(value, 0) + 1
                    )

        presenter_names_this_session = {
            name.strip().lower()
            for name in str(session["Name"]).split(",")
            if name.strip()
        }

        attendees = 0

        for _, row in attendance.iterrows():
            email        = str(row["Email"]).lower().strip()
            display_name = email_to_name.get(email, email)

            if email == BOT_EMAIL:
                continue

            # Warn once per unknown email — helps identify employees missing
            # from employee_master. Row is still processed normally.
            if email not in email_to_name and email not in unknown_emails_warned:
                logger.warning(
                    f"[{session_id}] Email '{email}' found in attendance "
                    f"but not in employee_master.xlsx — "
                    f"add this employee to employee_master to resolve their name."
                )
                unknown_emails_warned.add(email)

            # Presenter detected — track presence and headcount only.
            if display_name.lower() in presenter_names_this_session:
                participant_history_rows.append({
                    "Session_Date": start_dt.date(),
                    "Email":        email,
                })
                attendees += 1
                continue

            participant_history_rows.append({
                "Session_Date": start_dt.date(),
                "Email":        email,
            })
            attendees += 1

            try:
                join_time  = pd.to_datetime(row["First Join"])
                leave_time = pd.to_datetime(row["Last Leave"])
            except (ValueError, TypeError):
                continue

            overlap_seconds = max(
                0,
                (
                    min(leave_time, ideal_end) -
                    max(join_time,  ideal_start)
                ).total_seconds(),
            )

            attendance_pct    = round(overlap_seconds / ideal_seconds * 100, 2)
            attendance_points = get_attendance_points(attendance_pct)
            feedback_points   = FEEDBACK_POINTS if email in feedback_emails else 0
            total_points      = attendance_points + feedback_points

            history_rows.append([
                session_id, topic, display_name,
                attendance_pct, attendance_points, feedback_points,
                0, 0, 0,
                total_points,
            ])

        # Presenter rows — 100 pts flat, Attendance_% = 100 (by definition)
        for presenter_name in [
            x.strip() for x in str(session["Name"]).split(",") if x.strip()
        ]:
            history_rows.append([
                session_id, topic, presenter_name,
                100, 0, 0,
                PRESENTATION_POINTS,
                0, 0,
                PRESENTATION_POINTS,
            ])

        duration_minutes = round((end_dt - start_dt).total_seconds() / 60, 2)
        session_summary_rows.append([
            session_id, topic, duration_minutes,
            attendees, feedback_count, positive_feedback_count,
        ])

    # --- Volunteer and consecutive bonus ---
    _append_volunteer_rows(
        history_rows, presenter_details, email_to_name, logger
    )
    _append_consecutive_bonus_rows(history_rows, presenter_details)

    # --- Build DataFrames ---
    history = pd.DataFrame(
        history_rows,
        columns=[
            "Session_ID", "Topic", "Employee",
            "Attendance_%", "Attendance_Points", "Feedback_Points",
            "Presentation_Points", "Volunteer_Points", "Consecutive_Bonus",
            "Total_Points",
        ],
    )

    leaderboard = (
        history
        .groupby("Employee", as_index=False)
        [[
            "Attendance_Points", "Feedback_Points", "Presentation_Points",
            "Volunteer_Points", "Consecutive_Bonus", "Total_Points",
        ]]
        .sum()
        .sort_values("Total_Points", ascending=False)
        .reset_index(drop=True)
    )
    leaderboard.insert(0, "Rank", leaderboard.index + 1)

    session_summary = pd.DataFrame(
        session_summary_rows,
        columns=[
            "Session_ID", "Topic", "Duration_Minutes",
            "Attendees", "Feedback_Count", "Positive_Feedback_Count",
        ],
    )

    feedback_insights = pd.DataFrame(
        [[k, v] for k, v in feedback_category_counter.items()],
        columns=["Category", "Count"],
    )

    # --- Write output files ---
    with open(LEADERBOARD_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "title": "Season Standings",
                "data": [
                    {"name": str(r["Employee"]), "score": int(r["Total_Points"])}
                    for _, r in leaderboard.iterrows()
                ],
            },
            f,
            indent=2,
        )

    leaderboard.to_excel(LEADERBOARD_EXCEL_PATH, index=False)

    with pd.ExcelWriter(SESSION_SUMMARY_PATH, engine="openpyxl") as writer:
        session_summary.to_excel(
            writer, sheet_name=SESSION_SUMMARY_SHEET, index=False
        )
        feedback_insights.to_excel(
            writer, sheet_name=FEEDBACK_INSIGHTS_SHEET, index=False
        )

    # --- Update all-time participant history ---
    new_records = pd.DataFrame(participant_history_rows).drop_duplicates()

    if PARTICIPANT_HISTORY_PATH.exists():
        existing = pd.read_excel(PARTICIPANT_HISTORY_PATH)
        existing["Session_Date"] = pd.to_datetime(
            existing["Session_Date"]
        ).dt.date
        combined = (
            pd.concat([existing, new_records])
            .drop_duplicates()
            .sort_values("Session_Date")
            .reset_index(drop=True)
        )
    else:
        combined = (
            new_records
            .sort_values("Session_Date")
            .reset_index(drop=True)
        )

    combined.to_excel(PARTICIPANT_HISTORY_PATH, index=False)

    logger.info(
        f"Output files saved — "
        f"{LEADERBOARD_EXCEL_PATH.name}, "
        f"{SESSION_SUMMARY_PATH.name}, "
        f"{LEADERBOARD_JSON_PATH.name}, "
        f"{PARTICIPANT_HISTORY_PATH.name}"
    )

    return history
