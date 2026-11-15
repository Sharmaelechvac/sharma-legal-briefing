#!/usr/bin/env python3
"""Build the Sharma Legal Briefing static site from the daily research reports.

Content is taken verbatim from the report.md files in ~/workspace/research_notes/.
No content is summarised away or invented: every story's full text stays on the
page (folded inside a "Read the full story" <details> element), and the decks,
Sharma-impact lines and At-a-Glance bullets are extracted from the reports' own
words (their What-happened / Sharma-impact lines and summary sections).

Usability pass (Sanjay's direction, 2026-11-15 — "photos needed, more user
friendly, just a lot of words"): each edition page opens with an At-a-Glance
box, stories show headline + deck + Sharma-impact line with the full text
folded, a sticky section jump-nav sits under the masthead, and photos pulled
from the cited source articles themselves (see IMAGES) run in newspaper B&W.

Design: classic broadsheet newspaper — paper-white page, black ink, serif
nameplate/headlines, double rules, hairline separations, boxed double-rule
notices for unverified/recycled sections. Keep it that way.

Daily update: add the new report to EDITIONS, optionally add its cited-article
photos to IMAGES (download the cited article's lead image into docs/img/ and
credit the publication), re-run this script, commit and push.
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

# Photos pulled from the cited source articles themselves (Sanjay's direction,
# 2026-11-15: "Pull photos from the articles you are citing"). Keyed by edition
# date, then slot: "lead" = above the lead story; "s1".."s5" = top of that
# numbered section. An edition/slot with no entry renders cleanly with no
# photo. Only verified, downloaded image files from the cited article may be
# added — never a stock substitute, never a publication logo/seal or a generic
# site fallback graphic. Credit always names the source publication.
IMAGES = {
    "2026-11-12": {
        "lead": {
            "file": "2026-11-12-lead-bankruptcy.jpg",
            "caption": "The Bankruptcy Threshold Adjustment Act permanently raises the Subchapter V small-business Chapter 11 debt limit to $7.5 million.",
            "credit": "Image: ArentFox Schiff — from the law-firm alert cited in this edition",
            "alt": "Courthouse columns overlaid with a hundred-dollar bill, from the ArentFox Schiff alert on the bankruptcy threshold law",
        },
        "s2": {
            "file": "2026-11-12-s2-florida-capitol.jpg",
            "caption": "The Florida Capitol in Tallahassee, with case files in the foreground.",
            "credit": "Photo: US News Pulse — from the article cited at §2.1",
            "alt": "The Florida Capitol in Tallahassee",
        },
    },
    "2026-11-13": {
        "s3": {
            "file": "2026-11-13-s3-payroll-fraud.jpg",
            "caption": "Payroll records — a Miami construction owner was charged with workers' comp payroll fraud, reported Nov 13.",
            "credit": "Photo: Insurance Journal — from the article cited at §3.3",
            "alt": "A sticky note reading Payroll Fraud on a stack of payroll documents",
        },
    },
    "2026-11-14": {
        "s1": {
            "file": "2026-11-14-s1-cfpb.jpg",
            "caption": "The Consumer Financial Protection Bureau — the Eleventh Circuit upheld its PACE-loan rule on Fri Nov 13.",
            "credit": "Photo: Bloomberg Law — from the article cited at §1B",
            "alt": "CFPB signage, from the Bloomberg Law report on the PACE-loan ruling",
        },
        "s2": {
            "file": "2026-11-14-s2-avmed.jpg",
            "caption": "From the report on the Third DCA's AvMed decision — no competitive bidding was required for Miami-Dade's self-insured plan administrator.",
            "credit": "Photo: Insurance Business Magazine — from the article cited at §2B",
            "alt": "A boardroom table set with contract documents, from Insurance Business Magazine",
        },
    },
    "2026-11-15": {
        "lead": {
            "file": "2026-11-15-lead-east-potomac.jpg",
            "caption": "Barricades at East Potomac Park in Washington, D.C., whose golf course a federal judge kept from closing — for now.",
            "credit": "Photo: Reuters — via 1049 The Wolf, the report cited at §1.1",
            "alt": "Barricades and a Do Not Enter sign at an entrance to East Potomac Park, Washington, D.C.",
        },
    },
}

URL_RE = re.compile(r"https?://[^\s<>\"'\)\]]+")


def linkify(md_text: str) -> str:
    """Wrap bare URLs in markdown link syntax, trimming trailing sentence punctuation."""
    def repl(m):
        url = m.group(0)
        trail = ""
        while url and url[-1] in ".,;:!?":
            trail = url[-1] + trail
            url = url[:-1]
        return f"[{url}]({url}){trail}"
    return URL_RE.sub(repl, md_text)


def md2html(md_text: str) -> str:
    return markdown.markdown(
        linkify(md_text),
        extensions=["tables", "sane_lists", "fenced_code"],
        output_format="html5",
    )


def inline_md(text: str) -> str:
    """Convert a one-line markdown fragment to inline HTML (no <p> wrapper)."""
    out = markdown.markdown(text, extensions=["sane_lists"], output_format="html5")
    return re.sub(r"^<p>|</p>$", "", out.strip())


def strip_md(text: str) -> str:
    """Plain-text version of a markdown fragment (URLs and markup removed)."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)          # links -> text
    text = re.sub(r"https?://\S+", "", text)                       # bare URLs
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)          # images -> alt
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"\1", text)      # italics
    text = text.replace("`", "")
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = text.replace("|", " ")
    return re.sub(r"\s+", " ", text).strip()


ABBREV = {
    "U.S", "No", "Nos", "Dr", "Mr", "Mrs", "Ms", "St", "vs", "Inc", "Corp",
    "Fla", "D.C", "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep",
    "Sept", "Oct", "Nov", "Dec", "Sen", "Rep", "Gov", "Gen", "e.g", "i.e",
}


def first_sentence(text: str) -> str:
    """First sentence of a plain-text string, abbreviation-aware."""
    text = " ".join(text.split())
    for m in re.finditer(r"[.!?](?=\s+[A-Z\"“(\[])", text):
        before = text[: m.start()].split()
        tok = before[-1].strip('"“”()') if before else ""
        if tok in ABBREV or len(tok) == 1 or re.fullmatch(r"([A-Z]\.)*[A-Z]", tok or " "):
            continue
        return text[: m.start() + 1]
    return text


def split_sentences(text: str):
    out, rest = [], " ".join(text.split())
    while rest:
        s = first_sentence(rest)
        if not s:
            break
        out.append(s)
        rest = rest[len(s):].strip()
        if len(out) > 40:
            break
    return out


def cap_text(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    idx = max(cut.rfind(". "), cut.rfind("; "), cut.rfind(", "))
    if idx > limit * 0.55:
        return cut[: idx + 1]
    idx = cut.rfind(" ")
    return (cut[:idx] if idx > 0 else cut) + "…"


# --------------------------------------------------------------------------
# Report parsing: split into heading chunks, classify sections, fold stories
# --------------------------------------------------------------------------

def split_chunks(text: str):
    chunks = []
    cur = {"level": 0, "title": "", "lines": []}
    for line in text.splitlines():
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            chunks.append(cur)
            cur = {"level": len(m.group(1)), "title": m.group(2).strip(), "lines": []}
        else:
            cur["lines"].append(line)
    chunks.append(cur)
    return [c for c in chunks if c["title"] or any(l.strip() for l in c["lines"])]


def story_section_number(title: str):
    """Return 1-5 for a numbered briefing section, 'detail' for the Nov 14
    lead-story section, or None for front/back matter."""
    t = title.strip()
    if t.lower().startswith("biggest story in detail"):
        return "detail"
    m = re.match(r"^\(?([1-5])\)?\s*[.\)\s—–-]", t)
    return int(m.group(1)) if m else None


NOTICE_KINDS = [
    (re.compile(r"recycled", re.I), "sec-recycled", "Recycled"),
    (re.compile(r"unverified|quarantined", re.I), "sec-unverified", "Unverified"),
    (re.compile(r"could not verify|could-not-verify", re.I), "sec-couldnot", "Could Not Verify"),
]


def chunk_md(chunk) -> str:
    head = ("#" * chunk["level"] + " " + chunk["title"]) if chunk["level"] else ""
    return (head + "\n" if head else "") + "\n".join(chunk["lines"])


def render_raw(chunk, anchors):
    out = md2html(chunk_md(chunk))
    for rx, aid, _label in NOTICE_KINDS:
        if chunk["level"] == 2 and rx.search(chunk["title"]):
            out = out.replace("<h2>", f'<h2 id="{aid}">', 1)
            anchors.add(aid)
            return f'<div class="notice">{out}</div>'
    return out


ITEM_BOLD = re.compile(r"^\*\*\s*(\d+(?:\.\d+)?[A-Z]?)\s*([—–\-:.])\s*(.*?)\*\*\s*(.*)$")
ITEM_BULLET = re.compile(r"^-\s+\*\*([^*]{25,}?)\*\*\s*(.*)$")
LABEL_LINE = re.compile(
    r"^(What happened|Why it matters|Sharma impact|How it|Source|Sources)\b", re.I
)


def split_items(lines):
    """Split a story section's lines into (intro, [(title, body_md)], outro).

    Items begin at a bold numbered lead paragraph (**1.1 — …**) or at a
    top-level bullet with a long bold lead (- **…:** …). A line opening an
    'Explicit statement/negatives' block closes the current item and starts
    the outro, so section-level statements are not buried inside a story.
    """
    intro, items, outro = [], [], []
    cur = None
    mode = "intro"
    for ln in lines:
        s = ln.strip()
        m = ITEM_BOLD.match(s) if s.startswith("**") else None
        mb = ITEM_BULLET.match(s) if s.startswith("- **") else None
        if m and re.search(r"explicit", m.group(3), re.I):
            m = None
            if cur is not None:
                mode = "outro"
        if m:
            title = f"{m.group(1)} {m.group(2)} {m.group(3)}"
            cur = {"title": " ".join(title.split()), "body": [m.group(4)] if m.group(4) else []}
            items.append(cur)
            mode = "item"
            continue
        if mb:
            cur = {"title": " ".join(mb.group(1).split()).rstrip(":"), "body": [mb.group(2)] if mb.group(2) else []}
            items.append(cur)
            mode = "item"
            continue
        if mode == "intro":
            intro.append(ln)
        elif mode == "outro":
            outro.append(ln)
        else:
            cur["body"].append(ln)
    return intro, [(it["title"], "\n".join(it["body"]).strip()) for it in items], outro


WHAT_LABEL = r"What happened[^:]*:"
IMPACT_LABELS = [
    r"Sharma impact\s*(?:—[^:]*)?:",
    r"How it hits Sharma\s*:",
    r"How it could hit Sharma[^:]*:",
    r"Relevance to Sharma[^:]*",
]


def segment_after_label(body_md: str, label_patterns) -> str:
    """Plain text following a labelled line (e.g. '*What happened:* …'),
    including its continuation lines, up to the next labelled bullet."""
    lines = body_md.splitlines()
    for idx, ln in enumerate(lines):
        plain_ln = strip_md(ln)
        for pat in label_patterns:
            m = re.search(pat, plain_ln, re.I)
            if m:
                seg = plain_ln[m.end():].strip()
                j = idx + 1
                while j < len(lines):
                    nxt_raw = lines[j].strip()
                    nxt = strip_md(nxt_raw)
                    if LABEL_LINE.match(nxt) or nxt_raw.startswith("- **") or nxt_raw.startswith("**"):
                        break
                    if nxt:
                        seg += " " + nxt
                    j += 1
                return seg
    return ""


def story_html(title: str, body_md: str) -> str:
    plain = strip_md(body_md)
    head = f'<h3 class="story-head">{inline_md(html.escape(title))}</h3>'
    if len(plain) < 240:
        return f'<div class="story">{head}<div class="story-body">{md2html(body_md)}</div></div>'
    deck_src = segment_after_label(body_md, [WHAT_LABEL]) or plain
    deck = cap_text(first_sentence(deck_src) if deck_src else "", 320)
    impact_src = segment_after_label(body_md, IMPACT_LABELS)
    impact = ""
    if impact_src and len(impact_src) >= 25 and re.match(r"[A-Za-z0-9\"“]", impact_src):
        imp = first_sentence(impact_src)
        if len(imp) < 110:
            rest = impact_src[len(imp):].strip()
            if rest:
                imp = (imp + " " + first_sentence(rest)).strip()
        impact = cap_text(imp, 330)
    parts = [f'<div class="story">{head}']
    if deck:
        parts.append(f'<p class="deck">{html.escape(deck)}</p>')
    if impact:
        parts.append(
            f'<p class="impact"><span class="impact-kick">Sharma impact — </span>{html.escape(impact)}</p>'
        )
    parts.append(
        '<details class="full"><summary>Read the full story</summary>'
        f'<div class="story-body">{md2html(body_md)}</div></details></div>'
    )
    return "".join(parts)


def photo_html(ed, slot, root, cls):
    img = IMAGES.get(ed["date"], {}).get(slot)
    if not img:
        return ""
    return (
        f'<figure class="photo {cls}"><img src="{root}img/{img["file"]}" alt="{html.escape(img["alt"])}">'
        f'<figcaption>{html.escape(img["caption"])}'
        f'<span class="credit">{html.escape(img["credit"])}</span></figcaption></figure>'
    )


def render_story_section(ed, chunk, story_chunks, anchors, root):
    num = story_section_number(chunk["title"])
    banner = inline_md(chunk["title"])
    if isinstance(num, int):
        anchors.add(f"sec-{num}")
        out = [f'<h2 class="sec-banner" id="sec-{num}">{banner}</h2>']
    else:
        out = [f'<h2 class="sec-banner">{banner}</h2>']
    if isinstance(num, int):
        out.append(photo_html(ed, f"s{num}", root, "sec-photo"))
    intro_md = "\n".join(chunk["lines"]).strip()
    if story_chunks:
        if intro_md:
            out.append(md2html(intro_md))
        for sc in story_chunks:
            out.append(story_html(sc["title"], "\n".join(sc["lines"]).strip()))
    else:
        intro, items, outro = split_items(chunk["lines"])
        intro_md = "\n".join(intro).strip()
        if intro_md:
            out.append(md2html(intro_md))
        for title, body in items:
            out.append(story_html(title, body))
        outro_md = "\n".join(outro).strip()
        if outro_md:
            out.append(md2html(outro_md))
    return "".join(out)


def build_article(ed, chunks, root):
    out, anchors = [], set()
    i = 0
    while i < len(chunks):
        c = chunks[i]
        if c["level"] <= 1:
            out.append(render_raw(c, anchors))
            i += 1
            continue
        if c["level"] == 2 and story_section_number(c["title"]) is not None:
            j = i + 1
            stories = []
            while j < len(chunks) and chunks[j]["level"] == 3:
                stories.append(chunks[j])
                j += 1
            out.append(render_story_section(ed, c, stories, anchors, root))
            i = j
            continue
        if c["level"] == 3 and story_section_number(c["title"]) is not None:
            out.append(render_story_section(ed, c, [], anchors, root))
            i += 1
            continue
        out.append(render_raw(c, anchors))
        i += 1
    return "".join(out), anchors


# --------------------------------------------------------------------------
# At a Glance — distilled only from the report's own summary / ranked list
# --------------------------------------------------------------------------

def find_chunk(chunks, level, pat):
    rx = re.compile(pat, re.I)
    for c in chunks:
        if c["level"] == level and rx.search(c["title"]):
            return c
    return None


def glance_for(ed, chunks):
    bullets = [ed["biggest"]]
    deadline = None
    top = find_chunk(chunks, 2, r"top of the briefing")
    summary = find_chunk(chunks, 2, r"^summary")
    if top is not None:
        items = []
        for ln in top["lines"]:
            m = re.match(r"^\d+\.\s+(.*)$", ln.strip())
            if m:
                txt = re.sub(r"\s*→.*$", "", strip_md(m.group(1)))
                items.append(txt)
        bullets += items[1:5]
        for txt in items:
            if re.search(r"deadline", txt, re.I) and re.search(r"\b(Nov|Dec|Jan|Fri|Tue|Thu|Mon|Wed|Sat|Sun)\b", txt):
                deadline = txt
                break
    elif summary is not None and any(ln.strip().startswith("|") for ln in summary["lines"]):
        rows = []
        for ln in summary["lines"]:
            s = ln.strip()
            if s.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", s):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if len(cells) >= 3 and cells[0].isdigit():
                    rows.append(strip_md(cells[1]))
        bullets += rows[1:5]
        for r in rows:
            if re.search(r"deadline", r, re.I):
                deadline = r
                break
    elif summary is not None:
        text = strip_md("\n".join(summary["lines"]))
        sents = split_sentences(text)
        picked = []
        for s in sents[1:]:
            if len(s) >= 80:
                picked.append(cap_text(s, 240))
            if len(picked) == 4:
                break
        bullets += picked
    if deadline is None:
        search_space = []
        if summary is not None:
            search_space.append("\n".join(summary["lines"]))
        for c in chunks:
            if story_section_number(c["title"]) is not None:
                search_space.append(chunk_md(c))
        for blob in search_space:
            for s in split_sentences(strip_md(blob)):
                if re.search(r"deadline", s, re.I) and re.search(
                    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b\.?\s+\d{1,2}", s
                ):
                    deadline = cap_text(s, 260)
                    break
            if deadline:
                break
    return bullets[:5], deadline


def glance_html(bullets, deadline):
    lis = "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
    dl = (
        f'<p class="glance-deadline"><strong>Deadlines — </strong>{html.escape(deadline)}</p>'
        if deadline
        else ""
    )
    return (
        '<aside class="glance"><h2>At a Glance</h2>'
        f"<ul>{lis}</ul>{dl}"
        '<p class="glance-note">One line per story — the full briefing follows, folded under each headline.</p></aside>'
    )


SECTION_LABELS = {
    "sec-1": "§1 Big Legal News",
    "sec-2": "§2 Florida",
    "sec-3": "§3 Business Law",
    "sec-4": "§4 Construction &amp; Contractor Law",
    "sec-5": "§5 Money &amp; Deal Law",
    "sec-recycled": "Recycled",
    "sec-unverified": "Unverified",
    "sec-couldnot": "Could Not Verify",
}


def jumpnav_html(anchors):
    order = ["sec-1", "sec-2", "sec-3", "sec-4", "sec-5", "sec-recycled", "sec-unverified", "sec-couldnot"]
    links = "".join(
        f'<a href="#{a}">{SECTION_LABELS[a]}</a>' for a in order if a in anchors
    )
    if not links:
        return ""
    return f'<nav class="jumpnav"><span class="jump-kick">Jump to</span>{links}</nav>'


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
/* ---------- Photos (newspaper B&W, from the cited articles) ---------- */
.photo{margin:20px auto}
.photo img{width:100%;height:auto;display:block;border:1px solid var(--ink);filter:grayscale(92%) contrast(1.06)}
.photo figcaption{font-style:italic;font-size:.88rem;color:var(--gray);padding-top:6px;text-align:left;line-height:1.45}
.photo .credit{display:block;font-style:normal;font-family:var(--sans);font-size:.7rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin-top:3px}
.lead-photo{max-width:820px}
.sec-photo{max-width:460px;margin:14px 0 6px}
/* ---------- At a Glance ---------- */
.glance{max-width:820px;margin:24px auto 0;border:3px double var(--ink);background:var(--paper2);padding:16px 22px 12px;text-align:left}
.glance h2{font-family:var(--sans);font-size:.82rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;margin:0 0 10px;color:var(--accent)}
.glance ul{margin:0;padding-left:20px}
.glance li{margin:5px 0;line-height:1.5}
.glance-deadline{border-top:1px solid var(--hair2);margin:12px 0 2px;padding-top:9px}
.glance-note{font-style:italic;color:var(--gray);font-size:.9rem;margin:8px 0 4px}
/* ---------- Sticky section jump-nav ---------- */
.jumpnav{position:sticky;top:0;z-index:10;background:var(--paper);border-bottom:3px double var(--ink);margin-top:22px;padding:9px 2px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;justify-content:center}
.jumpnav .jump-kick{font-family:var(--sans);font-size:.74rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--faint);margin-right:4px}
.jumpnav a{font-family:var(--sans);font-size:.8rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;padding:10px 12px;border:1px solid var(--hair2);line-height:1.1}
.jumpnav a:hover{background:var(--paper2);color:var(--accent);text-decoration:underline}
/* ---------- Article ---------- */
article{margin-top:10px}
article h1{font-family:var(--serif);font-weight:800;font-size:clamp(1.45rem,3.6vw,2rem);line-height:1.25;text-align:center;margin:26px 0 6px;padding-bottom:14px;border-bottom:1px solid var(--hair2)}
article h2{margin:42px 0 18px;padding:9px 6px;text-align:center;font-family:var(--body);font-weight:700;font-size:1.08rem;letter-spacing:.14em;text-transform:uppercase;line-height:1.5;
  border-top:3px solid var(--ink);border-bottom:1px solid var(--ink);clear:both}
article h3{margin:30px 0 8px;padding-top:15px;border-top:1px solid var(--hair);font-family:var(--serif);font-weight:700;font-size:1.22rem;line-height:1.35}
article h4{margin:22px 0 6px;font-size:1.02rem;font-style:italic}
article p,article li{color:var(--ink);max-width:68ch}
article strong{color:#000}
article hr{border:none;border-top:1px solid var(--hair2);margin:30px auto;width:55%}
article table{border-collapse:collapse;width:100%;margin:16px 0;font-size:.92rem;display:block;overflow-x:auto;font-family:var(--sans)}
article th,article td{border:1px solid var(--ink);padding:7px 10px;text-align:left;vertical-align:top}
article th{background:var(--paper2)}
article code{background:#efe9d6;padding:1px 5px;font-size:.88em}
article blockquote{margin:18px 10px;padding:2px 18px;border-left:2px solid var(--ink);font-style:italic;color:var(--gray)}
.lead-p::first-letter{font-family:var(--serif);font-weight:900;float:left;font-size:3.4em;line-height:.82;padding:4px 10px 0 0}
.deadline-flag{border-left:2px solid var(--accent);padding-left:10px}
/* ---------- Stories (headline + deck + impact, full text folded) ---------- */
.story{border-top:1px solid var(--hair);padding:18px 0 6px;margin-top:8px}
article h3.story-head{border-top:none;padding-top:0;margin:0 0 6px;font-size:1.3rem;line-height:1.32}
.deck{font-size:1.07rem;font-style:italic;color:#26231c;margin:0 0 9px}
.impact{border-left:3px solid var(--accent);padding-left:12px;margin:0 0 12px}
.impact-kick{font-family:var(--sans);font-size:.74rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}
details.full{margin:2px 0 14px}
details.full summary{cursor:pointer;list-style:none;font-family:var(--sans);font-size:.85rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  padding:13px 16px;border:1px solid var(--ink);background:var(--paper2);min-height:48px}
details.full summary::-webkit-details-marker{display:none}
details.full summary::after{content:' +';color:var(--accent)}
details.full[open] summary::after{content:' –'}
details.full summary:hover{background:#efe8d2}
.story-body{padding:8px 2px 2px}
.story-body p,.story-body li{max-width:68ch}
/* ---------- Boxed notices (unverified / recycled / could-not-verify) ---------- */
.notice{border:3px double var(--ink);background:var(--paper2);padding:4px 24px 20px;margin:36px 0}
.notice h2{border-top:none;border-bottom:1px solid var(--ink);text-align:left;color:var(--accent);margin-top:18px}
/* ---------- Pager ---------- */
.pager{display:flex;flex-wrap:wrap;margin-top:34px;border-top:3px double var(--ink)}
.pager a{flex:1;min-width:200px;text-align:center;padding:12px 8px;color:var(--ink);text-decoration:none;
  font-family:var(--sans);font-size:.82rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase}
.pager a + a{border-left:1px solid var(--hair)}
.pager a:hover{text-decoration:underline;color:var(--accent)}
.backtop{text-align:center;margin-top:26px;font-family:var(--sans);font-size:.82rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase}
.backtop a{text-decoration:none}
.backtop a:hover{text-decoration:underline;color:var(--accent)}
/* ---------- Archive / back issues ---------- */
.backissues{margin-top:8px}
.issue{display:flex;gap:18px;align-items:flex-start;padding:18px 4px 20px;border-bottom:1px solid var(--hair2);color:var(--ink);text-decoration:none}
.issue:first-child{border-top:1px solid var(--ink)}
.issue:hover{text-decoration:none;background:#f3eee0}
.issue:hover .d{text-decoration:underline}
.issue-thumb{width:118px;height:86px;object-fit:cover;flex:none;border:1px solid var(--ink);filter:grayscale(92%) contrast(1.06);margin-top:4px}
.issue-text{flex:1;min-width:0}
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
  .glance{padding:14px 16px 10px}
  .jumpnav{justify-content:flex-start}
  .sec-photo{max-width:100%}
  .issue{flex-direction:column;gap:10px}
  .issue-thumb{width:100%;height:auto;max-height:190px}
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
<div class="wrap" id="top">
<header class="masthead">
<img class="logo" src="{root}logo.png" alt="Sharma Electric &amp; HVAC logo">
<div class="nameplate">The Sharma Legal Briefing</div>
<p class="tagline">Daily legal news for Sharma Electric &amp; HVAC — a Florida electrical &amp; HVAC subcontractor</p>
<div class="dateline"><span>Orlando, Florida</span><span class="dl-c">{html.escape(dateline)}</span><span>Daily Edition</span></div>
<nav class="pagenav"><a href="{root}index.html">Latest Edition</a><a href="{root}archive/index.html">Archive — Back Issues</a></nav>
</header>
{hero}
{body}
<p class="backtop"><a href="#top">↑ Back to top</a></p>
<footer>Sharma Electric &amp; HVAC — daily legal news briefing for the office. General legal information only, not legal advice on a specific job. Every item carries its source link in the briefing text.</footer>
</div>
{JS}
</body>
</html>
"""


def hero_for(ed, latest: bool, glance: str, lead_photo: str, jumpnav: str) -> str:
    tag = "Latest Edition" if latest else "Archive Edition"
    return f"""<section class="frontmatter">
<span class="kick">{tag}</span>
<h1 class="headline">Legal News Briefing — {html.escape(ed['weekday'])}, {html.escape(ed['date'])}</h1>
<p class="coverage">Coverage window: {html.escape(ed['window'])} (Eastern Time) · Prepared for Sharma Electric &amp; HVAC — builder clients, supplier accounts, crews statewide.</p>
<div class="lead"><span class="lead-kick">★ Lead Story</span><p>{html.escape(ed['biggest'])}</p></div>
{lead_photo}
{glance}
<p class="contents">In this edition — §1 Big Legal News &nbsp;·&nbsp; §2 Florida &nbsp;·&nbsp; §3 Business Law &nbsp;·&nbsp; §4 Construction &amp; Contractor Law &nbsp;·&nbsp; §5 Money &amp; Deal Law<br>Each story shows its headline, a one-line deck and the Sharma impact; tap “Read the full story” for the complete text and source links. Unverified and recycled items appear in boxed notices at the end of each edition, as in the source reports.</p>
</section>
{jumpnav}"""


def main():
    (DOCS / "archive").mkdir(parents=True, exist_ok=True)
    parsed = {}
    for ed in EDITIONS:
        src = Path(ed["src"]).expanduser()
        text = src.read_text(encoding="utf-8")
        chunks = split_chunks(text)
        bullets, deadline = glance_for(ed, chunks)
        parsed[ed["date"]] = {
            "chunks": chunks,
            "glance": glance_html(bullets, deadline),
        }

    latest = EDITIONS[-1]
    # Per-day archive pages
    for i, ed in enumerate(EDITIONS):
        article, anchors = build_article(ed, parsed[ed["date"]]["chunks"], "../")
        hero = hero_for(
            ed,
            ed is latest,
            parsed[ed["date"]]["glance"],
            photo_html(ed, "lead", "../", "lead-photo"),
            jumpnav_html(anchors),
        )
        pager = ['<div class="pager"><a href="index.html">← All Editions</a>']
        if i > 0:
            p = EDITIONS[i - 1]
            pager.append(f'<a href="{p["date"]}.html">← {p["weekday"]} {p["date"]}</a>')
        if i < len(EDITIONS) - 1:
            n = EDITIONS[i + 1]
            pager.append(f'<a href="{n["date"]}.html">{n["weekday"]} {n["date"]} →</a>')
        pager.append('<a href="../index.html">Latest Edition →</a></div>')
        body = f"<article>{article}</article>" + "".join(pager)
        out = page(f"{ed['label']} — Legal News Briefing", hero, body, "../", ed["label"])
        (DOCS / "archive" / f"{ed['date']}.html").write_text(out, encoding="utf-8")
        print("wrote archive", ed["date"])

    # Latest = home page (full latest briefing)
    article, anchors = build_article(latest, parsed[latest["date"]]["chunks"], "")
    hero = hero_for(
        latest,
        True,
        parsed[latest["date"]]["glance"],
        photo_html(latest, "lead", "", "lead-photo"),
        jumpnav_html(anchors),
    )
    body = f"<article>{article}</article>"
    body += '<div class="pager"><a href="archive/index.html">Browse the Archive — Every Edition →</a></div>'
    (DOCS / "index.html").write_text(
        page("Latest — Legal News Briefing", hero, body, "", latest["label"]), encoding="utf-8"
    )
    print("wrote index (latest)", latest["date"])

    # Archive index — back-issues list (lead photo as thumbnail where one exists)
    rows = []
    for ed in reversed(EDITIONS):
        img = IMAGES.get(ed["date"], {}).get("lead")
        thumb = (
            f'<img class="issue-thumb" src="../img/{img["file"]}" alt="{html.escape(img["alt"])}">'
            if img
            else ""
        )
        rows.append(f"""<a class="issue" href="{ed['date']}.html">{thumb}<span class="issue-text">
<span class="kick">{html.escape(ed['weekday'])} Edition</span>
<div class="d">{html.escape(ed['label'])}</div>
<p><span class="leadlabel">Lead Story — </span>{html.escape(ed['biggest'])}</p>
<p class="win">Coverage window: {html.escape(ed['window'])} (ET) →</p></span></a>""")
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
