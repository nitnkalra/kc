from pathlib import Path

# ==================================================
# DATA SOURCE
# ==================================================

# Root folder containing session subfolders, employee_master.xlsx,
# and presenter_details.xlsx. Change per season.
# Example: r"D:\kc\...\season_4", r"D:\kc\...\season_5"
SEASON_FOLDER = Path(
    r"D:\kc\INXITE-OUT PRIVATE LIMITED\KnowledgeClub - Documents\kc\season_5"
)

# ==================================================
# INPUT FILES  (relative names — resolved at runtime)
# ==================================================

# Files inside SEASON_FOLDER
EMPLOYEE_MASTER_FILE    = "employee_master.xlsx"
PRESENTER_DETAILS_FILE  = "presenter_details.xlsx"
ATTENDANCE_FILE         = "attendance.xlsx"
FEEDBACK_FILE           = "feedback.xlsx"

# Files inside SEASON_FOLDER.parent  (kc/ root — all-time data)
ALL_SESSIONS_FILE       = "all_session_details.xlsx"
PARTICIPANT_HISTORY_FILE = "all_participant_history.xlsx"

# ==================================================
# BOT / SYSTEM ACCOUNT
# ==================================================

# Teams meeting bot account — excluded from all attendance counts
BOT_EMAIL = "knowledge_club@inxiteout.ai"

# ==================================================
# OUTPUT FILES & FOLDERS
# ==================================================

# Sub-folder created inside SEASON_FOLDER for all generated outputs
OUTPUT_FOLDER = "outputs"

# Excel outputs
LEADERBOARD_EXCEL_FILE  = "Leaderboard.xlsx"
SESSION_HISTORY_FILE    = "Session_History.xlsx"
SESSION_SUMMARY_FILE    = "Session_Summary.xlsx"

# Excel sheet names inside SESSION_SUMMARY_FILE
SESSION_SUMMARY_SHEET   = "Session_Summary"
FEEDBACK_INSIGHTS_SHEET = "Feedback_Insights"

# JSON output
LEADERBOARD_JSON_FILE   = "leaderboard.json"

# PNG outputs
LEADERBOARD_PNG_FILE            = "leaderboard.png"
FEEDBACK_TREND_PNG              = "feedback_trend.png"
SESSION_COUNT_PNG               = "session_count.png"
EMPLOYEES_VS_PARTICIPANTS_PNG   = "employees_vs_participants.png"

# ==================================================
# SCORING RULES
# ==================================================

# Attendance % -> points mapping (first threshold met, descending order)
# scoring.py iterates keys sorted descending — insertion order doesn't matter.
# Example: 92% -> 25 pts (>= 90)
# Example: 76% -> 20 pts (>= 75, not >= 90)
# Example: 40% ->  5 pts (>= 25, not >= 50)
# Example: 10% ->  0 pts (>= 0,  not >= 25)
ATTENDANCE_BANDS = {
    90: 25,   # >= 90% attendance -> 25 points
    75: 20,   # >= 75% attendance -> 20 points
    50: 10,   # >= 50% attendance -> 10 points
    25: 5,    # >= 25% attendance ->  5 points
    0: 0,     # >= 0%  attendance ->  0 points  (catches < 25%)
}

# Flat points for submitting session feedback form
# Example: submitted feedback -> 25 pts, did not submit -> 0 pts
FEEDBACK_POINTS = 25

# Flat points for presenting a session
# Example: presented session_03 -> 100 pts
PRESENTATION_POINTS = 100

# Grace period (minutes) after session start before attendance is counted
# Example: session starts 4:00 PM, join buffer = 3 -> ideal start = 4:03 PM
JOIN_BUFFER_MINUTES = 3

# Grace period (minutes) before session end — leaving after this is OK
# Example: session ends 5:00 PM, leave buffer = 5 -> ideal end = 4:55 PM
LEAVE_BUFFER_MINUTES = 5

# ==================================================
# CONSECUTIVE SESSION BONUS
# ==================================================

# Points awarded for each consecutive session pair attended
# (session N and session N+1, ordered by date, with no gap).
# Example: attended session_01 AND session_02 → +5
#          attended session_02 AND session_03 → +5 (another +5)
CONSECUTIVE_SESSION_BONUS = 5

# ==================================================
# VOLUNTEER POINTS
# ==================================================

# Points per role per session for knowledge-club volunteers.
# These map directly to column names in
# kc_volunteer_team.xlsx → session_activity_tracker sheet.

VOLUNTEER_HOSTING_POINTS = 10       # Session Hosting
VOLUNTEER_BACKEND_POINTS = 5        # Backend Management (invites, forms, etc.)
VOLUNTEER_SPEAKER_COORD_POINTS = 5  # Speaker Coordination (date, demo, PPT)
VOLUNTEER_LASTMINUTE_POINTS = 5     # Last-minute issue handled successfully

# Maps column names in session_activity_tracker to point values.
# Add / rename keys here to support new roles without touching processor.py.
VOLUNTEER_ROLE_POINTS = {
    "Session_hosting":      VOLUNTEER_HOSTING_POINTS,
    "Backend_management":   VOLUNTEER_BACKEND_POINTS,
    "Speaker_coordination": VOLUNTEER_SPEAKER_COORD_POINTS,
    "Last-minute issue":    VOLUNTEER_LASTMINUTE_POINTS,
}

# Volunteer file config
VOLUNTEER_FILE          = "kc_volunteer_team.xlsx"
VOLUNTEER_TRACKER_SHEET = "session_activity_tracker"
VOLUNTEER_DETAILS_SHEET = "volunteer_details"

# ==================================================
# FEEDBACK CONFIG
# ==================================================

# Column name in feedback Excel that contains the session rating
# Example: "How would you rate today's session overall?"
FEEDBACK_RATING_COLUMN = "How would you rate today's session overall?"

# Ratings that count as "positive" feedback (matched case-insensitive)
# All other ratings are counted as neutral/negative
# Example values in data: "Excellent", "Very good", "Good", "Average", "Poor"
# Adjust this list to control what counts as positive:
#   Only top: ["excellent"]
#   Top two:  ["excellent", "very good"]
#   Top three: ["excellent", "very good", "good"]
POSITIVE_RATINGS = ["excellent", "very good"]

# Column name for qualitative feedback ("What did you like most?")
# Used for feedback category insights
FEEDBACK_CATEGORY_COLUMN = "What did you like most about the session?"

# ==================================================
# THEME COLORS (shared across leaderboard & graphs)
# ==================================================
# Change these to update the entire visual theme.
# All hex color codes. Example alternatives:
#   Purple theme: BG="#1a0a2e", ACCENT="#a855f7"
#   Green theme:  BG="#0a1f1a", ACCENT="#34d399"

BG_COLOR       = "#071326"    # Dark navy — canvas/chart background
ACCENT_COLOR   = "#E6C15A"    # Gold — titles, scores, borders, primary line
SECONDARY_COLOR = "#4FC3F7"   # Cyan — secondary line in charts
TEXT_COLOR     = "#F5F5F5"    # Off-white — names, axis labels, tick marks
GRID_COLOR     = "#1A2A42"    # Subtle blue — chart grid lines, spines
LINE_COLOR     = "#2A3A52"    # Lighter blue — row separators
ROW_ALT_COLOR  = "#0D1E36"    # Slightly lighter BG — alternating rows

# ==================================================
# LEADERBOARD PNG SIZE & LAYOUT (pixels)
# ==================================================
# Controls the leaderboard.png dimensions.
# WIDTH is fixed; HEIGHT is calculated dynamically based on row count.
# Example: 10 rows -> HEIGHT = 100 + 70 + (10*70) + 60 + 40 = 970px

LEADERBOARD_WIDTH          = 1200   # Total image width (px)
LEADERBOARD_PADDING_TOP    = 100    # Space above the table (for title)
LEADERBOARD_PADDING_BOTTOM = 60     # Space below the table
LEADERBOARD_HEADER_HEIGHT  = 70     # Table header row height (px)
LEADERBOARD_ROW_HEIGHT     = 70     # Each data row height (px)
LEADERBOARD_MARGIN_X       = 80     # Left/right margin (px)
LEADERBOARD_MAX_ROWS       = 10     # Number of top entries to show

# ==================================================
# CHART PNG SIZE (pixels / inches)
# ==================================================
# Controls feedback_trend.png and future chart dimensions.
# figsize is in inches; dpi converts to pixels.
# Example: (12, 6) at 150 dpi = 1800 x 900 px

CHART_FIGSIZE = (12, 6)   # (width_inches, height_inches)
CHART_DPI     = 150       # Dots per inch — higher = sharper PNG
