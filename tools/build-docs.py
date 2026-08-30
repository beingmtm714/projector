#!/usr/bin/env python3
"""Render the Projectionist documents into the published site.

What belongs here: things worth someone's real review. The product spec, the
deck, the design language, the plans, the brief. What does not: meeting notes,
transcripts, and background analyses like the Teleport write-up. Those are
working material, they live in the vault, and putting them in front of a reader
who wants to know what the product is wastes their time.

The Markdown in the vault is the only copy. This reads it and writes plain
pages next to the wireframes, so anyone can read a finished document without a
Google account and without anybody keeping a second version in step.

    python3 build-docs.py

Adding a document is one line in DOCS. Removing one is deleting that line.
"""

import html as H
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).parent.parent          # the projector repo
VAULT = ROOT.parent                                  # Ventures/Projectionist
REPO = VAULT.parent.parent                           # ~/Claude
OUT = ROOT / "site" / "docs"
PRIVATE = OUT / "private"                            # behind the access gate

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800"
         "&family=Hanken+Grotesk:wght@300..800&family=JetBrains+Mono:wght@300..600"
         "&family=Source+Serif+4:opsz,wght@8..60,300..600&display=swap")

# These two are not for a link anyone can guess. They go behind the gate, and
# the index shows their titles without linking a body anyone can read.
GATED = {"investor-deck", "pre-seed-bar"}

# slug, title, source, one line for the index
DOCS = [
    ("product-spec", "Product Spec", VAULT / "Projectionist-Product-Spec.md",
     "What gets built and when, screen by screen. Eleven sections."),
    ("sprint-plan", "Sprint Plan", VAULT / "Projectionist-Sprint-Plan.md",
     "Six sprints, 31 August to 20 November. The operating document."),
    ("investor-deck", "Investor Deck", VAULT / "Projectionist-Investor-Deck.md",
     "Fourteen slides of copy, waiting on numbers from the proof of concept."),
    ("design-language", "Design Language", ROOT / "DESIGN.md",
     "The settled system. Two lighting states, the curtain, type, motion."),
    ("build-plan", "Build Plan", VAULT / "Projectionist-Build-Plan.md",
     "About 35 hours of Michael and twelve engineer days, and where they go."),
    ("build-environment", "Build Environment", VAULT / "Projectionist-Build-Environment.md",
     "A repository rather than a hosted builder, agents, and the visual loop."),
    ("engineer-brief", "Engineer Brief", VAULT / "Projectionist-Engineer-Brief.md",
     "The contract role: the session clock, the firing engine, and the review."),
    ("pre-seed-bar", "Pre-Seed Bar", REPO / "notes/ventures/projectionist-preseed-bar.md",
     "What a $2M round requires, written in the voice of an investor."),
    ("short-copy", "Short Copy", VAULT / "Projectionist-Blurbs.md",
     "Two blurbs at roughly 300 characters, for outreach and intros."),
]

SECTIONS = [
    ("The product", ["product-spec", "sprint-plan"]),
    ("Design", ["design-language"]),
    ("Build", ["build-plan", "build-environment", "engineer-brief"]),
    ("Fundraising", ["investor-deck", "pre-seed-bar", "short-copy"]),
]

# Prose refers to sibling documents by filename. Turn those into links.
FILE_TO_SLUG = {p.name: slug for slug, _, p, _ in DOCS}


def last_touched(path):
    """DESIGN.md lives in the site repo and the rest in the vault, so ask the
    repository that actually owns the file rather than assuming one of them."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path.parent,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        out = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=format:%-d %B %Y",
                              "--", str(path)],
                             cwd=top or path.parent, capture_output=True, text=True, timeout=10)
        return out.stdout.strip()
    except Exception:
        return ""


def inline(t, linkify=True):
    t = H.escape(t)
    t = re.sub(r'`([^`]+)`', lambda m: '<code>' + m.group(1) + '</code>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<em>\1</em>', t)
    if linkify:
        for name, slug in FILE_TO_SLUG.items():
            t = t.replace('<code>' + H.escape(name) + '</code>',
                          f'<a class="xref" href="./{slug}.html">{H.escape(name)}</a>')
    return t


def is_rule(row):
    cells = [c.strip() for c in row.strip().strip('|').split('|')]
    return bool(cells) and all(re.fullmatch(r':?-{2,}:?', c) for c in cells)


def slugify(s):
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60]


def render(src):
    lines = src.replace('\r\n', '\n').split('\n')
    out, toc, i, n = [], [], 0, len(lines)
    while i < n:
        line = lines[i]

        if line.strip().startswith('```'):
            i += 1; buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(H.escape(lines[i])); i += 1
            i += 1
            out.append('<pre><code>' + '\n'.join(buf) + '</code></pre>'); continue

        if re.fullmatch(r'\s*(-{3,}|\*{3,}|_{3,})\s*', line):
            out.append('<hr>'); i += 1; continue

        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lvl, txt = len(m.group(1)), inline(m.group(2).strip())
            if lvl == 1:
                i += 1; continue          # the page header carries the title
            a = slugify(txt)
            if lvl == 2:
                toc.append((a, re.sub(r'<[^>]+>', '', txt)))
            out.append(f'<h{lvl} id="{a}">{txt}</h{lvl}>'); i += 1; continue

        if line.strip().startswith('|') and i + 1 < n and is_rule(lines[i + 1]):
            hdr = [c.strip() for c in line.strip().strip('|').split('|')]
            i += 2; body = []
            while i < n and lines[i].strip().startswith('|'):
                body.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            t = ['<div class="tw"><table><thead><tr>']
            t += [f'<th>{inline(c)}</th>' for c in hdr]
            t.append('</tr></thead><tbody>')
            for row in body:
                t.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in row) + '</tr>')
            t.append('</tbody></table></div>')
            out.append(''.join(t)); continue

        m = re.match(r'^\s*([-*+])\s+(.*)$', line)
        if m:
            items = []
            while i < n:
                mm = re.match(r'^\s*([-*+])\s+(.*)$', lines[i])
                if not mm:
                    if lines[i].strip() and lines[i].startswith(('  ', '\t')) and items:
                        items[-1] += ' ' + lines[i].strip(); i += 1; continue
                    break
                items.append(mm.group(2)); i += 1
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>'); continue

        m = re.match(r'^\s*\d+\.\s+(.*)$', line)
        if m:
            items = []
            while i < n:
                mm = re.match(r'^\s*\d+\.\s+(.*)$', lines[i])
                if not mm:
                    if lines[i].strip() and lines[i].startswith(('  ', '\t')) and items:
                        items[-1] += ' ' + lines[i].strip(); i += 1; continue
                    break
                items.append(mm.group(1)); i += 1
            out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ol>'); continue

        if line.strip().startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip()); i += 1
            out.append('<blockquote>' + inline(' '.join(buf)) + '</blockquote>'); continue

        if not line.strip():
            i += 1; continue

        out.append('<p>' + inline(line.strip()) + '</p>'); i += 1

    return '\n'.join(out), toc


CSS = """
  :root{--paper:#e7e3da;--card:#f2efe8;--ink:#1a1917;--ink-soft:#57534a;--ink-faint:#8a8477;
    --line:rgba(0,0,0,.12);--board:#14110b;--board-line:#453a26;--bulb:#f4e4bc;--pink:#a01a86}
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{margin:0;background:var(--paper);color:var(--ink);
    font-family:'Hanken Grotesk',-apple-system,system-ui,sans-serif;line-height:1.6;
    -webkit-font-smoothing:antialiased}
  a{color:inherit}
  .bar{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:16px;
    padding:11px 16px;background:var(--paper);border-bottom:1px solid var(--line)}
  .bar a{color:var(--ink-soft);text-decoration:none}
  .bar a:hover{color:var(--pink)}
  .bar .who{flex:1;min-width:0;display:flex;align-items:baseline;gap:10px}
  .bar .name{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:700;
    font-size:14px;letter-spacing:.02em;text-transform:uppercase;white-space:nowrap}
  .bar .meta,.bar .back{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;
    letter-spacing:.12em;text-transform:uppercase;color:var(--ink-faint);white-space:nowrap;
    overflow:hidden;text-overflow:ellipsis}
  main{max-width:720px;margin:0 auto;padding:44px 24px 80px}
  .doc h1{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;
    font-size:clamp(26px,6vw,38px);letter-spacing:.03em;text-transform:uppercase;
    margin:0 0 6px;line-height:1.05}
  .stamp{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;letter-spacing:.18em;
    text-transform:uppercase;color:var(--ink-faint);margin-bottom:30px}
  .toc{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:16px 0;margin-bottom:34px}
  .toc ol{list-style:none;margin:0;padding:0;columns:2;column-gap:28px}
  .toc li{break-inside:avoid;margin:0 0 5px}
  .toc a{font-size:13.5px;color:var(--ink-soft);text-decoration:none}
  .toc a:hover{color:var(--pink)}
  .doc h2{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;font-size:13px;
    letter-spacing:.14em;text-transform:uppercase;margin:46px 0 0;padding-bottom:9px;
    border-bottom:1px solid var(--line);scroll-margin-top:60px}
  .doc h3{font-size:17px;font-weight:700;margin:32px 0 0;scroll-margin-top:60px}
  .doc h4{font-size:14px;font-weight:700;margin:24px 0 0;color:var(--ink-soft)}
  .doc p{margin:12px 0;max-width:66ch}
  .doc ul,.doc ol{margin:12px 0;padding-left:20px;max-width:66ch}
  .doc li{margin:6px 0}
  .doc hr{border:0;border-top:1px solid var(--line);margin:38px 0}
  .doc blockquote{margin:16px 0;padding:2px 0 2px 16px;border-left:2px solid var(--line);
    font-family:'Source Serif 4',Georgia,serif;font-size:16px;color:var(--ink-soft);max-width:62ch}
  .doc code{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:.86em;
    background:rgba(0,0,0,.055);padding:1px 5px;border-radius:3px}
  .doc pre{background:var(--board);color:#d8cfae;padding:14px 16px;border-radius:8px;overflow-x:auto}
  .doc pre code{background:none;color:inherit;padding:0;font-size:12.5px;line-height:1.55}
  .doc a{color:var(--ink);text-decoration:none;border-bottom:1px solid rgba(0,0,0,.28)}
  .doc a:hover{color:var(--pink);border-color:var(--pink)}
  .lockline{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;
    letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);
    border:1px solid var(--line);border-radius:999px;padding:5px 11px;display:inline-block;
    margin:0 0 26px}
  .doc a.xref{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:.84em;
    background:rgba(160,26,134,.07);border-bottom:1px solid rgba(160,26,134,.35);
    padding:1px 5px;border-radius:3px}
  .tw{overflow-x:auto;margin:18px 0}
  table{border-collapse:collapse;width:100%;font-size:14px}
  th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
  th{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;letter-spacing:.12em;
    text-transform:uppercase;color:var(--ink-faint);font-weight:400;white-space:nowrap}
  .pager{display:flex;justify-content:space-between;gap:16px;margin-top:56px;
    border-top:1px solid var(--line);padding-top:18px;
    font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;letter-spacing:.12em;
    text-transform:uppercase}
  .pager a{color:var(--ink-soft);text-decoration:none}
  .pager a:hover{color:var(--pink)}
  .pager span{color:#bdb8ac}
  @media (max-width:620px){.toc ol{columns:1}.bar .meta{display:none}}
  @media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""


def shell(title, body, head_extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{H.escape(title)}</title>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
{head_extra}
</head>
<body>
{body}
</body>
</html>
"""


def dest(slug):
    return (PRIVATE if slug in GATED else OUT) / f"{slug}.html"


def href(slug, from_private=False):
    """Links have to work from both docs/ and docs/private/."""
    if slug in GATED:
        return f"./{slug}.html" if from_private else f"./private/{slug}.html"
    return f"../{slug}.html" if from_private else f"./{slug}.html"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    PRIVATE.mkdir(parents=True, exist_ok=True)
    order = [d[0] for d in DOCS]
    by_slug = {d[0]: d for d in DOCS}

    for idx, (slug, title, path, blurb) in enumerate(DOCS):
        if not path.exists():
            print(f"  MISSING {path}"); continue
        body, toc = render(path.read_text())
        stamp = last_touched(path)

        toc_html = ""
        if len(toc) > 2:
            items = "".join(f'<li><a href="#{a}">{H.escape(t)}</a></li>' for a, t in toc)
            toc_html = f'<nav class="toc"><ol>{items}</ol></nav>'

        pager = []
        prev = by_slug[order[idx - 1]] if idx else None
        nxt = by_slug[order[idx + 1]] if idx + 1 < len(order) else None
        here = slug in GATED
        pager.append(f'<a href="{href(prev[0], here)}">← {H.escape(prev[1])}</a>' if prev else "<span></span>")
        pager.append(f'<a href="{href(nxt[0], here)}">{H.escape(nxt[1])} →</a>' if nxt else "<span></span>")

        lock = ('<div class="lockline">Shared by link. Not listed publicly.</div>'
                if slug in GATED else "")
        page = f"""<header class="bar">
  <a class="back" href="{'../' if slug in GATED else './'}">← Documents</a>
  <div class="who"><span class="name">{H.escape(title)}</span></div>
  <span class="meta">{H.escape(stamp)}</span>
</header>
<main class="doc">
<h1>{H.escape(title)}</h1>
<div class="stamp">{H.escape(blurb)}</div>
{lock}
{toc_html}
{body}
<nav class="pager">{pager[0]}{pager[1]}</nav>
</main>"""
        out = dest(slug)
        out.write_text(shell(f"{title} · Projectionist", page))
        print(f"wrote {out.relative_to(ROOT)}")

    # index
    groups = []
    for heading, slugs in SECTIONS:
        rows = []
        for s in slugs:
            _, title, path, blurb = by_slug[s]
            stamp = last_touched(path)
            mark = ' <span class="lock">by link only</span>' if s in GATED else ''
            rows.append(
                f'<li><a href="{href(s)}"><span class="entry">'
                f'<span class="name">{H.escape(title)}{mark}</span>'
                f'<span class="desc">{H.escape(blurb)}</span></span>'
                f'<span class="when">{H.escape(stamp)}</span></a></li>')
        groups.append(f'<h2>{H.escape(heading)}</h2><ul>{"".join(rows)}</ul>')

    index_css = """
  main{max-width:680px}
  .board{background:var(--board);border:1px solid var(--board-line);border-radius:14px;
    padding:26px 22px;text-align:center;margin-bottom:34px}
  .bulbs{height:6px;background-image:radial-gradient(circle at 5px 3px,rgba(244,228,188,.85) 0 1.8px,
    rgba(244,228,188,.15) 2.8px,transparent 3.5px);background-size:15px 6px;background-repeat:repeat-x}
  .board h1{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;
    font-size:clamp(24px,6vw,34px);letter-spacing:.04em;text-transform:uppercase;color:var(--bulb);
    text-shadow:0 0 18px rgba(244,228,188,.30);margin:16px 0 6px;line-height:1.05}
  .board .sub{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;letter-spacing:.22em;
    text-transform:uppercase;color:#b8a77f;margin-bottom:18px}
  .lede{font-size:14.5px;color:var(--ink-soft);max-width:60ch;margin:0 0 8px}
  h2{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;font-size:13px;
    letter-spacing:.14em;text-transform:uppercase;margin:38px 0 0;padding-bottom:9px;
    border-bottom:1px solid var(--line)}
  ul{list-style:none;margin:0;padding:0}
  li{border-bottom:1px solid var(--line)}
  li a{display:flex;align-items:baseline;gap:14px;padding:16px 6px;text-decoration:none;
    transition:background .15s ease}
  li a:hover{background:rgba(0,0,0,.045)}
  li a:hover .name{color:var(--pink)}
  .entry{flex:1;min-width:0}
  .name{display:block;font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;
    font-size:15px;letter-spacing:.02em;text-transform:uppercase}
  .desc{display:block;font-size:13.5px;color:var(--ink-soft);margin-top:3px;max-width:48ch}
  .lock{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:9px;letter-spacing:.14em;
    text-transform:uppercase;color:var(--ink-faint);border:1px solid var(--line);
    border-radius:999px;padding:2px 7px;margin-left:8px;vertical-align:1px;font-stretch:normal;
    font-weight:400;letter-spacing:.12em}
  .when{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;letter-spacing:.1em;
    color:var(--ink-faint);flex:none;text-align:right}
  footer{max-width:680px;margin:0 auto;padding:0 24px 56px}
  footer p{font-size:13px;color:var(--ink-soft);margin:0 0 10px;max-width:60ch}
  footer a{color:inherit;border-bottom:1px solid rgba(0,0,0,.25);text-decoration:none}
  footer a:hover{color:var(--pink);border-color:var(--pink)}
  @media (max-width:560px){.when{display:none}}
"""
    index_body = f"""<main>
  <div class="board">
    <div class="bulbs"></div>
    <h1>Projectionist</h1>
    <div class="sub">Documents</div>
    <div class="bulbs"></div>
  </div>
  <p class="lede">A curator picks a film, sets a showtime, and hosts a screening. You watch on your
  own television, on whatever service you already pay for, and their Liner Notes arrive on your phone
  in time with the film.</p>
  <p class="lede"><a href="../wireframes/">The wireframes are here</a>, eleven boards covering every screen.</p>
  {''.join(groups)}
</main>
<footer>
  <p>These pages are rendered from the Markdown in the vault every time it is pushed. There is one
  copy of each document and this is a view of it, so nothing here can fall behind the original.</p>
  <p class="lede" style="font-size:12px">Working document. Numbers in square brackets are placeholders.</p>
</footer>"""
    (OUT / "index.html").write_text(
        shell("Projectionist · Documents", index_body, f"<style>{index_css}</style>"))
    print("wrote docs/index.html")


if __name__ == "__main__":
    build()
