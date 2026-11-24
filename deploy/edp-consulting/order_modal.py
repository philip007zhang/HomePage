"""Move the opening/order form out of the homepage flow into a dialog opened by the plan buttons.

Run from anywhere; edits the repo-root index.html, order.js and order.css in place (idempotent).
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
html_path, js_path, css_path = root / 'index.html', root / 'order.js', root / 'order.css'
html = html_path.read_text(encoding='utf-8-sig')

if 'id="order-dialog"' not in html:
    start = html.index('<section class="wrap section order-section" id="order"')
    end = html.index('</section>', start) + len('</section>')
    section = html[start:end]
    inner = section[section.index('>') + 1:-len('</section>')]
    html = html[:start] + html[end:]
    dialog = ('<dialog class="order-dialog" id="order-dialog" aria-labelledby="order-title">'
              '<button type="button" class="order-close" aria-label="Close">×</button>'
              '<div class="order-section" id="order">' + inner + '</div></dialog>')
    html = html.replace('<script src="bilingual.js"></script>', dialog + '<script src="bilingual.js"></script>', 1)
    html_path.write_text(html, encoding='utf-8')

js = js_path.read_text(encoding='utf-8-sig')
marker = '/* order dialog */'
if marker not in js:
    js += marker + r'''
(() => {
  const dialog = document.getElementById('order-dialog');
  if (!dialog) return;
  const open = () => { if (!dialog.open) dialog.showModal(); dialog.scrollTop = 0; };
  document.querySelectorAll('a[href="#order"]').forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    open();
  }));
  dialog.querySelector('.order-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  if (location.hash === '#order') open();
})();
'''
    js_path.write_text(js, encoding='utf-8')

css = css_path.read_text(encoding='utf-8-sig')
if '.order-dialog' not in css:
    css += ('.order-dialog{width:min(1120px,calc(100% - 32px));max-height:calc(100dvh - 32px);overflow:auto;border:0;'
            'border-radius:8px;padding:34px 34px 28px;background:var(--paper);color:var(--ink);box-shadow:0 30px 80px #1d2d3940}'
            '.order-dialog::backdrop{background:#1d2d3999}'
            '.order-dialog .order-section{border-top:0}.order-dialog .section-heading{margin-top:12px}'
            '.order-close{position:sticky;top:0;float:right;margin:-18px -14px 0 0;border:0;background:var(--paper);'
            'font-size:30px;line-height:1;cursor:pointer;color:var(--muted);z-index:2;padding:4px 8px;border-radius:4px}'
            '.order-close:hover{color:var(--ink)}'
            '@media(max-width:760px){.order-dialog{padding:22px 14px}.order-close{margin:-10px -6px 0 0}}\n')
    css_path.write_text(css, encoding='utf-8')
print('ok')

# The form is no longer "below": point visitors to the plan buttons instead.
import json
js_text = (root / 'bilingual.js').read_text(encoding='utf-8-sig')
prefix = 'const translations = '
offset = js_text.index(prefix) + len(prefix)
translations, size = json.JSONDecoder().raw_decode(js_text[offset:])
translations['pricingNote'] = {
    'en': 'Use the button under a plan to open the opening-details form before confirming your order. Orders and payment arrangements are currently confirmed with you by email; this page does not collect payment or automatically deploy a system. Installation and migration are quoted separately. Final amounts are confirmed with your order.',
    'zh': '点击方案下方的按钮，即可打开开通资料表格，填写后再确认订单。目前订单与付款安排仍由我们通过邮件与您确认；本页不收取款项，也不会自动部署系统。安装与迁移另行报价，最终金额以确认订单为准。',
}
js_text = js_text[:offset] + json.dumps(translations, ensure_ascii=False, indent=2) + js_text[offset + size:]
(root / 'bilingual.js').write_text(js_text, encoding='utf-8')
html = html_path.read_text(encoding='utf-8')
import re
html, n = re.subn(r'(data-i18n="pricingNote"[^>]*>)[^<]*', lambda m: m.group(1) + translations['pricingNote']['en'], html)
html_path.write_text(html, encoding='utf-8')
print('pricingNote updated', n)
