import json
from PIL import Image, ImageDraw, ImageFont

from config import (
    BG_COLOR,
    ACCENT_COLOR,
    TEXT_COLOR,
    LINE_COLOR,
    ROW_ALT_COLOR,
    LB_RANK1_COLOR,
    LB_RANK2_COLOR,
    LB_RANK3_COLOR,
    LEADERBOARD_WIDTH,
    LEADERBOARD_PADDING_TOP,
    LEADERBOARD_PADDING_BOTTOM,
    LEADERBOARD_HEADER_HEIGHT,
    LEADERBOARD_ROW_HEIGHT,
    LEADERBOARD_MARGIN_X,
    LEADERBOARD_MAX_ROWS,
    LEADERBOARD_CORNER_RADIUS,
    LEADERBOARD_HEADER_RADIUS,
    LEADERBOARD_BORDER_OFFSET,
    LEADERBOARD_BADGE_RADIUS,
    LEADERBOARD_COL_RANK_X,
    LEADERBOARD_COL_NAME_X,
    LEADERBOARD_COL_SCORE_X,
    LEADERBOARD_FONT_TITLE,
    LEADERBOARD_FONT_HEADER,
    LEADERBOARD_FONT_RANK,
    LEADERBOARD_FONT_NAME,
    LEADERBOARD_FONT_SCORE,
    # Paths
    LEADERBOARD_JSON_PATH,
    LEADERBOARD_PNG_PATH,
    OUTPUT_FOLDER,
)


def _load_fonts() -> dict:
    """Load fonts at config-driven sizes with silent fallback to default."""
    candidates_bold = [
        "arialbd.ttf", "Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    candidates_regular = [
        "arial.ttf", "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    def _try(candidates, size):
        size = max(8, size)   # prevent size=0 at very small widths
        for c in candidates:
            try:
                return ImageFont.truetype(c, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    return {
        "title":  _try(candidates_bold,    LEADERBOARD_FONT_TITLE),
        "header": _try(candidates_bold,    LEADERBOARD_FONT_HEADER),
        "row":    _try(candidates_regular, LEADERBOARD_FONT_NAME),
        "rank":   _try(candidates_bold,    LEADERBOARD_FONT_RANK),
        "score":  _try(candidates_bold,    LEADERBOARD_FONT_SCORE),
    }


def _truncate_name(name: str, font: ImageFont.FreeTypeFont, max_px: int) -> str:
    """Truncate name to fit within max_px pixels using actual font metrics."""
    if font.getlength(name) <= max_px:
        return name
    while len(name) > 1 and font.getlength(name + "..") > max_px:
        name = name[:-1]
    return name + ".."


def render_leaderboard_png() -> "Path":
    """
    Render leaderboard.png from leaderboard.json.
    Reads LEADERBOARD_JSON_PATH, writes LEADERBOARD_PNG_PATH.
    All layout values are proportional — changing LEADERBOARD_WIDTH
    in config/graphs.py is the only edit needed to resize.
    """
    OUTPUT_FOLDER.mkdir(exist_ok=True)

    if not LEADERBOARD_JSON_PATH.exists():
        raise FileNotFoundError(
            f"Leaderboard JSON not found: {LEADERBOARD_JSON_PATH}"
        )

    with LEADERBOARD_JSON_PATH.open("r", encoding="utf-8") as f:
        data_json = json.load(f)

    data = sorted(
        data_json.get("data", []),
        key=lambda x: x.get("score", 0),
        reverse=True,
    )[:LEADERBOARD_MAX_ROWS]

    if not data:
        raise ValueError("No data entries found in leaderboard JSON.")

    fonts = _load_fonts()

    # Canvas dimensions
    table_h = LEADERBOARD_HEADER_HEIGHT + len(data) * LEADERBOARD_ROW_HEIGHT
    height  = LEADERBOARD_PADDING_TOP + table_h + LEADERBOARD_PADDING_BOTTOM + 40

    img  = Image.new("RGB", (LEADERBOARD_WIDTH, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # -----------------------------------------------------------------------
    # Layout anchors — all derived from width so they scale automatically
    # -----------------------------------------------------------------------
    left        = LEADERBOARD_MARGIN_X
    top         = LEADERBOARD_PADDING_TOP + 10
    table_width = LEADERBOARD_WIDTH - 2 * LEADERBOARD_MARGIN_X

    rank_x  = left + int(LEADERBOARD_COL_RANK_X  * table_width)
    name_x  = left + int(LEADERBOARD_COL_NAME_X  * table_width)
    score_x = left + int(LEADERBOARD_COL_SCORE_X * table_width)

    # Max pixels available for the name before it hits the score column
    name_max_px = score_x - name_x - int(LEADERBOARD_FONT_NAME * 1.5)

    # Title — vertically centred in the top padding area
    title_y = LEADERBOARD_PADDING_TOP // 2
    draw.text(
        (LEADERBOARD_WIDTH // 2, title_y), "SEASON STANDINGS",
        fill=ACCENT_COLOR, font=fonts["title"], anchor="mm",
    )

    # -----------------------------------------------------------------------
    # Header row
    # -----------------------------------------------------------------------
    draw.rounded_rectangle(
        [left, top, left + table_width, top + LEADERBOARD_HEADER_HEIGHT],
        radius=LEADERBOARD_HEADER_RADIUS, fill=ACCENT_COLOR,
    )
    mid_h = top + LEADERBOARD_HEADER_HEIGHT // 2
    draw.text((rank_x,  mid_h), "RANK",  fill="black", font=fonts["header"], anchor="mm")
    draw.text((name_x,  mid_h), "NAME",  fill="black", font=fonts["header"], anchor="lm")
    draw.text((score_x, mid_h), "SCORE", fill="black", font=fonts["header"], anchor="mm")

    # -----------------------------------------------------------------------
    # Data rows
    # -----------------------------------------------------------------------
    rank_colors = {
        1: LB_RANK1_COLOR,
        2: LB_RANK2_COLOR,
        3: LB_RANK3_COLOR,
    }

    for idx, row in enumerate(data, start=1):
        y        = top + LEADERBOARD_HEADER_HEIGHT + (idx - 1) * LEADERBOARD_ROW_HEIGHT
        center_y = y + LEADERBOARD_ROW_HEIGHT // 2

        # Alternating row tint
        if idx % 2 == 0:
            draw.rectangle(
                [left, y, left + table_width, y + LEADERBOARD_ROW_HEIGHT],
                fill=ROW_ALT_COLOR,
            )

        # Row separator line
        draw.line(
            [left + 20, y + LEADERBOARD_ROW_HEIGHT,
             left + table_width - 20, y + LEADERBOARD_ROW_HEIGHT],
            fill=LINE_COLOR, width=1,
        )

        # Rank badge (medal circle for top 3)
        rank_color = rank_colors.get(idx, TEXT_COLOR)
        draw.text(
            (rank_x, center_y), str(idx),
            fill=rank_color, font=fonts["rank"], anchor="mm",
        )
        if idx <= 3:
            r = LEADERBOARD_BADGE_RADIUS
            draw.ellipse(
                [rank_x - r, center_y - r, rank_x + r, center_y + r],
                outline=rank_color, width=2,
            )

        # Name — pixel-aware truncation prevents overlap with score
        name = _truncate_name(row.get("name", ""), fonts["row"], name_max_px)
        draw.text(
            (name_x, center_y), name,
            fill=TEXT_COLOR, font=fonts["row"], anchor="lm",
        )

        # Score
        draw.text(
            (score_x, center_y), str(row.get("score", 0)),
            fill=ACCENT_COLOR, font=fonts["score"], anchor="mm",
        )

    # -----------------------------------------------------------------------
    # Outer border
    # -----------------------------------------------------------------------
    off = LEADERBOARD_BORDER_OFFSET
    draw.rounded_rectangle(
        [off, off, LEADERBOARD_WIDTH - off, height - off],
        radius=LEADERBOARD_CORNER_RADIUS, outline=ACCENT_COLOR, width=3,
    )

    img.save(LEADERBOARD_PNG_PATH)
    return LEADERBOARD_PNG_PATH


if __name__ == "__main__":
    saved = render_leaderboard_png()
    print(f"Saved: {saved}")
