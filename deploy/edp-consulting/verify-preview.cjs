// Screenshots and checks for site-preview (file:// load, no server). Output: preview-2026-11/
const {chromium} = require('C:/Users/philip/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const path = require('path');
const fs = require('fs');
const out = path.join(__dirname, 'preview-2026-11');
fs.mkdirSync(out, {recursive: true});
const url = 'file:///' + path.join(__dirname, 'site-preview', 'index.html').replace(/\\/g, '/');
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'msedge'});
  const results = {};
  for (const [name, viewport, lang] of [
    ['desktop-zh', {width: 1440, height: 1000}, 'zh'],
    ['desktop-en', {width: 1440, height: 1000}, 'en'],
    ['mobile-zh', {width: 390, height: 844}, 'zh'],
  ]) {
    const page = await browser.newPage({viewport, deviceScaleFactor: name.startsWith('mobile') ? 2 : 1});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto(url, {waitUntil: 'load'});
    await page.locator(`[data-lang="${lang}"]`).click();
    await page.waitForTimeout(300);
    await page.screenshot({path: path.join(out, `${name}-full.png`), fullPage: true});
    for (const id of ['experience', 'highlights', 'downloads', 'whats-new', 'pricing', 'questions']) {
      await page.locator('#' + id).screenshot({path: path.join(out, `${name}-${id}.png`)});
    }
    await page.evaluate(() => scrollTo(0, 0));
    await page.locator('a.topbar-feedback').click();
    await page.waitForTimeout(300);
    await page.screenshot({path: path.join(out, `${name}-feedback-modal.png`)});
    results[name + '-modal'] = await page.evaluate(() => document.getElementById('feedback').open);
    await page.keyboard.press('Escape');
    await page.screenshot({path: path.join(out, `${name}-hero.png`)});
    results[name] = {
      errors,
      overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth),
      untranslated: await page.evaluate(() => [...document.querySelectorAll('[data-i18n]')].filter(e => !e.innerHTML.trim()).map(e => e.dataset.i18n)),
      subscribe: await page.locator('#pricing a.button').evaluateAll(a => a.map(x => x.getAttribute('href'))),
    };
    await page.close();
  }
  await browser.close();
  console.log(JSON.stringify(results, null, 1));
})().catch(e => { console.error(e.message); process.exitCode = 1; });
