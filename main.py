import sys

from config import (
    LEADERBOARD_PNG_PATH,
    FEEDBACK_TREND_PNG_PATH,
    SESSION_COUNT_PNG_PATH,
    EMPLOYEES_VS_PARTICIPANTS_PNG_PATH,
    EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH,
    PARTICIPATION_RATE_PNG_PATH,
    SEASON_PARTICIPATION_PNG_PATH,
    SEASON_PARTICIPATION_LINE_PNG_PATH,
    SEASON_PARTICIPATION_LOLLIPOP_PNG_PATH,
    SEASON_PARTICIPATION_AREA_PNG_PATH,
    SEASON_PARTICIPATION_HBAR_PNG_PATH,
    SEASON_PARTICIPATION_STEP_PNG_PATH,
    SEASON_PARTICIPATION_DOT_PNG_PATH,
    SEASON_PARTICIPATION_GAUGE_PNG_PATH,
    SEASON_PARTICIPATION_DELTA_PNG_PATH,
    SCORE_TIMELINE_PATH,
)
from src.logger import get_logger
from src.processor import process_season
from leaderboard import render_leaderboard_png
from score_timeline import build_score_timeline
from visualization import (
    generate_feedback_trend_png,
    generate_session_count_png,
    generate_employees_vs_participants_png,
    generate_employees_vs_participants_monthly_png,
    generate_participation_rate_png,
    generate_season_participation_png,
    generate_season_participation_line_png,
    generate_season_participation_lollipop_png,
    generate_season_participation_area_png,
    generate_season_participation_hbar_png,
    generate_season_participation_step_png,
    generate_season_participation_dot_png,
    generate_season_participation_gauge_png,
    generate_season_participation_delta_png,
)


def main():

    logger = get_logger()
    logger.info("Process started")

    try:

        # 1. Core processing — scores, leaderboard, session summary
        #    Returns history DataFrame directly (no intermediate file)
        history_df = process_season(logger)

        # 2. Leaderboard PNG
        render_leaderboard_png()
        logger.info(f"PNG saved — {LEADERBOARD_PNG_PATH.name}")

        # 3. Score timeline — receives history in-memory, no disk read
        build_score_timeline(history_df, logger)
        logger.info(f"Excel saved — {SCORE_TIMELINE_PATH.name}")

        # 4. Charts — core
        generate_feedback_trend_png()
        logger.info(f"PNG saved — {FEEDBACK_TREND_PNG_PATH.name}")

        generate_session_count_png()
        logger.info(f"PNG saved — {SESSION_COUNT_PNG_PATH.name}")

        generate_employees_vs_participants_png()
        logger.info(f"PNG saved — {EMPLOYEES_VS_PARTICIPANTS_PNG_PATH.name}")

        generate_employees_vs_participants_monthly_png()
        logger.info(f"PNG saved — {EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH.name}")

        generate_participation_rate_png()
        logger.info(f"PNG saved — {PARTICIPATION_RATE_PNG_PATH.name}")

        generate_season_participation_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_PNG_PATH.name}")

        # 5. Season Participation — 8 variant charts
        generate_season_participation_line_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_LINE_PNG_PATH.name}")

        generate_season_participation_lollipop_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_LOLLIPOP_PNG_PATH.name}")

        generate_season_participation_area_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_AREA_PNG_PATH.name}")

        generate_season_participation_hbar_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_HBAR_PNG_PATH.name}")

        generate_season_participation_step_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_STEP_PNG_PATH.name}")

        generate_season_participation_dot_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_DOT_PNG_PATH.name}")

        generate_season_participation_gauge_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_GAUGE_PNG_PATH.name}")

        generate_season_participation_delta_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_DELTA_PNG_PATH.name}")

        logger.info("Process completed successfully")

    except Exception as e:
        logger.error(str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
