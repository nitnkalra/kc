# KC Leaderboard - Backend

Python pipeline: reads the KC Excel files, calculates scores and writes the
leaderboard, reports, charts and the website data (`src/frontend/src/data/`).

All commands below are run from `src/backend/`.

## Folder structure

```
src/backend/
├── main.py              <- run this
├── requirements.txt     <- Python package versions (single source)
├── config/
│   ├── settings.py      <- KC_ROOT, SEASON, ACTIVE_THEME (the only file you normally edit)
│   ├── paths.py         <- all input / output / project paths (derived)
│   ├── scoring_rules.py <- every point value (pipeline + website)
│   ├── data_format.py   <- Excel column / sheet names, bot email
│   ├── theme.py         <- active theme colors
│   ├── themes.py        <- theme palettes
│   ├── graphs.py        <- leaderboard PNG layout + chart size
│   ├── site.py          <- website publishing (auto git push, winners)
│   └── categories.py    <- free-text category -> site category mapping
├── core/                <- processor.py (scoring pipeline), scoring.py, score_timeline.py
├── reports/             <- leaderboard.py (PNG), charts.py (graphs)
├── publish/             <- publish_site.py (website JSON + auto git push)
├── utils/               <- logger.py
├── scripts/             <- one-time scripts (build_participant_history.py)
└── notebooks/           <- analysis, Color Theme Preview
```

## Create venv

```bash
python -m venv venv
```

## Activate

Windows

```bash
venv\Scripts\activate
```

macOS / Linux

```bash
source venv/bin/activate
```

## Install

```bash
pip install -r requirements.txt
```

## Update config/settings.py

Set:

- `KC_ROOT` — absolute path to the KC data folder (season folders + `all_session_details.xlsx`) on this machine
- `SEASON` — active season sub-folder name (e.g. `"season_6"`)

> `KC_ROOT` only needs updating when moving to a new machine or sharing with someone else.

## Run

Always run on the `develop` branch (auto git push only works from `develop`):

```bash
git checkout develop
git pull
cd src/backend
python main.py
```

The run pushes `src/frontend/src/data/*.json` to `develop`. To go live:
merge PR `develop -> qa`, then PR `qa -> main` (GitHub Actions deploys the site).

Outputs saved to `season_5/outputs/`:

- `leaderboard.png`
- `leaderboard.json`
- `Leaderboard.xlsx`
- `Session_Summary.xlsx`
- `Score_Timeline.xlsx`
- `feedback_trend.png`
- `session_count.png`
- `employees_vs_participants.png`
- `employees_vs_participants_monthly.png`
- `participation_rate.png`

---

## Adding a New Session

Follow these steps every time a new Knowledge Club session takes place.

### Step 1 — Create the Session Folder

Inside the active season folder (e.g. `season_5/`), create a new sub-folder named after the session ID.

```
season_5/
└── session_06/
```

---

### Step 2 — Add Attendance Data

Place the attendance file inside the session folder.

```
season_5/session_06/attendance.xlsx
```

> File must follow the same column structure as previous sessions.

---

### Step 3 — Add Feedback Data

Place the feedback file inside the same session folder.

```
season_5/session_06/feedback.xlsx
```

> File must follow the same column structure as previous sessions.

---

### Step 4 — Update Session Details (KC_ROOT level)

Open `all_session_details.xlsx` located at the `KC_ROOT` level (not inside any season folder) and add a new row for this session.

```
KC_ROOT/all_session_details.xlsx
```

Required columns to fill for each session:

| Column | Description |
| --- | --- |
| `Season` | Active season (e.g. `season_5`) |
| `Session_ID` | Must match the session folder name (e.g. `session_06`) |
| `Name` | Presenter's display name |
| `Email` | **Presenter's email — must match `employee_master.xlsx`** |
| `Topic` | Session topic |
| `Session_Type` | Type of session (e.g. `presentation`, `decode`) |

> **Email is mandatory.** Presenter detection and score assignment are email-based. A missing or mismatched email will cause the presenter to be treated as a regular attendee and result in incorrect scores.

> **Date & Time are auto-derived.** The system calculates session date, start time, and end time from the KC bot (`knowledge_club@inxiteout.ai`) join/leave timestamps in `attendance.xlsx`.

---

### Step 5 — Update Volunteer Records

Open `kc_volunteer_team.xlsx` inside the active season folder. Switch to the `session_activity_tracker` sheet and add entries for all volunteers who participated in this session.

```
season_5/kc_volunteer_team.xlsx  →  sheet: session_activity_tracker
```

Volunteer roles and their points:

| Role | Points |
| --- | --- |
| Session hosting | 10 + 25 (attendance) = **35 total** |
| Backend management | 5 |
| Speaker coordination | 5 |
| Last-minute issue handling | 5 |

> **Session hosting includes automatic attendance points.** Hosts are confirmed 100% present but do not appear in `attendance.xlsx`. The system awards +25 attendance points (max band) automatically via the volunteer file. If the host happens to be in the attendance file too, the attendance points are skipped to avoid double-counting.

**Name matching:** Volunteer names in `session_activity_tracker` do not need to be exact or full. Short forms are supported — for example, writing `Nitin` will automatically resolve to `Nitin Kalra` using the email mapping in the `volunteer_details` sheet. Email is always used as the canonical identifier, so as long as the name is recognisable (first name, partial name, or full name), the system will resolve it correctly. If a name is ambiguous or completely unrecognised, a warning will appear in the run log.

> Skip this step if there were no volunteers for this session.

---

### Step 6 — Run the Pipeline

Once all files are in place, run the main script from `src/backend/` (on the `develop` branch).

```bash
cd src/backend
python main.py
```

---

### Step 7 — Verify Outputs

Check the `outputs/` folder inside the active season for updated files.

```
season_5/outputs/
├── leaderboard.png                        ← updated leaderboard image
├── leaderboard.json                       ← raw leaderboard data
├── Leaderboard.xlsx                       ← leaderboard in Excel
├── Session_Summary.xlsx                   ← per-session summary + feedback insights
├── Score_Timeline.xlsx                    ← score history across sessions
├── feedback_trend.png
├── session_count.png
├── employees_vs_participants.png
├── employees_vs_participants_monthly.png
└── participation_rate.png
```

---

### Optional Updates (only when needed)

| Situation | File to Update |
| --- | --- |
| A new employee has joined | `<season>/employee_master.xlsx` |
| Starting a new season | `config/settings.py` → change `SEASON = "season_7"` |
| Changing the visual theme | `config/settings.py` → change `ACTIVE_THEME` |
| Updating scoring rules or points | `config/scoring_rules.py` (website updates automatically on next run) |
| Resizing the leaderboard image | `config/graphs.py` → change `LEADERBOARD_WIDTH` |
| Excel column / sheet name changed | `config/data_format.py` |
| New free-text category on the site | `config/categories.py` |
| Upgrading a Python package | `requirements.txt` (only place) |

---

## Scoring Rules Reference

| Activity | Points |
| --- | --- |
| Attended 90–100% of session | 25 |
| Attended 75–89% of session | 20 |
| Attended 50–74% of session | 15 |
| Attended 25–49% of session | 10 |
| Attended 5–24% of session | 5 |
| Attended < 5% of session | 0 |
| Submitted feedback form | 25 |
| Presented a session | 100 (flat) |
| Consecutive session bonus (per pair) | +5 |
| Volunteer — Session hosting | 10 + 25 (attendance) = **35** |
| Volunteer — Backend management | 5 |
| Volunteer — Speaker coordination | 5 |
| Volunteer — Last-minute issue | 5 |

**Notes:**

- Attendance % is calculated against the ideal session window (start + 3 min grace → end − 5 min grace). Start/end are auto-derived from the KC bot’s join/leave timestamps in `attendance.xlsx`.
- Consecutive bonus requires **≥ 5% attendance** in both sessions of the pair. Joining briefly (< 5%) does not count toward a streak.
- Presenters receive **100 pts flat**. Attendance points and feedback points are not applicable to presenters.
- Volunteer points stack — a volunteer who hosts AND manages backend in the same session earns 35 + 5 = 40 pts.
- **Session hosts** receive **+25 attendance points** automatically (confirmed 100% present). This is skipped if the host already appears in `attendance.xlsx` for that session. Hosts also qualify for the consecutive session bonus.
