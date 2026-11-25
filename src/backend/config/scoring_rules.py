"""
Scoring rules - single source of truth for every point value.

Used by the pipeline (core/) AND published to the website
(publish/publish_site.py -> frontend/src/data/scoring.json),
so the site's points table and calculator always match this file.
"""

# ===========================================================================
# ATTENDANCE
# ===========================================================================

# Attendance % -> points  (core/scoring.py iterates keys sorted descending)
# Bands are uniform +5 per tier. Below 5% (ghost joins) -> 0 pts.
# Example: 92% -> 25, 76% -> 20, 55% -> 15, 30% -> 10, 10% -> 5, 3% -> 0
ATTENDANCE_BANDS = {
    90: 25,
    75: 20,
    50: 15,
    25: 10,
    5:  5,
    0:  0,
}

JOIN_BUFFER_MINUTES  = 3    # grace period after session start
LEAVE_BUFFER_MINUTES = 5    # grace period before session end

# ===========================================================================
# FEEDBACK + PRESENTATION
# ===========================================================================

FEEDBACK_POINTS     = 25    # flat pts for submitting feedback form
PRESENTATION_POINTS = 100   # flat pts for presenting a regular session

# Decode-It sessions - presentation pool shared equally among all presenters.
# Regular  : each presenter -> PRESENTATION_POINTS (100) flat
# Decode-It: each presenter -> round(DECODE_PRESENTATION_POOL / num_presenters)
#   2 presenters -> 50 each, 3 -> 33 each, 4 -> 25 each
DECODE_SESSION_TYPE      = "decode-it"
DECODE_PRESENTATION_POOL = 100

# ===========================================================================
# CONSECUTIVE SESSION BONUS
# ===========================================================================

# +points per consecutive pair (session N attended AND session N+1 attended).
# Resets automatically when SEASON changes - each season processes fresh.
# Minimum attendance threshold: >= 5% (Attendance_Points > 0) required.
CONSECUTIVE_SESSION_BONUS = 5

# ===========================================================================
# VOLUNTEER POINTS
# ===========================================================================

# Column names in kc_volunteer_team.xlsx -> session_activity_tracker sheet
VOLUNTEER_HOSTING_POINTS       = 10   # Session_hosting
VOLUNTEER_BACKEND_POINTS       = 5    # Backend_management
VOLUNTEER_SPEAKER_COORD_POINTS = 5    # Speaker_coordination
VOLUNTEER_LASTMINUTE_POINTS    = 5    # Last-minute issue

VOLUNTEER_ROLE_POINTS = {
    "Session_hosting":      VOLUNTEER_HOSTING_POINTS,
    "Backend_management":   VOLUNTEER_BACKEND_POINTS,
    "Speaker_coordination": VOLUNTEER_SPEAKER_COORD_POINTS,
    "Last-minute issue":    VOLUNTEER_LASTMINUTE_POINTS,
}

# Host attendance - hosts are confirmed 100% present but typically do not
# appear in attendance.xlsx. Award max-band attendance points automatically.
# Skipped if the host already has an attendance row for this session.
VOLUNTEER_HOST_ATTENDANCE_POINTS = 25
