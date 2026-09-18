# Design: Vibe Code Camp

Future retro, playful but serious, terminal-nerdy, one coherent whole across the game (`src/style.css`), the terminal companion (rich and Textual), the vault (`vault/.obsidian/snippets/vibe.css`) and the docs. The palette is fixed by `toms-toolbox.toml [palette]`; every number below was fetched or measured on 2026-09-16 (sources at the end).

## Principles

1. **Black is the canvas, colour is a signal.** Each hue means one thing (red action and errors, green done, blue paths and organisation, yellow curiosity and warnings, orange XP), like Blueprint's four intents and Powerlevel10k's `prompt_char` that "turns red on error". Example: the only green on the stage is a lit OKR rune.
2. **Dense but calm.** Blueprint is "optimized for building complex, data-dense web interfaces"; density is earned with size and muted text, not boxes. Example: the KPI row is three Sora numerals with 10px muted labels and no card.
3. **State at a glance, like a prompt.** Powerlevel10k shows that "the effect of every command is instantly reflected by the very next prompt". Example: every screen opens with one status line: name, persona, level, XP, stops done.
4. **Elevation is light on an edge, not a shadow.** Blueprint's dark elevation is `inset 0 0 0 1px rgba(white, 20%)` plus a soft drop; on OLED black a shadow is invisible, so levels are surface tints plus a hairline. Example: sheet on surface-1, title box on surface-2.
5. **Motion explains, then leaves.** One motion per component, 150 to 400 ms, `transform` and `opacity` only (web.dev), inside NN/g's 100 to 500 ms window, and honoured `prefers-reduced-motion`. Example: the Enter pill rises 8px in 300 ms; with reduced motion it fades.
6. **Warmth through words, one accent, restraint.** Claude's product design uses cream `#FAF9F5`, sand `#E3DACC`, one terracotta accent `#D97757`, serif headlines and plain copy; we keep Sora headings, Rolinda's voice, and one yellow primary button per view.
7. **Retro is a seasoning.** Exactly three future-retro touches, each under 8 percent opacity or bounded in time, never on body text.

## Tokens

```css
:root{
  --bg:#000000; --surface-1:#0A0A0A; --surface-2:#141414; --surface-3:#1A1A1A;
  --hairline:rgba(255,255,255,.10); --hairline-2:rgba(255,255,255,.18);
  --text:#F1F1F8; --muted:#8B93A7;
  --red:#D32F2F; --red-dim:#9A2A2A; --red-bright:#F04923;
  --orange:#FF8C1A; --orange-dim:#C26A14; --orange-bright:#FFA94D;
  --yellow:#FFBF00; --yellow-dim:#C29200; --yellow-bright:#FFD500;
  --green:#00A86B; --green-dim:#0A7A52; --green-bright:#00D084;
  --blue:#0067A5; --blue-dim:#0A4E7A; --blue-bright:#0088CC;
  --radius-s:8px; --radius-m:12px; --radius-l:16px; --radius-pill:999px;
  --space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px; --space-6:24px; --space-8:32px;
  --font-display:Sora,system-ui,sans-serif; --font-body:Inter,system-ui,sans-serif;
  --font-mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  --text-xs:10px; --text-sm:13px; --text-md:16px; --text-lg:22px; --text-xl:clamp(28px,7vw,40px);
  --edge:inset 0 0 0 1px rgba(255,255,255,.08); --lift:0 10px 30px rgba(0,0,0,.6);
  --glow-green:0 0 12px rgba(0,208,132,.45); --glow-yellow:0 0 12px rgba(255,213,0,.40);
  --t-fast:150ms; --t-base:240ms; --t-slow:400ms; --t-sky:2s;
  --ease:cubic-bezier(.4,1,.75,.9); --ease-out:cubic-bezier(.2,.8,.2,1);
}
```

Measured contrast on `#000000`: text 18.7:1, muted 6.8:1, yellow 12.7, orange 9.0, green 6.8, red 4.2, blue 3.5. So base red and base blue are fills, borders and 3D materials only; as text use `--red-bright` (5.7:1) and `--blue-bright` (5.4:1). Filled buttons: black text on yellow, orange or green; white text on blue (5.4:1); never text on a red fill.

| Token | Game CSS | Textual `Theme(...)` and CSS | rich style (`palette.py`) | Obsidian snippet |
| --- | --- | --- | --- | --- |
| background | `--bg` | `background="#000000"`, `$background` | default | `--background-primary`, `--color-base-00` |
| surface 1, 2 | `--surface-1/2` | `surface="#0A0A0A"`, `panel="#141414"` | `Panel(border_style="accent")` | `--background-primary-alt`, `--background-secondary` |
| text, muted | `--text`, `--muted` | `foreground="#F1F1F8"`, `$text-muted` | default, `muted` | `--text-normal`, `--text-muted` |
| red | `--red*` | `error="#D32F2F"`, `$error` | `err` | `--color-red`, `--color-red-rgb` |
| green | `--green*` | `success`, `accent="#00A86B"` | `ok`, `done`, `accent` | `--color-green`, `--text-success` |
| blue | `--blue*` | `secondary="#0067A5"` | `path` | `--color-blue`, `--text-accent` |
| yellow | `--yellow*` | `primary`, `warning="#FFBF00"` | `title`, `warn` | `--color-yellow`, `--text-warning` |
| orange | `--orange*` | `variables={"xp": "#FF8C1A"}` | `xp` | `--color-orange` |
| radii | `--radius-s/m/l` | not applicable (cells) | not applicable | `--radius-s/m/l` (4, 8, 12px) |
| spacing | `--space-*` | `padding: 1 2` (cells) | `padding=(0, 1)` | `--size-4-1` to `--size-4-8` |
| mono | `--font-mono` | terminal font | terminal font | `--font-monospace-theme` |
| motion | `--t-*`, `--ease*` | none by default | spinner only | Obsidian's own |

Textual: `dark=True`, register with `self.register_theme(theme); self.theme = "vibe"`.

## Components

| Component | Look | The one motion | Accessibility |
| --- | --- | --- | --- |
| Title screen | Surface-2 box, `--radius-l`, hairline-2, Sora h1, three paragraphs, name input, one yellow primary button | Box fades in and rises 8px, 300 ms `--ease-out` | Input keeps `aria-label`; 2px `--yellow-bright` focus ring, offset 2px; reduced motion: opacity only |
| HUD pills | Pill radius, surface-1 at 78 percent with blur, 10px uppercase, 7px rune dots | Rune fills green over 240 ms | Buttons at least 32px tall; muted labels 6.8:1 |
| KPI tiles | Sora tabular numerals in `--text` (no gradient text), 10px muted labels | Number counts up over 400 ms | Group has `aria-live="polite"` |
| Sheet (lesson) | Surface-1, hairline top, 640px column, `pre` in mono 12.5/1.5 on surface-2 | Smooth `scrollIntoView` (exists) | `role="dialog"` plus `aria-labelledby` the h2; Close first in tab order; Escape closes |
| Callouts | 1px border at 40 percent hue, fill at 8 percent, 10px uppercase label in the bright variant: done green, why blue, try yellow, Rolinda orange 3px left rule, italic | None | The label word carries the meaning, colour never alone |
| Buttons | Secondary: surface-2, hairline-2, `--text`. Primary: yellow fill, black text (12.7:1). Danger (reset): `--red-bright` text and border, no fill | Hover lifts 1px in 150 ms; active resets | `:focus-visible` ring as above; disabled keeps text at 35 percent opacity plus a "blocked" word |
| Dashboard tiles | Surface-2 card, `--radius-m`, 10px uppercase muted label, Sora tabular numeral, 11px caption, a 120 by 26 sparkline in the tile's hue; a tile whose seven days are all zero shows no line | None | The tile group is `aria-live="polite"`; the number is never colour alone |
| Charts (game panel and `vibe dashboard`) | Inline SVG sized by its `viewBox`, so one layout works from 393px up: rings for progress (green when full, yellow while in progress), one orange line for XP, a single-hue green heatmap for activity, blue bars for magnitude, red never used for a value. Thin marks, 4px rounded data ends, recessive `--hairline` grid, mono tabular labels | None | Every chart is `role="img"` with an `aria-label` that states the reading, every mark carries an SVG `<title>`, and a legend names what colour means |
| Vault graph and reader | Black canvas; nodes by tag (workstream green, people blue, tech yellow, decision red, concept orange, as in `vibe.css`); links white 16 percent; selected halo `--blue-bright` at 25 percent. Reader: Inter 15/1.6, wikilinks `--blue-bright` | Halo scales 1 to 1.15 in 240 ms on select; the force layout is content, not decoration | Canvas `aria-label` with counts; every note reachable through the Tech tree buttons by keyboard; links focusable |
| TUI welcome | `Panel` with `accent` border, `title` style header, one status line: name, persona, level, XP, stops | None | Pass and fail are words, colour is extra |
| TUI checks | Table tool, tier, status, what; status `ok`, `err` (missing), `warn` (hint) | Spinner only while a probe runs | Documented install command printed in `path`, copyable |
| TUI launcher | Numbered `Button` list: game, vault, docs, claude; focused button uses `$primary` | None | Keys 1 to 9 bound, footer lists them |
| TUI map | The 4 by 8 grid from `status`: done `ok`, todo `muted`, current `warn` | None | Legend line under the grid |
| README hero | One title line, one sentence, a fenced block of three lines of `just start` output, one 1200 by 630 screenshot on black | None; a GIF only if under 3 MB and shows one action | Alt text names the screen; no badge row longer than one line |

## Future-retro touches

1. **Scanlines on the title box only** (adapted from Alec Lownes' CRT CSS, which uses `rgba(0,0,0,.25)` at 2px; ours is 4 percent):

```css
#title .box{position:relative;overflow:hidden}
#title .box::after{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(0deg,transparent 0 1px,rgba(0,0,0,.04) 1px 2px);
}
```

2. **Phosphor glow on an OKR rune when it lights** (the one glow on the stage):

```css
.pill i.on{background:var(--green-bright);box-shadow:var(--glow-green)}
@media (prefers-reduced-motion:no-preference){
  .pill i.on{animation:rune 400ms var(--ease-out)}
  @keyframes rune{0%{transform:scale(.6);box-shadow:none}
    60%{transform:scale(1.3);box-shadow:0 0 18px rgba(0,208,132,.8)}100%{transform:scale(1)}}
}
```

3. **Typewriter on Rolinda's line**, 20 ms per character, capped at 1.2 s, in `say()`:

```js
function type(el,text){
  el.setAttribute("aria-label",text);
  if(matchMedia("(prefers-reduced-motion: reduce)").matches){el.textContent=text;return}
  const step=Math.min(20,1200/text.length);let i=0;el.textContent="";
  clearInterval(el._tw);
  el._tw=setInterval(()=>{el.textContent=text.slice(0,++i);if(i>=text.length)clearInterval(el._tw)},step);
}
```

Tom's lines stay instant; only Rolinda types.

## Do not

- No rainbow gradients on text (the current `.kpi b` gradient goes).
- No more than one glow per view.
- No animation over 400 ms except the sky fade (2 s, in three.js).
- No base red or base blue as text on black; bright variants only.
- No cyan, violet or pink leftovers (`#22D3EE`, `#8B5CF6`, `#A78BFA`, `#F472B6`); map them to blue, orange and the bright variants.
- No CRT effect on body text, no flicker, no curvature.
- No second theme for the game; black is the brand. The vault and terminal follow the OS.
- No em dashes, no emoji (`tools/checks.py style` enforces it).

## Sources

- Blueprint: https://github.com/palantir/blueprint (README, "data-dense", Apache-2.0); https://raw.githubusercontent.com/palantir/blueprint/develop/packages/core/src/common/_variables.scss (elevation shadows, 100 ms transition, `cubic-bezier(0.4, 1, 0.75, 0.9)`, 10px grid, 4px radius); https://raw.githubusercontent.com/palantir/blueprint/develop/packages/core/src/common/_color-aliases.scss (intents, dark text `light-gray5`, muted `gray4`, contrast comment); https://raw.githubusercontent.com/palantir/blueprint/develop/packages/colors/src/_colors.scss; https://blueprintjs.com and https://blueprintjs.com/docs/ (landing pages only, the docs body is client-rendered).
- marimo: https://marimo.io; https://github.com/marimo-team/marimo ("a reactive Python notebook that's reproducible, git-friendly, and deployable as scripts or apps", Apache-2.0, `marimo edit`, `marimo run notebook.py`); https://docs.marimo.io/getting_started/installation/ (`uv add marimo`, then `marimo tutorial intro`). It fits the Data Warehouse workstream: a notebook that is a plain `.py` file, so git and the agent can read it.
- Powerlevel10k: https://github.com/romkatv/powerlevel10k (styles Lean, Classic, Rainbow, Pure "differ only in presentation"; Rainbow shows "bright white text on blue background"; git status symbols; show on command; transient prompt).
- Claude: https://claude.com (headline "Think fast, build faster"; CSS tokens `#FAF9F5`, `#E3DACC`, `#D97757`, `--font-anthropic-serif` and `-sans`); https://code.claude.com/docs/en/overview (dark code blocks on `#0B0C0E`, Anthropic Sans and Serif Display).
- Motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion (the path without `@media` returns 404); https://web.dev/articles/prefers-reduced-motion; https://web.dev/articles/animations-guide (animate `transform` and `opacity` only); https://www.nngroup.com/articles/animation-duration/ (100 to 500 ms; "the more frequent the animation, the more subtle and shorter"). https://m3.material.io/styles/motion/easing-and-duration/tokens-specs and https://m2.material.io/design/motion/speed.html returned no text (client-rendered).
- CRT: https://aleclownes.com/2017/02/01/crt-display.html (scanlines via `linear-gradient` at 2px, flicker, chromatic text shadow; we keep only the scanlines and cut opacity to 4 percent).
- Obsidian variables: https://docs.obsidian.md/Reference/CSS+variables/Foundations/Colors, .../Radiuses, .../Spacing, .../Typography.
- Textual theme API: https://textual.textualize.io/guide/design/.
