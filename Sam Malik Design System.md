---
name: sam-malik-design
description: Design system and brand guide for Sam Malik — a data engineer / cybernetic theory-fiction personal brand. Use to generate on-brand interfaces, portfolio pages, résumés, decks, and assets, in production or as throwaway prototypes/mocks. Self-contained: all tokens, type, voice, components, and usage are inline.
user-invocable: true
---

# Sam Malik — Design System

A personal brand for **Sam Malik**: a recent University of Washington Informatics & Data Science
graduate breaking into **Data Engineering**, and an avid reader of cybernetic theory-fiction
(CCRU, Nick Land, Mark Fisher), transhumanism, and gothic materialism.

This single file is **self-contained** — every token value, font, voice rule, and component API needed
to design on-brand is inline below. Drop it into a project and design from it directly.

---

## 1 · The concept — "Two Currents"

Everything sits on a near-black **void**. Two accent currents cross it:

- **Cybernetic current** — acid terminal **phosphor** (`#c8f24a`), monospace data, decimal/numeric
  indexing (a nod to the CCRU *numogram*), faint CRT glow. *This is the engineer.* Use for anything
  interactive, technical, or "live."
- **Gothic current** — a high-contrast serif (**Cormorant**), **oxblood** (`#8e1c24`), italics,
  hauntological grain. *This is the reader of theory-fiction.* Use for the literary / headline voice.

The result reads as **terminal-meets-gothic**: precise, a little eerie, never decorative.
Keep accent **sparse** — most of any surface is void + bone; phosphor is a *signal*, not a fill.

---

## 2 · Voice & tone (how the brand writes)

- **Voice:** first person (**I**), dry, declarative, a little literary. *"I build the plumbing that
  moves data quietly and correctly."* Confidence without hype.
- **Register:** technical precision braided with theory. A pipeline is named in the same breath as a
  Mark Fisher concept ("Hauntology of the Legacy System"). That friction *is* the brand.
- **Casing:** Sentence case for prose & headlines. **UPPERCASE MONO** for labels, eyebrows, metadata,
  statuses — always letter-spaced ~0.14em.
- **Decimal indices everywhere:** `0.0`, `§ 0.1`, `:01`, `¶ 02`, `k(0)=9`.
- **You vs I:** Sam speaks in **I**. Addresses the reader as **you** only in CTAs ("Get in touch").
- **Tone words:** exact, idempotent, observable, load-bearing; lost futures, the eerie, gothic,
  decimal labyrinth, ruins of the present.
- **Emoji:** **never.** Iconography is restrained Unicode glyphs.
- **Connective tissue:** the middot `·` — `SAM·MALIK`, `Data Engineer · Theory-Fiction`,
  `Seattle · 47.6°N`.
- **Examples:**
  - Eyebrow: `0.0 — DATA ENGINEER / THEORY-FICTION`
  - Headline: *Building infrastructure for lost futures.*
  - Status line: `Pipeline lemuria.0.3 // green`
  - Essay title: *The Lakehouse as Decimal Labyrinth*

---

## 3 · Color

Color is sparse: mostly void + bone, with accent as a signal. Two accents only.

### Ground / voids (darkest → raised)
| Token | Hex | Use |
|---|---|---|
| `--pitch` | `#060608` | deepest layer, wells, page edges |
| `--void` | `#0b0b0f` | **primary background** |
| `--slab` | `#131318` | raised surface / card |
| `--slab-2` | `#1b1b22` | hover / inset surface |
| `--hairline` | `#26262e` | 1px borders, dividers |
| `--hairline-2` | `#34343e` | stronger border on hover |

### Bone / text neutrals (brightest → faint)
| Token | Hex | Use |
|---|---|---|
| `--bone` | `#ece7d8` | primary text — warm paper white (not pure white) |
| `--bone-dim` | `#b6b1a4` | secondary / body text |
| `--ash` | `#847f74` | tertiary, meta, captions |
| `--ash-dim` | `#555049` | disabled, faint labels |

### Cybernetic current — phosphor
| Token | Hex | Use |
|---|---|---|
| `--phosphor` | `#c8f24a` | hero accent, interactive, signal |
| `--phosphor-dim` | `#9bbd38` | pressed / muted accent |
| `--phosphor-deep` | `#2c360f` | accent surface tint on void |
| `--phosphor-glow` | `rgba(200,242,74,.32)` | CRT glow |

### Gothic current — oxblood
| Token | Hex | Use |
|---|---|---|
| `--oxblood` | `#8e1c24` | gothic accent, danger, the literary |
| `--oxblood-lift` | `#b3303a` | hover oxblood |
| `--oxblood-deep` | `#2a0c0f` | oxblood surface tint |

### Semantic signals
| Token | Hex | Use |
|---|---|---|
| `--signal-good` | `#c8f24a` | success (= phosphor) |
| `--signal-warn` | `#e0a838` | warning, amber |
| `--signal-bad` | `#b3303a` | error |
| `--signal-info` | `#6f8fb8` | info, cold steel |

**Semantic aliases:** `--bg-page → void`, `--bg-sunk → pitch`, `--surface-card → slab`,
`--border-default → hairline`, `--text-display → bone`, `--text-body → bone-dim`,
`--text-meta → ash`, `--text-accent → phosphor`, `--accent → phosphor`, `--accent-2 → oxblood`.

---

## 4 · Typography

Three families, one per facet of the brand:

| Role | Family | Use |
|---|---|---|
| **Display** | **Cormorant** (300–700, roman + italic) | gothic high-contrast serif — big headlines, pull-quotes, names. Often italic. |
| **Interface / body** | **Space Grotesk** (300–700) | mechanical grotesque — UI, body, long-form. |
| **Data** | **IBM Plex Mono** (400–600, roman + italic) | labels, code, numerics, the signature UPPERCASE meta style. |

Load (Google Fonts CDN):
```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,300..700;1,400..600&family=Space+Grotesk:wght@300..700&family=IBM+Plex+Mono:ital,wght@0,400..600;1,400..500&display=swap');
```
> ⚠ Fonts load from the Google Fonts CDN, not self-hosted binaries. To self-host, drop `.woff2`
> files in and replace the `@import` with local `@font-face` rules.

**Families:** `--font-display: 'Cormorant', serif` · `--font-ui: 'Space Grotesk', sans-serif` ·
`--font-mono: 'IBM Plex Mono', monospace`

**Scale (16px base):** `--t-mega 7rem` · `--t-display 4rem` · `--t-h1 2.25` · `--t-h2 1.625` ·
`--t-h3 1.25` · `--t-lg 1.125` · `--t-body 1` · `--t-sm .875` · `--t-xs .75` · `--t-micro .6875`

**Rules:** Display set tight (`letter-spacing −0.02 to −0.03em`, line-height ~1.0).
Mono labels spaced wide (`letter-spacing .14em`, uppercase). Body in Space Grotesk, line-height ~1.6.

**Signature mono label** (`.sm-label`): `font: 11px IBM Plex Mono; letter-spacing:.14em; text-transform:uppercase; color: ash`.

---

## 5 · Spacing, radii, effects

- **Spacing** (8px grid): `--sp-1 4` · `2 8` · `3 12` · `4 16` · `5 24` · `6 32` · `7 48` · `8 64` · `9 96` · `10 128`.
- **Radii** (hard gothic edges): `--r-none 0` · `--r-sm 2px` · `--r-md 3px` · `--r-pill 999px`. Corners stay sharp; pills only for status dots.
- **Borders:** structure is carried by **1px hairlines**, not soft shadows. `--bw-hair 1px` · `--bw-thick 2px`.
- **Shadows** (mostly flat): `--shadow-none` default; `--shadow-lift` / `--shadow-deep` (deep black) when elevation is truly needed.
- **CRT glow** (restrained, phosphor only): `--glow-sm` / `--glow-md` / `--glow-text`. Use on primary actions and signal text — never everywhere.
- **Texture:** hauntological **grain** overlay (`--grain`, ~3.5% screen-blended fractal noise) and optional CRT **scanlines** (`.sm-scan`). No photographic imagery in the core system. **No gradient meshes** — explicitly off-brand.
- **Motion:** mechanical, no bounce. `--ease cubic-bezier(.22,.61,.36,1)`, `--ease-out cubic-bezier(.16,1,.3,1)`, durations `--dur-fast 120ms / --dur 180ms / --dur-slow 320ms`. Page transitions = 6px rise + fade (animate **transform only**, never gate content opacity on an animation). No infinite decorative loops on content.
- **Hover:** accent brightens, border lifts to `--hairline-2`, surfaces step to `--slab-2`, links draw a phosphor underline. **Press:** 1px downward nudge (`translateY(1px)`), no color flip.
- **Focus:** 2px phosphor ring with a void gap + glow.
- **Transparency/blur:** only the sticky nav — void at ~82% with a 10px backdrop blur (HUD effect).

---

## 6 · Iconography

**Glyph-first, not icon-library-first.** Typographic marks carry meaning:

- `›` prompt / list bullet · `→` forward / link · `§` section · `¶` essay · `///` and `·` separators · `▲ ▼` trend · `↳` source.
- **Status** = a small glowing dot (phosphor = live, ash = done, dim = shelved), not an icon.
- **No emoji, ever.** No multicolor icon set.
- **Logo / monogram are typographic:** the `SAM·MALIK` wordmark (Cormorant + phosphor middot) and the
  `SM` "gate" monogram (numogram-flavored square).
- If line icons are ever needed, substitute **Lucide** at 1.5px stroke (matches the hairline weight) — and flag the substitution.

---

## 7 · Components (React primitives)

Self-contained React components styled entirely via the CSS variables above. Named PascalCase exports.

- **Button** — primary action. Mono UPPERCASE label, hard edges, phosphor glow on primary.
  Variants `primary | secondary | ghost | danger`; sizes `sm | md | lg`; props `icon`, `iconRight`, `full`, `as="a"`, `disabled`.
  ```jsx
  <Button variant="primary" iconRight="→">Deploy pipeline</Button>
  <Button variant="danger">Drop table</Button>
  ```
- **Tag** — mono metadata chip (tech, category, status). Variants `default | phosphor | oxblood | outline`; `dot` adds a glowing status indicator.
  ```jsx
  <Tag variant="phosphor" dot>Live</Tag>  <Tag variant="oxblood">Hauntology</Tag>
  ```
- **Card** — raised void surface. `index="0.3"` prints a decimal label in the corner; `interactive` adds hover lift; `accent` adds a phosphor top edge; `padded={false}` for full-bleed.
- **Input** — single-line field. Mono UPPERCASE label, sunk well, phosphor focus. `prompt` adds a leading `›`; `invalid` switches to oxblood; `hint` for helper/error text.
- **DataField** — labeled metric readout (the engineering signature). `label`, `value`, `unit`, `index=":01"`, `trend="up"|"down"`, `mono={false}` to render the value in the gothic serif.
- **Rule** — hairline section divider with optional mono `label` + `index` (e.g. `§ 0.0`), `align`, `accent`.
- **Marquee** — continuous mono ticker / signal band; `items[]`, `speed` (sec/loop), `variant`, `sep`. Pauses on hover.

**Composition pattern (a work card):**
```jsx
<Card index="0.1" interactive accent>
  <Tag variant="phosphor" dot>Live</Tag>
  <h3>Lemuria</h3>
  <p>Exactly-once CDC from 40+ Postgres shards into an Iceberg lakehouse.</p>
  <DataField label="Freshness" value="48s p99" />
</Card>
```

---

## 8 · Using this in a project

1. Apply the **color + type tokens** as CSS custom properties on `:root` (Section 3–5), and load the
   font `@import` (Section 4). That alone makes any page feel on-brand.
2. Headings default to **Cormorant**; body to **Space Grotesk**; labels/data to **IBM Plex Mono**.
3. Backgrounds are solid **void**; structure with **1px hairlines** and hard corners; accent **sparingly** with phosphor; reserve oxblood for the literary/danger voice.
4. For visual artifacts (slides, mocks, résumés), build static HTML using these tokens. For production, recreate the components in Section 7 against your framework.
5. **Never:** emoji, gradient meshes, soft rounded cards, content whose visibility depends on an animation completing.

**Canonical surfaces in the full system:** an interactive portfolio site (home · work · writing · about)
and a one-page gothic-terminal résumé/CV (print/PDF ready).

> Built in the ruins of the present. © Sam Malik.
