# KC - Knowledge Club

Leaderboard pipeline + public website for Knowledge Club.

```
kc/
├── .github/workflows/deploy.yml   <- builds + deploys the website (main branch only)
├── .gitignore
├── README.md
└── src/
    ├── backend/    <- Python pipeline (scores, reports, website data)  -> see src/backend/README.md
    └── frontend/   <- Astro website (GitHub Pages)                    -> see src/frontend/README.md
```

## Single source of truth

| What | Where (only here) |
| --- | --- |
| KC_ROOT, SEASON, theme | `src/backend/config/settings.py` |
| Point values (pipeline + website) | `src/backend/config/scoring_rules.py` |
| Python package versions | `src/backend/requirements.txt` |
| Node version + website package versions | `src/frontend/package.json` (lock file generated from it) |
| Website static text | `src/frontend/src/data/kc.json` |

## Branch flow

1. Work and run the pipeline on `develop`: `cd src/backend && python main.py` (auto-pushes site data to `develop`).
2. PR `develop -> qa`, merge, check.
3. PR `qa -> main`, merge - GitHub Actions deploys https://nitnkalra.github.io/kc/
