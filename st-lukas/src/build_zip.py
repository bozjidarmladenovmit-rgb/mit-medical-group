"""Builds st-lukas/dist/St-Lukas-Dekemvri-2026.zip: one folder per day of the December plan.
Ready items contain the media + caption; items the school films contain a filming brief + caption idea.
Run from st-lukas/:  python3 src/build_zip.py
"""
import os
import re
import shutil
import zipfile

NAME = 'St-Lukas-Dekemvri-2026'
OUT = f'dist/{NAME}'

# (date, weekday, time, format, folder, media files or None, caption section in TEKSTOVI.md or brief dict)
READY, FILM = 'ready', 'film'
PLAN = [
    ('2026-12-01', 'Вторник', '20:00', 'Reel', 'Test-koj-profil', READY, ['videa/video-1-koj-profil.mp4'], 1),
    ('2026-12-02', 'Среда', '19:00', 'Reel', 'Profil-medicinska-sestra', READY, ['videa/video-profil-1-sestra.mp4'], 2),
    ('2026-12-04', 'Петок', '20:00', 'Reel', 'SNIMAJTE-POV-krven-pritisok', FILM, None,
     dict(idea='POV: првпат мериш крвен притисок',
          shots='1) Текст на екран: „POV: првпат мериш крвен притисок“ 2) Раце кои ја ставаат манжетната (на соученик или симулатор) 3) Стрелката на апаратот 4) Насмевка или палец горе.',
          caption='POV: првпат мериш крвен притисок 🩺 Колку беше нервозен/а? 😅 Во Св. Лука сè учиш на симулатори, со ментор до тебе.\n\n📞 078 324 324 · 🌐 stlukas.edu.mk\n#POV #медицинскасестра #СвЛука')),
    ('2026-12-05', 'Сабота', '11:00', 'Story', 'SNIMAJTE-Pogodi-sto-e-ova', FILM, None,
     dict(idea='Погоди што е ова? (макро фотографија)',
          shots='Фотографирајте од многу блиску дел од инструмент или модел (на пр. стетоскоп, микроскоп, анатомски модел) така што да не е очигледно. Во Story додадете анкета (Poll) или „Quiz“ стикер со 3 одговори. Следниот ден објавете ја целата фотографија.',
          caption='🔍 Погоди што е ова? Одговорот утре!')),
    ('2026-12-07', 'Понеделник', '19:00', 'Reel', 'Profil-zaben-tehnicar', READY, ['videa/video-profil-2-zaben.mp4'], 3),
    ('2026-12-09', 'Среда', '18:30', 'Објава', 'Za-roditelite', READY, ['objavi/objava-1-roditeli.png'], 6),
    ('2026-12-11', 'Петок', '20:00', 'Reel', 'SNIMAJTE-Prv-model-na-zab', FILM, None,
     dict(idea='Првото мое…: мојот прв модел на заб',
          shots='1) Текст: „Мојот прв модел на заб 🦷“ 2) Гипс или восок во раце 3) Брзо (timelapse) обликување 4) Готовиот модел во дланка.',
          caption='Мојот прв модел на заб 🦷 Од гипс до прецизна форма. Така почнува секој забен техничар!\n\n📞 078 324 324 · 🌐 stlukas.edu.mk\n#забентехничар #СвЛука')),
    ('2026-12-12', 'Сабота', '11:00', 'Story', 'SNIMAJTE-Prasaj-pravce', FILM, None,
     dict(idea='Прашај прваче: 3 брзи прашања',
          shots='3–4 ученици од прва година (со согласност од родителите), секој по 5 секунди: 1) „Зошто Св. Лука?“ 2) „Најинтересен час?“ 3) „Еден збор за првиот месец?“',
          caption='🎤 Прашај прваче! Што велат нашите ученици од прва година? 💙')),
    ('2026-12-14', 'Понеделник', '19:00', 'Reel', 'Profil-fizioterapevtski', READY, ['videa/video-profil-3-fizio.mp4'], 4),
    ('2026-12-15', 'Вторник', '18:30', 'Објава', 'NACRT-Otvoren-den', READY, ['objavi/objava-2-otvoren-den-NACRT.png'], 7),
    ('2026-12-16', 'Среда', '19:00', 'Reel', '6-pricini-za-Sv-Luka', READY, ['videa/video-2-zosto-sv-luka.mp4'], 8),
    ('2026-12-18', 'Петок', '20:00', 'Reel', 'SNIMAJTE-60-sekundi-so-profesor', FILM, None,
     dict(idea='60 секунди со професор',
          shots='Наставник пред анатомски модел или во лабораторија кажува еден интересен факт за 30–60 секунди (на пр. „Колку коски има човекот?“). Снимајте вертикално, со добар звук (телефонот близу).',
          caption='⏱ 60 секунди со професор: дали го знаевте ова? Пишете ни што да објасниме следно! 👇\n\n#СвЛука #60секунди')),
    ('2026-12-19', 'Сабота', '11:00', 'Live / Stories', 'SNIMAJTE-Otvoren-den-vo-zivo', FILM, None,
     dict(idea='Отворен ден: во живо',
          shots='Facebook/Instagram Live од 5–10 минути на почетокот, или Stories на секои 30 минути: гости на симулаторите, наставници, насмевки. Само со согласност за лицата на децата.',
          caption='🔴 Во живо од Отворениот ден во Св. Лука!')),
    ('2026-12-21', 'Понеделник', '19:00', 'Reel', 'Profil-kozmeticki', READY, ['videa/video-profil-4-kozmeticki.mp4'], 5),
    ('2026-12-23', 'Среда', '18:30', 'Галерија', 'SNIMAJTE-Galerija-otvoren-den', FILM, None,
     dict(idea='Фотографии од отворениот ден (5–10 слики)',
          shots='Најдобрите фотографии од отворениот ден: симулатори, разговори, групна фотографија. Објавете како галерија (повеќе слики во една објава).',
          caption='Ви благодариме на сите што дојдовте на Отворениот ден! 💙 Ако не стигнавте, јавете ни се и закажете посета.\n\n📞 078 324 324 · 🌐 stlukas.edu.mk\n#ОтворенДен #СвЛука')),
    ('2026-12-25', 'Петок', '20:00', 'Reel', 'SNIMAJTE-POV-posleden-cas', FILM, None,
     dict(idea='POV: последниот час пред распустот',
          shots='1) Текст: „POV: последниот час пред распустот 🎄“ 2) Ѕвоно или часовник 3) Ученици спакуваат 4) Излегување од училиштето, снег или празнични светла.',
          caption='POV: последниот час пред распустот 🎄 Добро заслужен одмор, се гледаме во новата година! 💙\n#СвЛука #распуст')),
    ('2026-12-28', 'Понеделник', '18:30', 'Story + објава', 'SNIMAJTE-Povik-pismo-do-sebe', FILM, None,
     dict(idea='Повик: Напиши писмо до себе за 4 години',
          shots='Story со текст и „Question“ стикер: „Што би си напишал/а за 4 години?“. Или учениците пишуваат на хартија во училиште, а писмата се фотографираат (без презимиња).',
          caption='💌 Напиши писмо до себе за 4 години! Најубавите ќе ги објавиме на 30.12.')),
    ('2026-12-30', 'Среда', '18:30', 'Галерија', 'SNIMAJTE-Najubavite-pisma', FILM, None,
     dict(idea='Најубавите писма од учениците (галерија)',
          shots='5–8 фотографии од рачно напишани писма (само име или иницијали).',
          caption='💌 Најубавите писма „до мене за 4 години“ од нашите ученици. Ни се стопи срцето! 💙\n#ПисмоДоСебе #СвЛука')),
    ('2026-12-31', 'Четврток', '12:00', 'Reel', 'Pismo-do-sebe-Nova-godina', READY, ['videa/video-3-pismo-do-sebe.mp4'], 9),
]


def captions():
    out = {}
    for part in re.split(r'\n---\n', open('TEKSTOVI.md').read()):
        m = re.search(r'^## (\d+)\.', part, re.M)
        if not m:
            continue
        body = part[m.end():].split('\n', 1)[1].strip()
        notes = [l for l in body.splitlines() if l.startswith('⚠️')]
        text = '\n'.join(l for l in body.splitlines() if not l.startswith('⚠️')).strip()
        out[int(m.group(1))] = (text, notes)
    return out


def main():
    caps = captions()
    shutil.rmtree('dist', ignore_errors=True)
    os.makedirs(OUT)
    rows = []
    for i, (date, day, time, fmt, name, kind, files, cap) in enumerate(PLAN, 1):
        folder = f'{OUT}/{i:02d}_{date}_{name}'
        os.makedirs(folder)
        info = f'Датум: {day}, {date}\nЧас: {time}\nФормат: {fmt}\n'
        if kind == READY:
            for f in files:
                ext = os.path.splitext(f)[1]
                shutil.copy(f, f'{folder}/{"video" if ext == ".mp4" else "slika"}{ext}')
                if ext == '.mp4':
                    shutil.copy(f.replace('.mp4', '-naslovna.jpg'), f'{folder}/naslovna.jpg')
            text, notes = caps[cap]
            open(f'{folder}/TEKST.txt', 'w').write(text + '\n')
            info += 'Каде: Facebook + Instagram' + (' + TikTok' if fmt == 'Reel' else '') + '\n'
            for n in notes:
                info += '\n' + n + '\n'
            if any(f.endswith('.mp4') for f in files):
                info += '\n• Додадете популарна музика од библиотеката на Instagram/TikTok. Насловна слика: naslovna.jpg.\n'
            mark = '✅'
        else:
            info += f'\nСНИМА УЧИЛИШТЕТО\nИдеја: {cap["idea"]}\n\nКако да се сними:\n{cap["shots"]}\n\n'
            info += 'Правила: вертикално (9:16), 7–15 секунди, дневна светлина, текст на екранот во првите 2 секунди.\n'
            info += 'Ученици се малолетни: само со писмена согласност од родителите, или кадри без лица.\n'
            open(f'{folder}/TEKST.txt', 'w').write(cap['caption'] + '\n')
            mark = '📱'
        open(f'{folder}/UPATSTVO.txt', 'w').write(info)
        rows.append(f'{mark} {i:02d}. {day:<10} {date} {time}  {fmt:<15} {name.replace("-", " ")}')

    readme = '''Приватно медицинско средно училиште Св. Лука
План за социјалните мрежи, декември 2026
===========================================

✅ = готово (видео или слика + текст)
📱 = снима училиштето: во папката е упатство како да се сними и предлог текст

Во секоја папка: TEKST.txt (за копирање), UPATSTVO.txt (датум, час, совети),
а кај готовите и video.mp4 / slika.png + naslovna.jpg.

Закажување: Meta Business Suite (business.facebook.com) → Create post / Create reel
→ прикачи → залепи TEKST.txt → Facebook + Instagram → Schedule.
За TikTok: објавете го истото видео во апликацијата TikTok.

ВАЖНО: „NACRT-Otvoren-den“ е предлог-настан. Датумот (сабота, 19.12, 11–14 ч)
мора да го потврди училиштето пред објавување.

РАСПОРЕД
''' + '\n'.join(rows) + '\n\nЦелиот план и анализата: PLAN-DEKEMVRI.md\n'
    open(f'{OUT}/PROCITAJ-ME.txt', 'w').write(readme)
    shutil.copy('PLAN-DEKEMVRI.md', f'{OUT}/PLAN-DEKEMVRI.md')
    zpath = f'dist/{NAME}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, names in sorted(os.walk(OUT)):
            for n in sorted(names):
                p = os.path.join(root, n)
                z.write(p, os.path.relpath(p, 'dist'))
    print(zpath, os.path.getsize(zpath) // 1024, 'KB')


if __name__ == '__main__':
    main()
