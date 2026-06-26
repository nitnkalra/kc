import json
import pandas as pd
from pathlib import Path
from datetime import timedelta

from config import (
    FEEDBACK_POINTS,
    PRESENTATION_POINTS,
    JOIN_BUFFER_MINUTES,
    LEAVE_BUFFER_MINUTES,
    FEEDBACK_RATING_COLUMN,
    POSITIVE_RATINGS,
    FEEDBACK_CATEGORY_COLUMN,
    CONSECUTIVE_SESSION_BONUS,
    VOLUNTEER_ROLE_POINTS,
    VOLUNTEER_FILE,
    VOLUNTEER_TRACKER_SHEET,
    VOLUNTEER_DETAILS_SHEET,
    # File names
    EMPLOYEE_MASTER_FILE,
    PRESENTER_DETAILS_FILE,
    ATTENDANCE_FILE,
    FEEDBACK_FILE,
    PARTICIPANT_HISTORY_FILE,
    BOT_EMAIL,
    # Output
    OUTPUT_FOLDER,
    LEADERBOARD_JSON_FILE,
    LEADERBOARD_EXCEL_FILE,
    SESSION_HISTORY_FILE,
    SESSION_SUMMARY_FILE,
    SESSION_SUMMARY_SHEET,
    FEEDBACK_INSIGHTS_SHEET,
)

from src.scoring import get_attendance_points


# ---------------------------------------------------------------------------
# Volunteer points helper
# ---------------------------------------------------------------------------

def _append_volunteer_rows(
    history_rows: list,
    presenter_details: pd.DataFrame,
    base_folder: Path,
    email_to_name: dict,
    logger,
) -> None:
    """
    Read kc_volunteer_team.xlsx and append one history row
    per volunteer activity per session.

    - Volunteer names are matched to emails via the
      volunteer_details sheet.
    - Each role column may contain a single name or a
      comma-separated list of names.
    - Unknown names are logged as warnings and skipped.
    """
    volunteer_file = base_folder / VOLUNTEER_FILE

    if not volunteer_file.exists():
        logger.warning(
            f"Volunteer file not found: "
            f"{volunteer_file.name} "
            "— skipping volunteer points."
        )
        return

    try:
        tracker = pd.read_excel(
            volunteer_file,
            sheet_name=VOLUNTEER_TRACKER_SHEET,
        )
        tracker = tracker.rename(columns=str.strip)

        details = pd.read_excel(
            volunteer_file,
            sheet_name=VOLUNTEER_DETAILS_SHEET,
        )
        details = details.rename(columns=str.strip)

    except Exception as e:
        logger.error(
            f"Error loading volunteer file: {e}"
        )
        return

    # Build name (lowercase) → email mapping
    name_to_email = {
        str(r.get("Volunteer_name", ""))
        .strip()
        .lower(): str(r.get("Volunteer_email", ""))
        .strip()
        .lower()
        for _, r in details.iterrows()
        if pd.notna(r.get("Volunteer_name"))
        and pd.notna(r.get("Volunteer_email"))
    }

    # Session_ID → Topic from presenter_details
    session_topics = {
        str(r["Session_ID"]).strip(): str(
            r["Topic"]
        ).strip()
        for _, r in presenter_details.iterrows()
    }

    for _, row in tracker.iterrows():

        session_id = str(
            row.get("Session_ID", "")
        ).strip()

        topic = session_topics.get(
            session_id,
            str(row.get("Session_name", "")).strip(),
        )

        for col, points in VOLUNTEER_ROLE_POINTS.items():

            if col not in tracker.columns:
                continue

            cell = str(row.get(col, "")).strip()

            if not cell or cell.lower() in (
                "nan", "none", ""
            ):
                continue

            # Support comma-separated names
            for name in [
                n.strip() for n in cell.split(",")
            ]:
                if not name:
                    continue

                email = name_to_email.get(
                    name.lower()
                )

                if email is None:
                    logger.warning(
                        f"Volunteer '{name}' not "
                        f"found in "
                        f"{VOLUNTEER_DETAILS_SHEET}"
                        " — skipped."
                    )
                    continue

                display_name = email_to_name.get(
                    email, name
                )

                history_rows.append(
                    [
                        session_id,
                        topic,
                        display_name,
                        0,       # Attendance_%
                        0,       # Attendance_Points
                        0,       # Feedback_Points
                        0,       # Presentation_Points
                        points,  # Volunteer_Points
                        0,       # Consecutive_Bonus
                        points,  # Total_Points
                    ]
                )


# ---------------------------------------------------------------------------
# Consecutive session bonus helper
# ---------------------------------------------------------------------------

def _append_consecutive_bonus_rows(
    history_rows: list,
    presenter_details: pd.DataFrame,
) -> None:
    """
    Award CONSECUTIVE_SESSION_BONUS points for every pair
    of consecutive sessions an employee attends.

    Consecutive = session N and session N+1 ordered by Date.
    Pure volunteer rows (Attendance_% == 0,
    Presentation_Points == 0, Volunteer_Points > 0) are
    excluded from the attendance check — volunteering alone
    does not count as attending.
    """
    sessions = presenter_details.copy()
    sessions["Date"] = pd.to_datetime(
        sessions["Date"], errors="coerce"
    )
    sessions = (
        sessions
        .dropna(subset=["Date"])
        .sort_values("Date")
    )

    session_order = (
        sessions["Session_ID"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    if len(session_order) < 2:
        return

    valid_session_ids = set(session_order)

    # Build employee → set of attended session IDs
    attended: dict = {}

    for row in history_rows:

        sid = row[0]

        if sid not in valid_session_ids:
            continue

        # Exclude pure volunteer rows
        is_volunteer_only = (
            row[3] == 0      # Attendance_%
            and row[6] == 0  # Presentation_Points
            and row[7] > 0   # Volunteer_Points
        )

        if is_volunteer_only:
            continue

        emp = row[2]

        if emp not in attended:
            attended[emp] = set()

        attended[emp].add(sid)

    # Append one bonus row per consecutive pair attended
    for employee, sessions_attended in attended.items():

        for i in range(len(session_order) - 1):

            s1 = session_order[i]
            s2 = session_order[i + 1]

            if (
                s1 in sessions_attended
                and s2 in sessions_attended
            ):
                history_rows.append(
                    [
                        f"{s1} \u2192 {s2}",
                        "Consecutive Attendance Bonus",
                        employee,
                        0,  # Attendance_%
                        0,  # Attendance_Points
                        0,  # Feedback_Points
                        0,  # Presentation_Points
                        0,  # Volunteer_Points
                        CONSECUTIVE_SESSION_BONUS,
                        CONSECUTIVE_SESSION_BONUS,
                    ]
                )


# ---------------------------------------------------------------------------
# Main season processor
# ---------------------------------------------------------------------------

def process_season(base_folder, logger):

    employee_master = pd.read_excel(
        base_folder / EMPLOYEE_MASTER_FILE
    )
    employee_master = employee_master.rename(columns=str.strip)

    employee_master["Email"] = (
        employee_master["Email"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    # Build email -> proper name mapping (robust to column name variations)
    name_col = None
    for col in employee_master.columns:
        if "name" in col.lower():
            name_col = col
            break
    if name_col is None:
        for col in employee_master.columns:
            if col.lower() != "email":
                name_col = col
                break

    email_to_name = {}
    if name_col is not None:
        for _, r in employee_master.iterrows():
            em = str(r.get("Email", "")).lower().strip()
            nm = r.get(name_col)
            if not em:
                continue
            if pd.isna(nm):
                continue
            nm = str(nm).strip()
            if nm:
                email_to_name[em] = nm

    logger.info("Input files loaded successfully")

    presenter_details = pd.read_excel(
        base_folder / PRESENTER_DETAILS_FILE
    )
    presenter_details = presenter_details.rename(columns=str.strip)

    history_rows = []

    feedback_category_counter = {}

    session_summary_rows = []

    # Collects (Session_Date, Email) for all-time participant history
    participant_history_rows = []

    for _, session in presenter_details.iterrows():

        session_id = str(
            session["Session_ID"]
        ).strip()

        topic = str(
            session["Topic"]
        ).strip()

        session_folder = (
            base_folder / session_id
        )

        attendance_file = (
            session_folder / ATTENDANCE_FILE
        )

        feedback_file = (
            session_folder / FEEDBACK_FILE
        )

        if not attendance_file.exists():

            logger.error(
                f"Attendance missing: {session_id}"
            )

            continue

        try:

            start_dt = pd.to_datetime(
                f"{session['Date']} "
                f"{session['Start Time']}"
            )

            end_dt = pd.to_datetime(
                f"{session['Date']} "
                f"{session['End Time']}"
            )

        except Exception as e:

            logger.error(
                f"{session_id} "
                f"datetime error: {e}"
            )

            continue

        ideal_start = (
            start_dt +
            timedelta(
                minutes=JOIN_BUFFER_MINUTES
            )
        )

        ideal_end = (
            end_dt -
            timedelta(
                minutes=LEAVE_BUFFER_MINUTES
            )
        )

        ideal_seconds = max(
            (
                ideal_end -
                ideal_start
            ).total_seconds(),
            1
        )

        attendance = pd.read_excel(
            attendance_file
        )
        attendance = attendance.rename(columns=str.strip)

        attendance["Email"] = (
            attendance["Email"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        feedback_emails = set()

        positive_feedback_count = 0

        feedback_count = 0

        if feedback_file.exists():

            feedback = pd.read_excel(
                feedback_file
            )
            feedback = feedback.rename(columns=str.strip)

            feedback["Email"] = (
                feedback["Email"]
                .astype(str)
                .str.lower()
                .str.strip()
            )

            feedback_emails = set(
                feedback["Email"]
            )

            feedback_count = len(
                feedback
            )

            # Find rating column — config constant first, fuzzy fallback
            if FEEDBACK_RATING_COLUMN in feedback.columns:
                rating_col = FEEDBACK_RATING_COLUMN
            else:
                rating_col = next(
                    (
                        col for col in feedback.columns
                        if "rate" in col.lower()
                        and "session" in col.lower()
                    ),
                    None
                )

            if rating_col is not None:

                positive_feedback_count = (
                    feedback[rating_col]
                    .astype(str)
                    .str.lower()
                    .str.strip()
                    .isin(POSITIVE_RATINGS)
                    .sum()
                )

            # Find category/like column — config constant first, fuzzy fallback
            if FEEDBACK_CATEGORY_COLUMN in feedback.columns:
                like_col = FEEDBACK_CATEGORY_COLUMN
            else:
                like_col = next(
                    (
                        col for col in feedback.columns
                        if "like" in col.lower()
                        and "session" in col.lower()
                    ),
                    None
                )

            if like_col is not None:

                for value in (
                    feedback[like_col]
                    .dropna()
                ):

                    feedback_category_counter[
                        value
                    ] = (
                        feedback_category_counter.get(
                            value,
                            0
                        )
                        + 1
                    )

        attendees = 0

        for _, row in attendance.iterrows():

            email = str(
                row["Email"]
            ).lower().strip()

            # Prefer proper name from employee master when available
            display_name = email_to_name.get(email, email)

            if email == BOT_EMAIL:
                continue

            participant_history_rows.append(
                {
                    "Session_Date": start_dt.date(),
                    "Email": email,
                }
            )

            attendees += 1

            try:

                join_time = pd.to_datetime(
                    row["First Join"]
                )

                leave_time = pd.to_datetime(
                    row["Last Leave"]
                )

            except (ValueError, TypeError):
                continue

            overlap_seconds = max(
                0,
                (
                    min(
                        leave_time,
                        ideal_end
                    )
                    -
                    max(
                        join_time,
                        ideal_start
                    )
                ).total_seconds()
            )

            attendance_pct = round(
                (
                    overlap_seconds /
                    ideal_seconds
                ) * 100,
                2
            )

            attendance_points = (
                get_attendance_points(
                    attendance_pct
                )
            )

            feedback_points = (
                FEEDBACK_POINTS
                if email in feedback_emails
                else 0
            )

            total_points = (
                attendance_points
                + feedback_points
            )

            history_rows.append(
                [
                    session_id,
                    topic,
                    display_name,
                    attendance_pct,
                    attendance_points,
                    feedback_points,
                    0,   # Presentation_Points
                    0,   # Volunteer_Points
                    0,   # Consecutive_Bonus
                    total_points
                ]
            )

        presenters = [
            x.strip()
            for x in str(
                session["Name"]
            ).split(",")
        ]

        for presenter in presenters:

            history_rows.append(
                [
                    session_id,
                    topic,
                    presenter,
                    100,
                    0,
                    0,
                    PRESENTATION_POINTS,
                    0,   # Volunteer_Points
                    0,   # Consecutive_Bonus
                    PRESENTATION_POINTS
                ]
            )

        duration_minutes = round(
            (
                end_dt -
                start_dt
            ).total_seconds() / 60,
            2
        )

        session_summary_rows.append(
            [
                session_id,
                topic,
                duration_minutes,
                attendees,
                feedback_count,
                positive_feedback_count
            ]
        )

    # --- Volunteer points (per session, per role) ---
    _append_volunteer_rows(
        history_rows,
        presenter_details,
        base_folder,
        email_to_name,
        logger,
    )

    # --- Consecutive session bonus ---
    _append_consecutive_bonus_rows(
        history_rows,
        presenter_details,
    )

    history = pd.DataFrame(
        history_rows,
        columns=[
            "Session_ID",
            "Topic",
            "Employee",
            "Attendance_%",
            "Attendance_Points",
            "Feedback_Points",
            "Presentation_Points",
            "Volunteer_Points",
            "Consecutive_Bonus",
            "Total_Points"
        ]
    )

    leaderboard = (
        history
        .groupby(
            "Employee",
            as_index=False
        )
        [
            [
                "Attendance_Points",
                "Feedback_Points",
                "Presentation_Points",
                "Volunteer_Points",
                "Consecutive_Bonus",
                "Total_Points"
            ]
        ]
        .sum()
    )

    leaderboard = (
        leaderboard
        .sort_values(
            "Total_Points",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    leaderboard.insert(
        0,
        "Rank",
        leaderboard.index + 1
    )

    session_summary = pd.DataFrame(
        session_summary_rows,
        columns=[
            "Session_ID",
            "Topic",
            "Duration_Minutes",
            "Attendees",
            "Feedback_Count",
            "Positive_Feedback_Count"
        ]
    )

    feedback_insights = pd.DataFrame(
        [
            [k, v]
            for k, v in
            feedback_category_counter.items()
        ],
        columns=[
            "Category",
            "Count"
        ]
    )

    output_folder = (
        base_folder / OUTPUT_FOLDER
    )

    output_folder.mkdir(
        exist_ok=True
    )

    # All participants — full season standings
    leaderboard_json = {
        "title": "Season Standings",
        "data": [
            {
                "name": str(row["Employee"]),
                "score": int(row["Total_Points"])
            }
            for _, row in leaderboard.iterrows()
        ]
    }

    with open(
        output_folder / LEADERBOARD_JSON_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(leaderboard_json, f, indent=2)

    leaderboard.to_excel(
        output_folder / LEADERBOARD_EXCEL_FILE,
        index=False
    )

    history.to_excel(
        output_folder / SESSION_HISTORY_FILE,
        index=False
    )

    with pd.ExcelWriter(
        output_folder / SESSION_SUMMARY_FILE,
        engine="openpyxl"
    ) as writer:

        session_summary.to_excel(
            writer,
            sheet_name=SESSION_SUMMARY_SHEET,
            index=False
        )

        feedback_insights.to_excel(
            writer,
            sheet_name=FEEDBACK_INSIGHTS_SHEET,
            index=False
        )

    # --- Update all-time participant history ---
    participant_history_file = (
        base_folder.parent / PARTICIPANT_HISTORY_FILE
    )

    new_records = (
        pd.DataFrame(participant_history_rows)
        .drop_duplicates()
    )

    if participant_history_file.exists():
        existing = pd.read_excel(
            participant_history_file
        )
        # Normalize to datetime.date — Excel reads Session_Date
        # back as Timestamp; new_records contains datetime.date
        # from start_dt.date(). Mixed types break sort_values.
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

    combined.to_excel(
        participant_history_file,
        index=False
    )

    logger.info(
        "Output files saved — "
        f"{LEADERBOARD_EXCEL_FILE}, "
        f"{SESSION_HISTORY_FILE}, "
        f"{SESSION_SUMMARY_FILE}, "
        f"{LEADERBOARD_JSON_FILE}, "
        f"{PARTICIPANT_HISTORY_FILE}"
    )
