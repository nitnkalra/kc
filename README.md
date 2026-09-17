# KC Leaderboard

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

## Update config.py

Set:

- `KC_ROOT` — absolute path to the kc project root folder on this machine
- `SEASON` — active season sub-folder name (e.g. `"season_5"`)

> `KC_ROOT` only needs updating when moving to a new machine or sharing with someone else.

## Run

```bash
python main.py
```

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

Once all files are in place, run the main script from the `kc/` directory.

```bash
python main.py
```

---

### Step 8 — Verify Outputs

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
| A new employee has joined | `season_5/employee_master.xlsx` |
| Starting a new season | `config.py` → change `SEASON = "season_6"` |
| Changing the visual theme | `config.py` → change `ACTIVE_THEME` |
| Updating scoring rules or points | `config.py` → Scoring Rules section |
| Resizing the leaderboard image | `config.py` → change `LEADERBOARD_WIDTH` |

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
