# Databricks notebook source
# MAGIC %md
# MAGIC # KC Leaderboard — Output Analysis & Cross-Check
# MAGIC
# MAGIC Load all files from `outputs/` and validate consistency across **Leaderboard**, **Session History**, and **Session Summary**.

# COMMAND ----------

from pathlib import Path

import pandas as pd

from config import (
    SEASON_FOLDER,
    ATTENDANCE_BANDS,
    FEEDBACK_POINTS,
    PRESENTATION_POINTS,
)

OUTPUT_FOLDER = SEASON_FOLDER / "outputs"

leaderboard = pd.read_excel(OUTPUT_FOLDER / "Leaderboard.xlsx")
history = pd.read_excel(OUTPUT_FOLDER / "Session_History.xlsx")
session_summary = pd.read_excel(
    OUTPUT_FOLDER / "Session_Summary.xlsx",
    sheet_name="Session_Summary",
)
feedback_insights = pd.read_excel(
    OUTPUT_FOLDER / "Session_Summary.xlsx",
    sheet_name="Feedback_Insights",
)

for name, df in [
    ("Leaderboard", leaderboard),
    ("Session History", history),
    ("Session Summary", session_summary),
    ("Feedback Insights", feedback_insights),
]:
    print(f"{name}: {df.shape[0]} rows x {df.shape[1]} cols")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Preview loaded outputs

# COMMAND ----------

display(leaderboard.head(10))
display(history.head(10))
display(session_summary)
display(feedback_insights)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Cross-check validations

# COMMAND ----------

def get_attendance_points(attendance_pct):
    for threshold, points in ATTENDANCE_BANDS.items():
        if attendance_pct >= threshold:
            return points
    return 0


def run_check(name, passed, details=None):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    if details is not None and len(details):
        display(details)
    return passed


results = []

# COMMAND ----------

# Check 1: Total_Points = Attendance + Feedback + Presentation (per history row)
expected_total = (
    history["Attendance_Points"]
    + history["Feedback_Points"]
    + history["Presentation_Points"]
)
total_mismatch = history[expected_total != history["Total_Points"]].copy()
total_mismatch["Expected_Total"] = expected_total[expected_total != history["Total_Points"]]

results.append(
    run_check(
        "History row totals add up correctly",
        total_mismatch.empty,
        total_mismatch if not total_mismatch.empty else None,
    )
)

# COMMAND ----------

# Check 2: Leaderboard aggregates match Session History
recomputed = (
    history.groupby("Employee", as_index=False)[
        [
            "Attendance_Points",
            "Feedback_Points",
            "Presentation_Points",
            "Total_Points",
        ]
    ]
    .sum()
    .sort_values("Total_Points", ascending=False)
    .reset_index(drop=True)
)

leaderboard_sorted = (
    leaderboard.sort_values("Total_Points", ascending=False)
    .drop(columns=["Rank"])
    .reset_index(drop=True)
)

compare_cols = [
    "Employee",
    "Attendance_Points",
    "Feedback_Points",
    "Presentation_Points",
    "Total_Points",
]
merged = recomputed.merge(
    leaderboard_sorted,
    on="Employee",
    how="outer",
    suffixes=("_history", "_leaderboard"),
    indicator=True,
)

point_cols = [
    "Attendance_Points",
    "Feedback_Points",
    "Presentation_Points",
    "Total_Points",
]
mismatch_mask = merged["_merge"] != "both"
for col in point_cols:
    mismatch_mask |= merged[f"{col}_history"].fillna(-1) != merged[
        f"{col}_leaderboard"
    ].fillna(-1)

leaderboard_mismatch = merged[mismatch_mask]

results.append(
    run_check(
        "Leaderboard matches history aggregation",
        leaderboard_mismatch.empty,
        leaderboard_mismatch if not leaderboard_mismatch.empty else None,
    )
)

# COMMAND ----------

# Check 3: Rank order follows Total_Points (descending)
expected_ranks = (
    leaderboard.sort_values("Total_Points", ascending=False)
    .reset_index(drop=True)
)
expected_ranks["Expected_Rank"] = expected_ranks.index + 1
rank_check = leaderboard.merge(
    expected_ranks[["Employee", "Expected_Rank"]],
    on="Employee",
    how="left",
)
rank_mismatch = rank_check[rank_check["Rank"] != rank_check["Expected_Rank"]]

results.append(
    run_check(
        "Leaderboard ranks are sorted by Total_Points",
        rank_mismatch.empty,
        rank_mismatch if not rank_mismatch.empty else None,
    )
)

# COMMAND ----------

# Check 4: Attendance points follow configured bands (attendees only)
attendee_history = history[history["Presentation_Points"] == 0].copy()
attendee_history["Expected_Attendance_Points"] = attendee_history[
    "Attendance_%"
].apply(get_attendance_points)
attendance_mismatch = attendee_history[
    attendee_history["Attendance_Points"]
    != attendee_history["Expected_Attendance_Points"]
][
    [
        "Session_ID",
        "Employee",
        "Attendance_%",
        "Attendance_Points",
        "Expected_Attendance_Points",
    ]
]

results.append(
    run_check(
        "Attendance points match ATTENDANCE_BANDS (attendees only)",
        attendance_mismatch.empty,
        attendance_mismatch if not attendance_mismatch.empty else None,
    )
)

# COMMAND ----------

# Check 5: Feedback points are 0 or FEEDBACK_POINTS
valid_feedback = history["Feedback_Points"].isin([0, FEEDBACK_POINTS])
feedback_invalid = history[~valid_feedback][
    ["Session_ID", "Employee", "Feedback_Points"]
]

results.append(
    run_check(
        f"Feedback points are 0 or {FEEDBACK_POINTS}",
        feedback_invalid.empty,
        feedback_invalid if not feedback_invalid.empty else None,
    )
)

# COMMAND ----------

# Check 6: Presentation points are 0 or PRESENTATION_POINTS
valid_presentation = history["Presentation_Points"].isin(
    [0, PRESENTATION_POINTS]
)
presentation_invalid = history[~valid_presentation][
    ["Session_ID", "Employee", "Presentation_Points"]
]

results.append(
    run_check(
        f"Presentation points are 0 or {PRESENTATION_POINTS}",
        presentation_invalid.empty,
        presentation_invalid if not presentation_invalid.empty else None,
    )
)

# COMMAND ----------

# Check 7: Session summary attendee count vs history (exclude presenter rows)
presenter_rows = history[history["Presentation_Points"] > 0]
attendee_rows = history[history["Presentation_Points"] == 0]

history_counts = (
    attendee_rows.groupby("Session_ID", as_index=False)
    .size()
    .rename(columns={"size": "History_Attendees"})
)

summary_compare = session_summary.merge(
    history_counts,
    on="Session_ID",
    how="left",
)
summary_compare["Attendee_Match"] = (
    summary_compare["Attendees"] == summary_compare["History_Attendees"]
)
attendee_mismatch = summary_compare[~summary_compare["Attendee_Match"]]

results.append(
    run_check(
        "Session Summary attendee count matches history",
        attendee_mismatch.empty,
        attendee_mismatch if not attendee_mismatch.empty else None,
    )
)

# COMMAND ----------

# Check 8: Feedback count in summary vs history rows with feedback points
# Note: a mismatch can occur when someone submits feedback but is not in attendance.
history_feedback_counts = (
    history.groupby("Session_ID", as_index=False)["Feedback_Points"]
    .apply(lambda s: (s == FEEDBACK_POINTS).sum())
    .rename(columns={"Feedback_Points": "History_Feedback_Count"})
)

feedback_compare = session_summary.merge(
    history_feedback_counts,
    on="Session_ID",
    how="left",
)
feedback_compare["Feedback_Match"] = (
    feedback_compare["Feedback_Count"]
    == feedback_compare["History_Feedback_Count"]
)
feedback_count_mismatch = feedback_compare[~feedback_compare["Feedback_Match"]]

results.append(
    run_check(
        "Session Summary feedback count matches history feedback points",
        feedback_count_mismatch.empty,
        feedback_count_mismatch if not feedback_count_mismatch.empty else None,
    )
)

# COMMAND ----------

# Check 9: Each session has exactly one presenter row
presenter_counts = (
    presenter_rows.groupby("Session_ID", as_index=False)
    .size()
    .rename(columns={"size": "Presenter_Rows"})
)
presenter_count_issues = presenter_counts[
    presenter_counts["Presenter_Rows"] != 1
]

results.append(
    run_check(
        "Each session has exactly one presenter row in history",
        presenter_count_issues.empty,
        presenter_count_issues if not presenter_count_issues.empty else None,
    )
)

# COMMAND ----------

# Check 10: Feedback insights category counts sum to total feedback responses
insights_total = feedback_insights["Count"].sum()
feedback_total = session_summary["Feedback_Count"].sum()

results.append(
    run_check(
        "Feedback insights counts sum to total feedback submissions",
        insights_total == feedback_total,
        pd.DataFrame(
            {
                "Metric": [
                    "Insights category sum",
                    "Session summary feedback total",
                ],
                "Value": [insights_total, feedback_total],
            }
        )
        if insights_total != feedback_total
        else None,
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Data quality insights
# MAGIC
# MAGIC Optional drill-down when feedback counts differ — feedback submitters missing from attendance.

# COMMAND ----------

from config import SEASON_FOLDER

for session_id in session_summary["Session_ID"]:
    session_folder = SEASON_FOLDER / session_id
    attendance_file = session_folder / "attendance.xlsx"
    feedback_file = session_folder / "feedback.xlsx"

    if not attendance_file.exists() or not feedback_file.exists():
        continue

    attendance = pd.read_excel(attendance_file)
    feedback = pd.read_excel(feedback_file)
    attendance.columns = attendance.columns.str.strip()
    feedback.columns = feedback.columns.str.strip()

    attendance_emails = set(
        attendance["Email"].astype(str).str.lower().str.strip()
    )
    feedback_emails = set(
        feedback["Email"].astype(str).str.lower().str.strip()
    )

    missing_from_attendance = sorted(feedback_emails - attendance_emails)
    if missing_from_attendance:
        print(f"{session_id}: feedback without attendance match")
        display(pd.DataFrame({"Email": missing_from_attendance}))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Summary

# COMMAND ----------

passed = sum(results)
total = len(results)

print(f"\nCross-check result: {passed}/{total} checks passed")

if passed == total:
    print("All outputs are internally consistent.")
else:
    print("Review failed checks above for mismatches.")