# Media

Every image in this folder, what it shows, what renders it and where it is used. A picture nobody links to is either a job for a document or a job for the bin; this table is how that stays true.

Regenerate with `just media` (the game, through Playwright, from the built file) and `just tui-media` (the terminal screens and the pets, from real terminal output). Both write here. Never hand-edit an image in place; render it again.

| File | Shows | Rendered by | Used in |
|---|---|---|---|
| `hero.png` | The island at 1200x630, the Open Graph size | `just media` | The social preview of the repository and the hosted site |
| `island-campus.png` | Evening 1, the Innovation Campus at dusk | `just media` | `README.md` |
| `island-winter.png` | Evening 2, the Cold Storage Cluster | `just media` | `docs/ABOUT.md` |
| `island-desert.png` | Evening 3, the Sandbox Environment | `just media` | `docs/ABOUT.md` |
| `island-prod.png` | Evening 4, the Production Environment | `just media` | `docs/ABOUT.md` |
| `roadmap.png` | The Roadmap panel, full page | `just media` | `docs/ABOUT.md` |
| `vault.png` | The vault graph | `just media` | `docs/ABOUT.md` |
| `tree.png` | The tech tree | `just media` | `docs/ABOUT.md` |
| `phone.png` | The HUD at 393 points wide | `just media` | `docs/ABOUT.md` |
| `gameplay.gif` | Walking to the signpost, opening a stop, lighting the OKR | `just media` | `README.md` |
| `island-campus-start.png` | The campus as a first visit finds it | by hand | `CHANGELOG.md` |
| `island-winter-artifacts.png` | The winter island with its three artifacts | by hand | `README.md` |
| `artifact-cafe.png` | The cafe sheet: a 200, then a 429 | by hand | `README.md` |
| `onboarding-start.png` | The title screen on a first visit | by hand | `README.md` |
| `tui-welcome.png` | `just start`, the Welcome screen | by hand | `README.md` |
| `tui-map.png` | `just start`, the campaign map | by hand | `README.md` |
| `tui-pet.png`, `tui-pet.gif` | The pet strolling under the launch screen | `just tui-media` | `README.md` |
| `pets.png`, `pets/*` | The six pixel species, still and animated | `just tui-media --pets` | `README.md`, `docs/ABOUT.md` |
| `pets-game/*` | The same six as they appear in the browser game | by hand | a record of the pets-in-the-game work |
