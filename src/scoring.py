from config import ATTENDANCE_BANDS


def get_attendance_points(attendance_pct: float) -> int:
    """
    Return the points earned for a given attendance percentage.

    Thresholds from ATTENDANCE_BANDS in config.py.
    Keys are sorted descending at call time — safe regardless of
    insertion order in the config dict.

    Example:
        92% -> 25 pts  (>= 90)
        76% -> 20 pts  (>= 75)
        55% -> 10 pts  (>= 50)
        30% ->  5 pts  (>= 25)
         5% ->  0 pts  (>= 0)
    """
    for threshold in sorted(ATTENDANCE_BANDS.keys(), reverse=True):
        if attendance_pct >= threshold:
            return ATTENDANCE_BANDS[threshold]

    return 0
