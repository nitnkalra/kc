import sys

from config import (
    SEASON_FOLDER,
    LEADERBOARD_PNG_FILE,
    FEEDBACK_TREND_PNG,
    SESSION_COUNT_PNG,
    EMPLOYEES_VS_PARTICIPANTS_PNG,
)
from src.logger import get_logger
from src.processor import process_season
from leaderboard import render_leaderboard_png
from visualization import (
    generate_feedback_trend_png,
    generate_session_count_png,
    generate_employees_vs_participants_png,
)


def main():

    logger = get_logger()

    logger.info("Process started")

    try:

        process_season(
            SEASON_FOLDER,
            logger
        )

        render_leaderboard_png(SEASON_FOLDER)

        logger.info(f"PNG saved — {LEADERBOARD_PNG_FILE}")

        generate_feedback_trend_png()

        logger.info(f"PNG saved — {FEEDBACK_TREND_PNG}")

        generate_session_count_png()

        logger.info(f"PNG saved — {SESSION_COUNT_PNG}")

        generate_employees_vs_participants_png()

        logger.info(f"PNG saved — {EMPLOYEES_VS_PARTICIPANTS_PNG}")

        logger.info("Process completed successfully")

    except Exception as e:

        logger.error(
            str(e),
            exc_info=True
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
