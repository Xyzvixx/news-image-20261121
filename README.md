# The World in One Day — 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/competitions/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Xyzvixx/news-image-20261121/rank.svg)](https://make.fun/competitions/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Xyzvixx/news-image-20261121/reward.svg)](https://make.fun/competitions/news-image-20261121)

A one-page newspaper for the make.fun `news-image-20261121` bounty:
**55 verified stories** — 8 featured stories from Saturday 21 November 2026
plus 47 briefs covering the week Mon 17 – Sat 21 Nov 2026 (UTC).

Top stories: COP31 in overtime in Antalya, three Houthi missiles downed
over Riyadh, the M6.7 Junin earthquake in Peru, strikes on Kryvyi Rih,
KL Rahul's Wellington century, Bitcoin below $59,000, the UK–EU reset
deal, and Trump's threatened tax on overseas data centres.

## Render

```sh
MAKEFUN_OUTPUT_DIR=/output python3 -P -s main.py
```

Writes only `entry.png` into `$MAKEFUN_OUTPUT_DIR` (default `/output`).
Python 3.13, standard library + Pillow only. Deterministic: two runs
produce byte-identical output.

## Layout

1024×1024 PNG: masthead, UTC wire strip, 8 featured panels, a world-map
strip marking the featured-story locations, briefs in three columns
grouped by day, and a footer with the date-check line. Briefs that
happened Mon–Fri carry their day mark — (Tue), (Thu) or (Fri);
unmarked briefs are Sat 21 Nov.

## Sources

BBC, Reuters, AP, AFP, USGS, NASA, European Commission. All times UTC.
Figures as reported at build time.
