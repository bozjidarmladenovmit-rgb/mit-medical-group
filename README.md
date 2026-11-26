# МИТ Дентална клиника: социјални мрежи

Објави, видео анимации и план за социјалните мрежи на МИТ Универзитетската клиника по дентална медицина.

| Папка / датотека | Што содржи |
|---|---|
| `ANALIZA-I-PLAN.md` | Анализа на Facebook страницата, план за 30 дена, буџет |
| `TEKSTOVI-ZA-OBJAVI.md` | Готови текстови и хаштагови за секоја објава |
| `objavi/` | Слики за објави (1080×1350, за Facebook и Instagram) |
| `videa/` | Видео анимации (1080×1920, за Reels, Stories и TikTok) и насловни слики |
| `src/` | Изворните дизајни (HTML) од кои се прават сликите и видеата |
| `assets/` | Логото (засега исечено од screenshot; да се замени со оригиналната датотека) |

## Повторно правење на сликите и видеата

Потребни се Node.js, Playwright и ffmpeg.

```bash
node src/render.js            # сите
node src/render.js video-1    # само едно
python3 src/build_zip.py      # ZIP за преземање (dist/)
```

## Св. Лука (средно медицинско училиште)

Папката `st-lukas/` содржи посебен план и материјали за Приватното медицинско средно училиште Св. Лука:
`PLAN-DEKEMVRI.md`, `TEKSTOVI.md`, `objavi/`, `videa/`, `src/`.

```bash
cd st-lukas
python3 src/make_profiles.py   # ги прави 4-те видеа „Профил на неделата“ (HTML)
node src/render.js             # слики и видеа
python3 src/build_zip.py       # ZIP за преземање (st-lukas/dist/)
```
