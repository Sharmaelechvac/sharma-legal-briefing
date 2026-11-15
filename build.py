#!/usr/bin/env python3
"""Build the Sharma Legal Briefing static site from the daily research reports.

Content is taken verbatim from the report.md files in ~/workspace/research_notes/.
No content is summarised or invented: markdown is converted to HTML, bare URLs are
linkified, and the reports' own summary sections supply the archive one-liners.
Re-run after adding a new day's report: add an entry to EDITIONS and run this script.

Design: classic broadsheet newspaper (Sanjay's direction, 2026-11-15) — paper-white
page, black ink, serif nameplate/headlines, double rules, hairline separations,
boxed double-rule notices for unverified/recycled sections. Keep it that way.
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


def box_notices(body_html: str) -> str:
    """Wrap unverified / recycled / could-not-verify sections in a boxed notice.

    Newspaper treatment: a double-rule bordered box, applied at build time so the
    served HTML itself carries the distinction. A section runs from its <h2> up to
    the next <h2> (or the end of the article).
    """
    parts = re.split(r"(?=<h2>)", body_html)
    out = []
    for part in parts:
        m = re.match(r"<h2>(.*?)</h2>", part, re.S)
        if m:
            heading_text = re.sub(r"<[^>]+>", "", m.group(1))
            if re.search(r"unverified|recycled|could not verify", heading_text, re.I):
                part = '<div class="notice">' + part + "</div>"
        out.append(part)
    return "".join(out)


def convert(src_path: Path) -> str:
    text = src_path.read_text(encoding="utf-8")
    text = linkify(text)
    body = markdown.markdown(
        text,
        extensions=["tables", "sane_lists", "fenced_code"],
        output_format="html5",
    )
    return box_notices(body)


CSS = """
:root{
  --paper:#faf8f2; --paper2:#f5f0e1; --ink:#111111; --gray:#4a463c; --faint:#6d675a;
  --hair:#cfc7ae; --hair2:#a89f83; --accent:#7a1f1f;
  --serif:'Playfair Display',Georgia,'Times New Roman',Times,serif;
  --body:Georgia,'Times New Roman',Times,serif;
  --sans:Helvetica,Arial,'Segoe UI',sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);line-height:1.6;font-size:16.5px}
a{color:var(--ink);text-decoration:underline;text-underline-offset:2px;word-break:break-word}
a:hover{color:var(--accent)}
.wrap{max-width:980px;margin:0 auto;padding:0 20px 64px}
@media(min-width:1060px){.wrap{border-left:1px solid var(--hair);border-right:1px solid var(--hair)}}
/* ---------- Masthead ---------- */
.masthead{text-align:center;padding:26px 0 0}
.masthead img.logo{height:64px;width:auto}
.nameplate{font-family:var(--serif);font-weight:900;font-size:clamp(2.1rem,6.2vw,3.6rem);line-height:1.05;letter-spacing:.01em;margin:10px 0 4px;color:var(--ink)}
.tagline{font-style:italic;color:var(--gray);font-size:.98rem;margin:0 0 14px}
.dateline{border-top:1px solid var(--ink);border-bottom:3px solid var(--ink);padding:6px 2px;display:flex;gap:10px;align-items:baseline;justify-content:space-between;flex-wrap:wrap;
  font-family:var(--sans);font-size:.78rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
.dateline .dl-c{text-align:center;flex:1}
.dateline a{text-decoration:none}
.dateline a:hover{text-decoration:underline;color:var(--accent)}
.pagenav{border-bottom:1px solid var(--hair2);padding:7px 0;text-align:center;font-family:var(--sans);font-size:.8rem;letter-spacing:.22em;text-transform:uppercase}
.pagenav a{text-decoration:none;margin:0 14px}
.pagenav a:hover{text-decoration:underline;color:var(--accent)}
/* ---------- Front matter (edition header) ---------- */
.frontmatter{margin:26px 0 4px;text-align:center}
.kick{font-family:var(--sans);font-size:.78rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--accent)}
.frontmatter h1.headline{font-family:var(--serif);font-weight:800;font-size:clamp(1.7rem,4.6vw,2.6rem);line-height:1.15;margin:.3em 0 .25em}
.coverage{font-style:italic;color:var(--gray);margin:0 auto;max-width:720px}
.lead{max-width:820px;margin:22px auto 0;text-align:left;border-top:3px solid var(--ink);border-bottom:1px solid var(--ink);padding:14px 4px 16px}
.lead .lead-kick{font-family:var(--sans);font-size:.75rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:6px}
.lead p{font-family:var(--serif);font-size:clamp(1.12rem,2.6vw,1.35rem);line-height:1.45;margin:0}
.contents{margin:18px auto 0;max-width:820px;border-top:1px solid var(--hair2);border-bottom:1px solid var(--hair2);padding:8px 4px;
  font-family:var(--sans);font-size:.8rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gray);text-align:center;line-height:1.9}
/* ---------- Article ---------- */
article{margin-top:10px}
article h1{font-family:var(--serif);font-weight:800;font-size:clamp(1.45rem,3.6vw,2rem);line-height:1.25;text-align:center;margin:26px 0 6px;padding-bottom:14px;border-bottom:1px solid var(--hair2)}
article h2{margin:42px 0 18px;padding:9px 6px;text-align:center;font-family:var(--body);font-weight:700;font-size:1.08rem;letter-spacing:.14em;text-transform:uppercase;line-height:1.5;
  border-top:3px solid var(--ink);border-bottom:1px solid var(--ink)}
article h3{margin:30px 0 8px;padding-top:15px;border-top:1px solid var(--hair);font-family:var(--serif);font-weight:700;font-size:1.22rem;line-height:1.35}
article h4{margin:22px 0 6px;font-size:1.02rem;font-style:italic}
article p,article li{color:var(--ink)}
article strong{color:#000}
article hr{border:none;border-top:1px solid var(--hair2);margin:30px auto;width:55%}
article table{border-collapse:collapse;width:100%;margin:16px 0;font-size:.92rem;display:block;overflow-x:auto;font-family:var(--sans)}
article th,article td{border:1px solid var(--ink);padding:7px 10px;text-align:left;vertical-align:top}
article th{background:var(--paper2)}
article code{background:#efe9d6;padding:1px 5px;font-size:.88em}
article blockquote{margin:18px 10px;padding:2px 18px;border-left:2px solid var(--ink);font-style:italic;color:var(--gray)}
.lead-p::first-letter{font-family:var(--serif);font-weight:900;float:left;font-size:3.4em;line-height:.82;padding:4px 10px 0 0}
.deadline-flag{border-left:2px solid var(--accent);padding-left:10px}
/* ---------- Boxed notices (unverified / recycled / could-not-verify) ---------- */
.notice{border:3px double var(--ink);background:var(--paper2);padding:4px 24px 20px;margin:36px 0}
.notice h2{border-top:none;border-bottom:1px solid var(--ink);text-align:left;color:var(--accent);margin-top:18px}
/* ---------- Pager ---------- */
.pager{display:flex;flex-wrap:wrap;margin-top:34px;border-top:3px double var(--ink)}
.pager a{flex:1;min-width:200px;text-align:center;padding:12px 8px;color:var(--ink);text-decoration:none;
  font-family:var(--sans);font-size:.82rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
.pager a + a{border-left:1px solid var(--hair)}
.pager a:hover{text-decoration:underline;color:var(--accent)}
/* ---------- Archive / back issues ---------- */
.backissues{margin-top:8px}
.issue{display:block;padding:18px 4px 20px;border-bottom:1px solid var(--hair2);color:var(--ink);text-decoration:none}
.issue:first-child{border-top:1px solid var(--ink)}
.issue:hover{text-decoration:none;background:#f3eee0}
.issue:hover .d{text-decoration:underline}
.issue .kick{font-size:.74rem}
.issue .d{font-family:var(--serif);font-weight:800;font-size:1.45rem;line-height:1.25;margin:6px 0 6px}
.issue p{margin:0;color:var(--gray)}
.issue .leadlabel{font-family:var(--sans);font-size:.74rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--accent)}
.issue .win{margin-top:7px;font-style:italic;font-size:.95rem}
footer{border-top:4px double var(--ink);margin-top:38px;padding-top:14px;text-align:center;color:var(--gray);font-size:.9rem;font-style:italic}
@media(max-width:640px){
  .masthead img.logo{height:50px}
  .dateline{justify-content:center;text-align:center}
  .dateline .dl-c{flex-basis:100%;order:3}
  article{font-size:16px}
  .notice{padding:2px 15px 16px}
  .pager a{min-width:150px}
}
"""

JS = """
<script>
// Newspaper touches applied at read time (content itself is untouched):
// a drop cap on the article's first paragraph, and a burgundy rule beside any
// block whose own text states a deadline (the reports carry no separate
// 'Act on it' marker list, so none is invented).
(function(){
  var first = document.querySelector('article p');
  if(first && first.textContent.trim().length > 120){first.classList.add('lead-p');}
  document.querySelectorAll('article li, article p').forEach(function(el){
    if(/deadline/i.test(el.textContent) && el.textContent.length < 900){el.classList.add('deadline-flag');}
  });
})();
</script>
"""


def page(title: str, hero: str, body: str, root: str, dateline: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — The Sharma Legal Briefing</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="masthead">
<img class="logo" src="{root}logo.png" alt="Sharma Electric &amp; HVAC logo">
<div class="nameplate">The Sharma Legal Briefing</div>
<p class="tagline">Daily legal news for Sharma Electric &amp; HVAC — a Florida electrical &amp; HVAC subcontractor</p>
<div class="dateline"><span>Orlando, Florida</span><span class="dl-c">{html.escape(dateline)}</span><span>Daily Edition</span></div>
<nav class="pagenav"><a href="{root}index.html">Latest Edition</a><a href="{root}archive/index.html">Archive — Back Issues</a></nav>
</header>
{hero}
{body}
<footer>Sharma Electric &amp; HVAC — daily legal news briefing for the office. General legal information only, not legal advice on a specific job. Every item carries its source link in the briefing text.</footer>
</div>
{JS}
</body>
</html>
"""


def hero_for(ed, latest: bool) -> str:
    tag = "Latest Edition" if latest else "Archive Edition"
    return f"""<section class="frontmatter">
<span class="kick">{tag}</span>
<h1 class="headline">Legal News Briefing — {html.escape(ed['weekday'])}, {html.escape(ed['date'])}</h1>
<p class="coverage">Coverage window: {html.escape(ed['window'])} (Eastern Time) · Prepared for Sharma Electric &amp; HVAC — builder clients, supplier accounts, crews statewide.</p>
<div class="lead"><span class="lead-kick">★ Lead Story</span><p>{html.escape(ed['biggest'])}</p></div>
<p class="contents">In this edition — §1 Big Legal News &nbsp;·&nbsp; §2 Florida &nbsp;·&nbsp; §3 Business Law &nbsp;·&nbsp; §4 Construction &amp; Contractor Law &nbsp;·&nbsp; §5 Money &amp; Deal Law<br>Blocks ruled in burgundy state a deadline in the report text. Unverified and recycled items appear in boxed notices at the end of each edition, as in the source reports.</p>
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
        pager = ['<div class="pager"><a href="index.html">← All Editions</a>']
        if i > 0:
            p = EDITIONS[i - 1]
            pager.append(f'<a href="{p["date"]}.html">← {p["weekday"]} {p["date"]}</a>')
        if i < len(EDITIONS) - 1:
            n = EDITIONS[i + 1]
            pager.append(f'<a href="{n["date"]}.html">{n["weekday"]} {n["date"]} →</a>')
        pager.append('<a href="../index.html">Latest Edition →</a></div>')
        body = f"<article>{bodies[ed['date']]}</article>" + "".join(pager)
        out = page(f"{ed['label']} — Legal News Briefing", hero_for(ed, ed is latest), body, "../", ed["label"])
        (DOCS / "archive" / f"{ed['date']}.html").write_text(out, encoding="utf-8")
        print("wrote archive", ed["date"])

    # Latest = home page (full Nov 15 briefing)
    body = f"<article>{bodies[latest['date']]}</article>"
    body += '<div class="pager"><a href="archive/index.html">Browse the Archive — Every Edition →</a></div>'
    (DOCS / "index.html").write_text(
        page("Latest — Legal News Briefing", hero_for(latest, True), body, "", latest["label"]), encoding="utf-8"
    )
    print("wrote index (latest)", latest["date"])

    # Archive index — back-issues list
    rows = []
    for ed in reversed(EDITIONS):
        rows.append(f"""<a class="issue" href="{ed['date']}.html">
<span class="kick">{html.escape(ed['weekday'])} Edition</span>
<div class="d">{html.escape(ed['label'])}</div>
<p><span class="leadlabel">Lead Story — </span>{html.escape(ed['biggest'])}</p>
<p class="win">Coverage window: {html.escape(ed['window'])} (ET) →</p></a>""")
    hero = f"""<section class="frontmatter">
<span class="kick">Back Issues</span>
<h1 class="headline">The Archive</h1>
<p class="coverage">Every edition of the daily Sharma legal briefing, kept — {len(EDITIONS)} editions, {EDITIONS[0]['label']} through {EDITIONS[-1]['label']}. New editions are added daily; nothing is overwritten.</p>
</section>"""
    arch_body = '<div class="backissues">' + "".join(rows) + "</div>"
    arch_body += '<div class="pager"><a href="../index.html">← Latest Edition</a></div>'
    (DOCS / "archive" / "index.html").write_text(
        page("Archive — Legal News Briefing", hero, arch_body, "../", "Archive — Back Issues"), encoding="utf-8"
    )
    print("wrote archive index")


if __name__ == "__main__":
    main()
