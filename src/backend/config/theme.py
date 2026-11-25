"""
Active theme colors - auto-loaded from settings.ACTIVE_THEME.
To change the look, edit ACTIVE_THEME in settings.py (palettes: themes.py).
"""

from .settings import ACTIVE_THEME
from .themes import THEMES

if ACTIVE_THEME not in THEMES:
    raise ValueError(
        f"Unknown ACTIVE_THEME '{ACTIVE_THEME}'. Available: {sorted(THEMES)}"
    )

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
