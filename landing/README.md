# Knowledge Club Landing Page

Static site built with **Astro 5 + Tailwind CSS v4 + Chart.js**, deployed to **GitHub Pages** via GitHub Actions.

## Structure
```
public/logo.png            # add the KC logo here
src/data/kc.json           # all content: leaderboard, points, insights (update each season)
src/pages/index.astro      # landing page
src/styles/global.css      # brand theme + animations
.github/workflows/deploy.yml
```

## Run locally
```bash
npm install
npm run dev      # http://localhost:4321/knowledge-club
```

## Deploy
1. Edit `astro.config.mjs`: set `site` to `https://<github-user>.github.io` and `base` to `/<repo-name>` (use `/` for a `<user>.github.io` repo or custom domain).
2. Push to `main`.
3. GitHub repo -> Settings -> Pages -> Source: **GitHub Actions**.

## Updating data
* **Leaderboard:** copy KC output `<season>/outputs/leaderboard.json` to `src/data/leaderboard.json` (same format, no edits). Page shows top 10 by score.
* **Sessions / stats:** add each new session to `sessions` in `src/data/kc.json` (`season` = current season number).
* **New season:** update `season` and `lastSeason` in `kc.json`.
* Commit + push to `main` -> GitHub Actions rebuilds and deploys in ~1-2 min.

`insights` currently holds SAMPLE values; replace with real numbers.
