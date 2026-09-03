# The Playback Room — Design Language

The product recreates a night at the movies: a marquee out front, a lobby full of people, curtains, a dark room, a curator who runs the show. Every visual decision serves that ritual. The system must carry *In the Mood for Love* and *Road House* with equal conviction — test any new surface against both before shipping it.

## Three temperatures

The app moves through three color temperatures over the course of a night. They never mix.

1. **Marquee (anticipation).** Warm bulb-gold on near-black. The lobby board, the showtime calls, the resting marquee. Incandescent, not fluorescent.
2. **Curtain (threshold).** Oxblood red. Appears exactly twice: the curtain that parts at T-0, and nowhere else. It is a moment, not a theme.
3. **Night (the show).** Blue-black ground, off-white type, hairline borders. The whole live experience plays here.

At rest, the app is matte: typographic, hairlines, zero glow. A monograph, not a poster.

## Palette

| Token | Value | Job |
|---|---|---|
| Night ground | `#12141f` | Live-room background |
| Resting ground | `#1a1917` | Everything not live |
| Paper | `oklch(0.93 0.005 75)` | Primary type |
| Bulb gold | `#f4e4bc` on `#14110b` | Marquee board, countdowns, pre-show |
| Curtain | `#7c1f2e` (folds `#5c131c`) | T-0 only |
| Electric silver | `#f2f7ff` | The live signal — see below |
| Timecode blue | `oklch(0.72 0.13 240)` | Sync position |
| Hairline | `oklch(0.32 0.006 60)` | Borders everywhere |

## Light, not paint

Electric silver is the only live signal, and it is rationed. It fires for: the ON AIR sign and dot, the "now" tick on a firing Liner Note, the primary button at showtime, Telestrator ink. Nothing else. It always carries its glow — a tight white core with a cold blue halo:

```
color: #f2f7ff;
text-shadow: 0 0 8px rgba(244,248,255,.85), 0 0 22px rgba(150,190,255,.5);
box-shadow: 0 0 7px rgba(255,255,255,.6), 0 0 20px rgba(160,195,255,.55), 0 0 40px rgba(120,165,255,.30);
```

The cold cast against warm gold and oxblood is what makes it read electric. If a surface is not live, it gets no silver and no glow.

## The curtain mark

The curtain's one lasting presence outside T-0 is a soft scallop bled into the top corners of every live and paused screen — never fabric with a straight edge, never a shape with a point. Three attempts got cut before this one: a rendered valance and pleated screen edges read as costume department, not brand system; a typographic `)( ` glyph worked but competed with the timecode it sat next to and wasn't worth the added punctuation. What survived is quieter than either — cloth barely caught at the edge of frame, built from a single smooth curve, not a geometric wedge:

```
width: 92px; height: 46px; position: absolute; top: 0; z-index: -1; pointer-events: none;
background-image: url("data:image/svg+xml,...");  /* one <path> with a quadratic Q curve, no straight edges */
/* left corner: left: 0;   right corner: same image, right: 0; transform: scaleX(-1); */
```

The SVG path is a single quadratic curve — `M0,0 Q44,44 88,0 Z` — filled with an oxblood-to-transparent gradient and a light Gaussian blur. No clip-path, no polygon, no vertex: a straight-edged triangle reads as geometry; a curve with a soft blurred edge reads as cloth. **Content always paints on top of the corners, never the reverse.** That only holds if the screen's `.scr` establishes its own stacking context (`position: relative; z-index: 0;`) — without the explicit `z-index: 0`, a `z-index: -1` child can bubble past its intended parent and paint behind the whole phone frame instead of just behind the header. Skip T-0: it's already the full curtain, and a corner catch on top of curtain fabric is redundant.

Used everywhere a live or paused screen states its film and position together: the Room headers, note arrival, intermission ("paused"), Telestrator, reel change, the curator's on-air console. The film title and timecode simply sit next to each other, joined by a plain `·` — no custom punctuation, no glyph to maintain.

## Type

- **Archivo Expanded** — title-cards and the marquee. On the board it goes warm bulb-white with a soft incandescent shadow.
- **Switzer / Hanken Grotesk** — UI.
- **Source Serif 4** — Liner Notes only. The serif is the curator's voice; chat never gets it.
- **JetBrains Mono** — timecode, countdowns, labels, anything that ticks.

## The chat rule

Chat is the room's default surface, always labeled (`THE ROOM — CHAT`). It never leaves the screen. When a curator element fires — Liner Note, Telestrator, the curtain itself — chat minimizes to a strip at the bottom (label, ghost line, expand cue). A Liner Note holds ~7 seconds: read, look up at the TV, read again. The Telestrator holds until the curator releases it. Then chat expands back.

## Always on screen

Once the film runs, the title and the min:sec position are visible somewhere on every surface. Intermission shows `paused` with the timestamp. A viewer who glances at their phone always knows what's playing and where the room is.

## The pre-show ritual

Doors open at T-30: marquee board (film, start time, runtime, countdown) over open chat with the curator. The house calls at −10:00 and −1:00 ("cue the film on your TV"). At −0:15 a film leader takes the screen — rings, crosshair, sweep — and the room counts down together. On zero the curtains part and the sign ignites. Desync later is never a failure; it's a reel change.

## Motion

Notes fade up like subtitles (4px rise, soft haptic, no badge). Bulbs chase in a slow two-step. The live dot breathes. Curtains part once. The leader sweeps once per second. Everything respects `prefers-reduced-motion`. No bounce, no elastic, nothing that draws attention to itself.

## Don'ts

- No silver on resting surfaces. No glow at rest.
- No badges or unread counters on Liner Notes.
- The serif never appears in chat; the marquee gold never appears mid-film.
- Intermission stays matte and empty — no countdown glow, no decoration.
- Spec notes and internal instructions live in documentation, never inside the UI.
- Never design a surface that works for one register (arthouse or popcorn) but not the other.
