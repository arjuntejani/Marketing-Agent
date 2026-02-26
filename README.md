# Pomelli-Style Capability Stack (Customizable)

This repository contains a lightweight framework to clone a Google-Pomelli-style capability set and then layer in your own custom capabilities.

## Important: GitHub Pages support

GitHub Pages cannot run Python servers (`scripts/capability_api.py`). It only hosts static files.

So this repo now includes a **static web tool** at `docs/index.html` that performs merge logic in the browser and can be hosted on `github.io`.

## Option A: Run locally (CLI/API)

### CLI

```bash
python3 scripts/capability_tool.py build
python3 scripts/capability_tool.py list --file capabilities/final_capabilities.json
```

### API server (not for GitHub Pages)

```bash
python3 scripts/capability_api.py --host 0.0.0.0 --port 8080
```

## Option B: Host on GitHub Pages (URL)

1. Push this repo to GitHub.
2. Ensure default branch is `main` (or adjust `.github/workflows/pages.yml`).
3. In GitHub: **Settings → Pages** and set Source to **GitHub Actions**.
4. Push to `main` to trigger deployment.
5. Open your site at:

```text
https://<your-username>.github.io/<repo-name>/docs/
```

## What the hosted page does

The page at `docs/index.html` lets you:

- Load `capabilities/base_capabilities.json` and `capabilities/custom_capabilities.json`.
- Merge them using the same rules as the Python merge script.
- Download `final_capabilities.json`.

## Files added for GitHub Pages

- `docs/index.html` (static merge app)
- `.github/workflows/pages.yml` (deploy workflow)
- `.nojekyll` (serve files as-is)
