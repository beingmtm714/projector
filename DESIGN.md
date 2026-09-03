# Projector design system

The look of every Projector screen. Read this before drawing or building anything. The wireframe guide in the vault says what each screen is for; this file says how it looks. Approved by Michael on 2026-09-02 after six rounds on the phone room and the curator's note editor, and every rule in the "Don't" section came out of that review.

## Premise

A movie palace in your hand. Velvet, gold leaf and a marquee for the blockbuster crowd; a serif, a repertory listing and restraint for the Criterion crowd. The phone is a companion to the television, so nothing on it competes for the eye.

## Palette

Six colours plus two neutrals. Every screen uses the ground, the paper, crimson and gold. Teal and emerald are small accents, never fills. Use each hex as written; there is one crimson and one gold.

| Role | Hex | Use |
|---|---|---|
| Plum ground | `#1A0F2E` | Phone background, dark panels, text on paper |
| Plum raised | `#2B1A4A` | Chat bubbles, inputs on plum |
| Plum line | `#5A3C7A` | Borders on plum, secondary buttons on plum |
| Ivory paper | `#FBF1DC` | Desk background, Liner Note tickets, text on plum |
| Parchment | `#EFE3CC` | Chips and quiet fills on paper |
| Crimson | `#A3122B` | Marquee, primary buttons, moment stamps, note labels |
| Gold | `#F2C75C` | Titles on plum, timecodes, active tab, bulbs, rules |
| Teal | `#1C8C9E` | The session clock, one avatar, dashed frame slots |
| Emerald | `#2FA37A` | Intermissions, one avatar, the one card shadow on the desk |
| Muted on plum | `#C9A96E` | Secondary text on dark |
| Muted on paper | `#7A6A5A` | Secondary text and section labels on light |
| Placeholder | `#A08A5E` | Empty inputs |
| Crimson deep | `#5E0A1A` | Link hover only |

White `#FFFFFF` is allowed for the main card on a desk screen and nowhere else.

## Type

Three faces, from Google Fonts, each with a fallback.

- **Instrument Serif** (regular and italic). Film titles, Liner Note prose, the italic "Liner Note · Nadia" label, panel headings, anything a cinephile reads. Fallback Georgia.
- **DM Sans** (400, 500, 700). All interface text: chat, buttons, metadata, labels. Fallback Helvetica Neue.
- **Space Mono** (700). Timecodes and the session clock only. Fallback Menlo.

Sizes that recur: film title 24px on the phone and 30px on the desk, note prose 18px/24px on the phone and 24px/32px on the desk, chat 15px/20px, metadata 12px/16px, section labels 12px uppercase with 0.1em tracking in muted-on-paper. The big moment field on the desk is 72px Space Mono in a gold tile.

Never set a title in heavy uppercase grotesque. The year and running time sit beside the title in italic serif, smaller, like a repertory listing: "The Long Hour *1974 · 84 min*".

## Components

**Marquee (phone header).** Crimson rounded panel, 18px radius, 8px padding. A row of seven 8px bulbs alternating ivory and gold, no glow. Inside, a plum box with the film title in gold serif, a metadata line beneath, and the clock pill on the right.

**Clock pill.** Teal, ivory text, 10px radius. Space Mono time over a 9px uppercase "Now". This is the only teal fill on the phone.

**Liner Note ticket.** Ivory, 12px radius, 12px by 14px padding, with two plum semicircle notches at the vertical middle of each side. Header row: italic serif "Liner Note · Nadia" in crimson on the left, moment stamp on the right. Prose in serif below. If the note carries a frame, it shows as a 96px thumbnail to the left of the prose, 2.39:1, with a 1px plum border. Every Liner Note looks identical, fired or pending, old or new. No dimming, no highlight, no colour change for the newest.

**Moment stamp.** Crimson, ivory Space Mono digits, 6px radius, 2px by 7px padding.

**Frame open.** A near-black scrim over the room, `rgba(12, 6, 24, 0.92)`. The frame full width at 2.39:1 with a 1px gold border, label and stamp above, prose below, and two 48px buttons at the bottom: a plum-line secondary and a gold primary.

**Chat bubble.** Plum raised, 16px radius with a 4px bottom-left corner, 9px by 13px padding, ivory text. A 28px avatar circle to the left with the initial in plum on gold, teal or emerald. No timestamps, no read marks, no unread counters anywhere.

**Composer.** 48px pill, plum raised with a plum-line border, placeholder in the placeholder colour. Send is a 48px crimson circle with an ivory arrow.

**Arrangement switcher.** Three 44px pills in a row under the composer. Active is gold with plum text, inactive is a plum-line outline with muted-on-plum text. Labels: Chat, Notes, Quiet.

**Buttons.** 48px on the phone, 52px on the desk, fully rounded. Primary is crimson with ivory text on the desk and gold with plum text on the phone. Secondary is an outline in the surface's line colour. Type is DM Sans 700, mixed case.

**Desk header.** 80px crimson bar with a 4px gold rule beneath. Back link in gold on the left, film title in gold serif, metadata in muted-on-plum, a gold status pill on the right.

**Desk card.** White, 2px plum border, 24px radius, one emerald offset shadow of 8px. A crimson label tab overlaps the top-left corner in italic serif, sitting straight.

**Running order panel.** Plum, 24px radius, no border, no shadow. Rows of gold dot, gold Space Mono timecode, ivory first line. The row being edited is a gold fill with plum text and a small crimson "writing" badge. Intermissions are an emerald dashed outline with the label in teal.

**Section label.** 12px DM Sans 700, uppercase, 0.1em tracking, muted-on-paper on light surfaces and muted-on-plum on dark. "Optional" trails in the placeholder colour, mixed case.

**Disabled button.** Parchment fill, placeholder-colour text, no border. The reason it is disabled sits beside it in plain words, never in a tooltip.

**Icons.** Inline stroke SVG on a 24px grid, 2px to 2.4px stroke, round caps. Never emoji.

## Frames

Phone 390 by 844 with 52px top padding left clear for the real status bar and 24px at the bottom. Desk 1440 by 900. The root element is sized to the frame. No fake status bar, no fake keyboard, no device bezel.

## Product rules that shape the design

- The phone is a companion. Nothing on it demands attention. No badges, counters, or pulsing.
- Every Liner Note stays in the conversation after it fires.
- Any control used during the film is thumb-reachable and at least 44px tall.
- The moment field is the primary control on the note editor. Prose is secondary.
- Falling behind is never worded as an error.
- The account ask appears once, four minutes into Lights Up, and nowhere else.
- Go live stays disabled until there is at least one armed note and a showtime.

## Don't

- Don't highlight the newest Liner Note in yellow or any other colour. All notes are identical.
- Don't run a frame full width inside the chat. It is a thumbnail until tapped.
- Don't add glow to the bulbs, a sunburst behind the header, a dotted paper pattern, or pinstripe rings.
- Don't rotate stickers, rows or labels.
- Don't stack shadows. One offset shadow per desk screen, on the main card.
- Don't use more than one teal and one emerald element per screen. They are accents.
- Don't use a second crimson or a second gold.
- Don't use heavy uppercase display type. The serif does that job.
- Don't draw a status bar, a keyboard, or a device frame.
- Don't dim, shrink or grey out older notes.

## Files

`wireframes/_kit.txt` holds the palette as CSS custom properties and the font link. The artboard bodies in `wireframes/_body_*.html` carry the same values inline, because the canvas editor's property panel edits inline styles. A value in a body that is not in the kit is a mistake, and the fix goes in the kit first. `wireframes/canvas.json` lays the boards out on two pages, Audience and Curator. `Main.dc.html` is the cover.

The boards are published at https://beingmtm714.github.io/projector/wireframes/ and the editable canvas is a Claude artifact. Sample data on every board is invented: the film "The Long Hour" (1974, 84 min), curator Nadia Reyes, and the audience names Theo, Priya and Marcus.
