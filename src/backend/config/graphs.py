"""
Graph settings - leaderboard PNG layout (reports/leaderboard.py) and
chart size (reports/charts.py + core/score_timeline.py).
"""

# ===========================================================================
# LEADERBOARD PNG LAYOUT  (pixels)
#
#   *** ONLY change LEADERBOARD_WIDTH - everything else scales automatically ***
#
#   LEADERBOARD_HEIGHT:
#       None  -> auto-calculated from row count (recommended)
#       <int> -> fixed pixel height; rows are scaled to fit
# ===========================================================================

LEADERBOARD_WIDTH    = 1200   # px - only knob you need to touch
LEADERBOARD_HEIGHT   = None   # px - None = auto from row count
LEADERBOARD_MAX_ROWS = 10     # max rows shown (count, not px - does not scale)

# Scale factor - derived from width; drives ALL pixel values below.
# Reference width = 1200 px -> scale = 1.0 ; 600 px -> 0.5 (everything halves)
_LB_SCALE = LEADERBOARD_WIDTH / 1200

# Layout - all auto-scaled
LEADERBOARD_PADDING_TOP    = int(100 * _LB_SCALE)
LEADERBOARD_PADDING_BOTTOM = int(60  * _LB_SCALE)
LEADERBOARD_MARGIN_X       = int(80  * _LB_SCALE)
LEADERBOARD_CORNER_RADIUS  = int(25  * _LB_SCALE)   # outer border radius; 0 = sharp
LEADERBOARD_HEADER_RADIUS  = int(10  * _LB_SCALE)   # header bar corner radius
LEADERBOARD_BORDER_OFFSET  = int(20  * _LB_SCALE)   # inset of outer border from edge
LEADERBOARD_HEADER_HEIGHT  = int(70  * _LB_SCALE)
LEADERBOARD_ROW_HEIGHT     = int(70  * _LB_SCALE)
LEADERBOARD_BADGE_RADIUS   = int(22  * _LB_SCALE)   # medal circle radius (ranks 1-3)

# Column x positions - fraction of table_width (0.0 -> 1.0)
#   table_width = LEADERBOARD_WIDTH - 2 * LEADERBOARD_MARGIN_X
LEADERBOARD_COL_RANK_X  = 0.08   # rank badge/number x-center  (~8% from left)
LEADERBOARD_COL_NAME_X  = 0.20   # name text x-start           (~20% from left)
LEADERBOARD_COL_SCORE_X = 0.88   # score text x-center         (~88% from left)

# Font sizes - base values calibrated at 1200 px, auto-scaled
LEADERBOARD_FONT_TITLE  = int(58 * _LB_SCALE)   # "SEASON STANDINGS" heading
LEADERBOARD_FONT_HEADER = int(30 * _LB_SCALE)   # RANK / NAME / SCORE labels
LEADERBOARD_FONT_RANK   = int(30 * _LB_SCALE)   # rank number per row
LEADERBOARD_FONT_NAME   = int(28 * _LB_SCALE)   # employee name per row
LEADERBOARD_FONT_SCORE  = int(28 * _LB_SCALE)   # score value per row
LEADERBOARD_FONT_BADGE  = int(14 * _LB_SCALE)   # medal / badge labels

# ===========================================================================
# CHART SIZE  (graphs only - NOT the leaderboard PNG)
#
#   feedback_trend, session_count, employees_vs_participants(_monthly),
#   participation_rate, season_participation (+ variants)
#
#   Output pixel size = inches x DPI  ->  12 x 150 = 1800 px, 6 x 150 = 900 px
# ===========================================================================

CHART_FIGSIZE = (12, 6)   # (width_inches, height_inches)
CHART_DPI     = 150       # dots per inch - increase for sharper output
