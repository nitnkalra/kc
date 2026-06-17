from config import SEASON_FOLDER

from src.logger import get_logger
from src.processor import process_season
from leaderboard import render_leaderboard_png


def main():

    logger = get_logger()

    logger.info(
        "Process Started"
    )

    try:

        process_season(
            SEASON_FOLDER,
            logger
        )

        render_leaderboard_png(SEASON_FOLDER)

        logger.info(
            "Outputs saved successfully"
        )

    except Exception as e:

        logger.error(
            str(e)
        )


if __name__ == "__main__":
    main()