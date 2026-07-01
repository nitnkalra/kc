# ===========================================================================
# THEMES — All color schemes for leaderboard + charts
#
#   Each theme defines the full set of color tokens consumed by
#   leaderboard.py and chart generation scripts.
#
#   To add a custom theme: copy any existing block, give it a new key,
#   and update the hex values. Then reference the key in config.py.
#
#   Keys per theme:
#       BG_COLOR        — main canvas / leaderboard body background
#       HEADER_COLOR    — leaderboard header bar background
#       ACCENT_COLOR    — score values, title text, highlights
#       SECONDARY_COLOR — secondary chart / UI accent
#       TEXT_COLOR      — primary body text (names, ranks)
#       HEADER_TEXT     — text color on the header bar
#       GRID_COLOR      — chart grid lines
#       LINE_COLOR      — row separators
#       ROW_ALT_COLOR   — alternating row tint
#       CHART_BG_COLOR  — chart canvas background
#       CHART_GRID_COLOR— chart grid line color
#       CHART_TEXT_COLOR— chart axis labels and titles
#       CHART_COLORS    — ordered data-series palette (list of 8)
#       LB_RANK1_COLOR  — rank 1 badge color (gold)
#       LB_RANK2_COLOR  — rank 2 badge color (silver)
#       LB_RANK3_COLOR  — rank 3 badge color (bronze)
# ===========================================================================

THEMES = {

    # -------------------------------------------------------------------------
    # power_bi_light — white canvas, Power BI blue accent  [DEFAULT]
    # -------------------------------------------------------------------------
    "power_bi_light": {
        "BG_COLOR":         "#FFFFFF",
        "HEADER_COLOR":     "#0078D4",
        "ACCENT_COLOR":     "#0078D4",
        "SECONDARY_COLOR":  "#E66C37",
        "TEXT_COLOR":       "#252423",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#E1DFDD",
        "LINE_COLOR":       "#C8C6C4",
        "ROW_ALT_COLOR":    "#F3F2F1",
        "CHART_BG_COLOR":   "#FFFFFF",
        "CHART_GRID_COLOR": "#E1DFDD",
        "CHART_TEXT_COLOR": "#252423",
        "CHART_COLORS": [
            "#0078D4",  # Blue
            "#E66C37",  # Orange
            "#107C10",  # Green
            "#FFB900",  # Yellow
            "#D64550",  # Red
            "#00B0FF",  # Cyan
            "#744EC2",  # Purple
            "#E044A7",  # Pink
        ],
        "LB_RANK1_COLOR":   "#FFB900",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # power_bi_dark — dark canvas, Power BI blue accent
    # -------------------------------------------------------------------------
    "power_bi_dark": {
        "BG_COLOR":         "#252423",
        "HEADER_COLOR":     "#118DFF",
        "ACCENT_COLOR":     "#118DFF",
        "SECONDARY_COLOR":  "#E66C37",
        "TEXT_COLOR":       "#FFFFFF",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#3B3B3B",
        "LINE_COLOR":       "#404040",
        "ROW_ALT_COLOR":    "#1F1F1F",
        "CHART_BG_COLOR":   "#252423",
        "CHART_GRID_COLOR": "#3B3B3B",
        "CHART_TEXT_COLOR": "#FFFFFF",
        "CHART_COLORS": [
            "#118DFF",  # Blue
            "#E66C37",  # Orange
            "#107C10",  # Green
            "#FFB900",  # Yellow
            "#D64550",  # Red
            "#00B0FF",  # Cyan
            "#744EC2",  # Purple
            "#E044A7",  # Pink
        ],
        "LB_RANK1_COLOR":   "#FFB900",
        "LB_RANK2_COLOR":   "#C8C8C8",
        "LB_RANK3_COLOR":   "#CD7F32",
    },

    # -------------------------------------------------------------------------
    # power_bi_executive — near-black canvas, gold accent  (award / premium feel)
    # -------------------------------------------------------------------------
    "power_bi_executive": {
        "BG_COLOR":         "#1F1F1F",
        "HEADER_COLOR":     "#7A5C1E",
        "ACCENT_COLOR":     "#FFB900",
        "SECONDARY_COLOR":  "#C8C8C8",
        "TEXT_COLOR":       "#FFFFFF",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#2D2D2D",
        "LINE_COLOR":       "#383838",
        "ROW_ALT_COLOR":    "#252525",
        "CHART_BG_COLOR":   "#1F1F1F",
        "CHART_GRID_COLOR": "#2D2D2D",
        "CHART_TEXT_COLOR": "#FFFFFF",
        "CHART_COLORS": [
            "#FFB900",  # Gold
            "#E66C37",  # Orange
            "#00B0FF",  # Cyan
            "#107C10",  # Green
            "#D64550",  # Red
            "#C8C8C8",  # Silver
            "#744EC2",  # Purple
            "#E044A7",  # Pink
        ],
        "LB_RANK1_COLOR":   "#FFB900",
        "LB_RANK2_COLOR":   "#C8C8C8",
        "LB_RANK3_COLOR":   "#CD7F32",
    },

    # -------------------------------------------------------------------------
    # power_bi_innovate — white canvas, purple accent  (modern / tech)
    # -------------------------------------------------------------------------
    "power_bi_innovate": {
        "BG_COLOR":         "#FFFFFF",
        "HEADER_COLOR":     "#5C2D91",
        "ACCENT_COLOR":     "#5C2D91",
        "SECONDARY_COLOR":  "#E66C37",
        "TEXT_COLOR":       "#252423",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#E1DFDD",
        "LINE_COLOR":       "#C8C6C4",
        "ROW_ALT_COLOR":    "#F8F0FF",
        "CHART_BG_COLOR":   "#FFFFFF",
        "CHART_GRID_COLOR": "#E1DFDD",
        "CHART_TEXT_COLOR": "#252423",
        "CHART_COLORS": [
            "#5C2D91",  # Purple
            "#E66C37",  # Orange
            "#0078D4",  # Blue
            "#107C10",  # Green
            "#D64550",  # Red
            "#FFB900",  # Yellow
            "#744EC2",  # Violet
            "#E044A7",  # Pink
        ],
        "LB_RANK1_COLOR":   "#FFB900",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # power_bi_frontier — white canvas, teal accent  (fresh / energetic)
    # -------------------------------------------------------------------------
    "power_bi_frontier": {
        "BG_COLOR":         "#FFFFFF",
        "HEADER_COLOR":     "#00897B",
        "ACCENT_COLOR":     "#00897B",
        "SECONDARY_COLOR":  "#E66C37",
        "TEXT_COLOR":       "#252423",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#E0F2F1",
        "LINE_COLOR":       "#B2DFDB",
        "ROW_ALT_COLOR":    "#F0FAF9",
        "CHART_BG_COLOR":   "#FFFFFF",
        "CHART_GRID_COLOR": "#E0F2F1",
        "CHART_TEXT_COLOR": "#252423",
        "CHART_COLORS": [
            "#00897B",  # Teal
            "#E66C37",  # Orange
            "#0078D4",  # Blue
            "#FFB900",  # Yellow
            "#D64550",  # Red
            "#00B0FF",  # Cyan
            "#5C2D91",  # Purple
            "#107C10",  # Green
        ],
        "LB_RANK1_COLOR":   "#FFB900",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # mckinsey — white canvas, deep navy + sky blue  (premium consulting)
    # -------------------------------------------------------------------------
    "mckinsey": {
        "BG_COLOR":         "#FFFFFF",
        "HEADER_COLOR":     "#002D62",
        "ACCENT_COLOR":     "#00A3E0",
        "SECONDARY_COLOR":  "#E8402A",
        "TEXT_COLOR":       "#1A1A1A",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#E8E8E8",
        "LINE_COLOR":       "#D0D0D0",
        "ROW_ALT_COLOR":    "#F5F8FB",
        "CHART_BG_COLOR":   "#FFFFFF",
        "CHART_GRID_COLOR": "#E8E8E8",
        "CHART_TEXT_COLOR": "#1A1A1A",
        "CHART_COLORS": [
            "#00A3E0",  # Sky blue
            "#002D62",  # Deep navy
            "#E8402A",  # Red
            "#7AC143",  # Green
            "#F7A800",  # Amber
            "#9B5EA2",  # Purple
            "#00B5AD",  # Teal
            "#F0965A",  # Peach
        ],
        "LB_RANK1_COLOR":   "#F7A800",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # tableau — off-white canvas, Tableau muted-blue series
    # -------------------------------------------------------------------------
    "tableau": {
        "BG_COLOR":         "#F5F5F5",
        "HEADER_COLOR":     "#4E79A7",
        "ACCENT_COLOR":     "#4E79A7",
        "SECONDARY_COLOR":  "#F28E2B",
        "TEXT_COLOR":       "#2D2D2D",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#DDDDDD",
        "LINE_COLOR":       "#CCCCCC",
        "ROW_ALT_COLOR":    "#EBEBEB",
        "CHART_BG_COLOR":   "#F5F5F5",
        "CHART_GRID_COLOR": "#DDDDDD",
        "CHART_TEXT_COLOR": "#2D2D2D",
        "CHART_COLORS": [
            "#4E79A7",  # Steel blue
            "#F28E2B",  # Orange
            "#E15759",  # Red
            "#76B7B2",  # Teal
            "#59A14F",  # Green
            "#EDC948",  # Yellow
            "#B07AA1",  # Mauve
            "#FF9DA7",  # Pink
        ],
        "LB_RANK1_COLOR":   "#EDC948",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # salesforce — light gray canvas, Salesforce blue
    # -------------------------------------------------------------------------
    "salesforce": {
        "BG_COLOR":         "#F3F3F3",
        "HEADER_COLOR":     "#0176D3",
        "ACCENT_COLOR":     "#0176D3",
        "SECONDARY_COLOR":  "#FE9339",
        "TEXT_COLOR":       "#181818",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#DDDBDA",
        "LINE_COLOR":       "#C9C7C5",
        "ROW_ALT_COLOR":    "#EAEAEA",
        "CHART_BG_COLOR":   "#F3F3F3",
        "CHART_GRID_COLOR": "#DDDBDA",
        "CHART_TEXT_COLOR": "#181818",
        "CHART_COLORS": [
            "#0176D3",  # Salesforce blue
            "#FE9339",  # Orange
            "#2E844A",  # Green
            "#DD7A01",  # Amber
            "#BA0517",  # Red
            "#0B827C",  # Teal
            "#9050E9",  # Purple
            "#D4504C",  # Coral
        ],
        "LB_RANK1_COLOR":   "#DD7A01",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # google_looker — white canvas, Google blue
    # -------------------------------------------------------------------------
    "google_looker": {
        "BG_COLOR":         "#FFFFFF",
        "HEADER_COLOR":     "#1A73E8",
        "ACCENT_COLOR":     "#1A73E8",
        "SECONDARY_COLOR":  "#EA4335",
        "TEXT_COLOR":       "#202124",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#DADCE0",
        "LINE_COLOR":       "#BDC1C6",
        "ROW_ALT_COLOR":    "#F8F9FA",
        "CHART_BG_COLOR":   "#FFFFFF",
        "CHART_GRID_COLOR": "#DADCE0",
        "CHART_TEXT_COLOR": "#202124",
        "CHART_COLORS": [
            "#1A73E8",  # Google blue
            "#EA4335",  # Google red
            "#34A853",  # Google green
            "#FBBC04",  # Google yellow
            "#FA7B17",  # Orange
            "#46BDC6",  # Cyan
            "#9C27B0",  # Purple
            "#FF6D00",  # Deep orange
        ],
        "LB_RANK1_COLOR":   "#FBBC04",
        "LB_RANK2_COLOR":   "#8A8886",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # minimal_corporate — near-white canvas, dark slate + clean blue
    # -------------------------------------------------------------------------
    "minimal_corporate": {
        "BG_COLOR":         "#FAFAFA",
        "HEADER_COLOR":     "#2C3E50",
        "ACCENT_COLOR":     "#3498DB",
        "SECONDARY_COLOR":  "#E67E22",
        "TEXT_COLOR":       "#2C3E50",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#ECF0F1",
        "LINE_COLOR":       "#D5D8DC",
        "ROW_ALT_COLOR":    "#F2F3F4",
        "CHART_BG_COLOR":   "#FAFAFA",
        "CHART_GRID_COLOR": "#ECF0F1",
        "CHART_TEXT_COLOR": "#2C3E50",
        "CHART_COLORS": [
            "#3498DB",  # Blue
            "#E67E22",  # Orange
            "#2ECC71",  # Emerald
            "#E74C3C",  # Red
            "#9B59B6",  # Purple
            "#1ABC9C",  # Turquoise
            "#F1C40F",  # Yellow
            "#95A5A6",  # Gray
        ],
        "LB_RANK1_COLOR":   "#F1C40F",
        "LB_RANK2_COLOR":   "#95A5A6",
        "LB_RANK3_COLOR":   "#A0522D",
    },

    # -------------------------------------------------------------------------
    # microsoft_office — white canvas, Office green header + blue accent
    # -------------------------------------------------------------------------
    "microsoft_office": {
        "BG_COLOR":         "#FFFFFF",
        "HEADER_COLOR":     "#217346",
        "ACCENT_COLOR":     "#0070C0",
        "SECONDARY_COLOR":  "#ED7D31",
        "TEXT_COLOR":       "#000000",
        "HEADER_TEXT":      "#FFFFFF",
        "GRID_COLOR":       "#D9D9D9",
        "LINE_COLOR":       "#BFBFBF",
        "ROW_ALT_COLOR":    "#E2EFDA",
        "CHART_BG_COLOR":   "#FFFFFF",
        "CHART_GRID_COLOR": "#D9D9D9",
        "CHART_TEXT_COLOR": "#000000",
        "CHART_COLORS": [
            "#4472C4",  # Blue
            "#ED7D31",  # Orange
            "#A9D18E",  # Light green
            "#FFC000",  # Gold
            "#FF0000",  # Red
            "#00B0F0",  # Sky blue
            "#7030A0",  # Purple
            "#00B050",  # Green
        ],
        "LB_RANK1_COLOR":   "#FFC000",
        "LB_RANK2_COLOR":   "#808080",
        "LB_RANK3_COLOR":   "#A0522D",
    },
}
