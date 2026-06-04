import { chromium } from 'playwright';
import { mkdirSync } from 'fs';

mkdirSync('./verify-screenshots', { recursive: true });

const pages = [
  { name: 'dashboard', url: 'http://localhost:5174/dashboard' },
  { name: 'leads', url: 'http://localhost:5174/leads' },
  { name: 'approvals', url: 'http://localhost:5174/approvals' },
  { name: 'campaign-builder', url: 'http://localhost:5174/campaigns/new' },
  { name: 'ai-quality', url: 'http://localhost:5174/quality' },
];

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const errors = [];

for (const p of pages) {
  const page = await ctx.newPage();
  page.on('console', m => { if (m.type() === 'error') errors.push(`[${p.name}] ${m.text()}`); });
  page.on('pageerror', e => errors.push(`[${p.name}] PAGE ERROR: ${e.message}`));
  await page.goto(p.url, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(1500); // let animations settle
  await page.screenshot({ path: `./verify-screenshots/${p.name}.png`, fullPage: false });
  const h1 = await page.locator('h1, h2').first().textContent().catch(() => '(no heading)');
  console.log(`✅ ${p.name}: heading="${h1?.trim()}" url=${page.url()}`);
  await page.close();
}

await browser.close();

if (errors.length) {
  console.log('\n⚠️  Console errors:');
  errors.forEach(e => console.log(' ', e));
} else {
  console.log('\n✅ No console errors detected.');
}
