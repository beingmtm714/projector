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

`wireframes/_kit.txt` is the list of design values. The artboard bodies carry
the same values inline, because the canvas editor edits inline styles, so a
value in a body that is not in the kit is a mistake. **Never invent one.** If a
colour, size or weight is needed and it is not there, that is a question, not a
decision to make in CSS. `DESIGN.md` carries the rules the tokens cannot
express, and its "Don't" list is the record of what Michael rejected.

`site/wireframes/canvas/index.html` is the design canvas page, generated from
`wireframes/*.dc.html` and `canvas.json` by the Claude Design canvas helper in
Claude Code. No script in this repository regenerates it: after an artboard
edit, ask Claude Code to re-seed the canvas from the wireframes folder, or it
drifts.

## Publishing

GitHub Pages serves `site/` and nothing else, via `.github/workflows/pages.yml`
on every push to `main`. There is no build step in CI; pages are generated
locally by `tools/build-docs.py` and `tools/build-wireframes.py` and reviewed
before they are pushed, so a broken build is never a live one.

Live at https://beingmtm714.github.io/projector/

**Everything in `site/` is public, and so is this repository.** It went public on
2 September 2026 because GitHub Pages is not available for a private repository
on the free plan. There is no access gate any more and there cannot be one:
Pages runs no server code. The Netlify edge function that used to 401 the
investor deck and the pre-seed memo is deleted, and both documents are now
published like every other one. Every page carries
`<meta name="robots" content="noindex">`, which keeps them out of search results
and is not access control.

**So nothing secret goes in this repository, including in a commit that is later
reverted.** History is public too.

## Working on the boards

Edit `wireframes/_body_<Board>.html`, run `python3 wireframes/assemble.py
<Board> <w> <h>`, then `python3 tools/build-wireframes.py`. Never edit a
generated page. A new artboard has to be registered in the `BOARDS` list in
`tools/build-wireframes.py` and given an entry in `wireframes/canvas.json`, or
the build throws `KeyError`.

Board heights live in `canvas.json` as well as in the artboard markup, and they
have to agree or content clips with nothing to show for it.

**Do not run aesthetic-direction skills against this repository.** The look was
settled on 2 September 2026, the movie palace, and lives in `DESIGN.md` and the
tokens. It replaced the August projection-booth system in full. A screen that
is not already an artboard gets drawn as one first; an agent should only ever
be implementing a design.
