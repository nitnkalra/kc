"""
KC configuration package.

    settings.py       KC_ROOT, SEASON, ACTIVE_THEME   <- the only file you normally edit
    paths.py          all input / output / project paths (derived)
    scoring_rules.py  every point value (pipeline + website)
    data_format.py    Excel column / sheet names, bot email
    theme.py          active theme colors (palettes in themes.py)
    graphs.py         leaderboard PNG layout + chart size
    site.py           website publishing (auto git push, winners)
    categories.py     free-text category -> site category mapping

Everything is re-exported here, so modules simply use:
    from config import SEASON, ATTENDANCE_BANDS, CHART_DPI
"""

from .settings import *        # noqa: F401,F403
from .paths import *           # noqa: F401,F403
from .scoring_rules import *   # noqa: F401,F403
from .data_format import *     # noqa: F401,F403
from .theme import *           # noqa: F401,F403
from .graphs import *          # noqa: F401,F403
from .site import *            # noqa: F401,F403
