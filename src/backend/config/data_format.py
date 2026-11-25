"""
Input data format - column names, sheet names and special values that the
Excel input files must use. Change here if a source file format changes.
"""

# ---------------------------------------------------------------------------
# all_session_details.xlsx
# ---------------------------------------------------------------------------

# Column that identifies session type.
# If column is missing or value is blank -> defaults to "regular".
SESSION_TYPE_COLUMN = "Session_Type"

# ---------------------------------------------------------------------------
# kc_volunteer_team.xlsx
# ---------------------------------------------------------------------------

VOLUNTEER_TRACKER_SHEET = "session_activity_tracker"
VOLUNTEER_DETAILS_SHEET = "volunteer_details"

# ---------------------------------------------------------------------------
# feedback.xlsx
# ---------------------------------------------------------------------------

FEEDBACK_RATING_COLUMN   = "How would you rate today's session overall?"
POSITIVE_RATINGS         = ["excellent", "very good"]
FEEDBACK_CATEGORY_COLUMN = "What did you like most about the session?"

# Anonymous feedback detection - emails matching any of these markers are
# treated as unidentifiable. Points cannot be awarded but feedback counts
# and ratings are still used for graphs (feedback_trend, session_summary).
ANONYMOUS_EMAIL_MARKERS = ["anonymous", "anonymous@", ""]

# ---------------------------------------------------------------------------
# attendance.xlsx - KC bot / system account
# Session start/end are derived from this account's join/leave times.
# ---------------------------------------------------------------------------

BOT_EMAIL = "knowledge_club@inxiteout.ai"
