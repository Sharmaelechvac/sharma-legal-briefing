# Sharma Legal Briefing

Daily legal news briefing for Sharma Electric & HVAC (Florida electrical & HVAC subcontractor), prepared for Harvey · Legal Advisor.

- **Live site:** https://sharmaelechvac.github.io/sharma-legal-briefing/
- **Latest edition:** shown on the home page.
- **Archive:** every edition is kept permanently under `docs/archive/YYYY-MM-DD.html` — new editions are added, never overwritten.

## Daily update

1. Save the new day's researched report as `report.md` in its research-notes folder.
2. Add an entry for the new date to `EDITIONS` in `build.py` (date, weekday, coverage window, biggest-story line taken from that report's own summary).
3. Run the builder (needs python-markdown):
   `python3 -m venv /tmp/mdvenv && /tmp/mdvenv/bin/pip install markdown && /tmp/mdvenv/bin/python build.py`
4. Commit and push to `main`. GitHub Pages serves `docs/` — the new edition becomes the home page and joins the archive automatically.

Content rule: briefing text comes verbatim from the researched reports — nothing is summarised away or invented, every item keeps its source link, and unverified/recycled items stay in their quarantined sections.
