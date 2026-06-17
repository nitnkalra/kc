from config import ATTENDANCE_BANDS


def get_attendance_points(attendance_pct):

    for threshold, points in ATTENDANCE_BANDS.items():

        if attendance_pct >= threshold:
            return points

    return 0