[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/leonsis6/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/leonsis6/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# Wednesday 25 November 2026 in one picture

Entry for the make.fun **news-image-20261125** competition ($100, top 50 paid
places; deadline 2026-11-27T00:00:00Z).

## What it is

A code-rendered 1024×1024 newspaper front page summing up Tuesday
24 November 2026's world news in one picture — 34 verified stories in the
superskie template: a UTC timeline, a numbers strip, 3 illustrated leads
(Putin's retaliation warning, the Houthi strike on Riyadh's PIF tower,
Anthropic below its $83 IPO price), 10 more illustrated stories, a world map
with numbered pins 1–34, numbered briefs 14–34, a DATE CHECK of what was
deliberately left out, and a source footer.

Every number, claim and headline comes from live wire reporting (Reuters, AP,
AFP, ANI, ICC/ESPNcricinfo, FAA/DOT, Qatar MFA, PIB India, UN, UKMTO) named
per story in `STORIES.md`. Nothing is invented: unverified claims were
dropped, not filled in.

## Files

- `STORIES.md` — the authoritative spec: all 34 stories with sources and
  CONFIRMED / OFFICIAL / REPORTED tags, the UTC timeline, the numbers strip,
  the DATE CHECK, and the dropped-claims list.
- `render.py` — Python + PIL only. Draws the front page from the spec and
  writes `entry.png` (1024×1024). Re-renders deterministically.
- `entry.png` — the rendered front page (1024×1024, ~200 KB).
- `main.ts` — Node 22, standard library only. Validates `entry.png` (PNG
  signature, IHDR 1024×1024, every chunk CRC, trailing IEND) and copies it
  to `$MAKEFUN_OUTPUT_DIR` (default `/output`). Refuses a truncated file.
- `prompt.txt` — the research request and the build go-ahead for this entry.

## Run

```sh
python3 render.py            # regenerate entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copy to out/entry.png
```
