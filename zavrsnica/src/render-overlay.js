// Renders an overlay page to transparent PNG frames (30 fps) for compositing over video with ffmpeg.
//   node src/render-overlay.js overlay-dental.html out-dir
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const [file, outDir] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, file));
  await page.evaluate(() => document.fonts.ready);
  const dur = await page.evaluate(() => Number(document.body.dataset.duration || 4));
  for (let i = 0; i < dur * 30; i++) {
    await page.evaluate((ms) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }), (i / 30) * 1000);
    await page.screenshot({ path: path.join(outDir, `o${String(i).padStart(4, '0')}.png`), omitBackground: true });
  }
  await browser.close();
  console.log('frames', dur * 30);
})();
