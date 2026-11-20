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
folded, a sticky section jump-nav sits under the header, and photos pulled
from the cited source articles themselves (see IMAGES) run full color.

Design (Sanjay, 2026-11-15 — "words way too small, need a hot modern look";
supersedes the broadsheet newspaper template): the standing Sharma design
system in ~/workspace/DESIGN-RULES.md — navy #264387 / dark navy #1a2f61 /
gold #F0A846 on page #f4f6fb, kit display headings, Inter body
at 18px, IBM Plex Mono for numbers/dates, real logo on a white header with a
3px gold line under it, flat white panels, full-color photos, plain section
headings ("Not confirmed", "Older stories going around again", "Could not
check"). No gradients, shadows, pills, emoji icons or newspaper costume.

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
    {
        "date": "2026-11-16",
        "weekday": "Monday",
        "label": "Monday, November 16, 2026",
        "window": "Sun Nov 15 – Mon Nov 16, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-16-20261116-1000/report.md",
        "biggest": "DOJ warns Sen. Elizabeth Warren on Sunday, Nov 15 to preserve records over her planned Trump investigations, citing \"significant legal consequences\" — U.S. Attorney Aaron Reitz's letter is the latest in a series to Democrats.",
    },
    {
        "date": "2026-11-17",
        "weekday": "Tuesday",
        "label": "Tuesday, November 17, 2026",
        "window": "Mon Nov 16 – Tue Nov 17, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-17-20261117-0959/report.md",
        "biggest": "California sues OpenAI on Mon Nov 16 over rogue AI-agent cyberattacks \u2014 AG Bonta says OpenAI lost control of its agents more than 80 times in testing, including the July Hugging Face breach.",
    },
    {
        "date": "2026-11-18",
        "weekday": "Wednesday",
        "label": "Wednesday, November 18, 2026",
        "window": "Tue Nov 17 \u2013 Wed Nov 18, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-18-20261118-0502/report.md",
        "biggest": "Oregon sues OpenAI on Tue Nov 17 over ChatGPT child safety \u2014 AG Rayfield seeks at least $2.035 billion, alleging the chatbot was marketed as safe for kids while exposing them to harmful content.",
    },
    {
        "date": "2026-11-19",
        "weekday": "Thursday",
        "label": "Thursday, November 19, 2026",
        "window": "Wed Nov 18 \u2013 Thu Nov 19, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-19-20261119-0959/report.md",
        "biggest": "Senate clears the BAAJA permitting bill's last 60-vote hurdle on Wed Nov 18 \u2014 budget waiver 70\u201326, Capito substitute adopted 69\u201327, final cloture 65\u201331 \u2014 with the passage vote still pending at the cutoff.",
    },
    {
        "date": "2026-11-20",
        "weekday": "Friday",
        "label": "Friday, November 20, 2026",
        "window": "Thu Nov 19 \u2013 Fri Nov 20, 2026 (core)",
        "src": "~/workspace/research_notes/sharma-legal-news-briefing-2026-11-20-20261120-0500/report.md",
        "biggest": "Senate passes the BAAJA permitting bill 62\u201333 on Thu Nov 19 and sends it to the House \u2014 plus DOL's final independent-contractor rule, the GSA/DHS E-Verify sweep (responses due Dec 16), Florida's record 20th execution (Overton), and the OSHA HazCom substances deadline today.",
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
    "2026-11-16": {
        "lead": {
            "file": "2026-11-16-lead-doj.jpg",
            "caption": "The Department of Justice headquarters sign in Washington — the Justice Department warned Sen. Elizabeth Warren on Sunday to preserve records over her planned investigations.",
            "credit": "Photo: Reuters — from the report cited at §1.1",
            "alt": "Department of Justice headquarters sign, Washington, D.C., from the Reuters report on the Warren preservation letter",
        },
    },
    "2026-11-17": {
        "lead": {
            "file": "2026-11-17-lead-openai.jpg",
            "caption": "California Attorney General Rob Bonta sued OpenAI on Monday, Nov 16, accusing it of testing AI models without the safeguards needed to keep its autonomous agents from attacking outside systems.",
            "credit": "Photo: Engadget \u2014 from the article cited at \u00a71.1",
            "alt": "Lead image from the Engadget report on California's lawsuit against OpenAI over the Hugging Face rogue-agent incident",
        },
        "s5": {
            "file": "2026-11-17-s5-visa.jpg",
            "caption": "Visa and Mastercard asked a Brooklyn judge on Monday, Nov 16 for final approval of their $38 billion swipe-fee settlement; he did not rule.",
            "credit": "Photo: PYMNTS \u2014 from the article cited at \u00a75.1",
            "alt": "Credit cards, from the PYMNTS report on the Visa and Mastercard swipe-fee settlement hearing",
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
    "2026-11-18": {
        "lead": {
            "file": "2026-11-18-lead-openai.jpg",
            "caption": "The OpenAI logo on a smartphone — Oregon Attorney General Dan Rayfield sued OpenAI on Tuesday, Nov 17, alleging ChatGPT endangers children and was misrepresented as safe for them, seeking at least $2.035 billion.",
            "credit": "Photo: Evolf/Shutterstock via Engadget — from the article cited at §1.1",
            "alt": "The OpenAI logo on a smartphone, from the Engadget report on Oregon's lawsuit against OpenAI",
        },
    },
    "2026-11-20": {
        "s3": {
            "file": "2026-11-20-s3-dol.jpg",
            "caption": "Labor Secretary Keith Sonderling — the Department of Labor announced its final independent-contractor rule on Thursday, Nov 19, restoring a control-and-profit/loss test.",
            "credit": "Photo: Win McNamee via Getty Images \u2014 from the HR Dive article cited at \u00a73.1",
            "alt": "Secretary of Labor Keith Sonderling, from the HR Dive report on the Department of Labor's independent-contractor final rule",
        },
    },
    "2026-11-19": {
        "lead": {
            "file": "2026-11-19-lead-baaja.jpg",
            "caption": "The U.S. Capitol at dusk \u2014 the Senate on Wednesday, Nov 18 cleared the BAAJA permitting bill's last 60-vote hurdle (final cloture 65\u201331), leaving only a simple-majority passage vote, which had not occurred by the cutoff.",
            "credit": "Photo: Heatmap News \u2014 from the article cited at \u00a71.1",
            "alt": "The U.S. Capitol dome at dusk with lit windows, from the Heatmap News report on the Senate's permitting-bill votes",
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
    (re.compile(r"recycled", re.I), "sec-recycled", "Older stories going around again"),
    (re.compile(r"unverified|quarantined", re.I), "sec-unverified", "Not confirmed"),
    (re.compile(r"could not verify|could-not-verify", re.I), "sec-couldnot", "Could not check"),
]


def chunk_md(chunk) -> str:
    head = ("#" * chunk["level"] + " " + chunk["title"]) if chunk["level"] else ""
    return (head + "\n" if head else "") + "\n".join(chunk["lines"])


def render_raw(chunk, anchors):
    out = md2html(chunk_md(chunk))
    for rx, aid, label in NOTICE_KINDS:
        if chunk["level"] == 2 and rx.search(chunk["title"]):
            # Plain heading per the design rules; items and in-text flags unchanged.
            out = re.sub(r"<h2>.*?</h2>", f'<h2 id="{aid}">{label}</h2>', out, count=1, flags=re.S)
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
    "sec-recycled": "Older stories going around again",
    "sec-unverified": "Not confirmed",
    "sec-couldnot": "Could not check",
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
  --navy:#264387; --darknavy:#1a2f61; --gold:#F0A846; --ink:#1d2433;
  --gray:#5b6478; --line:#dfe4ee; --page:#f4f6fb; --panel:#ffffff;
  --head:-apple-system,'SF Pro Display',Inter,'Segoe UI',sans-serif;
  --body:-apple-system,'SF Pro Text',Inter,'Segoe UI',sans-serif;
  --mono:ui-monospace,'SF Mono',Consolas,'Courier New',monospace;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--page);color:var(--ink);font-family:var(--body);font-size:18px;line-height:1.65}
a{color:var(--navy);text-decoration:underline;text-underline-offset:2px;word-break:break-word}
a:hover{color:var(--darknavy)}
.wrap{max-width:1020px;margin:0 auto;padding:0 16px 64px}
/* ---------- Site header: white, real logo, gold line under ---------- */
.sitehead{background:var(--panel);border:1px solid var(--line);border-top:none;border-radius:0 0 5px 5px;border-bottom:3px solid var(--gold);padding:22px 26px 0;margin-bottom:22px}
.sitehead .brand{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.sitehead img.logo{height:56px;width:auto;flex:none}
.sitetitle{font-family:var(--head);font-weight:700;font-size:36px;line-height:1.05;color:var(--darknavy);letter-spacing:.01em}
.tagline{color:var(--gray);font-size:16px;margin:8px 0 0}
.meta{font-family:var(--mono);font-size:14px;color:var(--gray);margin-top:10px;display:flex;gap:8px;flex-wrap:wrap}
.pagenav{display:flex;flex-wrap:wrap;gap:4px 26px;margin-top:14px;border-top:1px solid var(--line)}
.pagenav a{font-family:var(--head);font-weight:700;font-size:18px;letter-spacing:.03em;color:var(--navy);text-decoration:none;padding:12px 2px;min-height:48px;display:inline-flex;align-items:center}
.pagenav a:hover{color:var(--darknavy);text-decoration:underline}
.pagenav a.active{color:var(--darknavy);box-shadow:inset 0 -3px 0 var(--gold)}
/* ---------- Front matter (edition header) ---------- */
.frontmatter{background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:26px 28px 24px;margin:0 0 20px;text-align:left}
.kick{font-family:var(--head);font-size:16px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--navy)}
.frontmatter h1.headline{font-family:var(--head);font-weight:700;font-size:clamp(34px,5.4vw,54px);line-height:1.08;color:var(--darknavy);margin:.22em 0 .3em}
.coverage{color:var(--gray);margin:0;max-width:760px;font-size:17px}
.lead{margin:22px 0 0;text-align:left;background:var(--panel);border:1px solid var(--line);border-left:5px solid var(--gold);border-radius:5px;padding:16px 20px 18px}
.lead .lead-kick{font-family:var(--head);font-size:16px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--navy);display:block;margin-bottom:6px}
.lead p{font-size:21px;line-height:1.5;margin:0;font-weight:500}
.contents{margin:18px 0 0;border-top:1px solid var(--line);padding-top:12px;font-size:16px;color:var(--gray);line-height:1.7}
/* ---------- Photos (full color, from the cited articles) ---------- */
.photo{margin:20px auto}
.photo img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:5px}
.photo figcaption{font-size:15px;color:var(--gray);padding-top:7px;text-align:left;line-height:1.5}
.photo .credit{display:block;font-family:var(--mono);font-size:13px;color:var(--gray);margin-top:3px}
.lead-photo{max-width:860px}
.sec-photo{max-width:520px;margin:16px 0 8px}
/* ---------- At a Glance ---------- */
.glance{max-width:860px;margin:22px auto 0;background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:18px 24px 14px;text-align:left}
.glance h2{font-family:var(--head);font-size:24px;font-weight:700;color:var(--darknavy);margin:0 0 10px;padding-bottom:8px;border-bottom:3px solid var(--gold)}
.glance ul{margin:0;padding-left:22px}
.glance li{margin:6px 0;line-height:1.55}
.glance-deadline{border-top:1px solid var(--line);margin:12px 0 2px;padding-top:10px}
.glance-note{color:var(--gray);font-size:15px;margin:8px 0 4px}
/* ---------- Sticky section jump-nav ---------- */
.jumpnav{position:sticky;top:0;z-index:10;background:var(--panel);border:1px solid var(--line);border-radius:5px;margin:0 0 20px;padding:8px 10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.jumpnav .jump-kick{font-family:var(--head);font-size:15px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--gray);margin:0 6px 0 4px}
.jumpnav a{font-family:var(--head);font-size:17px;font-weight:700;color:var(--navy);text-decoration:none;padding:10px 12px;min-height:48px;display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:5px;line-height:1.15}
.jumpnav a:hover{background:var(--page);color:var(--darknavy);text-decoration:underline}
/* ---------- Article ---------- */
article{background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:8px 30px 30px;margin-top:0}
article h1{font-family:var(--head);font-weight:700;font-size:32px;line-height:1.2;color:var(--darknavy);margin:26px 0 10px;padding-bottom:10px;border-bottom:3px solid var(--gold)}
article h2{margin:44px 0 18px;padding-bottom:8px;font-family:var(--head);font-weight:700;font-size:clamp(28px,4vw,32px);line-height:1.2;color:var(--darknavy);border-bottom:3px solid var(--gold);clear:both}
article h3{margin:30px 0 8px;padding-top:16px;border-top:1px solid var(--line);font-family:var(--head);font-weight:700;font-size:25px;line-height:1.25;color:var(--ink)}
article h4{margin:22px 0 6px;font-size:19px;font-weight:600}
article p,article li{color:var(--ink);max-width:68ch}
article strong{color:var(--darknavy)}
article hr{border:none;border-top:1px solid var(--line);margin:30px auto;width:55%}
article table{border-collapse:collapse;width:100%;margin:16px 0;font-size:16px;display:block;overflow-x:auto}
article th,article td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
article th{background:var(--page);font-family:var(--head);font-size:17px;color:var(--darknavy)}
article code{background:var(--page);padding:1px 5px;font-family:var(--mono);font-size:.9em}
article blockquote{margin:18px 10px;padding:2px 18px;border-left:3px solid var(--gold);color:var(--gray)}
.deadline-flag{border-left:3px solid var(--gold);padding-left:10px}
/* ---------- Stories (headline + deck + impact, full text folded) ---------- */
.story{border-top:1px solid var(--line);padding:20px 0 8px;margin-top:10px}
article h3.story-head{border-top:none;padding-top:0;margin:0 0 8px;font-size:clamp(24px,3.4vw,28px);line-height:1.22;color:var(--darknavy)}
.deck{font-size:20px;line-height:1.55;color:var(--ink);margin:0 0 10px;max-width:68ch}
.impact{border-left:3px solid var(--gold);background:var(--page);border-radius:0 5px 5px 0;padding:10px 14px;margin:0 0 14px;max-width:68ch}
.impact-kick{font-family:var(--head);font-size:15px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--navy)}
details.full{margin:2px 0 16px}
details.full summary{cursor:pointer;list-style:none;font-family:var(--head);font-size:18px;font-weight:700;letter-spacing:.04em;color:var(--navy);
  padding:12px 16px;border:1px solid var(--line);border-radius:5px;background:var(--panel);min-height:48px}
details.full summary::-webkit-details-marker{display:none}
details.full summary::after{content:' +';color:var(--gold)}
details.full[open] summary::after{content:' –'}
details.full summary:hover{background:var(--page)}
.story-body{padding:10px 2px 2px}
.story-body p,.story-body li{max-width:68ch}
/* ---------- Notice panels (not confirmed / older stories / could not check) ---------- */
.notice{border:1px solid var(--line);border-left:5px solid var(--navy);border-radius:5px;background:var(--panel);padding:6px 26px 22px;margin:30px 0}
.notice h2{border-bottom:3px solid var(--gold);color:var(--darknavy);margin-top:20px}
/* ---------- Pager ---------- */
.pager{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.pager a{flex:1;min-width:200px;text-align:center;padding:12px 10px;min-height:48px;display:inline-flex;align-items:center;justify-content:center;
  background:var(--panel);border:1px solid var(--line);border-radius:5px;color:var(--navy);text-decoration:none;
  font-family:var(--head);font-size:18px;font-weight:700;letter-spacing:.03em}
.pager a:hover{color:var(--darknavy);text-decoration:underline;background:var(--page)}
.backtop{text-align:center;margin-top:26px;font-family:var(--head);font-size:17px;font-weight:700;letter-spacing:.05em}
.backtop a{text-decoration:none}
.backtop a:hover{text-decoration:underline}
/* ---------- Archive / back issues ---------- */
.backissues{margin-top:0;display:flex;flex-direction:column;gap:14px}
.issue{display:flex;gap:18px;align-items:flex-start;padding:18px 20px;background:var(--panel);border:1px solid var(--line);border-radius:5px;color:var(--ink);text-decoration:none}
.issue:hover{text-decoration:none;background:var(--page)}
.issue:hover .d{text-decoration:underline}
.issue-thumb{width:150px;height:104px;object-fit:cover;flex:none;border:1px solid var(--line);border-radius:5px;margin-top:4px}
.issue-text{flex:1;min-width:0}
.issue .kick{font-size:15px}
.issue .d{font-family:var(--head);font-weight:700;font-size:27px;line-height:1.2;color:var(--darknavy);margin:5px 0 6px}
.issue p{margin:0;color:var(--gray);font-size:17px}
.issue .leadlabel{font-family:var(--head);font-size:15px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--navy)}
.issue .win{margin-top:7px;font-size:16px}
footer{border-top:1px solid var(--line);margin-top:34px;padding-top:14px;text-align:center;color:var(--gray);font-size:15px}
@media(max-width:640px){
  body{font-size:18px}
  .wrap{padding:0 10px 48px}
  .sitehead{padding:16px 16px 0}
  .sitehead img.logo{height:44px}
  .sitetitle{font-size:27px}
  .frontmatter{padding:20px 18px}
  article{padding:6px 16px 22px}
  .notice{padding:4px 16px 18px}
  .pager a{min-width:150px}
  .glance{padding:14px 16px 10px}
  .jumpnav{justify-content:flex-start}
  .sec-photo{max-width:100%}
  .issue{flex-direction:column;gap:10px}
  .issue-thumb{width:100%;height:auto;max-height:200px}
}

/* ---------- NYT LOOK (Sanjay 2026-11-20: "Still blocky — mimic NYT") —
   Replaces the Home News v3 card look. New York Times style: flat white
   paper, black serif headlines (Georgia), hairline rules instead of
   cards/shadows/rounded corners, small sans kickers. Content unchanged. --- */
body{background:#fff;color:#121212}
.sitehead{background:#fff;border:none;border-bottom:1px solid #121212;border-radius:0;
box-shadow:none;padding-top:18px;margin-top:0}
.sitetitle{font-family:Georgia,"Times New Roman",Times,serif;color:#121212}
.kick,.lead-kick,.impact-kick,.jump-kick{display:inline-block;background:none;color:#121212;
border-radius:0;padding:0;font-size:12px;font-weight:700;letter-spacing:.08em;
text-transform:uppercase;box-shadow:none}
.frontmatter{background:#fff;border:none;border-bottom:1px solid #DFDFDD;border-radius:0;
box-shadow:none;padding:20px 0 18px}
.frontmatter h1.headline{font-family:Georgia,"Times New Roman",Times,serif;color:#121212}
.lead{background:#fff;color:#121212;border:none;border-left:2px solid #121212;border-radius:0;
box-shadow:none;padding:4px 0 4px 16px}
.lead p{color:#121212;font-family:Georgia,"Times New Roman",Times,serif;font-size:21px}
.lead .lead-kick{background:none;color:#121212}
.photo img{border:none;border-radius:0;box-shadow:none}
.photo figcaption{color:#727272}
.glance{background:#fff;border:none;border-top:2px solid #121212;border-bottom:1px solid #DFDFDD;
border-radius:0;box-shadow:none;padding:14px 0 8px}
.glance h2{font-family:-apple-system,"SF Pro Text",Inter,Arial,sans-serif;font-size:14px;
text-transform:uppercase;letter-spacing:.08em;color:#121212;border-bottom:none}
.glance h2::after{display:none}
.jumpnav{background:#fff;border:none;border-bottom:1px solid #DFDFDD;border-radius:0;
box-shadow:none;padding:6px 0}
.jumpnav a{background:none;border:none;border-radius:0;box-shadow:none;min-height:44px;color:#121212}
article{background:#fff;border:none;border-radius:0;box-shadow:none}
article h1,article h2,article h3{font-family:Georgia,"Times New Roman",Times,serif;color:#121212}
article h2{border-bottom:1px solid #121212}
article h2::after{display:none}
article strong{color:#121212}
.story{background:#fff;border-top:1px solid #DFDFDD;border-radius:0;padding:20px 0 8px;margin-top:10px}
.impact{background:#F7F7F5;border-left:2px solid #121212;border-radius:0}
.impact-kick{background:none;color:#121212}
.issue{background:#fff;border-radius:0;box-shadow:none}
.issue-thumb{border-radius:0}
a{color:#121212}
html[data-scheme="dark"] .frontmatter,html[data-scheme="dark"] .glance,
html[data-scheme="dark"] article,html[data-scheme="dark"] .sitehead{background:#fff}
html[data-scheme="dark"] .story{background:#fff}
/* ---------- NYT FRONT PAGE STRUCTURE (Sanjay 2026-11-20: "Copy the real
   NYT front page layout exactly") — blackletter masthead with double rule,
   lead story centered in a wide middle column, secondary stories in ruled
   side rails, glance and archives flowing in newspaper columns. Hub-only
   grid uses :has(> .front) so edition/story pages keep the article layout. */
.masthead{text-align:center;padding:20px 0 12px;border-bottom:4px double #121212;margin-bottom:6px}
.mast-name{font-family:"UnifrakturMaguntia",Georgia,"Times New Roman",serif;
font-size:68px;line-height:1;color:#121212}
.mast-tag{font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#555;margin-top:8px}
@media(max-width:760px){.mast-name{font-size:44px}}
nav.main{border-top:1px solid #DFDFDD}
nav.main .in{justify-content:center}
.wrap:has(> .front){display:grid;grid-template-columns:1fr 2.1fr 1.15fr;
grid-template-areas:"head head head" "left center right" "left center right2"
"glance glance glance";column-gap:0}
.wrap:has(> .front) > .masthead{grid-area:head}
.wrap:has(> .front) > .front{display:contents}
.wrap:has(> .front) > .glance{grid-area:glance}
.wrap:has(> .front) > h2.sec,.wrap:has(> .front) > .arch{grid-column:1 / -1}
.nyt-lead{grid-area:center;padding:2px 22px 0 !important;border:none !important;
display:flex !important;flex-direction:column;text-align:center}
.nyt-lead .kicker{align-self:center}
.nyt-lead .headline{order:1;font-size:44px !important;line-height:1.08 !important;margin:12px 0 10px}
.nyt-lead .byline{order:2}
.nyt-lead .photolink{order:3;margin-top:12px}
.nyt-lead .photo figcaption{text-align:left}
.nyt-lead .cont{order:4;align-self:center}
.wrap:has(> .front) > .front .story:not(.nyt-lead){grid-area:left;
padding-right:18px !important;border-right:1px solid #DFDFDD}
.wrap:has(> .front) > .front .story:not(.nyt-lead) .headline{font-size:23px;line-height:1.22}
.wrap:has(> .front) > .techfeature{grid-area:right;display:block;
padding-left:18px;border-left:1px solid #DFDFDD;border-bottom:none}
.wrap:has(> .front) > .techfeature .headline{font-size:20px;line-height:1.25}
.wrap:has(> .front) > .techfeature.nophoto{grid-area:right2}
@media(max-width:860px){
.wrap:has(> .front){grid-template-columns:1fr;
grid-template-areas:"head" "center" "left" "right" "right2" "glance"}
.nyt-lead{padding:0 !important}
.nyt-lead .headline{font-size:33px !important}
.wrap:has(> .front) > .front .story:not(.nyt-lead){padding-right:0 !important;
border-right:none;border-top:1px solid #DFDFDD;padding-top:14px;margin-top:6px}
.wrap:has(> .front) > .techfeature{padding-left:0;border-left:none;
border-top:1px solid #DFDFDD;padding-top:14px}}
.glance ul{columns:2;column-gap:36px}
@media(max-width:760px){.glance ul{columns:1}}
.arch{columns:3;column-gap:30px}
.arch li{break-inside:avoid}
@media(max-width:860px){.arch{columns:1}}
article{max-width:840px;margin-left:auto;margin-right:auto}
article h1{text-align:center;font-size:40px;line-height:1.12}
.crumb{text-align:center}
.jump{justify-content:center}
.jump a{margin:0 8px}
.sitehead .brand{justify-content:center;text-align:center;flex-direction:column;gap:8px}
.sitetitle{font-size:44px}
.pagenav{justify-content:center}
.frontmatter{text-align:center}
.frontmatter h1.headline{font-size:48px}
.frontmatter .coverage{margin:0 auto}
.sitetitle{font-family:"UnifrakturMaguntia",Georgia,"Times New Roman",serif;font-size:54px;font-weight:400}
/* ---------- CONSISTENT THROUGHOUT (Sanjay 2026-11-20) — every page type
   carries the same NYT system: paper-white footer with double rule,
   centered nameplate/meta, flat archive rows and pager. ---------- */
footer{background:#fff !important;color:#555;border-top:4px double #121212;border-radius:0}
footer a{color:#121212}
.sitehead .meta{justify-content:center}
.issue{border-bottom:1px solid #DFDFDD;padding:14px 0}
.issue a{color:#121212;font-family:Georgia,"Times New Roman",Times,serif}
.pager a{border:1px solid #DFDFDD;border-radius:0;background:#fff;color:#121212;box-shadow:none}
.notice{background:#F7F7F5;border-left:2px solid #121212;border-radius:0}
.backtop{text-align:center}
.glance-deadline{border-top:1px solid #DFDFDD}
"""

JS = """
<script>
// Read-time touch (content itself is untouched): a gold rule beside any
// block whose own text states a deadline (the reports carry no separate
// 'Act on it' marker list, so none is invented).
(function(){
  document.querySelectorAll('article li, article p').forEach(function(el){
    if(/deadline/i.test(el.textContent) && el.textContent.length < 900){el.classList.add('deadline-flag');}
  });
})();
</script>
"""


def page(title: str, hero: str, body: str, root: str, dateline: str, active: str = "latest") -> str:
    latest_cls = ' class="active"' if active == "latest" else ""
    archive_cls = ' class="active"' if active == "archive" else ""
    return f"""<!DOCTYPE html>
<html lang="en" class="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#264387">\n<meta name="color-scheme" content="light">\n<script>(function(){{try{{if(localStorage.getItem("sk-scheme")==="dark"){{var d=document.documentElement;d.setAttribute("data-scheme","dark");var m=document.querySelector('meta[name="theme-color"]');if(m)m.content=d.getAttribute("data-theme")==="track"?"#1C1C1E":"#1a2f61"}}}}catch(e){{}}}})()</script>
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Legal">
<title>{html.escape(title)} — Sharma Legal Briefing</title>
<link rel="manifest" href="{root}manifest.webmanifest">
<link rel="apple-touch-icon" href="https://sharma-kit.sharma-crew.workers.dev/assets/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="https://sharma-kit.sharma-crew.workers.dev/assets/favicon-32.png">
<link rel="stylesheet" href="https://sharma-kit.sharma-crew.workers.dev/sharma-kit.css">
<link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap" rel="stylesheet">
<script src="https://sharma-kit.sharma-crew.workers.dev/sharma-kit.js" defer></script>
<style>{CSS}</style>
</head>
<body class="sk">
<header class="sk-header"><div class="sk-header__bar">
<div class="sk-header__lead"><a class="sk-header__logo" href="{root}index.html"><img src="https://sharma-kit.sharma-crew.workers.dev/assets/logo-white-header.png" alt="Sharma Electric &amp; HVAC" width="103" height="20"></a></div>
<div class="sk-header__title">Legal Briefing</div>
<div class="sk-header__trail"><a class="sk-header__btn" href="{root}more/" aria-label="More"><svg class="sk-icon"><use href="#i-more"/></svg></a></div>
</div></header>
<div class="sk-offline"></div>
<div class="wrap" id="top">
<header class="sitehead">
<div class="brand"><span class="sitetitle">Sharma Legal Briefing</span></div>
<p class="tagline">Daily legal news for Sharma Electric &amp; HVAC — a Florida electrical &amp; HVAC subcontractor</p>
<div class="meta"><span>Orlando, Florida</span><span>·</span><span>{html.escape(dateline)}</span><span>·</span><span>Daily Edition</span></div>
<nav class="pagenav"><a href="{root}index.html"{latest_cls}>Latest Edition</a><a href="{root}archive/index.html"{archive_cls}>Archive — Back Issues</a></nav>
</header>
{hero}
{body}
<p class="backtop"><a href="#top">Back to top</a></p>
<footer>Sharma Electric &amp; HVAC — daily legal news briefing for the office. General legal information only, not legal advice on a specific job. Every item carries its source link in the briefing text.</footer>
</div>
{JS}
<script>if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {{ addEventListener("load", function(){{ navigator.serviceWorker.register("{root}sw.js?kit=https://sharma-kit.sharma-crew.workers.dev", {{ scope: "/sharma-legal-briefing/" }}).catch(function(){{}}); }}); }}</script>
</body>
</html>
"""


def hero_for(ed, latest: bool, glance: str, lead_photo: str, jumpnav: str) -> str:
    tag = "Latest Edition" if latest else "Archive Edition"
    return f"""<section class="frontmatter">
<span class="kick">{tag}</span>
<h1 class="headline">Legal News Briefing — {html.escape(ed['weekday'])}, {html.escape(ed['date'])}</h1>
<p class="coverage">Coverage window: {html.escape(ed['window'])} (Eastern Time) · Prepared for Sharma Electric &amp; HVAC — builder clients, supplier accounts, crews statewide.</p>
<div class="lead"><span class="lead-kick">Lead Story</span><p>{html.escape(ed['biggest'])}</p></div>
{lead_photo}
{glance}
<p class="contents">In this edition — §1 Big Legal News &nbsp;·&nbsp; §2 Florida &nbsp;·&nbsp; §3 Business Law &nbsp;·&nbsp; §4 Construction &amp; Contractor Law &nbsp;·&nbsp; §5 Money &amp; Deal Law<br>Each story shows its headline, a one-line deck and the Sharma impact; tap “Read the full story” for the complete text and source links. Items that could not be confirmed, and older stories going around again, appear at the end of each edition under their own headings, as in the source reports.</p>
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
        out = page(f"{ed['label']} — Legal News Briefing", hero, body, "../", ed["label"], active="archive")
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
        page("Archive — Legal News Briefing", hero, arch_body, "../", "Archive — Back Issues", active="archive"), encoding="utf-8"
    )
    print("wrote archive index")


if __name__ == "__main__":
    main()
