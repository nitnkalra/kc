"""Export public-safe Knowledge Club data for the website.

Reads KC source files and writes JSON into ``src/frontend/src/data/``:

* ``sessions.json``    - all-time session log (topic, program, season, category)
* ``leaderboard.json`` - current season standings (name, score, lastUpdated)
* ``last_season.json`` - previous season top 3 (name, score)
* ``scoring.json``     - point values from config/scoring_rules.py

Only names, scores and topics are exported. Emails, attendance and
feedback data never leave the KC folder.

Run standalone (from src/backend):  python -m publish.publish_site
Or from main.py:                    publish_site(logger)
"""

import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from config import (
    ALL_SESSIONS_PATH,
    ATTENDANCE_BANDS,
    AUTO_GIT_PUSH,
    CATEGORY_COLUMN,
    CONSECUTIVE_SESSION_BONUS,
    DECODE_PLACEHOLDER_TOPIC,
    DECODE_PRESENTATION_POOL,
    DECODE_SESSION_TYPE,
    FEEDBACK_POINTS,
    KC_ROOT,
    LEADERBOARD_JSON_PATH,
    PRESENTATION_POINTS,
    PUSH_BRANCH,
    REPO_DIR,
    SEASON,
    SESSION_TYPE_COLUMN,
    SITE_DATA_DIR,
    WINNERS_COUNT,
)
from config.categories import SITE_CATEGORIES, map_category


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(value) -> str:
    """Return a stripped string; NaN/None -> ''."""
    return "" if pd.isna(value) else str(value).strip()


def _split(value) -> list:
    """Split a comma-separated cell into stripped, non-empty parts."""
    return [part.strip() for part in _clean(value).split(",") if part.strip()]


def _season_number(value) -> Optional[int]:
    """'season_6' -> 6; blank -> None."""
    match = re.search(r"\d+", _clean(value))
    return int(match.group()) if match else None


def _write(name: str, payload: dict, logger) -> None:
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = SITE_DATA_DIR / name
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info(f"Site data saved - {path.name}")


_MONTHS = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]


def _run_date(day: Optional[date] = None) -> str:
    """Run date as '25 November 2026' (English month, independent of OS locale)."""
    day = day or date.today()
    return f"{day.day} {_MONTHS[day.month - 1]} {day.year}"


def _read_standings(path: Path) -> Optional[list]:
    """Read a KC leaderboard.json -> [{name, score}] sorted by score desc."""
    if not path.exists():
        return None
    rows = json.loads(path.read_text(encoding="utf-8")).get("data", [])
    standings = [
        {"name": str(r["name"]).strip(), "score": r["score"]}
        for r in rows
        if r.get("name") is not None and r.get("score") is not None
    ]
    return sorted(standings, key=lambda r: r["score"], reverse=True)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

def _build_sessions(logger) -> list:
    df = pd.read_excel(ALL_SESSIONS_PATH).rename(columns=str.strip)
    for col in (SESSION_TYPE_COLUMN, CATEGORY_COLUMN):
        if col not in df.columns:
            logger.warning(f"Column '{col}' missing in {ALL_SESSIONS_PATH.name}")
            df[col] = None

    sessions, unknown, mapped = [], set(), {}
    for rec in df.to_dict("records"):
        topic = _clean(rec.get("Topic"))
        if not topic:
            continue

        season = _season_number(rec.get("Season"))
        session_type = _clean(rec.get(SESSION_TYPE_COLUMN)).lower() or "regular"
        # Free-text labels -> one of the 5 site categories (None = no match)
        categories = []
        for label in _split(rec.get(CATEGORY_COLUMN)):
            category = map_category(label)
            categories.append(category)
            if category is None:
                unknown.add(label)
            elif category != label:
                mapped[label] = category
        if session_type != DECODE_SESSION_TYPE and not categories:
            logger.warning(f"No category for '{topic}' (season {season})")

        if session_type == DECODE_SESSION_TYPE:
            titles = [] if topic.lower() == DECODE_PLACEHOLDER_TOPIC else _split(topic)
            if titles and len(categories) != len(titles):
                logger.warning(
                    f"DECODE-iT season {season} {_clean(rec.get('Session_ID'))}: "
                    f"{len(titles)} topics but {len(categories)} categories"
                )
            sessions.append({
                "title": "DECODE-iT",
                "program": "decode-it",
                "season": season,
                "topics": [
                    {"title": t, "category": categories[i] if i < len(categories) else None}
                    for i, t in enumerate(titles)
                ],
            })
        else:
            sessions.append({
                "title": topic,
                "program": "tech-tuesdays",
                "season": season,
                "category": categories[0] if categories else None,
            })

    for label, category in sorted(mapped.items()):
        logger.info(f"Category mapped: '{label}' -> '{category}'")
    if unknown:
        logger.warning(
            f"Unmapped categories (not counted on site, add to config/categories.py): {sorted(unknown)}"
        )
    return sessions


def _build_scoring() -> dict:
    """Point values for the site (points table + calculator).

    Single source of truth = config/scoring_rules.py. Never edit
    scoring.json by hand - it is overwritten on every run.
    """
    bands = sorted(ATTENDANCE_BANDS.items(), key=lambda kv: kv[0], reverse=True)
    return {
        "attendanceBands": [[threshold, points] for threshold, points in bands],
        "feedback": FEEDBACK_POINTS,
        "presentation": PRESENTATION_POINTS,
        "decodePool": DECODE_PRESENTATION_POOL,
        "consecutiveBonus": CONSECUTIVE_SESSION_BONUS,
    }


def _build_last_season(current: int) -> Optional[dict]:
    """Top 3 from the previous season's leaderboard.json, if available."""
    relative = LEADERBOARD_JSON_PATH.relative_to(KC_ROOT / SEASON)
    previous = current - 1
    standings = _read_standings(KC_ROOT / f"season_{previous}" / relative)
    if not standings:
        return None
    return {"season": previous, "winners": standings[:WINNERS_COUNT]}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def publish_site(logger) -> None:
    if not SITE_DATA_DIR.parent.exists():
        logger.warning(f"Landing page not found at {SITE_DATA_DIR.parent} - skipped")
        return

    current = _season_number(SEASON)

    _write("scoring.json", _build_scoring(), logger)

    sessions = _build_sessions(logger)

    _write("sessions.json", {
        "currentSeason": current,
        "categories": SITE_CATEGORIES,
        "sessions": sessions,
    }, logger)

    this_season = [s for s in sessions if s["season"] == current]
    logger.info(
        f"Site sessions - all time: {len(sessions)} "
        f"(Tech Tuesdays {sum(s['program'] == 'tech-tuesdays' for s in sessions)}, "
        f"DECODE-iT {sum(s['program'] == 'decode-it' for s in sessions)}) | "
        f"season {current}: {len(this_season)}"
    )

    standings = _read_standings(LEADERBOARD_JSON_PATH)
    if standings is None:
        logger.warning(f"{LEADERBOARD_JSON_PATH.name} not found - leaderboard not updated")
    else:
        _write("leaderboard.json", {
            "title": "Season Standings",
            "lastUpdated": _run_date(),
            "data": standings,
        }, logger)

    last = _build_last_season(current) if current else None
    if last is None:
        logger.warning("Previous season leaderboard not found - winners not updated")
    else:
        _write("last_season.json", last, logger)

    if AUTO_GIT_PUSH:
        _git_push(logger)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_DIR, capture_output=True, text=True, check=False
    )


def _git_push(logger) -> None:
    """Stage only the site JSON; commit and push if anything changed."""
    try:
        if _git("rev-parse", "--is-inside-work-tree").returncode != 0:
            logger.warning(f"{REPO_DIR} is not a git repo - auto push skipped")
            return
        branch = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if branch != PUSH_BRANCH:
            logger.warning(
                f"On branch '{branch}', not '{PUSH_BRANCH}' - auto push skipped. "
                f"Run 'git checkout {PUSH_BRANCH}' and re-run to publish."
            )
            return
        data_glob = SITE_DATA_DIR.relative_to(REPO_DIR).as_posix() + "/*.json"
        _git("add", "--", data_glob)
        if _git("diff", "--cached", "--quiet", "--", data_glob).returncode == 0:
            logger.info("Site data unchanged - nothing to push")
            return
        commit = _git("commit", "-m", f"site: update data ({SEASON})", "--", data_glob)
        if commit.returncode != 0:
            logger.warning(f"git commit failed: {commit.stderr.strip()}")
            return
        push = _git("push")
        if push.returncode != 0:
            logger.warning(f"git push failed: {push.stderr.strip()}")
            return
        logger.info(
            f"Site data pushed to '{PUSH_BRANCH}' - merge {PUSH_BRANCH} -> qa -> main to go live"
        )
    except FileNotFoundError:
        logger.warning("git not installed / not on PATH - auto push skipped")


if __name__ == "__main__":
    from utils.logger import get_logger

    publish_site(get_logger())
