// Render every *.html in <srcDir> to a PNG of its own size in <outDir>.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [srcDir, outDir] = process.argv.slice(2);
  const browser = await chromium.launch();
  for (const file of fs.readdirSync(srcDir).filter(f => f.endsWith('.html')).sort()) {
    const story = file.includes('story');
    const page = await browser.newPage({ viewport: { width: 1080, height: story ? 1920 : 1350 } });
    await page.goto('file://' + path.join(srcDir, file), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(outDir, file.replace('.html', '.png')) });
    await page.close();
    console.log('rendered', file);
  }
  await browser.close();
})();
