# Static Assets

CSS, JS, images, and fonts for the legacy CityTours/Ansonika theme.

## Current status

Assets have been populated under:

```
static/
  css/      ← 10 stylesheets + slider assets
  js/       ← core scripts (some from Wayback Machine archive)
  img/      ← logos, slides, gallery, backgrounds
  fonts/    ← Font Awesome 4.5
```

Django templates load them via `{% static 'css/...' %}` and `{% static 'js/...' %}`.

## If assets are missing

**Option A — Re-download from live site:**

```bash
pip install requests
python manage.py download_static_assets
```

**Option B — Copy from original PHP project** (if you have the full zip):

```powershell
Copy-Item -Recurse -Force "..\css" ".\static\"
Copy-Item -Recurse -Force "..\js" ".\static\"
Copy-Item -Recurse -Force "..\img" ".\static\"
Copy-Item -Recurse -Force "..\fonts" ".\static\" -ErrorAction SilentlyContinue
```

Then hard-refresh the browser (`Ctrl+F5`).

## Note on JS

The live server (`bluelagoonholidays.net`) serves CSS but returns **404 for `/js/`**. Core scripts were recovered from the [Wayback Machine](https://web.archive.org); slider/map scripts use CDN or minimal stubs.
