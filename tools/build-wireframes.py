#!/usr/bin/env python3
"""Build the static wireframes pages from the canvas artboards.

Reads wireframes/src/*.dc.html plus wireframes/src/canvas.json — the same files
that make up the Claude design canvas — and writes one plain HTML page per
artboard, a shared stylesheet, and an index.

The canvas page itself (wireframes/canvas/) runs the whole editor and mounts
every artboard in its own srcdoc iframe, which iOS Safari kills on a phone.
These pages carry the same markup with none of that: one board per page, the
kit loaded once as an external stylesheet, no iframes, no editor.

    python3 build-wireframes.py
"""

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
SRC = ROOT / "wireframes"                 # the artboard sources, one copy
OUT = ROOT / "site" / "wireframes"        # what Netlify serves

FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800"
         "&family=Hanken+Grotesk:wght@300..800&family=JetBrains+Mono:wght@300..600"
         "&family=Source+Serif+4:opsz,wght@8..60,300..600&display=swap")

# Screen IDs and a line of description per board, in canvas order within a page.
BOARDS = {
    "Main": ("Cover", "The premise, the two lighting states, and how to read the boards."),
    "CuratorPrep": ("1J1–1J2", "Prep home, and the research agent that reads around the film."),
    "CuratorNotes": ("1J3–1J4", "Findings into notes, and the editor where a note gets pinned to a moment."),
    "CuratorQueue": ("1J5–1J6", "The note queue, and going live."),
    "CuratorLive": ("1J7 · 1J9", "On air, and the dry run."),
    "CuratorPhone": ("1J6 · 1J7 on a phone", "The two curator screens that are not desktop, because hosting happens with the film on the TV."),
    "CuratorShip": ("1J8", "The promo kit, and where the room came from."),
    "Discover": ("1E–1G", "Onboarding, the Marquee, the session page and the two prompts."),
    "TheNight": ("1D1–1D9", "Doors, the pre-show, the calls, the leader, the film, and falling behind."),
    "TheRoom": ("1A–1C", "The screen you hold during the film, and what happens when a note arrives."),
    "AfterTheShow": ("1H–1I", "The recap, Film DNA, and the Taste Passport."),
    "LightsUp": ("1D10", "The five minutes after the film, and the handoff out."),
    "CuratorProfile": ("1K", "What a link in her bio should open."),
}


def read_canvas():
    canvas = json.loads((SRC / "canvas.json").read_text())
    pages = canvas.get("pages") or [{"id": "page-1", "name": "Page 1"}]
    return canvas, pages


def artboard_body(name):
    """The artboard markup, minus the kit helmet and the (inert) dc script."""
    text = (SRC / f"{name}.dc.html").read_text()
    body = text.split("</helmet>", 1)[1].split("<script", 1)[0]
    return body.replace("</x-dc>", "").strip()


def kit_css():
    text = (SRC / "Main.dc.html").read_text()
    helmet = text.split("<helmet>", 1)[1].split("</helmet>", 1)[0]
    return re.search(r"<style>(.*?)</style>", helmet, re.S).group(1).strip()


# Which board each canvas note belongs to. The notes carry x/y but no page, and
# the two pages share a coordinate space, so geometry alone puts a page-one note
# on whichever page-two board happens to sit under it. An unlisted note falls
# back to the nearest board and says so.
NOTE_BOARD = {
    # Every note is mapped by hand. A note that is not listed here gets attached to
    # whichever board it happens to sit nearest on the canvas, which is how the
    # lighting note once ended up on TheNight.
    "board-main": "Main.dc.html",
    "board-curatorprep": "CuratorPrep.dc.html",
    "board-curatornotes": "CuratorNotes.dc.html",
    "board-curatorqueue": "CuratorQueue.dc.html",
    "board-curatorlive": "CuratorLive.dc.html",
    "board-curatorphone": "CuratorPhone.dc.html",
    "board-curatorship": "CuratorShip.dc.html",
    "board-discover": "Discover.dc.html",
    "board-thenight": "TheNight.dc.html",
    "board-theroom": "TheRoom.dc.html",
    "board-aftertheshow": "AfterTheShow.dc.html",
    "board-lightsup": "LightsUp.dc.html",
    "board-curatorprofile": "CuratorProfile.dc.html",
    # Canvas navigation, not board content: it tells you to switch pages in the
    # canvas toolbar, which these pages do not have. The index lists both pages.
    "audience-page": None,
}


def attach_notes(canvas):
    """Put each canvas annotation on its board."""
    notes = {}
    for ann in canvas.get("annotations", []):
        if ann.get("id") in NOTE_BOARD:
            target = NOTE_BOARD[ann["id"]]
            if target is None:
                continue
        else:
            best, best_d = None, None
            for art in canvas["artboards"]:
                dx = max(art["x"] - (ann["x"] + ann["w"]), ann["x"] - (art["x"] + art["w"]), 0)
                dy = max(art["y"] - ann["y"], ann["y"] - (art["y"] + art["h"]), 0)
                d = dx * dx + dy * dy
                if best_d is None or d < best_d:
                    best, best_d = art["file"], d
            target = best
            print(f"  note {ann.get('id')!r} is not in NOTE_BOARD - guessed {target}")
        notes.setdefault(target, []).append(ann["text"])
    return notes


def paragraphs(text):
    return "\n".join(f"<p>{html.escape(p)}</p>" for p in text.split("\n") if p.strip())


CHROME = """
  body{background:#0b0b0e}
  .bar{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:16px;
    padding:11px 16px;background:#e7e3da;color:#1a1917;border-bottom:1px solid rgba(0,0,0,.12)}
  .bar a{color:#57534a}
  .bar a:hover{color:#a01a86}
  .bar .who{flex:1;min-width:0;display:flex;align-items:baseline;gap:10px}
  .bar .name{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:700;
    font-size:14px;letter-spacing:.02em;text-transform:uppercase;white-space:nowrap}
  .bar .ids{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;
    letter-spacing:.12em;color:#8a8477;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bar .back,.bar .zoom{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;
    letter-spacing:.12em;text-transform:uppercase;white-space:nowrap}
  .zoom{border:1px solid rgba(0,0,0,.2);border-radius:999px;background:transparent;color:#57534a;
    padding:5px 11px;cursor:pointer;font-family:inherit}
  .zoom:hover{color:#a01a86;border-color:#a01a86}
  .memo{background:#14110b;color:#b8a77f;padding:12px 16px;font-family:'Source Serif 4',Georgia,serif;
    font-size:14.5px;line-height:1.5;border-bottom:1px solid #453a26}
  .memo summary{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;
    letter-spacing:.14em;text-transform:uppercase;color:#8a7c5c;cursor:pointer}
  .memo[open] summary{margin-bottom:10px}
  .memo p{margin:0 0 9px;max-width:70ch}
  .memo p:last-child{margin:0}
  .stage{padding:16px;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .art{transform-origin:top left}
  /* A board is a row of screens. Shrinking the whole row to fit a laptop turns
     1440px screens into diagrams you cannot read, so the row is allowed to wrap
     and the screens stack down the page instead. */
  .art.wrap > div:first-child{flex-wrap:wrap!important;align-content:flex-start!important}
  .pager{display:flex;justify-content:space-between;gap:16px;padding:16px 16px 40px;
    font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10.5px;letter-spacing:.12em;
    text-transform:uppercase}
  .pager span{color:#3a382f}
  @media (max-width:520px){.bar .ids{display:none}}
"""

BOARD_JS = """
(function(){
  var art=document.getElementById('art'),stage=document.getElementById('stage'),
      btn=document.getElementById('zoom');
  if(!art||!stage||!btn){return}
  var W=parseInt(art.getAttribute('data-w'),10),H=parseInt(art.getAttribute('data-h'),10);
  var root=art.firstElementChild;
  // Only a row of screens can be reflowed. Main is a single column and is left alone.
  var canWrap=false;
  try{canWrap=!!root&&getComputedStyle(root).flexDirection==='row'&&root.children.length>1}catch(e){}
  var actual=false,fitScale=1;
  function avail(){return Math.max(320,stage.clientWidth-32)}
  function apply(){
    try{
      btn.textContent=actual?'Fit to screen':'Actual size';
      art.classList.remove('wrap');
      art.style.width='';art.style.transform='';stage.style.height='';
      if(actual){return}
      var a=avail();
      if(!canWrap){
        // Nothing to reflow. Scale to fit, which is what Main wants anyway.
        if(W<=a){return}
        var s0=Math.min(1,a/W);
        fitScale=s0;
        art.style.transform='scale('+s0+')';
        stage.style.height=Math.ceil(Math.max(H,art.scrollHeight)*s0)+'px';
        return;
      }
      // Measure the screens at their natural size before constraining anything.
      art.classList.add('wrap');
      var widest=0,i;
      for(i=0;i<root.children.length;i++){
        widest=Math.max(widest,root.children[i].offsetWidth);
      }
      var cs=getComputedStyle(root);
      var pad=(parseFloat(cs.paddingLeft)||0)+(parseFloat(cs.paddingRight)||0);
      // Wrap at the window, unless one screen is wider than the window on its own,
      // in which case wrap at that screen and scale the difference away.
      var w=Math.max(a,widest+pad);
      art.style.width=w+'px';
      var s=Math.min(1,a/w);
      fitScale=s;
      if(s<1){art.style.transform='scale('+s+')'}
      stage.style.height=Math.ceil(art.scrollHeight*s)+'px';
    }catch(e){}
  }
  btn.addEventListener('click',function(){
    actual=!actual;apply();
    if(actual){window.scrollTo(0,0)}
  });
  window.addEventListener('resize',apply);
  apply();
  // Wrapping saves a laptop but not a phone: a 1440px screen in a 375px window is
  // still a shape rather than something you can read. Below a third, open it 1:1
  // and let it scroll sideways, which is at least legible a column at a time.
  if(!actual&&fitScale<0.35){actual=true;apply()}
  // The board is what you came for; on a phone the notes start folded away.
  try{
    var memo=document.getElementById('memo');
    if(memo&&window.innerWidth<700){memo.removeAttribute('open')}
  }catch(e){}
})();
"""


def board_page(name, art, notes, prev_art, next_art):
    ids, blurb = BOARDS[name]
    memo = ""
    if notes:
        body = "\n".join(paragraphs(n) for n in notes)
        label = "note" if len(notes) == 1 else "notes"
        memo = (f'<details class="memo" id="memo" open><summary>{len(notes)} {label} on this board</summary>'
                f"{body}</details>")
    pager = []
    if prev_art:
        p = prev_art["file"][:-len(".dc.html")]
        pager.append(f'<a href="./{p}.html">← {html.escape(p)}</a>')
    else:
        pager.append("<span></span>")
    if next_art:
        n = next_art["file"][:-len(".dc.html")]
        pager.append(f'<a href="./{n}.html">{html.escape(n)} →</a>')
    else:
        pager.append("<span></span>")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(name)} · Projector wireframes</title>
<meta name="description" content="{html.escape(blurb)}">
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../kit.css">
<style>{CHROME}</style>
</head>
<body>
<header class="bar">
  <a class="back" href="../">← Boards</a>
  <div class="who"><span class="name">{html.escape(name)}</span><span class="ids">{html.escape(ids)}</span></div>
  <button class="zoom" id="zoom" type="button">Actual size</button>
</header>
{memo}
<div class="stage" id="stage">
  <div class="art" id="art" data-w="{art['w']}" data-h="{art['h']}">
{artboard_body(name)}
  </div>
</div>
<nav class="pager">{pager[0]}{pager[1]}</nav>
<script>{BOARD_JS}</script>
</body>
</html>
"""


INDEX_CSS = """
  :root{--paper:#e7e3da;--ink:#1a1917;--ink-soft:#57534a;--ink-faint:#8a8477;
    --line:rgba(0,0,0,.12);--board:#14110b;--board-line:#453a26;--bulb:#f4e4bc}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);
    font-family:'Hanken Grotesk',-apple-system,system-ui,sans-serif;line-height:1.5}
  main{max-width:680px;width:100%;margin:0 auto;padding:56px 24px 72px}
  a{color:inherit;text-decoration:none}
  .board{background:var(--board);border:1px solid var(--board-line);border-radius:14px;
    padding:26px 22px;text-align:center;margin-bottom:36px}
  .bulbs{height:6px;background-image:radial-gradient(circle at 5px 3px,rgba(244,228,188,.85) 0 1.8px,
    rgba(244,228,188,.15) 2.8px,transparent 3.5px);background-size:15px 6px;background-repeat:repeat-x;
    animation:chase 1.4s steps(2) infinite}
  @keyframes chase{to{background-position-x:15px}}
  .board h1{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;
    font-size:clamp(24px,6vw,34px);letter-spacing:.04em;text-transform:uppercase;color:var(--bulb);
    text-shadow:0 0 18px rgba(244,228,188,.30);margin:16px 0 6px;line-height:1.05}
  .board .sub{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:10px;letter-spacing:.22em;
    text-transform:uppercase;color:#b8a77f;margin-bottom:18px}
  .lede{font-size:14.5px;color:var(--ink-soft);max-width:58ch;margin:0 0 34px}
  h2{font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;font-size:13px;
    letter-spacing:.14em;text-transform:uppercase;margin:34px 0 0;padding-bottom:9px;
    border-bottom:1px solid var(--line)}
  h2 .count{font-family:'JetBrains Mono',ui-monospace,monospace;font-weight:400;font-size:10.5px;
    letter-spacing:.12em;color:var(--ink-faint);margin-left:8px}
  ul{list-style:none;margin:0;padding:0}
  li{border-bottom:1px solid var(--line)}
  li a{display:flex;align-items:baseline;gap:16px;padding:18px 6px;transition:background .15s ease}
  li a:hover{background:rgba(0,0,0,.045)}
  li a:hover .name{color:#a01a86}
  .ids{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11px;color:var(--ink-faint);
    flex:none;width:74px}
  .entry{flex:1;min-width:0;display:block}
  .name{display:block}
  .name{display:block;font-family:'Archivo',system-ui,sans-serif;font-stretch:125%;font-weight:800;
    font-size:15px;letter-spacing:.02em;text-transform:uppercase}
  .desc{display:block;font-size:13.5px;color:var(--ink-soft);margin-top:3px;max-width:46ch}
  footer{max-width:680px;margin:0 auto;padding:0 24px 44px}
  footer p{font-size:13px;color:var(--ink-soft);margin:0 0 10px;max-width:58ch}
  footer .fine{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:9.5px;letter-spacing:.16em;
    text-transform:uppercase;color:var(--ink-faint)}
  footer a{border-bottom:1px solid rgba(0,0,0,.25)}
  footer a:hover{color:#a01a86;border-color:#a01a86}
  @media (prefers-reduced-motion:reduce){*{animation-duration:.001ms !important;
    animation-iteration-count:1 !important;transition-duration:.001ms !important}}
"""


def index_page(canvas, pages):
    by_page = {p["id"]: [] for p in pages}
    for art in canvas["artboards"]:
        by_page.setdefault(art["page"], []).append(art)
    sections = []
    for page in pages:
        arts = by_page.get(page["id"], [])
        rows = []
        for art in arts:
            name = art["file"][:-len(".dc.html")]
            ids, blurb = BOARDS[name]
            rows.append(
                f'    <li><a href="./b/{name}.html"><span class="ids">{html.escape(ids)}</span>'
                f'<span class="entry"><span class="name">{html.escape(name)}</span>'
                f'<span class="desc">{html.escape(blurb)}</span></span></a></li>'
            )
        sections.append(
            f'  <h2>{html.escape(page["name"])}<span class="count">{len(arts)} boards</span></h2>\n'
            f"  <ul>\n" + "\n".join(rows) + "\n  </ul>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Projector — Wireframes</title>
<meta name="description" content="Curator tools first, then the audience. One board per page.">
<link rel="stylesheet" href="{FONTS}">
<style>{INDEX_CSS}</style>
</head>
<body>
<main>
  <div class="board">
    <div class="bulbs"></div>
    <h1>Wireframes</h1>
    <div class="sub">Projector · v2 · August 2026</div>
    <div class="bulbs"></div>
  </div>

  <p class="lede">Curator tools are V1, minus the research agent and AI timestamping, which come after the raise. Five design partners get the rest, with no audience on the other end. The audience side is V2. Open a board on its own page. The toggle in the bar swaps between fitting the board to your screen and its full size, and the wide boards open full size on a phone so the type stays readable.</p>

{chr(10).join(sections)}
</main>

<footer>
  <p>The same boards live on one pan-and-zoom canvas at <a href="./canvas/">the full canvas</a>, which wants a laptop — it loads every board at once and a phone will drop the tab.</p>
  <p class="fine">Built from the canvas artboards · <a href="../">The workroom</a></p>
</footer>
</body>
</html>
"""


def main():
    canvas, pages = read_canvas()
    notes = attach_notes(canvas)
    (OUT / "kit.css").write_text(kit_css() + "\n")
    (OUT / "b").mkdir(exist_ok=True)
    arts = canvas["artboards"]
    for i, art in enumerate(arts):
        name = art["file"][:-len(".dc.html")]
        prev_art = arts[i - 1] if i else None
        next_art = arts[i + 1] if i + 1 < len(arts) else None
        page = board_page(name, art, notes.get(art["file"], []), prev_art, next_art)
        (OUT / "b" / f"{name}.html").write_text(page)
        print("wrote", f"wireframes/b/{name}.html", len(page))
    index = index_page(canvas, pages)
    (OUT / "index.html").write_text(index)
    print("wrote", "wireframes/index.html", len(index))


if __name__ == "__main__":
    main()
