from pathlib import Path

from themes import THEMES   # themes.py — same directory

# ===========================================================================
# !!  SETUP — ONLY CHANGE THIS SECTION
#
#   Moving to a new machine / sharing with someone else → update KC_ROOT
#   Starting a new season                               → update SEASON
#   Changing the look                                   → update ACTIVE_THEME
# ===========================================================================

# Absolute path to the kc project root folder on this machine
KC_ROOT = Path(
    r"D:\kc\INXITE-OUT PRIVATE LIMITED\KnowledgeClub - Documents\kc"
)

# Active season sub-folder name — change to "season_6", "season_7", etc.
SEASON = "season_6"

# ---------------------------------------------------------------------------
# Active theme — change this one value to reskin everything.
#
#   Available themes:
#       power_bi_light      — white bg, blue accent
#       power_bi_dark       — dark gray bg, blue accent
#       power_bi_executive  — near-black bg, gold accent
#       power_bi_innovate   — white bg, purple accent
#       power_bi_frontier   — white bg, teal accent           ← default
#       mckinsey            — white bg, deep navy + sky blue
#       tableau             — off-white bg, muted blue series
#       salesforce          — light gray bg, Salesforce blue
#       google_looker       — white bg, Google blue
#       minimal_corporate   — near-white bg, dark slate + blue
#       microsoft_office    — white bg, Office green + blue
# ---------------------------------------------------------------------------

ACTIVE_THEME = "power_bi_frontier"

# ===========================================================================
# DERIVED PATHS  (auto-built from KC_ROOT + SEASON — do not edit below)
# ===========================================================================

SEASON_FOLDER = KC_ROOT / SEASON

# ---------------------------------------------------------------------------
# Input paths — inside SEASON_FOLDER
# ---------------------------------------------------------------------------

EMPLOYEE_MASTER_PATH = SEASON_FOLDER / "employee_master.xlsx"
VOLUNTEER_PATH       = SEASON_FOLDER / "kc_volunteer_team.xlsx"

# Session sub-folder file names (joined dynamically with session_id at runtime)
# Usage: SEASON_FOLDER / session_id / ATTENDANCE_FILE
ATTENDANCE_FILE = "attendance.xlsx"
FEEDBACK_FILE   = "feedback.xlsx"

# ---------------------------------------------------------------------------
# Input paths — KC_ROOT level (all-time / cross-season data)
# ---------------------------------------------------------------------------

ALL_SESSIONS_PATH        = KC_ROOT / "all_session_details.xlsx"
PARTICIPANT_HISTORY_PATH = KC_ROOT / "all_participant_history.xlsx"

# ---------------------------------------------------------------------------
# Output folder  (created automatically if missing)
# ---------------------------------------------------------------------------

OUTPUT_FOLDER = SEASON_FOLDER / "outputs"

# ---------------------------------------------------------------------------
# Output file paths  (all inside OUTPUT_FOLDER)
# ---------------------------------------------------------------------------

# Excel
LEADERBOARD_EXCEL_PATH = OUTPUT_FOLDER / "Leaderboard.xlsx"
SESSION_SUMMARY_PATH   = OUTPUT_FOLDER / "Session_Summary.xlsx"
SCORE_TIMELINE_PATH    = OUTPUT_FOLDER / "Score_Timeline.xlsx"

# Sheet names inside Session_Summary.xlsx
SESSION_SUMMARY_SHEET   = "Session_Summary"
FEEDBACK_INSIGHTS_SHEET = "Feedback_Insights"

# JSON
LEADERBOARD_JSON_PATH = OUTPUT_FOLDER / "leaderboard.json"

# PNG — Core charts
LEADERBOARD_PNG_PATH                       = OUTPUT_FOLDER / "leaderboard.png"
FEEDBACK_TREND_PNG_PATH                    = OUTPUT_FOLDER / "feedback_trend.png"
SESSION_COUNT_PNG_PATH                     = OUTPUT_FOLDER / "session_count.png"
EMPLOYEES_VS_PARTICIPANTS_PNG_PATH         = OUTPUT_FOLDER / "employees_vs_participants.png"
EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH = OUTPUT_FOLDER / "employees_vs_participants_monthly.png"
PARTICIPATION_RATE_PNG_PATH                = OUTPUT_FOLDER / "participation_rate.png"
SEASON_PARTICIPATION_PNG_PATH              = OUTPUT_FOLDER / "season_participation.png"
SEASON_PARTICIPATION_HBAR_PNG_PATH         = OUTPUT_FOLDER / "season_participation_hbar.png"

# ===========================================================================
# SCORING RULES
# ===========================================================================

# Attendance % -> points  (scoring.py iterates keys sorted descending)
# Bands are uniform +5 per tier. Below 5% (ghost joins) → 0 pts.
# Example: 92% → 25 pts, 76% → 20 pts, 55% → 15 pts, 30% → 10 pts, 10% → 5 pts, 3% → 0 pts
ATTENDANCE_BANDS = {
    90: 25,
    75: 20,
    50: 15,
    25: 10,
    5:  5,
    0:  0,
}

FEEDBACK_POINTS     = 25    # flat pts for submitting feedback form
PRESENTATION_POINTS = 100   # flat pts for presenting a regular session

JOIN_BUFFER_MINUTES  = 3    # grace period after session start
LEAVE_BUFFER_MINUTES = 5    # grace period before session end

# ===========================================================================
# SESSION TYPES
# ===========================================================================

# Column in all_session_details.xlsx that identifies session type.
# If column is missing or value is blank → defaults to "regular".
SESSION_TYPE_COLUMN = "Session_Type"

# Decode-It sessions — presentation pool shared equally among all presenters.
# Regular: each presenter → PRESENTATION_POINTS (100) flat
# Decode-It: each presenter → round(DECODE_PRESENTATION_POOL / num_presenters)
#   2 presenters → 50 each, 3 → 33 each, 4 → 25 each
DECODE_SESSION_TYPE      = "decode-it"
DECODE_PRESENTATION_POOL = 100

# ===========================================================================
# CONSECUTIVE SESSION BONUS
# ===========================================================================

# +points per consecutive pair (session N attended AND session N+1 attended).
# Resets automatically when SEASON changes — each season processes fresh.
# Minimum attendance threshold: >= 5% (Attendance_Points > 0) required.
# Example: session_01 + session_02 attended → +5
#          session_02 + session_03 attended → +5  (another +5)
CONSECUTIVE_SESSION_BONUS = 5

# ===========================================================================
# VOLUNTEER POINTS
# ===========================================================================

# Column names in kc_volunteer_team.xlsx → session_activity_tracker sheet
VOLUNTEER_HOSTING_POINTS       = 10   # Session_hosting
VOLUNTEER_BACKEND_POINTS       = 5    # Backend_management
VOLUNTEER_SPEAKER_COORD_POINTS = 5    # Speaker_coordination
VOLUNTEER_LASTMINUTE_POINTS    = 5    # Last-minute issue

VOLUNTEER_ROLE_POINTS = {
    "Session_hosting":      VOLUNTEER_HOSTING_POINTS,
    "Backend_management":   VOLUNTEER_BACKEND_POINTS,
    "Speaker_coordination": VOLUNTEER_SPEAKER_COORD_POINTS,
    "Last-minute issue":    VOLUNTEER_LASTMINUTE_POINTS,
}

# Host attendance — hosts are confirmed 100% present but typically do not
# appear in attendance.xlsx. Award max-band attendance points automatically.
# Skipped if the host already has an attendance row for this session.
VOLUNTEER_HOST_ATTENDANCE_POINTS = 25

VOLUNTEER_TRACKER_SHEET = "session_activity_tracker"
VOLUNTEER_DETAILS_SHEET = "volunteer_details"

# ===========================================================================
# FEEDBACK CONFIG
# ===========================================================================

FEEDBACK_RATING_COLUMN   = "How would you rate today's session overall?"
POSITIVE_RATINGS         = ["excellent", "very good"]
FEEDBACK_CATEGORY_COLUMN = "What did you like most about the session?"

# Anonymous feedback detection — emails matching any of these markers are
# treated as unidentifiable. Points cannot be awarded but feedback counts
# and ratings are still used for graphs (feedback_trend, session_summary).
ANONYMOUS_EMAIL_MARKERS = ["anonymous", "anonymous@", ""]

# ===========================================================================
# BOT / SYSTEM ACCOUNT
# ===========================================================================

BOT_EMAIL = "knowledge_club@inxiteout.ai"

# ===========================================================================
# THEME COLORS  (auto-loaded from ACTIVE_THEME — do not edit below)
# ===========================================================================

_t = THEMES[ACTIVE_THEME]

BG_COLOR         = _t["BG_COLOR"]
HEADER_COLOR     = _t["HEADER_COLOR"]
ACCENT_COLOR     = _t["ACCENT_COLOR"]
SECONDARY_COLOR  = _t["SECONDARY_COLOR"]
TEXT_COLOR       = _t["TEXT_COLOR"]
HEADER_TEXT      = _t["HEADER_TEXT"]
GRID_COLOR       = _t["GRID_COLOR"]
LINE_COLOR       = _t["LINE_COLOR"]
ROW_ALT_COLOR    = _t["ROW_ALT_COLOR"]

CHART_COLORS     = _t["CHART_COLORS"]
CHART_BG_COLOR   = _t["CHART_BG_COLOR"]
CHART_GRID_COLOR = _t["CHART_GRID_COLOR"]
CHART_TEXT_COLOR = _t["CHART_TEXT_COLOR"]

LB_RANK1_COLOR   = _t["LB_RANK1_COLOR"]
LB_RANK2_COLOR   = _t["LB_RANK2_COLOR"]
LB_RANK3_COLOR   = _t["LB_RANK3_COLOR"]

del _t   # keep module namespace clean

# ===========================================================================
# LEADERBOARD PNG LAYOUT  (pixels)
#
#   *** ONLY change LEADERBOARD_WIDTH — everything else scales automatically ***
#
#   LEADERBOARD_HEIGHT:
#       None  → auto-calculated from row count (recommended)
#       <int> → fixed pixel height; rows are scaled to fit
# ===========================================================================

LEADERBOARD_WIDTH    = 1200   # px — only knob you need to touch
LEADERBOARD_HEIGHT   = None   # px — None = auto from row count
LEADERBOARD_MAX_ROWS = 10     # max rows shown (count, not px — does not scale)

# -------------------------------------------------------------------------------
# Scale factor — derived from width; drives ALL pixel values below.
# Reference width = 1200 px  →  scale = 1.0
# At 600 px                  →  scale = 0.5  (everything halves)
# -------------------------------------------------------------------------------

_LB_SCALE = LEADERBOARD_WIDTH / 1200

# ---------------------------------------------------------------------------
# Layout — all auto-scaled
# ---------------------------------------------------------------------------

LEADERBOARD_PADDING_TOP    = int(100 * _LB_SCALE)
LEADERBOARD_PADDING_BOTTOM = int(60  * _LB_SCALE)
LEADERBOARD_MARGIN_X       = int(80  * _LB_SCALE)
LEADERBOARD_CORNER_RADIUS  = int(25  * _LB_SCALE)   # outer border radius; 0 = sharp
LEADERBOARD_HEADER_RADIUS  = int(10  * _LB_SCALE)   # header bar corner radius
LEADERBOARD_BORDER_OFFSET  = int(20  * _LB_SCALE)   # inset of outer border from edge
LEADERBOARD_HEADER_HEIGHT  = int(70  * _LB_SCALE)
LEADERBOARD_ROW_HEIGHT     = int(70  * _LB_SCALE)
LEADERBOARD_BADGE_RADIUS   = int(22  * _LB_SCALE)   # medal circle radius (ranks 1-3)

# ---------------------------------------------------------------------------
# Column x positions — as a fraction of table_width (0.0 → 1.0)
#   Proportional layout: stays correct at ANY width automatically.
#   table_width = LEADERBOARD_WIDTH - 2 * LEADERBOARD_MARGIN_X
# ---------------------------------------------------------------------------

LEADERBOARD_COL_RANK_X  = 0.08   # rank badge/number x-center  (~8% from left)
LEADERBOARD_COL_NAME_X  = 0.20   # name text x-start           (~20% from left)
LEADERBOARD_COL_SCORE_X = 0.88   # score text x-center         (~88% from left)

# ---------------------------------------------------------------------------
# Font sizes — base values calibrated at 1200 px, auto-scaled below that
#   Base values MUST match actual leaderboard.py rendering sizes at 1200 px.
# ---------------------------------------------------------------------------

LEADERBOARD_FONT_TITLE     = int(58 * _LB_SCALE)   # "SEASON STANDINGS" heading
LEADERBOARD_FONT_HEADER    = int(30 * _LB_SCALE)   # RANK / NAME / SCORE labels
LEADERBOARD_FONT_RANK      = int(30 * _LB_SCALE)   # rank number per row
LEADERBOARD_FONT_NAME      = int(28 * _LB_SCALE)   # employee name per row
LEADERBOARD_FONT_SCORE     = int(28 * _LB_SCALE)   # score value per row
LEADERBOARD_FONT_BADGE     = int(14 * _LB_SCALE)   # medal / badge labels

# ===========================================================================
# CHART SIZE
#
#   NOTE: applies to graphs only — NOT the leaderboard.
#   Leaderboard uses LEADERBOARD_WIDTH above (PIL-based, pixels directly).
#
#   Graphs this controls (all in visualization.py + score_timeline.py):
#       - feedback_trend.png
#       - session_count.png
#       - employees_vs_participants.png
#       - employees_vs_participants_monthly.png
#       - participation_rate.png
#       - season_participation.png (+ 8 variant charts)
#
#   Actual output pixel size = inches × DPI
#   Default: 12 × 150 = 1800 px wide, 6 × 150 = 900 px tall
# ===========================================================================

CHART_FIGSIZE = (12, 6)   # (width_inches, height_inches)
CHART_DPI     = 150       # dots per inch — increase for sharper output
