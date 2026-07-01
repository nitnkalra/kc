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

## Install

```bash
pip install -r requirements.txt
```

## Update config.py

Set:

SEASON_FOLDER

## Run

```bash
python main.py
```

Outputs:

- Leaderboard.xlsx
- Session_History.xlsx
- Session_Summary.xlsx

Location:

Season_5/outputs

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

Fields to fill: session ID, date, topic, and any other required columns.

---

### Step 5 — Update Presenter Details

If a new presenter conducted this session, open `presenter_details.xlsx` inside the active season folder and add their details.

```
season_5/presenter_details.xlsx
```

> Skip this step if the presenter already exists in the file.

---

### Step 6 — Update Volunteer Records

Open `kc_volunteer_team.xlsx` inside the active season folder. Switch to the `session_activity_tracker` sheet and add entries for all volunteers who participated in this session.

```
season_5/kc_volunteer_team.xlsx  →  sheet: session_activity_tracker
```

Volunteer roles and their points:

| Role | Points |
| --- | --- |
| Session hosting | 10 |
| Backend management | 5 |
| Speaker coordination | 5 |
| Last-minute issue handling | 5 |

**Name matching:** Volunteer names in `session_activity_tracker` do not need to be exact or full. Short forms are supported — for example, writing `Nitin` will automatically resolve to `Nitin Kalra` using the email mapping in the `volunteer_details` sheet. Email is always used as the canonical identifier, so as long as the name is recognisable (first name, partial name, or full name), the system will resolve it correctly. If a name is ambiguous or completely unrecognised, a warning will appear in the run log.

> Skip this step if there were no volunteers for this session.

---

### Step 7 — Run the Pipeline

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
