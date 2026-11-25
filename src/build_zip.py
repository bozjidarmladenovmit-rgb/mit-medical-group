"""Builds dist/MIT-Dental-Dekemvri-2026.zip: one folder per scheduled post with the media,
the caption (TEKST.txt) and instructions (UPATSTVO.txt), plus a schedule overview.

Run from the repository root:  python3 src/build_zip.py
"""
import os
import re
import shutil
import zipfile

NAME = 'MIT-Dental-Dekemvri-2026'
OUT = f'dist/{NAME}'

# (date, weekday, time, type, folder name, media files, caption section in TEKSTOVI-ZA-OBJAVI.md)
SCHEDULE = [
    ('2026-12-01', 'Вторник', '19:30', 'Reel (видео)', 'Koi-sme-nie', ['videa/video-0-koi-sme-nie.mp4'], 6),
    ('2026-12-02', 'Среда', '19:30', 'Објава', 'Fakt-ili-zabluda-1', ['objavi/objava-1-fakt-ili-zabluda.png'], 1),
    ('2026-12-04', 'Петок', '19:30', 'Reel (видео)', 'Fakt-ili-zabluda-1-video', ['videa/video-1-fakt-ili-zabluda.mp4'], 2),
    ('2026-12-05', 'Сабота', '11:00', 'Reel (видео)', 'Prv-pregled-dete', ['videa/video-5-dete.mp4'], 7),
    ('2026-12-07', 'Понеделник', '19:30', 'Објава', 'Kviz', ['objavi/objava-2-kviz.png'], 3),
    ('2026-12-11', 'Петок', '19:30', 'Reel (видео)', '4-znaci', ['videa/video-2-4-znaci.mp4'], 4),
    ('2026-12-12', 'Сабота', '11:00', 'Reel (видео)', 'Pravilno-cetkanje', ['videa/video-3-cetkanje.mp4'], 8),
    ('2026-12-16', 'Среда', '19:30', 'Објава', 'Praznici-bez-karies', ['objavi/objava-3-praznici.png'], 5),
    ('2026-12-19', 'Сабота', '11:00', 'Reel (видео)', 'Konec-za-zabi', ['videa/video-4-konec.mp4'], 9),
    ('2026-12-21', 'Понеделник', '19:30', 'Reel + Објава', 'NACRT-Ponuda-januari', ['videa/video-7-ponuda-januari.mp4', 'objavi/objava-5-ponuda-januari.png'], 10),
    ('2026-12-23', 'Среда', '19:30', 'Објава', 'Fakt-ili-zabluda-2-belenje', ['objavi/objava-4-fakt-ili-zabluda-2-belenje.png'], 11),
    ('2026-12-26', 'Сабота', '11:00', 'Reel (видео)', 'Fakt-ili-zabluda-2-video', ['videa/video-6-fakt-ili-zabluda-2-belenje.mp4'], 11),
    ('2026-12-30', 'Среда', '19:30', 'Story (потсетник)', 'NACRT-Ponuda-potsetnik', ['videa/video-7-ponuda-januari.mp4'], 10),
    ('2026-12-31', 'Четврток', '12:00', 'Reel + Story', 'Nova-godina', ['videa/video-8-nova-godina.mp4'], 12),
]

NEEDS_PHOTOS = '''- Сре 09.12  Запознајте го тимот #1 (фотографија од стоматолог + 3 реченици)
- Пон 14.12  Пред/потоа (само со писмена согласност од пациентот)
- Пет 18.12  „Ден во клиниката“ (15 секунди снимки со телефон: стерилизација, опрема, тим)
- Пет 25.12  Професор одговара на едно прашање (видео со телефон)
- Пон 28.12  Празнична честитка од тимот (групна фотографија)'''


def captions():
    """Section number -> (caption text, notes for the instructions file)."""
    out = {}
    for part in re.split(r'\n---\n', open('TEKSTOVI-ZA-OBJAVI.md').read()):
        m = re.search(r'^## (\d+)\.', part, re.M)
        if not m:
            continue
        body = part[m.end():].split('\n', 1)[1].strip()
        notes, keep = [], []
        for line in body.splitlines():
            if line.startswith('> '):
                notes.append(line[2:].replace('Совет: ', ''))
            elif line.startswith('⚠️'):
                notes.insert(0, line)
            else:
                keep.append(line)
        text = '\n'.join(keep).strip()
        if '**Одговор' in text:
            text, answer = text.split('**Одговор', 1)
            notes.append('Story следниот ден, одговор на квизот: ' + answer.split(':**', 1)[-1].strip())
            text = text.strip()
        out[int(m.group(1))] = (text, notes)
    return out


def media_name(path):
    ext = os.path.splitext(path)[1]
    return ('video' if ext == '.mp4' else 'slika') + ext


def main():
    caps = captions()
    shutil.rmtree('dist', ignore_errors=True)
    os.makedirs(OUT)
    overview = []
    for i, (date, day, time, kind, name, files, sec) in enumerate(SCHEDULE, 1):
        folder = f'{OUT}/{i:02d}_{date}_{name}'
        os.makedirs(folder)
        for f in files:
            shutil.copy(f, f'{folder}/{media_name(f)}')
            if f.endswith('.mp4'):
                shutil.copy(f.replace('.mp4', '-naslovna.jpg'), f'{folder}/naslovna.jpg')
        text, notes = caps[sec]
        open(f'{folder}/TEKST.txt', 'w').write(text + '\n')
        where = 'Facebook + Instagram' + (' (+ TikTok)' if 'Reel' in kind else '')
        info = f'Датум: {day}, {date}\nЧас: {time}\nТип: {kind}\nКаде: {where}\n'
        if any(f.endswith('.mp4') for f in files):
            notes = notes + ['Додадете популарна музика од библиотеката на Facebook/Instagram. Како насловна слика користете naslovna.jpg.']
        if notes:
            info += '\n' + '\n'.join('• ' + n for n in notes) + '\n'
        open(f'{folder}/UPATSTVO.txt', 'w').write(info)
        overview.append(f'{i:02d}. {day:<10} {date} во {time}  –  {kind}: {name.replace("-", " ")}')

    readme = f'''МИТ Универзитетска клиника по дентална медицина
Објави за социјалните мрежи, декември 2026
==============================================

Во секоја папка:
  slika.png / video.mp4  – за објавување
  naslovna.jpg           – насловна слика за видеото
  TEKST.txt              – текст за копирање (со хаштагови)
  UPATSTVO.txt           – датум, час и совети

КАКО ДА ГИ ЗАКАЖЕТЕ (Meta Business Suite, бесплатно)
1. Отворете business.facebook.com или апликацијата „Meta Business Suite“.
2. Прв пат: Settings → Accounts → Instagram accounts → Connect (поврзете го Instagram).
3. Create post (за слика) или Create reel (за видео).
4. Прикачете ја slika.png или video.mp4 од папката.
5. Отворете TEKST.txt во истата папка, копирајте го целиот текст и залепете го.
6. Означете Facebook и Instagram.
7. Стрелката до „Publish“ → „Schedule“ → датум и час од UPATSTVO.txt.

ВАЖНО: папките со „NACRT“ се понуда (бесплатен преглед + чистење, 5–20 јануари)
која МОРА да ја потврди клиниката пред објавување.

РАСПОРЕД
''' + '\n'.join(overview) + f'''

ОБЈАВИ ЗА КОИ СЕ ПОТРЕБНИ ФОТОГРАФИИ ИЛИ ВИДЕА ОД КЛИНИКАТА
{NEEDS_PHOTOS}

Целиот план и анализата: ANALIZA-I-PLAN.md
'''
    open(f'{OUT}/PROCITAJ-ME.txt', 'w').write(readme)
    shutil.copy('ANALIZA-I-PLAN.md', f'{OUT}/ANALIZA-I-PLAN.md')
    zpath = f'dist/{NAME}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, names in sorted(os.walk(OUT)):
            for n in sorted(names):
                p = os.path.join(root, n)
                z.write(p, os.path.relpath(p, 'dist'))
    print(zpath, os.path.getsize(zpath) // 1024, 'KB')


if __name__ == '__main__':
    main()
