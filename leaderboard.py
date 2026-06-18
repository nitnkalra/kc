import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from config import (
    BG_COLOR,
    ACCENT_COLOR,
    TEXT_COLOR,
    LINE_COLOR,
    ROW_ALT_COLOR,
    LEADERBOARD_WIDTH,
    LEADERBOARD_PADDING_TOP,
    LEADERBOARD_PADDING_BOTTOM,
    LEADERBOARD_HEADER_HEIGHT,
    LEADERBOARD_ROW_HEIGHT,
    LEADERBOARD_MARGIN_X,
    LEADERBOARD_MAX_ROWS,
)


def _load_fonts():
    """Load fonts with fallback chain."""
    candidates_bold = [
        "arialbd.ttf", "Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf"
    ]
    candidates_regular = [
        "arial.ttf", "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]

    def try_load(candidates, size):
        for c in candidates:
            try:
                return ImageFont.truetype(c, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()

    return {
        "title": try_load(candidates_bold, 58),
        "header": try_load(candidates_bold, 30),
        "row": try_load(candidates_regular, 28),
        "rank": try_load(candidates_bold, 30),
        "score": try_load(candidates_bold, 28),
    }


def render_leaderboard_png(base_folder: Path):
    output_folder = base_folder / "outputs"
    input_json_path = output_folder / "leaderboard.json"
    output_file_path = output_folder / "leaderboard.png"

    if not input_json_path.exists():
        raise FileNotFoundError(
            f"Leaderboard JSON not found: {input_json_path}"
        )

    with input_json_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    data = sorted(
        config.get("data", []),
        key=lambda x: x.get("score", 0),
        reverse=True
    )[:LEADERBOARD_MAX_ROWS]

    if not data:
        raise ValueError("No data entries found in leaderboard JSON.")

    # --- Dynamic height ---
    num_rows = len(data)
    table_height = LEADERBOARD_HEADER_HEIGHT + (num_rows * LEADERBOARD_ROW_HEIGHT)
    HEIGHT = LEADERBOARD_PADDING_TOP + table_height + LEADERBOARD_PADDING_BOTTOM + 40

    # --- Canvas ---
    img = Image.new("RGB", (LEADERBOARD_WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    fonts = _load_fonts()

    # --- Title: Season Standings ---
    draw.text(
        (LEADERBOARD_WIDTH // 2, 55),
        "SEASON STANDINGS",
        fill=ACCENT_COLOR,
        font=fonts["title"],
        anchor="mm"
    )

    # --- Table layout ---
    left = LEADERBOARD_MARGIN_X
    top = LEADERBOARD_PADDING_TOP + 10
    table_width = LEADERBOARD_WIDTH - (2 * LEADERBOARD_MARGIN_X)

    # 3 columns: Rank, Name, Score
    rank_x = left + 80
    name_x = left + 200
    score_x = left + table_width - 100

    # --- Header row ---
    draw.rounded_rectangle(
        [left, top, left + table_width, top + LEADERBOARD_HEADER_HEIGHT],
        radius=10,
        fill=ACCENT_COLOR
    )

    draw.text(
        (rank_x, top + LEADERBOARD_HEADER_HEIGHT // 2),
        "RANK", fill="black",
        font=fonts["header"], anchor="mm"
    )
    draw.text(
        (name_x, top + LEADERBOARD_HEADER_HEIGHT // 2),
        "NAME", fill="black",
        font=fonts["header"], anchor="lm"
    )
    draw.text(
        (score_x, top + LEADERBOARD_HEADER_HEIGHT // 2),
        "SCORE", fill="black",
        font=fonts["header"], anchor="mm"
    )

    # --- Data rows ---
    for idx, row in enumerate(data, start=1):
        y = top + LEADERBOARD_HEADER_HEIGHT + (idx - 1) * LEADERBOARD_ROW_HEIGHT
        row_center_y = y + LEADERBOARD_ROW_HEIGHT // 2

        # Alternating row background
        if idx % 2 == 0:
            draw.rectangle(
                [left, y, left + table_width, y + LEADERBOARD_ROW_HEIGHT],
                fill=ROW_ALT_COLOR
            )

        # Row separator
        draw.line(
            [left + 20, y + LEADERBOARD_ROW_HEIGHT, left + table_width - 20, y + LEADERBOARD_ROW_HEIGHT],
            fill=LINE_COLOR,
            width=1
        )

        # Rank — colored for top 3
        if idx == 1:
            rank_color = "#FFD700"
        elif idx == 2:
            rank_color = "#C0C0C0"
        elif idx == 3:
            rank_color = "#CD7F32"
        else:
            rank_color = TEXT_COLOR

        draw.text(
            (rank_x, row_center_y),
            str(idx),
            fill=rank_color,
            font=fonts["rank"],
            anchor="mm"
        )

        # Top 3 circle indicator
        if idx <= 3:
            draw.ellipse(
                [rank_x - 22, row_center_y - 22,
                 rank_x + 22, row_center_y + 22],
                outline=rank_color,
                width=2
            )

        # Name
        name = row.get("name", "")
        if len(name) > 30:
            name = name[:28] + ".."

        draw.text(
            (name_x, row_center_y),
            name,
            fill=TEXT_COLOR,
            font=fonts["row"],
            anchor="lm"
        )

        # Score
        score = row.get("score", 0)
        draw.text(
            (score_x, row_center_y),
            str(score),
            fill=ACCENT_COLOR,
            font=fonts["score"],
            anchor="mm"
        )

    # --- Outer border ---
    draw.rounded_rectangle(
        [20, 20, LEADERBOARD_WIDTH - 20, HEIGHT - 20],
        radius=25,
        outline=ACCENT_COLOR,
        width=3
    )

    img.save(output_file_path)
    return output_file_path


if __name__ == "__main__":
    base = Path.cwd()
    saved = render_leaderboard_png(base)
    print(f"Saved: {saved}")
