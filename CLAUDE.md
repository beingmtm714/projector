# Projector — repo conventions

A curator-led film companion. A curator hosts a screening, the audience watches
on their own television, and the curator's notes arrive in sync on a second
screen. **The product never touches the film**: no player, no embed, no rights,
no platform integration. Everything runs off a shared start time.

This repository holds the wireframes, the published documents, and the build
scripts that turn one into the other. The application is a separate repository.

## What belongs in here, and what does not

**Only material worth someone's real review.** The product spec, the deck, the
wireframes, the design language, the plans, the engineer brief.

**Never:** meeting notes, call transcripts, and background analyses of options
that were considered and dropped. Those are working material. They live in the
vault, and putting them in front of someone who wants to know what the product
is wastes their attention and dates the repository. The Teleport write-up is the
type case: a real piece of thinking, and not something a curator or an engineer
should meet.

Adding a document is one line in `DOCS` in `tools/build-docs.py`. If a file does
not clear the bar above, it does not get a line.

## One copy of everything

The documents are Markdown in the vault at `Ventures/Projector/`, and
`tools/build-docs.py` renders them into `site/docs/`. The artboards are
`wireframes/*.dc.html`, built from `wireframes/_body_*.html` by
`wireframes/assemble.py`, and `tools/build-wireframes.py` renders them into
`site/wireframes/`. Nothing is copied and kept in step by hand. That practice
produced a Google Drive folder holding twelve stale duplicates, and unwinding it
took a day.

`wireframes/_kit.txt` is the only place a design value lives. **Never invent
one.** If a colour, size or weight is needed and it is not there, that is a
question, not a decision to make in CSS. `DESIGN.md` carries the rules the
tokens cannot express.

`site/wireframes/canvas/index.html` is a frozen export that no script
regenerates. An artboard edit has to be carried into it by hand or it drifts.

## Publishing

Netlify serves `site/` and nothing else. There is no build command; pages are
generated locally and reviewed before they are pushed, so a broken build is
never a live one.

`site/docs/private/` sits behind `netlify/edge-functions/gate.ts`. Anyone
without a token gets a 401 and the body is never sent. Tokens live in the
`PROJECTOR_TOKENS` environment variable on Netlify, never in this repository.
A new gated document needs a token entry or it 401s for everyone, including us.

## Working on the boards

Edit `wireframes/_body_<Board>.html`, run `python3 wireframes/assemble.py
<Board> <w> <h>`, then `python3 tools/build-wireframes.py`. Never edit a
generated page. A new artboard has to be registered in the `BOARDS` list in
`tools/build-wireframes.py` and given an entry in `wireframes/canvas.json`, or
the build throws `KeyError`.

Board heights live in `canvas.json` as well as in the artboard markup, and they
have to agree or content clips with nothing to show for it.

**Do not run aesthetic-direction skills against this repository.** The look was
settled in August and lives in the tokens. A screen that is not already an
artboard gets drawn as one first; an agent should only ever be implementing a
design.
