"""
All file and folder paths - derived from settings.py, do not edit by hand.

Two kinds of paths:
  * Project paths : inside this git repo (backend, frontend, logs)
  * Data paths    : inside KC_ROOT (private Excel inputs + season outputs)
"""

from pathlib import Path

from .settings import KC_ROOT, SEASON

# ===========================================================================
# PROJECT PATHS  (kc/src/backend/config/paths.py -> kc/)
# ===========================================================================

BACKEND_DIR   = Path(__file__).resolve().parents[1]      # kc/src/backend
REPO_DIR      = BACKEND_DIR.parents[1]                    # kc
FRONTEND_DIR  = REPO_DIR / "src" / "frontend"            # kc/src/frontend
SITE_DATA_DIR = FRONTEND_DIR / "src" / "data"           # JSON read by the site
LOG_DIR       = BACKEND_DIR / "logs"                       # git-ignored

# ===========================================================================
# DATA PATHS - inputs
# ===========================================================================

SEASON_FOLDER = KC_ROOT / SEASON

# Season-level inputs
EMPLOYEE_MASTER_PATH = SEASON_FOLDER / "employee_master.xlsx"
VOLUNTEER_PATH       = SEASON_FOLDER / "kc_volunteer_team.xlsx"

# Session sub-folder file names (joined with session_id at runtime)
# Usage: SEASON_FOLDER / session_id / ATTENDANCE_FILE
ATTENDANCE_FILE = "attendance.xlsx"
FEEDBACK_FILE   = "feedback.xlsx"

# KC_ROOT level (all-time / cross-season data)
ALL_SESSIONS_PATH        = KC_ROOT / "all_session_details.xlsx"
PARTICIPANT_HISTORY_PATH = KC_ROOT / "all_participant_history.xlsx"

# ===========================================================================
# DATA PATHS - outputs  (folder created automatically if missing)
# ===========================================================================

OUTPUT_FOLDER = SEASON_FOLDER / "outputs"

# Excel
LEADERBOARD_EXCEL_PATH = OUTPUT_FOLDER / "Leaderboard.xlsx"
SESSION_SUMMARY_PATH   = OUTPUT_FOLDER / "Session_Summary.xlsx"
SCORE_TIMELINE_PATH    = OUTPUT_FOLDER / "Score_Timeline.xlsx"

# Sheet names inside Session_Summary.xlsx
SESSION_SUMMARY_SHEET   = "Session_Summary"
FEEDBACK_INSIGHTS_SHEET = "Feedback_Insights"

# JSON
LEADERBOARD_JSON_PATH = OUTPUT_FOLDER / "leaderboard.json"

# PNG
LEADERBOARD_PNG_PATH                       = OUTPUT_FOLDER / "leaderboard.png"
FEEDBACK_TREND_PNG_PATH                    = OUTPUT_FOLDER / "feedback_trend.png"
SESSION_COUNT_PNG_PATH                     = OUTPUT_FOLDER / "session_count.png"
EMPLOYEES_VS_PARTICIPANTS_PNG_PATH         = OUTPUT_FOLDER / "employees_vs_participants.png"
EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH = OUTPUT_FOLDER / "employees_vs_participants_monthly.png"
PARTICIPATION_RATE_PNG_PATH                = OUTPUT_FOLDER / "participation_rate.png"
SEASON_PARTICIPATION_PNG_PATH              = OUTPUT_FOLDER / "season_participation.png"
SEASON_PARTICIPATION_HBAR_PNG_PATH         = OUTPUT_FOLDER / "season_participation_hbar.png"
