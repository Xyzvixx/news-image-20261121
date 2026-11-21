# The World in One Day — 21 November 2026

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Xyzvixx/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Xyzvixx/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

**46 Verified Stories, UTC Timeline & Date Check** — a one-image summary of
Saturday 21 November 2026's world news, drawn entirely in code.

## What it is

`main.py` (Python 3.13, standard library + Pillow) draws a 1024×1024
newspaper-style poster: masthead with an explicit date check, a UTC wire
timeline, 8 featured stories with editorial illustrations, 38 world briefs
grouped by region, a stylised world map, and a source footer.

Every story in the image was published or first reported on 21 November 2026
(UTC) by the source named on the poster. Events that happened on Friday
20 November are marked "Fri" — nothing is presented as happening on 21 November
when it did not. This is the v1 early-day edition, built while the news day was
only a few hours old; a full-day rebuild is planned for Saturday evening.

## Featured stories

1. **Peru** — 6.8 quake shakes central Peru (Junin; felt in Lima)
2. **Shenzhen** — Trump, Xi and Putin hold trilateral talks at APEC
3. **Poland** — Russian missile hits Poland, PM Tusk says
4. **Markets** — S&P -3.7%, Nasdaq -5.28%; Nvidia falls ~14% on SEC probe report
5. **Denmark** — Russian assassination plot foiled, diplomat expelled
6. **The Hague** — World Court: Myanmar committed genocide against the Rohingya
7. **New York** — Mamdani: close Rikers Island jail by 2032
8. **Washington** — Trump threatens a ban on overseas AI data centres

Plus 38 briefs: North America (10), Europe (10), Asia (9),
Middle East & Africa (5), Science, Tech & Sport (4).

## How to run

```sh
python3 main.py
```

The image is written to `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`
if that is set). The run is deterministic — running it twice produces
byte-identical output — and it needs no network access.

## Sources

Reuters, AP, AFP, BBC, Al Jazeera, Xinhua and wire reports, 21 November 2026
(UTC). Editorial illustrations, not photographs.

## License

MIT — see [LICENSE](LICENSE).
