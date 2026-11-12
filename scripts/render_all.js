const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const [, , html, out, n0, n1] = process.argv; fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']}); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + path.resolve(html)); await pg.evaluate(() => document.fonts.ready);
  for (let i = +n0; i < +n1; i++) { const f = `${out}/f_${String(i).padStart(5, '0')}.jpg`; if (fs.existsSync(f)) continue;
    await pg.evaluate(t => window.__setTime(t), i / (+process.env.FPS || 30)); await pg.screenshot({ path: f, type: 'jpeg', quality: 82, timeout: 120000 }); }
  await b.close();
})();
