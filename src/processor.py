import json
import pandas as pd
from pathlib import Path
from datetime import timedelta

from config import (
    FEEDBACK_POINTS,
    PRESENTATION_POINTS,
    JOIN_BUFFER_MINUTES,
    LEAVE_BUFFER_MINUTES
)

from src.scoring import get_attendance_points


def process_season(base_folder, logger):

    employee_master = pd.read_excel(
        base_folder / "employee_master.xlsx"
    )
    employee_master.columns = (
        employee_master.columns.str.strip()
    )

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

    try:
        logger.info(
            f"Built email->name map with {len(email_to_name)} entries"
        )
    except Exception:
        pass

    presenter_details = pd.read_excel(
        base_folder / "presenter_details.xlsx"
    )
    presenter_details.columns = (
        presenter_details.columns.str.strip()
    )

    history_rows = []

    feedback_category_counter = {}

    session_summary_rows = []

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
            session_folder /
            "attendance.xlsx"
        )

        feedback_file = (
            session_folder /
            "feedback.xlsx"
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
        attendance.columns = (
            attendance.columns.str.strip()
        )

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
            feedback.columns = (
                feedback.columns.str.strip()
            )

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

            rating_col = (
                "How would you rate "
                "today’s session overall?"
            )

            if rating_col in feedback.columns:

                positive_feedback_count = (
                    feedback[
                        rating_col
                    ]
                    .astype(str)
                    .str.lower()
                    .isin(
                        [
                            "excellent",
                            "very good",
                            "good"
                        ]
                    )
                    .sum()
                )

            like_col = (
                "What did you like "
                "most about the session?"
            )

            if like_col in feedback.columns:

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

            if (
                email ==
                "knowledge_club@inxiteout.ai"
            ):
                continue

            attendees += 1

            try:

                join_time = pd.to_datetime(
                    row["First Join"]
                )

                leave_time = pd.to_datetime(
                    row["Last Leave"]
                )

            except:
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
                    0,
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
        base_folder / "outputs"
    )

    output_folder.mkdir(
        exist_ok=True
    )

    top10 = leaderboard.head(10)
    leaderboard_json = {
        "title": "Leaderboard - Top 10",
        "data": [
            {
                "name": str(row["Employee"]),
                "score": int(row["Total_Points"])
            }
            for _, row in top10.iterrows()
        ]
    }

    with open(
        output_folder / "leaderboard.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(leaderboard_json, f, indent=2)

    leaderboard.to_excel(
        output_folder /
        "Leaderboard.xlsx",
        index=False
    )

    history.to_excel(
        output_folder /
        "Session_History.xlsx",
        index=False
    )

    with pd.ExcelWriter(
        output_folder /
        "Session_Summary.xlsx",
        engine="openpyxl"
    ) as writer:

        session_summary.to_excel(
            writer,
            sheet_name="Session_Summary",
            index=False
        )

        feedback_insights.to_excel(
            writer,
            sheet_name="Feedback_Insights",
            index=False
        )

