import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ==================================================
# CONFIG
# ==================================================

WIDTH = 1400
HEIGHT = 1100

BG_COLOR = "#071326"
HEADER_GOLD = "#E6C15A"
TEXT_WHITE = "#F5F5F5"
LINE_COLOR = "#2A3A52"


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

    title = config.get("title", "Leaderboard")
    data = sorted(
        config.get("data", []),
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arialbd.ttf", 70)
        header_font = ImageFont.truetype("arialbd.ttf", 36)
        row_font = ImageFont.truetype("arial.ttf", 34)
        score_font = ImageFont.truetype("arialbd.ttf", 34)
    except Exception:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        row_font = ImageFont.load_default()
        score_font = ImageFont.load_default()

    draw.text(
        (WIDTH // 2, 80),
        title,
        fill=HEADER_GOLD,
        font=title_font,
        anchor="mm"
    )

    left = 70
    top = 180
    table_width = WIDTH - 140

    header_height = 70
    row_height = 75

    draw.rounded_rectangle(
        [left, top, left + table_width, top + header_height],
        radius=12,
        fill=HEADER_GOLD
    )

    rank_x = left + 120
    name_x = left + 520
    score_x = left + table_width - 160

    draw.text((rank_x, top + 35), "RANK", fill="black",
              font=header_font, anchor="mm")
    draw.text((name_x, top + 35), "NAME", fill="black",
              font=header_font, anchor="mm")
    draw.text((score_x, top + 35), "SCORE", fill="black",
              font=header_font, anchor="mm")

    for idx, row in enumerate(data, start=1):
        y = top + header_height + (idx - 1) * row_height

        draw.rectangle(
            [left, y, left + table_width, y + row_height],
            outline=LINE_COLOR,
            width=1
        )

        if idx == 1:
            rank_text = "🥇"
        elif idx == 2:
            rank_text = "🥈"
        elif idx == 3:
            rank_text = "🥉"
        else:
            rank_text = str(idx)

        draw.text(
            (rank_x, y + row_height / 2),
            rank_text,
            fill=TEXT_WHITE,
            font=row_font,
            anchor="mm"
        )

        draw.text(
            (left + 260, y + row_height / 2),
            row.get("name", ""),
            fill=TEXT_WHITE,
            font=row_font,
            anchor="lm"
        )

        score = row.get("score", 0)
        draw.text(
            (score_x, y + row_height / 2),
            str(score),
            fill=HEADER_GOLD,
            font=score_font,
            anchor="mm"
        )

        bar_x = score_x + 80
        bar_y = y + 25
        bar_w = 180
        bar_h = 22

        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
            radius=10,
            fill="#303030"
        )

        fill_w = int(bar_w * min(score, 100) / 100)

        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
            radius=10,
            fill=HEADER_GOLD
        )

    draw.rounded_rectangle(
        [20, 20, WIDTH - 20, HEIGHT - 20],
        radius=25,
        outline=HEADER_GOLD,
        width=3
    )

    img.save(output_file_path)
    return output_file_path


if __name__ == "__main__":
    base = Path.cwd()
    saved = render_leaderboard_png(base)
    print(f"Saved: {saved}")

