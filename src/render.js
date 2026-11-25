// Renders the HTML designs into PNG posts and MP4 videos.
//   node src/render.js            -> everything
//   node src/render.js video-1    -> only files whose name contains "video-1"
// Videos: every CSS animation is paused and stepped frame by frame, so the output is smooth
// regardless of how fast this machine is. Frames are joined into MP4 with ffmpeg.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'src');
const FPS = 30;
const filter = process.argv[2] || '';

async function renderPost(browser, file) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(SRC, file));
  await page.evaluate(() => document.fonts.ready);
  const out = path.join(ROOT, 'objavi', file.replace(/\.html$/, '.png'));
  await page.locator('.canvas').screenshot({ path: out });
  await page.close();
  console.log('✓', path.relative(ROOT, out));
}

async function renderVideo(browser, file) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(SRC, file));
  await page.evaluate(() => document.fonts.ready);
  // Each video page declares its length in <body data-duration="seconds">.
  const duration = await page.evaluate(() => Number(document.body.dataset.duration || 10));
  const frames = Math.round(duration * FPS);
  const tmp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'frames-'));
  for (let i = 0; i < frames; i++) {
    const t = (i / FPS) * 1000;
    await page.evaluate((ms) => {
      for (const a of document.getAnimations()) {
        a.pause();
        a.currentTime = ms;
      }
    }, t);
    await page.screenshot({ path: path.join(tmp, `f${String(i).padStart(5, '0')}.png`), type: 'png' });
  }
  const out = path.join(ROOT, 'videa', file.replace(/\.html$/, '.mp4'));
  execFileSync('ffmpeg', [
    '-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(tmp, 'f%05d.png'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', '-movflags', '+faststart', out,
  ]);
  // A still cover image, useful as the video thumbnail.
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', String(Math.max(0, duration - 1.5)), '-i', out, '-frames:v', '1', out.replace(/\.mp4$/, '-naslovna.jpg')]);
  fs.rmSync(tmp, { recursive: true, force: true });
  await page.close();
  console.log('✓', path.relative(ROOT, out), `(${duration}s)`);
}

(async () => {
  fs.mkdirSync(path.join(ROOT, 'objavi'), { recursive: true });
  fs.mkdirSync(path.join(ROOT, 'videa'), { recursive: true });
  const browser = await chromium.launch();
  const files = fs.readdirSync(SRC).filter((f) => f.endsWith('.html') && f.includes(filter)).sort();
  for (const f of files) {
    if (f.startsWith('objava-')) await renderPost(browser, f);
    else if (f.startsWith('video-')) await renderVideo(browser, f);
  }
  await browser.close();
})();
