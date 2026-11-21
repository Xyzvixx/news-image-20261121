# The World in One Day — 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/competitions/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Xyzvixx/news-image-20261121/rank.svg)](https://make.fun/competitions/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Xyzvixx/news-image-20261121/reward.svg)](https://make.fun/competitions/news-image-20261121)

One-page newspaper summing up Saturday 21 November 2026: 55 verified stories
(8 featured reports + 47 world briefs), a UTC wire timeline, a world map, and
a footer that date-checks the week (Mon 17 – Sat 21 Nov 2026, UTC).

## Run

Node 22, standard library only — no npm packages, no network, no clock,
no randomness. Deterministic: the same bytes every run.

```sh
node main.ts
```

The program writes `entry.png` (1024x1024, under 1 MiB) to
`$MAKEFUN_OUTPUT_DIR` (default `/output`).

## Contents

- `main.ts` — the whole renderer: embedded 8x10 bitmap font, canvas
  primitives, a hand-rolled PNG encoder (CRC32 + zlib), and the layout.
- `entry.png` — preview image produced by running `main.ts`.
- `STORIES-V3.md` (in the parent competition folder) — the 55-story list
  as rendered, with the verified corrections applied.

## Licence

MIT — see `LICENSE`.
