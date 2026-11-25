import sys

from config import (
    LEADERBOARD_PNG_PATH,
    FEEDBACK_TREND_PNG_PATH,
    SESSION_COUNT_PNG_PATH,
    EMPLOYEES_VS_PARTICIPANTS_PNG_PATH,
    EMPLOYEES_VS_PARTICIPANTS_MONTHLY_PNG_PATH,
    PARTICIPATION_RATE_PNG_PATH,
    SEASON_PARTICIPATION_PNG_PATH,
    SEASON_PARTICIPATION_HBAR_PNG_PATH,
    SCORE_TIMELINE_PATH,
)
from core.processor import process_season
from core.score_timeline import build_score_timeline
from publish.publish_site import publish_site
from reports.leaderboard import render_leaderboard_png
from utils.logger import get_logger
from reports.charts import (
    generate_feedback_trend_png,
    generate_session_count_png,
    generate_employees_vs_participants_png,
    generate_employees_vs_participants_monthly_png,
    generate_participation_rate_png,
    generate_season_participation_png,
    generate_season_participation_hbar_png,
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

        generate_season_participation_hbar_png()
        logger.info(f"PNG saved — {SEASON_PARTICIPATION_HBAR_PNG_PATH.name}")

        # 5. Website data — public-safe JSON into src/frontend/src/data/
        publish_site(logger)

        logger.info("Process completed successfully")

    except Exception as e:
        logger.error(str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
