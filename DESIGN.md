# Projector — Design Language

## The thesis

**The system is the room, not the film.**

A repertory house in Los Angeles has enormous personality and does not change it when the programme changes. The Vista is the Vista whether it is showing Murnau or a midnight Hangover 2. The room is the constant, the film is the variable, and an audience understands that without being told.

Everything below follows. The interface never comments on what is being screened. It is the place you came to watch it. **A film's identity appears in exactly one place, the one-sheet, and nowhere else.** The marquee changes weekly. The building does not.

## Expressionism as a lighting model

The reference is German Expressionism and the noir that came out of it, taken as technique rather than costume.

The lasting contribution of Caligari is not crooked sets. It is that **light and shadow do the emotional work, and shadow is an active agent rather than an absence**. Noir points the same technique at moral ambiguity: a hard key, deep falloff, things half seen. Sunset Boulevard is lit the way it is because the film is about what a house conceals.

That is also what this product does. A curator takes an audience past the surface of a film into what is going on underneath. The design enacts that rather than illustrating it, which is why there is no set dressing anywhere in this document.

**The test: light has a direction and a source.** Every surface is legible because something is lighting it. If a screen could be flipped upside down without looking wrong, it is painted rather than lit, and it is not finished.

## Two states

**House up.** Everything before and after the film. Warm ambient falling from above, no visible source. Matte, low contrast, no glow. A lobby with the lamps low.

**House down.** The film itself. Near black, one cold key from above and behind, the way a projector sits over your shoulder. Everything falls off toward the bottom of the screen.

A surface declares its state with `.up` or `.dn`, which supply the light. Nothing else sets a ground.

**Squint at any two screens from opposite states. They must read as the same building at a different time of night.** If either reads as a different place, the model is broken and no token will fix it.

## Palette

| Token | Value | Job |
|---|---|---|
| `--house-up` | `#141210` | Warm ground, before and after |
| `--house-down` | `#0a0b10` | Cold ground, during the film |
| `--paper` | `oklch(0.93 0.005 75)` | Primary type |
| `--gold` | `#f4e4bc` | Warm light. Never hardware |
| `--silver` | `#f2f7ff` | The live signal, rationed |
| `--time` | `oklch(0.72 0.13 240)` | Sync position |
| `--curtain` | `#7c1f2e` | Light on cloth, T-0 and intermission only |
| `--hair` | `oklch(0.30 0.006 60)` | Borders |
| `--dim` / `--dimmer` | `oklch(0.58 / 0.44 …)` | Secondary and tertiary type |

Values live in `projector/wireframes/_kit.txt` and nowhere else. **Never invent one.** If a colour, size or weight is needed and it is not there, that is a question, not a decision to make in CSS.

## The live signal

Electric silver is the only thing that says *this is happening now*. It is rationed to four places: the ON AIR sign and its dot, the curator's name on a firing note, the primary action at showtime, and telestrator ink.

It always carries its glow.

```
color: #f2f7ff;
text-shadow: 0 0 8px rgba(244,248,255,.85), 0 0 22px rgba(150,190,255,.5);
box-shadow: 0 0 7px rgba(255,255,255,.6), 0 0 20px rgba(160,195,255,.55);
```

**A resting surface never gets silver and never glows.** On the Marquee the single on-air card is the only lit thing in a warm dim room. That contrast is the system working, not a decorative choice.

## The curtain

You never see a cinema curtain evenly lit. You see it raked, almost always from below, and its whole visual identity is vertical bands of light and shadow. It is the most Expressionist object in the building, which is why it survives when the rest of the memorabilia did not.

Oxblood is **the colour light picks up off cloth**: deep in the folds, warmer where the wash catches. It is never a fill. Use `.cloth`.

**It parts as darkness opening, not as panels sliding.** The gap is black and the inner edges catch a cold rim as they turn into the light. Use `.lip`.

Oxblood appears at T-0 and at intermission. Nowhere else, on any screen, for any reason.

## Grain

Film grain, scratches and dust appear where light is **projected**: the leader, the curtain wash, T-0. Use `.grain` and `.scratch`.

They never touch chat, the note editor, the Marquee, or any resting surface. That single rule is what keeps this from being a filter, keeps type legible, and stops a phone rendering noise for two hours.

The leader carries the most, which is true to life: the academy leader is the most-handled few feet of any print.

## Type

- **Archivo Expanded**, 125% width, for title cards and the marquee.
- **Hanken Grotesk** for interface.
- **Source Serif 4** is **the curator's voice**: Liner Notes, the one-sheet, her answers in the wrap. Never chat, never an interface label. The rule is about whose voice it is, not which component it is.
- **JetBrains Mono**, tabular, for timecode, countdowns, and anything that ticks.

## Chat

Chat is the room's default surface, always labelled, and it never leaves the screen. When a curator element fires it settles to a strip at the bottom, then expands back.

In house down it lives in the deepest part of the falloff. That is correct rather than incidental: it is the murmur of the room, and it belongs below the beam.

## Always on screen

Once the film runs, the title and the min:sec position are visible on every surface. Intermission shows `paused` with the timestamp. A viewer glancing at their phone always knows what is playing and where the room is.

## Motion

**The beam is struck, then allowed to decay.** Light arriving is an event; light leaving is not. `--beam-rise: 220ms` on `--ease-strike`, `--beam-fall: 640ms` on `--ease-decay`. Symmetrical timing makes a note cross-fade rather than land.

**One cue, then the next. Never both.** When a note fires, chat settles to its strip first over `--settle: 900ms`, and the beam comes up as it lands. Moving them together reads as a glitch.

**A note holds long enough to be read twice**, because the viewer looks up at the television in between. Four seconds plus reading time, floored at five, capped at nine. A fixed hold is too long for a short note and too short for a long one.

**Notes fade up like subtitles**: 4px rise, soft haptic, no badge.

**The curtain travels for ten seconds.** Real curtains take eight to twelve, and a fast curtain reads as cheap in a way that is hard to name and easy to feel.

Everything respects `prefers-reduced-motion`.

## The pre-show

The house settles first, and the leader only begins once the curtain is fully open, so nobody arrives mid-countdown.

| When | What |
|---|---|
| T&minus;30:00 | Doors. The Lobby opens, chat with the curator begins |
| T&minus;10:00 | The house call |
| T&minus;2:00 | The last call: starting in two minutes, cue the film on your TV |
| T&minus;1:00 | The curtain appears behind the chat |
| T&minus;0:25 | Chat settles to a strip, then the curtain begins to part |
| T&minus;0:15 | Fully open. The leader runs on the revealed surface, with grain |
| T&minus;0:00 | The leader ends, the sign ignites, the Room |

**There is no notification at T-1.** The curtain appearing is the one-minute call, and it is a better one: visible, permissionless, impossible to miss by someone already looking at the screen.

The surface revealed by the curtain is the app's own live area. The leader plays on it, then it becomes the Room. The curtain is not decoration around a screen; it reveals the thing you will spend two hours in.

Falling behind later is never a failure. It is a reel change.

## Form factors

Curator authoring screens are **desktop, 1440 by 900**, and are not responsive down to a phone. Below about 1100px they show a come-back-on-a-laptop message rather than a squeezed layout.

Two exceptions get a phone layout at **390 by 800**: Go live and On air. The curator hosts with the film on her television and the app in her hand, so she is an audience member with extra controls. Controls sit at the bottom, within reach of a thumb.

Every audience screen is a phone.

## Don'ts

- No silver and no glow on a resting surface, prep and session ready included.
- The serif never appears in chat and never on an interface label.
- Gold never appears mid-film, chat handles included; those take paper on the house-down ground.
- Curtain oxblood appears at T-0 and intermission and nowhere else.
- No grain on a resting surface.
- No badges and no unread counters on Liner Notes.
- Intermission stays matte and empty. No countdown glow, no decoration.
- No bulbs, no chases, no marquee hardware. The gold is light.
- Never design a surface that works for arthouse but not popcorn, or the reverse.

## Working against this

The eleven artboards in `projector/wireframes/` are the pixel references, and `_kit.txt` is the only source of values. Build against the artboard rather than against taste: serve, screenshot, compare image to image, change one property, re-screenshot. The `visual-loop` skill carries that discipline.

Do not run aesthetic-direction skills against this repo. The look is settled and lives in the tokens.

**A screen that is not already an artboard gets drawn as one first**, in the canvas, and only then built against the picture. An agent should only ever be implementing a design.
