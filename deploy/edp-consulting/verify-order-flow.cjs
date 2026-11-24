// Synthetic browser checks; never submit an email, payment or real customer order.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {chromium} = require('C:/Users/philip/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const output = process.env.EDP_QA_OUTPUT || path.resolve(root, '../order-qa');
const types = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png','.jpg':'image/jpeg','.pdf':'application/pdf'};
const server = http.createServer((req, res) => {
  const relative = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const file = path.resolve(root, '.' + (relative === '/' ? '/index.html' : relative));
  if (req.method !== 'GET' || !(file === root || file.startsWith(root + path.sep)) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404);res.end();return;
  }
  res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
(async () => {
  fs.mkdirSync(output,{recursive:true});
  let browser;
  const results = [];
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = process.env.EDP_SITE_URL || `http://127.0.0.1:${server.address().port}/`;
  try {
    browser = await chromium.launch({headless:true,channel:'msedge'});
    for (const language of ['en','zh']) {
      const page = await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});
      const errors=[];
      page.on('pageerror', error=>errors.push(error.message));
      page.on('response', response=>{if(response.status()>=400)errors.push(response.status()+' '+response.url());});
      await page.goto(url,{waitUntil:'networkidle'});
      await page.locator(`[data-lang="${language}"]`).click();
      await page.locator('[data-order-plan="monthly"]').click();
      const form=page.locator('#order-form');
      assert.equal(await page.locator('#order-plan').inputValue(),'monthly');
      await page.locator('#order-review').click();
      assert.equal(await page.locator('#order-summary').isVisible(),false,'Empty details must not produce a request');
      const values={company:'Synthetic <b>Test</b> Pty Ltd',billing_address:'1 Test Street, Test City, Australia 2000',contact:'Test Contact',owner_name:'Test Owner',owner_email:'owner@example.test',confirm_email:'different@example.test',billing_email:'billing@example.test'};
      for(const [name,value] of Object.entries(values))await form.locator(`[name="${name}"]`).fill(value);
      await form.locator('[name="country"]').selectOption('AU');
      await form.locator('[name="hosting_region"]').selectOption('AU');
      await form.locator('[name="users"]').fill('7');
      await form.locator('[name="details_confirmed"]').check();
      await page.locator('#order-review').click();
      assert.equal(await page.locator('#order-summary').isVisible(),false,'Email mismatch must be rejected');
      await form.locator('[name="confirm_email"]').fill('owner@example.test');
      async function reviewAndDownload(){
        await page.locator('#order-review').click();
        await page.locator('#order-summary').waitFor({state:'visible'});
        const href=await page.locator('#order-email').getAttribute('href');
        assert.ok(href.startsWith('mailto:philip.zhang@edp-consulting.au?'));
        assert.equal(await page.locator('#order-summary-list dd b').count(),0,'Customer text must not become HTML');
        const pending=page.waitForEvent('download');
        await page.locator('#order-download').click();
        const download=await pending;
        return JSON.parse(fs.readFileSync(await download.path(),'utf8'));
      }
      const monthly=await reviewAndDownload();
      assert.equal(monthly.activation.trial_calendar_months,3);
      assert.equal(monthly.activation.payment_before_activation,false);
      assert.equal(monthly.billable_users,10);
      assert.equal(monthly.estimate.total_cents,10754);
      assert.equal(monthly.request_status,'prepared_not_submitted');
      assert.equal(monthly.activation.max_capacity_wait_days,3);
      assert.equal(monthly.activation.final_activation_code_requires_finance_sync,true);
      assert.equal(monthly.activation.provisional_access_if_finance_sync_pending,true);
      await page.locator('#pricing').screenshot({path:path.join(output,language+'-pricing.png')});
      await form.screenshot({path:path.join(output,language+'-form.png')});
      const other=language==='en'?'zh':'en';
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('#order-dialog').evaluate(d=>d.open),false,'Escape closes the order dialog');
      await page.locator(`[data-lang="${other}"]`).click();
      assert.equal(await form.locator('[name="company"]').inputValue(),values.company,'Language switch must retain typed details');
      assert.equal(await page.locator('#order-summary').evaluate(e=>!e.hidden),true);
      await page.locator(`[data-lang="${language}"]`).click();
      await page.locator('[data-order-plan="yearly"]').click();
      assert.equal(await page.locator('#order-summary').isVisible(),false,'Plan change invalidates old review');
      assert.equal(await form.locator('[name="users"]').inputValue(),'7','Changing plans must retain edited user count');
      const yearly=await reviewAndDownload();
      assert.equal(yearly.activation.trial_calendar_months,0);
      assert.equal(yearly.activation.payment_before_activation,true);
      assert.equal(yearly.estimate.total_cents,107360);
      await page.keyboard.press('Escape');
      await page.locator('[data-order-plan="buyout"]').click();
      await page.locator('#order-review').click();
      assert.equal(await page.locator('#order-summary').isVisible(),false,'On-premises server readiness is required');
      await form.locator('[name="users"]').fill('23');
      await form.locator('[name="server_environment"]').fill('Ubuntu 24.04 LTS, x86_64');
      await form.locator('[name="server_ready"]').check();
      const buyout=await reviewAndDownload();
      assert.equal(buyout.activation.trial_calendar_months,0);
      assert.equal(buyout.activation.payment_before_activation,true);
      assert.equal(buyout.estimate.total_cents,213620);
      assert.equal(buyout.setup.hosting_region,null);
      assert.equal(buyout.setup.customer_server_ready,true);
      await form.locator('[name="company"]').fill(' ');
      await page.locator('#order-review').click();
      assert.equal(await page.locator('#order-summary').isVisible(),false,'Whitespace-only details must be rejected');
      await form.locator('[name="company"]').fill(values.company);
      await reviewAndDownload();
      await page.setViewportSize({width:390,height:844});
      await page.locator('#order-form').screenshot({path:path.join(output,language+'-mobile-form.png')});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      assert.equal(await page.locator('[data-i18n="phoneLabel"]').count(),0);
      assert.deepEqual(errors,[]);
      results.push({language,monthly_trial:3,yearly_trial:0,buyout_trial:0,required_details_checked:true,owner_email_match_checked:true,buyout_readiness_checked:true,no_mobile_overflow:true,no_page_errors:true});
      await page.close();
    }
    fs.writeFileSync(path.join(output,'verification.json'),JSON.stringify(results,null,2));
    console.log(JSON.stringify(results));
  } finally {
    if(browser)await browser.close();
    server.close();
  }
})().catch(error=>{console.error(error.stack);server.close();process.exitCode=1});
