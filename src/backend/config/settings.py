"""
SETUP - the only file you normally need to edit.

    Moving to a new machine / sharing with someone else -> KC_ROOT
    Starting a new season                               -> SEASON
    Changing the look of PNGs and charts                -> ACTIVE_THEME

Everything else (paths, scoring, graphs, site) is derived in the other
config/*.py files.
"""

from pathlib import Path

# Absolute path to the KC data folder (season folders + all_session_details.xlsx)
KC_ROOT = Path(
    r"D:\kc\INXITE-OUT PRIVATE LIMITED\KnowledgeClub - Documents\kc"
)

# Active season sub-folder name - change to "season_7", "season_8", etc.
SEASON = "season_6"

# ---------------------------------------------------------------------------
# Active theme - change this one value to reskin every PNG and chart.
# Palettes are defined in config/themes.py.
#
#   power_bi_light      - white bg, blue accent
#   power_bi_dark       - dark gray bg, blue accent
#   power_bi_executive  - near-black bg, gold accent
#   power_bi_innovate   - white bg, purple accent
#   power_bi_frontier   - white bg, teal accent           <- default
#   mckinsey            - white bg, deep navy + sky blue
#   tableau             - off-white bg, muted blue series
#   salesforce          - light gray bg, Salesforce blue
#   google_looker       - white bg, Google blue
#   minimal_corporate   - near-white bg, dark slate + blue
#   microsoft_office    - white bg, Office green + blue
# ---------------------------------------------------------------------------
ACTIVE_THEME = "power_bi_frontier"
