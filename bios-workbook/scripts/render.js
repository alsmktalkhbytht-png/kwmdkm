// render.js <in.html> <out.pdf> — paginate in Chromium, print A4 PDF, print QA report.
const { chromium } = require('playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const exe = process.env.CHROME || undefined;
  const browser = await chromium.launch({ executablePath: exe, args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[page error]', e.message));
  await page.goto('file://' + require('path').resolve(inp), { waitUntil: 'load' });
  await page.waitForFunction('window.PAGINATED === true', null, { timeout: 120000 });
  const qa = await page.evaluate('window.QA');
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  await browser.close();
  const bad = qa.pages.filter(p => p.overflow || p.lastIsHead);
  const low = qa.pages.slice(0, -1).filter(p => p.fill < 0.8);
  console.log(`pages: ${qa.pages.length} inner + cover`);
  console.log('fill:', qa.pages.map(p => p.fill).join(' '));
  if (low.length) console.log('LOW FILL:', low.map(p => `p${p.page}=${p.fill}`).join(', '));
  if (bad.length) console.log('PROBLEMS:', JSON.stringify(bad));
  if (qa.hscroll.length) console.log('H_SCROLL:', JSON.stringify(qa.hscroll));
  if (!bad.length && !qa.hscroll.length) console.log('OK — no layout problems');
})();
