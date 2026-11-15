#!/usr/bin/env python3
"""Build the Sharma Legal Briefing static site from the daily research reports.

Content is taken verbatim from the report.md files in ~/workspace/research_notes/.
No content is summarised or invented: markdown is converted to HTML, bare URLs are
linkified, and the reports' own summary sections supply the archive one-liners.
Re-run after adding a new day's report: add an entry to EDITIONS and run this script.
"""
import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("python-markdown not available: create a venv and `pip install markdown`")

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

EDITIONS = [
    {
        "date": "2026-11-12",
        "weekday": "Thursday",
        "label": "Thursday, November 12, 2026",
        "window": "Mon Nov 9 – Thu Nov 12, 2026",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-12-20261112-2053/report.md",
        "biggest": "Bankruptcy Threshold Adjustment Act signed Tue Nov 10 — Subchapter V small-business Chapter 11 debt limit permanently raised to $7.5 million.",
    },
    {
        "date": "2026-11-13",
        "weekday": "Friday",
        "label": "Friday, November 13, 2026",
        "window": "Thu Nov 12 – Fri Nov 13, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-13-20261113-2058/report.md",
        "biggest": "U.S. Supreme Court grants review of Trump's border asylum shutdown — Mullin v. RAICES, No. 26-239 (Fri Nov 13).",
    },
    {
        "date": "2026-11-14",
        "weekday": "Saturday",
        "label": "Saturday, November 14, 2026",
        "window": "Fri Nov 13 – Sat Nov 14, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-14-20261114-2101/report.md",
        "biggest": "FAA nationwide ground stop Fri Nov 13; Nov 14 follow-up blames a contractor's copper-to-fiber work at one remote site plus a flooding router.",
    },
    {
        "date": "2026-11-15",
        "weekday": "Sunday",
        "label": "Sunday, November 15, 2026",
        "window": "Sat Nov 14 – Sun Nov 15, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-15-20261115-2109/report.md",
        "biggest": "Judge Ana Reyes (D.D.C.) issues a Saturday Nov 14 TRO halting the East Potomac Park / golf-course closure and redevelopment through Nov 28; President vows an expedited appeal Nov 15.",
    },
]

URL_RE = re.compile(r"https?://[^\s<>\"'\)\]]+")


def linkify(md_text: str) -> str:
    """Wrap bare URLs in markdown link syntax, trimming trailing sentence punctuation."""
    def repl(m):
        url = m.group(0)
        trail = ""
        while url and url[-1] in ".,;:!?":
            trail = url[-1] + trail
            url = url[:-1]
        # balance a trailing ')' that belongs to the URL path (e.g. wiki-style) is rare in
        # these reports; a ')' captured from surrounding prose is stripped by the regex.
        return f"[{url}]({url}){trail}"
    return URL_RE.sub(repl, md_text)


def convert(src_path: Path) -> str:
    text = src_path.read_text(encoding="utf-8")
    text = linkify(text)
    return markdown.markdown(
        text,
        extensions=["tables", "sane_lists", "fenced_code"],
        output_format="html5",
    )


CSS = """
:root{
  --bg:#060b1d; --bg2:#0a1230; --card:rgba(255,255,255,.045); --card-brd:rgba(130,170,255,.18);
  --ink:#e8edfb; --muted:#9fb0d8; --blue:#3b82f6; --violet:#8b5cf6; --cyan:#22d3ee;
  --amber:#f5b544; --red:#fb7185; --grad:linear-gradient(92deg,#38bdf8,#818cf8,#c084fc);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:radial-gradient(1100px 520px at 85% -80px,rgba(99,102,241,.28),transparent 60%),radial-gradient(900px 500px at -10% 240px,rgba(14,165,233,.16),transparent 55%),var(--bg);
  color:var(--ink);font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.65;font-size:16.5px}
a{color:#7dd3fc;text-decoration:none;word-break:break-word}
a:hover{text-decoration:underline}
.wrap{max-width:1060px;margin:0 auto;padding:0 18px 70px}
header.site{position:sticky;top:0;z-index:50;backdrop-filter:blur(14px);background:rgba(6,11,29,.82);border-bottom:1px solid var(--card-brd)}
.nav{max-width:1060px;margin:0 auto;padding:10px 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.nav img.logo{height:52px;width:auto;background:#fff;border-radius:10px;padding:4px 8px}
.brand{font-weight:800;font-size:1.22rem;letter-spacing:.2px}
.brand .grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.nav .sp{flex:1}
.nav a.nl{color:var(--ink);font-weight:600;font-size:.95rem;padding:7px 13px;border:1px solid var(--card-brd);border-radius:999px;background:var(--card)}
.nav a.nl:hover{border-color:#60a5fa;text-decoration:none;box-shadow:0 0 14px rgba(96,165,250,.35)}
.hero{margin:26px 0 8px;padding:28px 26px;border:1px solid var(--card-brd);border-radius:22px;background:linear-gradient(140deg,rgba(59,130,246,.16),rgba(139,92,246,.12) 55%,rgba(34,211,238,.08)),var(--card);box-shadow:0 12px 44px rgba(2,6,23,.55)}
.hero h1{margin:.25em 0 .3em;font-size:clamp(1.65rem,4.4vw,2.5rem);line-height:1.18}
.hero h1 .grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.chip{display:inline-block;padding:3px 12px;border-radius:999px;font-size:.8rem;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#dbeafe;background:rgba(59,130,246,.18);border:1px solid rgba(96,165,250,.45)}
.chip.violet{color:#ede9fe;background:rgba(139,92,246,.18);border-color:rgba(167,139,250,.5)}
.chip.amber{color:#fef3c7;background:rgba(245,181,68,.14);border-color:rgba(245,181,68,.5)}
.biggest{margin-top:14px;padding:16px 18px;border-radius:16px;border:1px solid rgba(245,181,68,.45);background:rgba(245,181,68,.07)}
.biggest b{color:var(--amber)}
article{background:var(--card);border:1px solid var(--card-brd);border-radius:22px;padding:10px 30px 30px;margin-top:22px;box-shadow:0 12px 44px rgba(2,6,23,.45)}
article h1{font-size:1.55rem;line-height:1.3;margin-top:26px}
article h2{margin:38px 0 14px;padding:10px 16px;font-size:1.13rem;line-height:1.4;border-radius:12px;color:#eef2ff;
  background:linear-gradient(92deg,rgba(59,130,246,.30),rgba(139,92,246,.26));border:1px solid rgba(129,140,248,.5);box-shadow:0 0 18px rgba(99,102,241,.18)}
article h2.quarantine{background:linear-gradient(92deg,rgba(244,63,94,.26),rgba(245,181,68,.18));border-color:rgba(251,113,133,.55)}
article h3{margin:30px 0 8px;padding-left:13px;font-size:1.07rem;line-height:1.45;border-left:4px solid #60a5fa}
article h4{margin:22px 0 6px;font-size:1rem;color:#c7d6ff}
article p,article li{color:#dbe3f7}
article strong{color:#fff}
article hr{border:none;border-top:1px solid var(--card-brd);margin:30px 0}
article table{border-collapse:collapse;width:100%;margin:16px 0;font-size:.93rem;display:block;overflow-x:auto}
article th,article td{border:1px solid var(--card-brd);padding:8px 10px;text-align:left;vertical-align:top}
article th{background:rgba(59,130,246,.16)}
article code{background:rgba(148,163,255,.16);padding:1px 6px;border-radius:6px;font-size:.9em}
.deadline-flag{border-left:3px solid var(--amber)!important;padding-left:10px}
.pager{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.pager a{flex:1;min-width:210px;text-align:center;padding:12px;border-radius:14px;border:1px solid var(--card-brd);background:var(--card);color:var(--ink);font-weight:700}
.pager a:hover{border-color:#60a5fa;text-decoration:none;box-shadow:0 0 14px rgba(96,165,250,.3)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px;margin-top:22px}
.card{display:block;padding:20px;border-radius:18px;border:1px solid var(--card-brd);background:var(--card);color:var(--ink)}
.card:hover{text-decoration:none;border-color:#818cf8;box-shadow:0 0 22px rgba(99,102,241,.28)}
.card .d{font-size:1.12rem;font-weight:800;margin:8px 0 6px}
.card p{color:var(--muted);margin:0;font-size:.95rem}
footer{color:var(--muted);font-size:.88rem;margin-top:30px;text-align:center}
.legend{font-size:.9rem;color:var(--muted);margin-top:12px}
@media(max-width:640px){article{padding:6px 17px 24px}.nav img.logo{height:42px}.hero{padding:21px 18px}}
"""

JS = """
<script>
// Quarantine styling: keep unverified / recycled / could-not-verify sections visually
// separate, exactly as the reports separate them. Amber edge: blocks whose own text
// states a deadline (the reports carry no separate 'Act on it' marker list).
document.querySelectorAll('article h2').forEach(function(h){
  if(/unverified|recycled|could not verify/i.test(h.textContent)){h.classList.add('quarantine');}
});
document.querySelectorAll('article li, article p').forEach(function(el){
  if(/deadline/i.test(el.textContent) && el.textContent.length < 900){el.classList.add('deadline-flag');}
});
</script>
"""


def page(title: str, hero: str, body: str, root: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Sharma Legal Briefing</title>
<style>{CSS}</style>
</head>
<body>
<header class="site"><div class="nav">
<img class="logo" src="{root}logo.png" alt="Sharma Electric &amp; HVAC logo">
<span class="brand">Sharma <span class="grad">Legal Briefing</span></span>
<span class="sp"></span>
<a class="nl" href="{root}index.html">Latest</a>
<a class="nl" href="{root}archive/index.html">Archive</a>
</div></header>
<div class="wrap">
{hero}
{body}
<footer>Sharma Electric &amp; HVAC — daily legal news briefing for the office. General legal information only, not legal advice on a specific job. Every item carries its source link in the briefing text.</footer>
</div>
{JS}
</body>
</html>
"""


def hero_for(ed, latest: bool) -> str:
    tag = "Latest edition" if latest else "Archive edition"
    return f"""<section class="hero">
<span class="chip">{tag}</span> <span class="chip violet">{html.escape(ed['label'])}</span>
<h1>Legal News Briefing — <span class="grad">{html.escape(ed['weekday'])}, {html.escape(ed['date'])}</span></h1>
<p style="color:var(--muted);margin:0">Coverage window: {html.escape(ed['window'])} (Eastern Time) · For Sharma Electric &amp; HVAC — Florida electrical &amp; HVAC subcontractor, builder clients, supplier accounts.</p>
<div class="biggest"><b>★ Biggest story:</b> {html.escape(ed['biggest'])}</div>
<p class="legend">Sections: (1) Big legal news · (2) Florida · (3) Business law · (4) Construction &amp; contractor law · (5) Money &amp; deal law. Amber-edged blocks state a deadline in the report text. Unverified and recycled items stay in their own quarantined sections at the end of each edition, as in the source reports.</p>
</section>"""


def main():
    (DOCS / "archive").mkdir(parents=True, exist_ok=True)
    bodies = {}
    for ed in EDITIONS:
        src = Path(ed["src"]).expanduser()
        bodies[ed["date"]] = convert(src)

    latest = EDITIONS[-1]
    # Per-day archive pages
    for i, ed in enumerate(EDITIONS):
        pager = ['<div class="pager"><a href="index.html">← All editions (Archive)</a>']
        if i > 0:
            p = EDITIONS[i - 1]
            pager.append(f'<a href="{p["date"]}.html">← {p["weekday"]} {p["date"]}</a>')
        if i < len(EDITIONS) - 1:
            n = EDITIONS[i + 1]
            pager.append(f'<a href="{n["date"]}.html">{n["weekday"]} {n["date"]} →</a>')
        pager.append('<a href="../index.html">Latest edition →</a></div>')
        body = f"<article>{bodies[ed['date']]}</article>" + "".join(pager)
        out = page(f"{ed['label']} — Legal News Briefing", hero_for(ed, ed is latest), body, "../")
        (DOCS / "archive" / f"{ed['date']}.html").write_text(out, encoding="utf-8")
        print("wrote archive", ed["date"])

    # Latest = home page (full Nov 15 briefing)
    body = f"<article>{bodies[latest['date']]}</article>"
    body += '<div class="pager"><a href="archive/index.html">Browse the archive — every edition →</a></div>'
    (DOCS / "index.html").write_text(
        page("Latest — Legal News Briefing", hero_for(latest, True), body, ""), encoding="utf-8"
    )
    print("wrote index (latest)", latest["date"])

    # Archive index
    cards = []
    for ed in reversed(EDITIONS):
        cards.append(f"""<a class="card" href="{ed['date']}.html">
<span class="chip">{html.escape(ed['weekday'])}</span> <span class="chip violet">{html.escape(ed['date'])}</span>
<div class="d">{html.escape(ed['label'])}</div>
<p><b style="color:#f5b544">★ Biggest story:</b> {html.escape(ed['biggest'])}</p>
<p style="margin-top:8px">Coverage window: {html.escape(ed['window'])} (ET) →</p></a>""")
    hero = f"""<section class="hero">
<span class="chip">Archive</span>
<h1>Every edition, <span class="grad">kept</span></h1>
<p style="color:var(--muted);margin:0">The daily Sharma legal briefing archive — {len(EDITIONS)} editions, {EDITIONS[0]['label']} through {EDITIONS[-1]['label']}. New editions are added daily; nothing is overwritten.</p>
</section>"""
    arch_body = '<div class="cards">' + "".join(cards) + "</div>"
    arch_body += '<div class="pager"><a href="../index.html">← Latest edition</a></div>'
    (DOCS / "archive" / "index.html").write_text(
        page("Archive — Legal News Briefing", hero, arch_body, "../"), encoding="utf-8"
    )
    print("wrote archive index")


if __name__ == "__main__":
    main()
