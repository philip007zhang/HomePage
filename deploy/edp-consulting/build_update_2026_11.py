"""Build the November 2026 homepage update (what's new, pricing, subscribe/buy entry points).

Input:  deploy/edp-consulting/site          (the currently live release)
Output: deploy/edp-consulting/site-preview  (review copy; not deployed)

Sources: DragonERP one-pager EN 2026-11-21, double-sided overview EN 2026-11-22,
group consolidation one-pager 2026-11-23 (dgERP/docs/Marketing/OnePager), and the live
DragonERP Cloud pricing page https://edp-consulting.au/cloud-ops/pricing.
"""
import json
from pathlib import Path
import shutil

here = Path(__file__).parent
source = here / 'site'
destination = here / 'site-preview'
if destination.exists():
    shutil.rmtree(destination)
shutil.copytree(source, destination)

html = (source / 'index.html').read_text(encoding='utf-8')
javascript = (source / 'bilingual.js').read_text(encoding='utf-8')
prefix = 'const translations = '
offset = javascript.index(prefix) + len(prefix)
translations, length = json.JSONDecoder().raw_decode(javascript[offset:])

SUBSCRIBE_URL = 'https://edp-consulting.au/cloud-ops/pricing'
BUY_URL = 'mailto:philip.zhang@edp-consulting.au?subject=DragonERP%20on-premises%20licence'


def replace_once(text, old, new):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'Expected one match, found {count}: {old[:80]!r}')
    return text.replace(old, new)


def t(key, en, zh):
    translations[key] = {'en': en, 'zh': zh}


def el(tag, key, attrs=''):
    value = translations[key]['en']
    return f'<{tag} data-i18n="{key}"{attrs}>{value}</{tag}>'


# ---------------------------------------------------------------- announcement bar
t('draft',
  'NEW · November 2026: Export to Xero, AU/NZ group consolidation and cloud subscriptions <span>/ See what’s new →</span>',
  '新功能 · 2026 年 11 月：导出至 Xero、澳新集团合并报表、云订阅 <span>/ 查看更新 →</span>')
html = replace_once(html, '<div data-i18n="draft" class="draft">',
                    '<a data-i18n="draft" class="draft" href="#whats-new">')
html = replace_once(html, '</span></div><header>', '</span></a><header>')
html = html.replace(
    '<a data-i18n="draft" class="draft" href="#whats-new">EDP CONSULTING <span> / Enterprise technology and AI delivery.</span>',
    '<a data-i18n="draft" class="draft" href="#whats-new">' + translations['draft']['en'])

# ---------------------------------------------------------------- navigation
t('navNew', 'What’s new', '最新功能')
t('navPricing', 'Pricing', '价格与购买')
html = replace_once(
    html,
    '<a data-i18n="navApproach" href="#approach">My approach</a>',
    el('a', 'navNew', ' href="#whats-new"') + el('a', 'navPricing', ' href="#pricing"'))

# ---------------------------------------------------------------- hero
t('heroPricing', 'Subscribe or buy <span aria-hidden="true">↗</span>', '订阅或购买 <span aria-hidden="true">↗</span>')
html = replace_once(
    html,
    '<a data-i18n="heroContact" class="text-link" href="#contact">',
    el('a', 'heroPricing', ' class="button light" href="#pricing"')
    + '<a data-i18n="heroContact" class="text-link" href="#contact">')

# ---------------------------------------------------------------- highlights: migration card + source note
t('f3Title', 'Data migration, step by step', '数据迁移，分步进行')
t('f3Body',
  'Start with stock only and check it against Xero, or trial-import supported Xero, MYOB or SAP export files. Balances are checked before you move to full accounting and agree a cutover date.',
  '可以先只上库存，并与 Xero 的库存余额核对；也可以用 Xero、MYOB 或 SAP 的导出文件试运行导入。余额核对一致后，再转入完整账务并约定切换日期。')
t('sourceNote',
  'Based on the DragonERP product overview dated 21 November 2026. Feature availability, AI configuration, migration coverage and reporting arrangements are confirmed for each implementation. Statutory payroll outputs require accountant review before use.',
  '内容依据 2026 年 11 月 21 日的 DragonERP 产品介绍。功能范围、AI 配置、迁移范围和申报安排均按具体实施确认；法定薪资输出在使用前须经会计师复核。')
for key, old in [
    ('f3Title', 'Migration with checks'),
    ('f3Body', 'Use supported Xero, MYOB or SAP export files for a trial import. Reconcile account and customer/supplier balances before agreeing a cutover date.'),
    ('sourceNote', 'Based on the supplied product overview dated 6 November 2026. Feature availability, AI configuration, migration coverage and reporting arrangements are confirmed for each implementation. Statutory payroll outputs require accountant review before use.'),
]:
    html = replace_once(html, f'data-i18n="{key}" >{old}<', f'data-i18n="{key}" >{translations[key]["en"]}<') \
        if f'data-i18n="{key}" >{old}<' in html else \
        replace_once(html, f'>{old}<', f'>{translations[key]["en"]}<')

# ---------------------------------------------------------------- what's new section
t('newEye', 'What’s new · November 2026', '最新功能 · 2026 年 11 月')
t('newTitle', 'New in DragonERP.<br><em>Dated and tested.</em>', 'DragonERP 新功能。<br><em>有日期，有测试。</em>')
t('newIntro',
  'Recent work across DragonERP and DragonERP Cloud, with its status. Your accountant can stay on Xero while DragonERP runs China purchasing, landed cost and a bilingual warehouse.',
  'DragonERP 与 DragonERP 云服务的近期进展及当前状态。您的会计可以继续使用 Xero，DragonERP 负责中国采购、到岸成本和中英双语仓库。')
t('statusDone', 'Delivered', '已交付')
t('statusShipped', 'Shipped 16 Nov', '11 月 16 日上线')
t('statusProgress', 'In progress', '开发中')
t('statusCloud', 'Pricing live', '价格已上线')
news = [
    ('n0', 'statusDone', 'done', '⇪',
     'Export to Xero, phase 1', '导出至 Xero（第一阶段）',
     'Each month, export invoices, bills and an inventory journal to Xero with a control sheet and fingerprint. Any difference blocks the export, so your accountant keeps working in Xero.',
     '每月将销售发票、采购账单和库存凭证导出到 Xero，并附核对表和指纹校验；只要有差异就不允许导出，会计继续在 Xero 中工作。'),
    ('n1', 'statusShipped', 'done', '⊞',
     'AU/NZ group consolidation', '澳新集团合并报表',
     'Record intercompany once, eliminate only balances that reconcile, remove profit still sitting in group stock and translate NZD. Group adjustments carry a reason; company books are never rewritten.',
     '内部交易只录一次；只抵销能对上的余额；剔除仍留在集团库存中的未实现利润，并折算纽币。集团调整逐笔注明原因，不改写各公司账簿。'),
    ('n2', 'statusProgress', 'progress', '▦',
     'Stock-first setup', '先上库存',
     'Start with products and opening stock only, checked against Xero’s stock balance, before full accounting. The opening-stock import loads all rows or none.',
     '先只导入商品和期初库存，并与 Xero 库存余额核对，不必一开始就上完整账务。期初库存导入要么全部成功，要么一行都不写入。'),
    ('n3', 'statusProgress', 'progress', '?',
     'Smart query', '智能查询',
     'Ask in English or Chinese. AI writes a query specification, never SQL; it runs read-only and is checked against the standard report. Pin the queries you use often.',
     '用中文或英文提问。AI 只生成查询规格，不写 SQL；查询只读执行，并与标准报表交叉核对。常用查询可以固定。'),
    ('n4', 'statusProgress', 'progress', '▣',
     'Bill capture on your server', '本地服务器单据识别',
     'On-server OCR turns a photo or PDF into a draft bill, matched line by line to the purchase order and goods received. Differences go to a person.',
     '在您自己的服务器上用 OCR 把照片或 PDF 转为采购账单草稿，并与采购订单、收货逐行三单匹配；差异交由人工处理。'),
    ('n5', 'statusCloud', 'cloud', '☁',
     'DragonERP Cloud subscriptions', 'DragonERP 云订阅',
     'Hosted DragonERP with a separate database per customer, encrypted backups with restore checks and secure card binding through Stripe. Self-service sign-up is being prepared; until then we set you up personally.',
     '托管版 DragonERP：每位客户独立数据库，加密备份并定期做恢复检查，通过 Stripe 安全绑定付款方式。自助开通正在准备中，目前由我们为您人工开通。'),
]
cards = []
for key, status_key, status_class, icon, en_title, zh_title, en_body, zh_body in news:
    t(key + 'Title', en_title, zh_title)
    t(key + 'Body', en_body, zh_body)
    cards.append(
        f'<article class="news-card"><div class="news-top"><div class="feature-icon" aria-hidden="true">{icon}</div>'
        f'<span class="status {status_class}" data-i18n="{status_key}">{translations[status_key]["en"]}</span></div>'
        + el('h3', key + 'Title') + el('p', key + 'Body') + '</article>')
t('newNext',
  '<strong>Next:</strong> MYOB export (phase 2), an accountant console, and a full-month import test in a Xero trial organisation.',
  '<strong>下一步：</strong>导出至 MYOB（第二阶段）、会计师控制台，以及在 Xero 试用组织中进行整月导入测试。')
t('proof0Label', 'backend unit and integration tests passed in a full run (19 Nov 2026)', '后端单元与集成测试全部通过（2026 年 11 月 19 日全量运行）')
t('proof1Label', 'end-to-end browser scenarios passed, including stock-first setup and Export to Xero (18 Nov 2026)', '端到端浏览器场景全部通过，含“先上库存”与导出至 Xero（2026 年 11 月 18 日）')
t('proof2Label', 'trial balance P95 on 10 million ledger lines, down from 25.6 s (13 Nov 2026, synthetic data)', '一千万行总账上试算平衡表 P95 用时，此前为 25.6 秒（2026 年 11 月 13 日，合成数据）')
t('newNote',
  'Export to Xero is a file import, not an API link; DragonERP does not lodge directly with the ATO. Group consolidation covers management consolidation of wholly owned AU and NZ companies; equity elimination, goodwill and deferred tax remain with your accountant. Capabilities and timeframes are confirmed during evaluation. Full test records on request.',
  '导出至 Xero 为文件导入，不是 API 直连；DragonERP 不直接向 ATO 申报。集团合并适用于全资澳新公司的管理口径合并；权益抵销、商誉和递延所得税仍由会计师处理。功能与时间以评估确认为准，完整测试记录可按需提供。')
whats_new = (
    '<section class="wrap section whats-new" id="whats-new" aria-labelledby="new-title">'
    '<div class="eyebrow"><span class="dot"></span>' + el('span', 'newEye') + '</div>'
    '<div class="section-heading">' + el('h2', 'newTitle', ' id="new-title"') + el('p', 'newIntro') + '</div>'
    '<div class="news-grid">' + ''.join(cards) + '</div>'
    + el('p', 'newNext', ' class="news-next"')
    + '<div class="proof-strip">'
    '<div><strong>1,402</strong>' + el('span', 'proof0Label') + '</div>'
    '<div><strong>91 / 91</strong>' + el('span', 'proof1Label') + '</div>'
    '<div><strong>0.02 s</strong>' + el('span', 'proof2Label') + '</div>'
    '</div>' + el('p', 'newNote', ' class="source-note"') + '</section>')
html = replace_once(html, '<section class="wrap" aria-labelledby="focus-title">',
                    whats_new + '<section class="wrap" aria-labelledby="focus-title">')

# ---------------------------------------------------------------- getting started (migration path)
steps = {
    'step0Title': ('A walk-through', '先看一遍演示'),
    'step0Body': ('See an order from China through landed cost and sales to the export for Xero.',
                  '看一张订单从中国采购，经过到岸成本和销售，一直走到导出至 Xero。'),
    'step1Title': ('Start with stock', '先上库存'),
    'step1Body': ('Import products and opening stock and check them against Xero’s stock balance. Your accountant’s work stays the same.',
                  '导入商品和期初库存，并与 Xero 库存余额核对。会计的工作方式不变。'),
    'step2Title': ('An agreed plan', '约定上线计划'),
    'step2Body': ('Confirm modules, the export or full accounting, and training, then set the cutover date.',
                  '确认模块、只做导出还是上完整账务，以及培训安排，然后确定切换日期。'),
}
for key, (en, zh) in steps.items():
    old = translations[key]['en']
    html = replace_once(html, f'data-i18n="{key}" >{old}<', f'data-i18n="{key}" >{en}<')
    t(key, en, zh)
html = replace_once(html, f'>{translations["processEye"]["en"]}<', '>Getting started<')
t('processEye', 'Getting started', '如何开始')

# ---------------------------------------------------------------- pricing section
t('pricingEye', 'Pricing · subscribe or buy', '价格 · 订阅或购买')
t('pricingTitle', 'Clear pricing.<br><em>Subscribe or own it.</em>', '价格清楚。<br><em>订阅，或买断。</em>')
t('pricingIntro',
  'All prices in Australian dollars, excluding GST (10%). Cloud subscriptions are counted in blocks of five contract users, up to 50 users.',
  '所有价格以澳元计价，均不含 GST（10%）。云订阅每五位合同用户为一个计价单位，最多 50 人。')
t('planMonthlyName', 'Cloud · monthly', '云订阅 · 月付')
t('planMonthlyUnit', 'per month, per 5 users', '每月 / 每 5 位用户')
t('planYearlyName', 'Cloud · yearly', '云订阅 · 年付')
t('planYearlyUnit', 'per year, per 5 users', '每年 / 每 5 位用户')
t('planYearlyBadge', 'Save about 17%', '约省 17%')
t('planLicenceName', 'On-premises licence', '本地买断')
t('planLicenceUnit', 'one-off, 20 users', '一次性 / 20 位用户')
t('exGst', 'excl. GST', '未含 GST')
t('planMonthly0', 'Hosted by EDP, separate database per customer', 'EDP 托管，每位客户独立数据库')
t('planMonthly1', 'Encrypted backups with restore checks', '加密备份并做恢复检查')
t('planMonthly2', 'Three-month trial after card binding and activation', '绑定付款方式并开通后，可试用三个自然月')
t('planYearly0', 'Everything in the monthly plan', '包含月付的全部内容')
t('planYearly1', 'One payment a year instead of twelve', '一年付一次，免去每月扣款')
t('planYearly2', 'About 17% less than 12 monthly payments', '比按月付 12 个月约省 17%')
t('planLicence0', 'Runs on your own server', '部署在您自己的服务器上')
t('planLicence1', 'Local AI model options; your data stays with you', '可选本地 AI 模型，数据留在您手中')
t('planLicence2', 'Includes the first 12 months of updates; extra users A$18 each', '含首 12 个月更新；超过 20 人每人 A$18 加购')
t('planLicence3', 'Installation, migration and support quoted separately', '安装、迁移与支持另行报价')
t('ctaSubscribe', 'Subscribe <span aria-hidden="true">↗</span>', '立即订阅 <span aria-hidden="true">↗</span>')
t('ctaSubscribeYearly', 'Subscribe yearly <span aria-hidden="true">↗</span>', '按年订阅 <span aria-hidden="true">↗</span>')
t('ctaBuy', 'Buy a licence <span aria-hidden="true">↗</span>', '采购软件 <span aria-hidden="true">↗</span>')
t('pricingNote',
  'Subscribe opens the live price calculator in DragonERP Cloud. Self-service sign-up is being prepared, so orders are currently confirmed with you personally. Buy a licence opens an email to Philip. Implementation and data migration are not included and are quoted after a walk-through; final pricing per quote.',
  '“立即订阅”会打开 DragonERP 云服务的实时价格计算器；自助开通正在准备中，目前订单由我们与您人工确认。“采购软件”会打开写给 Philip 的邮件。实施与数据迁移不含在内，演示后另行报价，最终价格以报价为准。')


def plan(name, price, unit, items, cta, href, classes='', badge='', external=False):
    rel = ' target="_blank" rel="noopener"' if external else ''
    head = f'<div class="plan-head">{el("h3", name)}'
    head += (f'<span class="plan-badge" data-i18n="{badge}">{translations[badge]["en"]}</span>' if badge else '') + '</div>'
    body = (f'<p class="plan-price"><strong>{price}</strong>' + el('span', unit) + '</p>'
            + el('p', 'exGst', ' class="plan-tax"')
            + '<ul>' + ''.join(el('li', k) for k in items) + '</ul>')
    return (f'<article class="plan-card{classes}">' + head + body
            + f'<a class="button {"orange" if "featured" in classes else ""}" href="{href}"{rel} data-i18n="{cta}">'
            + translations[cta]['en'] + '</a></article>')


pricing = (
    '<section class="wrap section pricing" id="pricing" aria-labelledby="pricing-title">'
    '<div class="eyebrow"><span class="dot"></span>' + el('span', 'pricingEye') + '</div>'
    '<div class="section-heading">' + el('h2', 'pricingTitle', ' id="pricing-title"') + el('p', 'pricingIntro') + '</div>'
    '<div class="plan-grid">'
    + plan('planMonthlyName', 'A$48.88', 'planMonthlyUnit', ['planMonthly0', 'planMonthly1', 'planMonthly2'],
           'ctaSubscribe', SUBSCRIBE_URL, external=True)
    + plan('planYearlyName', 'A$488', 'planYearlyUnit', ['planYearly0', 'planYearly1', 'planYearly2'],
           'ctaSubscribeYearly', SUBSCRIBE_URL, ' featured', 'planYearlyBadge', external=True)
    + plan('planLicenceName', 'A$1,888', 'planLicenceUnit', ['planLicence0', 'planLicence1', 'planLicence2', 'planLicence3'],
           'ctaBuy', BUY_URL)
    + '</div>' + el('p', 'pricingNote', ' class="source-note"') + '</section>')
html = replace_once(html, '<section class="wrap section faq-layout" id="questions"',
                    pricing + '<section class="wrap section faq-layout" id="questions"')

# ---------------------------------------------------------------- FAQ
faq_updates = {
    'a2': ('Yes. Start with stock only and check it against Xero, or trial-import supported Xero, MYOB or SAP export files and reconcile balances. Coverage and the cutover plan are agreed after checking your data.',
           '可以。可以先只上库存并与 Xero 核对，也可以用 Xero、MYOB 或 SAP 的导出文件试运行导入并核对余额。迁移范围和切换计划在检查您的数据后约定。'),
    'a3': ('Cloud subscriptions are A$48.88 a month or A$488 a year per five users (excl. GST). An on-premises licence is A$1,888 one-off for 20 users (excl. GST). Implementation and migration are quoted after a walk-through.',
           '云订阅每 5 位用户每月 A$48.88，或每年 A$488（未含 GST）；本地买断为一次性 A$1,888（未含 GST），含 20 位用户。实施与迁移在演示后另行报价。'),
}
for key, (en, zh) in faq_updates.items():
    old = translations[key]['en']
    html = replace_once(html, f'data-i18n="{key}" >{old}<', f'data-i18n="{key}" >{en}<')
    t(key, en, zh)
t('q4', 'How do I subscribe or buy?', '如何订阅或采购？')
t('a4', 'Choose a plan under <a href="#pricing">Pricing</a>. Subscribe opens the DragonERP Cloud price calculator; Buy a licence opens an email to Philip. We confirm the order, terms and start date with you before anything is charged.',
  '在<a href="#pricing">价格与购买</a>中选择方案。“立即订阅”打开 DragonERP 云服务价格计算器；“采购软件”打开写给 Philip 的邮件。在任何扣款之前，我们会先与您确认订单、条款和开始日期。')
html = replace_once(html, '</details></div></section><section class="wrap contact"',
                    '</details><details>' + el('summary', 'q4') + el('p', 'a4') + '</details></div></section><section class="wrap contact"')

# ---------------------------------------------------------------- track record (from Philip's CV / LinkedIn)
# Sources: earlier approved homepage copy in data/company.json + data/expertise.json + data/cases.json,
# and the public LinkedIn profile (40+ years in IT, CNPC consolidation recommendation, languages).
t('xpEye', 'Track record', '过往经历')
t('xpTitle', 'Decades of enterprise IT.<br><em>Now built for smaller teams.</em>', '数十年企业级 IT 经验。<br><em>如今为中小团队所用。</em>')
t('xpIntro',
  'Before DragonERP, Philip spent his career in SAP architecture, system migration and enterprise transformation for large organisations in Asia, Australia and Europe. That experience shapes how DragonERP handles ledgers, migration and control.',
  '在开发 DragonERP 之前，Philip 长期从事 SAP 架构、系统迁移与企业转型，服务亚洲、澳洲和欧洲的大型企业。这些经验直接体现在 DragonERP 的账务设计、数据迁移和内控方式上。')
t('xpRolesTitle', 'Selected work', '代表性工作')
roles = [
    ('xpR0', 'msg Global Solutions China', 'Business Unit Director: built the business unit and owned delivery, growth and service quality.',
     '业务单元总监：负责业务单元的建设、交付、增长与服务质量。'),
    ('xpR1', 'SNP SE', 'Transformation Director: SAP transformation and data migration programmes, including system landscape consolidation.',
     '转型总监：负责 SAP 转型与数据迁移项目，包括系统架构整合。'),
    ('xpR2', 'SAP Australia / Germany', 'Principal Solution Architect and consultant across global projects and migrations.',
     '首席解决方案架构师及顾问，参与多个全球项目与系统迁移。'),
    ('xpR3', 'EDP Consulting GmbH, Germany', 'Founded in 1998: SAP consulting, development services and analytical software.',
     '1998 年创立：SAP 咨询、开发服务与分析软件。'),
]
role_items = ''
for key, org, en, zh in roles:
    t(key, en, zh)
    role_items += f'<li><strong>{org}</strong>' + el('span', key) + '</li>'
t('xpProjectsTitle', 'Selected projects', '代表性项目')
projects = [
    ('xpP0', 'CNPC · China', 'SAP system consolidation', 'SAP 系统整合',
     'Four years on CNPC’s SAP system consolidation: from business development with top IT management on the 12th Five-Year Plan direction to trusted advisor through delivery.',
     '参与中国石油（CNPC）SAP 系统整合项目四年：从配合高层制定“十二五”IT 方向的业务拓展，到贯穿交付全程的信任顾问。'),
    ('xpP1', 'SNP · global', 'S/4HANA migration & SLO', 'S/4HANA 迁移与 SLO 转型',
     'Company-code, system and landscape transformations with a focus on reducing downtime and keeping balances reconciled through cutover.',
     '公司代码、系统与架构层面的转型迁移，重点在缩短停机时间，并保证切换前后余额一致。'),
    ('xpP2', 'Lenovo · BMW · SONY · BHP', 'Enterprise SAP programmes', '大型企业 SAP 项目',
     'Client work across China, Singapore, Australia, Germany and France in manufacturing, automotive, consumer goods and energy, including global rollouts.',
     '客户覆盖中国、新加坡、澳大利亚、德国和法国，涉及制造、汽车、消费品和能源行业，包括全球推广项目。'),
    ('xpP3', 'EDP · today', 'Software built with AI agents', '与 AI agents 协同开发的软件',
     'DragonERP and DragonERP Cloud, plus an OCR schedule converter for a rehabilitation provider, a feedback and evaluation portal, a realtime voice-agent prototype and a WeChat Mini Program.',
     'DragonERP 与 DragonERP 云服务；另有康复机构的 OCR 排程转换工具、问卷与评估平台、实时语音助手原型，以及微信小程序。'),
]
project_cards = ''
for key, client, en_t, zh_t, en_b, zh_b in projects:
    t(key + 'Title', en_t, zh_t)
    t(key + 'Body', en_b, zh_b)
    project_cards += (f'<article class="xp-card"><span class="xp-client">{client}</span>'
                      + el('h3', key + 'Title') + el('p', key + 'Body') + '</article>')
t('xpLangs', 'Works in Chinese, German and English.', '中文、德语、英语均可工作交流。')
t('xpLink', 'Full profile and ERP articles on LinkedIn <span aria-hidden="true">↗</span>', '在领英查看完整履历与 ERP 系列文章 <span aria-hidden="true">↗</span>')
experience = (
    '<section class="wrap section experience" id="experience" aria-labelledby="xp-title">'
    '<div class="eyebrow"><span class="dot"></span>' + el('span', 'xpEye') + '</div>'
    '<div class="section-heading">' + el('h2', 'xpTitle', ' id="xp-title"') + el('p', 'xpIntro') + '</div>'
    '<div class="xp-layout"><div class="xp-roles">' + el('h3', 'xpRolesTitle') + '<ul>' + role_items + '</ul>'
    + el('p', 'xpLangs', ' class="xp-langs"')
    + '<a class="text-link" href="https://www.linkedin.com/in/philip-zhang-9a59007/" target="_blank" rel="noopener" data-i18n="xpLink">'
    + translations['xpLink']['en'] + '</a></div>'
    '<div class="xp-projects">' + el('h3', 'xpProjectsTitle') + '<div class="xp-grid">' + project_cards + '</div></div></div>'
    '</section>')
html = replace_once(html, '<section class="wrap section" id="services"', experience + '<section class="wrap section" id="services"')
t('navExperience', 'Experience', '过往经历')
html = replace_once(html, '<a data-i18n="navServices" href="#services">Services</a>',
                    el('a', 'navExperience', ' href="#experience"') + '<a data-i18n="navServices" href="#services">Services</a>')

# ---------------------------------------------------------------- DragonERP logo + downloadable materials
materials = here / 'materials'
shutil.copy2(materials / 'dragonerp-logo.png', destination / 'assets' / 'dragonerp-logo.png')
shutil.copytree(materials / 'downloads', destination / 'downloads')
shutil.copytree(materials / 'thumbs', destination / 'assets' / 'materials')

lockup = ('<div class="dragon-lockup"><img src="assets/dragonerp-logo.png" alt="DragonERP logo" width="78" height="90">'
          '<div><strong>Dragon <em>ERP</em></strong><span class="dragon-cn">龙 ERP</span></div></div>')
# Highlights heading: headline left, logo + description on the same row (two layout variants for review).
hl_head = '<div class="section-heading"><h2 data-i18n="highlightsTitle" id="highlights-title">'
i = html.index(hl_head)
j = html.index('</h2>', i) + len('</h2>')
k = html.index('</p></div>', j) + len('</p></div>')
h2_part = html[i + len('<div class="section-heading">'):j]
p_part = html[j:k - len('</div>')]
layout_a = '<div class="section-heading hl-head hl-a">' + h2_part + lockup + p_part + '</div>'
layout_b = '<div class="section-heading hl-head hl-b">' + h2_part + p_part + lockup + '</div>'
html = html[:i] + layout_b + html[k:]  # Philip chose layout B (logo far right) on 2026-11-23

t('dlEye', 'Learn more · downloads', '了解更多 · 资料下载')
t('dlTitle', 'Product materials<br><em>to download.</em>', '产品资料，<br><em>随时下载。</em>')
t('dlIntro', 'PDFs to read later or share with your accountant or business partner.', 'PDF 格式，方便稍后阅读，或转给您的会计和合作伙伴。')
t('dl0Title', 'One-page overview', '一页介绍')
t('dl0Meta', 'What DragonERP does, the latest progress and how to get started, on one page.', '一页看懂 DragonERP 的功能、最新进展和如何开始。')
t('dl1Title', 'Double-sided overview', '双面彩页')
t('dl1Meta', 'The full purchase-to-tax process, pricing and a three-year cost comparison.', '从采购到报税的完整流程、价格及三年成本对比。')
t('dl2Title', 'Group consolidation', '集团合并报表')
t('dl2Meta', 'How one ledger design consolidates several AU and NZ companies.', '一套账务设计，如何合并多家澳新公司的报表。')
t('dl3Title', 'Product white paper', '产品白皮书')
t('dl3Meta', 'Architecture, modules, AI controls and test results in depth.', '深入介绍架构、模块、AI 管控与测试结果。')
t('dlEn', 'English', '英文版')
t('dlZh', '中文', '中文版')
t('dlSoon', '中文 · coming soon', '中文版 · 即将推出')


def dl_item(key, thumb, en, zh):
    zh_btn = (f'<a class="dl-link" href="downloads/{zh}" download data-i18n="dlZh">{translations["dlZh"]["en"]}</a>' if zh
              else f'<span class="dl-link soon" data-i18n="dlSoon">{translations["dlSoon"]["en"]}</span>')
    en_btn = f'<a class="dl-link" href="downloads/{en}" download data-i18n="dlEn">{translations["dlEn"]["en"]}</a>'
    return (f'<article class="dl-item"><img class="dl-thumb" src="assets/materials/{thumb}" alt="" loading="lazy" width="40" height="56">'
            '<div class="dl-text">' + el('h3', key + 'Title') + el('p', key + 'Meta', ' class="dl-meta"') + '</div>'
            f'<div class="dl-links">{zh_btn}{en_btn}</div></article>')


downloads = (
    '<section class="wrap section downloads" id="downloads" aria-labelledby="dl-title">'
    '<div class="eyebrow"><span class="dot"></span>' + el('span', 'dlEye') + '</div>'
    '<div class="section-heading">' + el('h2', 'dlTitle', ' id="dl-title"') + el('p', 'dlIntro') + '</div>'
    '<div class="dl-list">'
    + dl_item('dl0', 'DragonERP-One-Pager-EN.jpg', 'DragonERP-One-Pager-EN.pdf', 'DragonERP-One-Pager-ZH.pdf')
    + dl_item('dl1', 'DragonERP-Double-sided-Overview-EN.jpg', 'DragonERP-Double-sided-Overview-EN.pdf', None)
    + dl_item('dl2', 'DragonERP-Group-Consolidation-EN.jpg', 'DragonERP-Group-Consolidation-EN.pdf', None)
    + dl_item('dl3', 'DragonERP-White-Paper-EN.jpg', 'DragonERP-White-Paper-EN.pdf', 'DragonERP-White-Paper-ZH.pdf')
    + '</div></section>')
html = replace_once(html, '<section class="wrap section whats-new"', downloads + '<section class="wrap section whats-new"')
t('navDownloads', 'Downloads', '资料下载')
html = replace_once(html, '<a data-i18n="navPricing" href="#pricing">',
                    el('a', 'navDownloads', ' href="#downloads"') + '<a data-i18n="navPricing" href="#pricing">')
html = replace_once(html, '<a data-i18n="navExperience" href="#experience">Experience</a>', '')

# ---------------------------------------------------------------- feedback / issue reporting
FEEDBACK_TO = 'philip.zhang@edp-consulting.au'
t('feedbackTop', 'Questions, feedback or a complaint? Tell us →', '有疑问、反馈或投诉？告诉我们 →')
html = replace_once(html, '<a data-i18n="draft" class="draft" href="#whats-new">',
                    '<div class="draft topbar"><a data-i18n="draft" class="topbar-news" href="#whats-new">')
html = replace_once(html, '</span></a><header>',
                    '</span></a>' + el('a', 'feedbackTop', ' class="topbar-feedback" href="#feedback"') + '</div><header>')
t('fbEye', 'Questions, feedback & complaints', '咨询、反馈与投诉')
t('fbTitle', 'A question or a problem?<br><em>Tell Philip directly.</em>', '有疑问，或哪里不好用？<br><em>直接告诉 Philip。</em>')
t('fbIntro',
  'Ask a question, report a bug or an inconvenient step, or make a complaint about DragonERP, DragonERP Cloud or this website. Every message is read by Philip, and you get a personal reply.',
  '关于 DragonERP、DragonERP 云服务或本网站，无论是咨询问题、遇到故障、操作不便，还是任何不满意，都可以在这里提出。每条留言都由 Philip 本人阅读并亲自回复。')
t('fbTypeLabel', 'Type', '类型')
t('fbTypeQuestion', 'Question', '咨询问题')
t('fbTypeBug', 'Something is not working', '功能故障 / 报错')
t('fbTypeUx', 'Inconvenient to use', '操作不便')
t('fbTypeComplaint', 'Complaint', '投诉')
t('fbTypeIdea', 'Suggestion', '建议')
t('fbProductLabel', 'About', '涉及')
t('fbProductErp', 'DragonERP', 'DragonERP')
t('fbProductCloud', 'DragonERP Cloud / billing', 'DragonERP 云服务 / 账单')
t('fbProductWeb', 'This website', '本网站')
t('fbMessageLabel', 'Your question or what happened', '您的问题或具体情况')
t('fbMessageHint', 'For a problem: what were you doing, what did you expect, and what happened instead?', '如果是问题：您当时在做什么？原本期望什么结果？实际发生了什么？')
t('fbNameLabel', 'Your name or company (optional)', '姓名或公司（选填）')
t('fbSubmit', 'Send <span aria-hidden="true">↗</span>', '提交 <span aria-hidden="true">↗</span>')
t('fbNote', 'Sending opens your own email app with the message filled in; nothing is stored on this website. Screenshots can be attached there. Or email <a href="mailto:philip.zhang@edp-consulting.au">philip.zhang@edp-consulting.au</a> directly.',
  '提交后会打开您自己的邮件应用并自动填好内容，本网站不保存任何信息；截图可在邮件中附上。也可以直接发邮件至 <a href="mailto:philip.zhang@edp-consulting.au">philip.zhang@edp-consulting.au</a>。')
t('fbEmpty', 'Please write your question or what happened first.', '请先填写您的问题或具体情况。')
feedback = (
    '<dialog class="fb-dialog" id="feedback" aria-labelledby="fb-title">'
    '<button type="button" class="fb-close" aria-label="Close">×</button><div class="fb-head">'
    '<div class="eyebrow"><span class="dot"></span>' + el('span', 'fbEye') + '</div>'
    + el('h2', 'fbTitle', ' id="fb-title"') + el('p', 'fbIntro') + '</div>'
    f'<form class="fb-form" id="feedback-form" data-to="{FEEDBACK_TO}" novalidate>'
    '<div class="fb-row"><label>' + el('span', 'fbTypeLabel') + '<select name="type">'
    + ''.join(f'<option value="{k}" data-i18n="{k}">{translations[k]["en"]}</option>' for k in ['fbTypeQuestion', 'fbTypeBug', 'fbTypeUx', 'fbTypeComplaint', 'fbTypeIdea'])
    + '</select></label><label>' + el('span', 'fbProductLabel') + '<select name="product">'
    + ''.join(f'<option value="{k}" data-i18n="{k}">{translations[k]["en"]}</option>' for k in ['fbProductErp', 'fbProductCloud', 'fbProductWeb'])
    + '</select></label></div>'
    '<label>' + el('span', 'fbMessageLabel') + '<textarea name="message" rows="5" required></textarea>'
    + el('small', 'fbMessageHint') + '</label>'
    '<label>' + el('span', 'fbNameLabel') + '<input name="name" type="text" autocomplete="organization"></label>'
    + el('p', 'fbEmpty', ' class="fb-error" hidden')
    + '<button type="submit" class="button orange" data-i18n="fbSubmit">' + translations['fbSubmit']['en'] + '</button>'
    + el('p', 'fbNote', ' class="fb-note"') + '</form></dialog>')
html = replace_once(html, '<script src="bilingual.js"></script>', feedback + '<script src="bilingual.js"></script>')
feedback_js = r'''
const fbForm=document.getElementById('feedback-form');
if(fbForm){fbForm.addEventListener('submit',event=>{event.preventDefault();
  const data=new FormData(fbForm);const message=(data.get('message')||'').trim();const error=fbForm.querySelector('.fb-error');
  if(!message){error.hidden=false;fbForm.message.focus();return;}error.hidden=true;
  const pick=name=>fbForm[name].options[fbForm[name].selectedIndex].text;
  const subject='[Website] '+pick('type')+' · '+pick('product');
  const body=message+'\n\n—\n'+pick('type')+' · '+pick('product')+(data.get('name')?'\n'+data.get('name'):'')+'\nPage: '+location.href;
  location.href='mailto:'+fbForm.dataset.to+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);fbDialog.close();});}
const fbDialog=document.getElementById('feedback');
function openFeedback(){if(fbDialog&&!fbDialog.open){fbDialog.showModal();fbForm.querySelector('select').focus();}}
document.querySelectorAll('a[href="#feedback"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();openFeedback();}));
if(fbDialog){fbDialog.querySelector('.fb-close').addEventListener('click',()=>fbDialog.close());
  fbDialog.addEventListener('click',e=>{if(e.target===fbDialog)fbDialog.close();});}
if(location.hash==='#feedback')openFeedback();
'''

# ---------------------------------------------------------------- comparison radar carousel
# Scores: "ERP Architecture for SMBs" (dgERP/docs/Marketing/Others, 16 Nov 2026) and LinkedIn carousel slide 3/7.
import math
dims = [
    ('Integration', '业财一体化'),
    ('Data volume', '数据量'),
    ('Concurrency', '并发'),
    ('Permissions', '权限'),
    ('Multi-company', '多公司合并'),
    ('Interfaces', '接口'),
    ('Audit', '审计'),
    ('Functions', '功能'),
    ('AU compliance', '本地合规'),
    ('Ease of use', '易用性'),
    ('Cost', '成本'),
    ('Data sovereignty', '数据主权'),
]
scores = {
    'Dragon ERP': [5, 4, 3, 4, 4, 4, 5, 4, 4, 4, 5, 5],  # multi-company 2 -> 4 after group consolidation shipped 16 Nov 2026
    'Xero': [2, 4, 3, 2, 2, 3, 3, 2, 5, 5, 4, 2],
    'MYOB': [2, 3, 2, 2, 2, 3, 3, 3, 5, 4, 4, 3],
    'QuickBooks Online': [2, 4, 3, 2, 2, 3, 3, 2, 4, 5, 4, 2],
    'SAP ECC': [4, 5, 5, 5, 5, 4, 4, 5, 3, 1, 1, 4],
    'SAP S/4HANA': [5, 5, 5, 5, 5, 4, 4, 5, 3, 1, 1, 3],
}
for i, (en, zh) in enumerate(dims):
    t(f'dim{i}', en, zh)


def radar_svg(other, other_scores):
    cx, cy, r = 300, 250, 165
    n = len(dims)
    pt = lambda i, v: (cx + r * v / 5 * math.sin(2 * math.pi * i / n), cy - r * v / 5 * math.cos(2 * math.pi * i / n))
    rings = ''.join('<polygon class="ring" points="' + ' '.join('%.1f,%.1f' % pt(i, k) for i in range(n)) + '"/>' for k in range(1, 6))
    axes = ''.join('<line class="axis" x1="%d" y1="%d" x2="%.1f" y2="%.1f"/>' % ((cx, cy) + pt(i, 5)) for i in range(n))
    labels = ''
    for i in range(n):
        x, y = pt(i, 5.95)
        anchor = 'middle' if abs(x - cx) < 20 else ('start' if x > cx else 'end')
        labels += f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="{anchor}" data-i18n="dim{i}">{dims[i][0]}</text>'
    poly = lambda s, cls: (f'<polygon class="{cls}" points="' + ' '.join('%.1f,%.1f' % pt(i, v) for i, v in enumerate(s)) + '"/>'
                           + ''.join('<circle class="%s-dot" cx="%.1f" cy="%.1f" r="3.5"/>' % ((cls,) + pt(i, v)) for i, v in enumerate(s)))
    return (f'<svg viewBox="-95 -5 790 510" role="img" aria-label="Dragon ERP vs {other}">' + rings + axes
            + poly(other_scores, 'other') + poly(scores['Dragon ERP'], 'dragon') + labels + '</svg>')


avg = [round(sum(scores[k][i] for k in scores if k != 'Dragon ERP') / 5, 1) for i in range(len(dims))]
slides = [(k, scores[k], sum(scores[k])) for k in ['Xero', 'MYOB', 'QuickBooks Online', 'SAP ECC', 'SAP S/4HANA']]
slides.append(('average', avg, round(sum(avg), 1)))
t('cmpAvgName', 'Average of the five', '五家平均')
t('cmpEye', 'How we compare', '横向对比')
t('cmpTitle', 'Twelve dimensions.<br><em>Six ERP architectures.</em>', '十二个维度，<br><em>六种 ERP 架构。</em>')
t('cmpIntro', 'Each system is scored 1 to 5 on what a 5–100 person business needs from an ERP. The slides change every five seconds; hover or tap to pause.',
  '按 5 至 100 人企业对 ERP 的实际需求，每个系统在每个维度上打 1 至 5 分。每五秒切换一张，鼠标悬停或点按即可暂停。')
t('cmpLegendDragon', 'Dragon ERP', 'Dragon ERP')
t('cmpCaption', '12 dimensions, 1–5 each, out of 60', '12 个维度，每项 1–5 分，满分 60')
t('cmpSource',
  'Six ERP architectures compared on what a 5–100 person business needs. Source: Philip Zhang, “ERP Architecture for Small and Medium Businesses”, 16 Nov 2026; competitors scored from public documentation and the author’s estimates; product maturity excluded. Dragon ERP multi-company raised from 2 to 4 after group consolidation shipped on 16 Nov. Third-party names identify products only.',
  '六种 ERP 架构，按 5 至 100 人企业的实际需求对比。来源：Philip Zhang《中小企业 ERP 架构：需求推导与六种架构对比》（2026 年 11 月 16 日）；竞品依据公开资料及作者估计评分，不含产品成熟度。11 月 16 日集团合并上线后，Dragon ERP“多公司合并”由 2 分调为 4 分。第三方名称仅用于产品识别。')
slide_html = ''
for idx, (name, s, total) in enumerate(slides):
    label = el('span', 'cmpAvgName') if name == 'average' else name
    slide_html += (f'<figure class="cmp-slide{" active" if idx == 0 else ""}" data-index="{idx}">' + radar_svg(name, s)
                   + f'<figcaption><span class="cmp-vs"><span class="key dragon"></span>Dragon ERP <strong>{sum(scores["Dragon ERP"])}</strong>'
                   f'<span class="cmp-sep">vs</span><span class="key other"></span>{label} <strong>{total:g}</strong></span>'
                   + el('span', 'cmpCaption', ' class="cmp-note"') + '</figcaption></figure>')
dots = ''.join(f'<button type="button" class="cmp-dot{" active" if i == 0 else ""}" aria-label="{i + 1}"></button>' for i in range(len(slides)))
comparison = (
    '<div class="cmp-carousel" id="cmp-carousel" aria-roledescription="carousel">'
    '<button type="button" class="cmp-nav prev" aria-label="Previous">‹</button>'
    '<div class="cmp-stage">' + slide_html + '</div>'
    '<button type="button" class="cmp-nav next" aria-label="Next">›</button>'
    '<div class="cmp-dots">' + dots + '</div></div>'
    + el('p', 'cmpSource', ' class="source-note cmp-source"'))
faq_title_end = '<h2 data-i18n="faqTitle" id="faq-title">Before we<br><em>get started.</em></h2></div>'
html = replace_once(html, faq_title_end, faq_title_end[:-len('</div>')] + comparison + '</div>')
carousel_js = r'''
(()=>{const root=document.getElementById('cmp-carousel');if(!root)return;
const slides=[...root.querySelectorAll('.cmp-slide')],dots=[...root.querySelectorAll('.cmp-dot')];let i=0,timer=null,paused=false;
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function show(n){i=(n+slides.length)%slides.length;slides.forEach((s,k)=>s.classList.toggle('active',k===i));dots.forEach((d,k)=>d.classList.toggle('active',k===i));}
function start(){stop();if(!reduce&&!paused)timer=setInterval(()=>show(i+1),5000);}
function stop(){if(timer)clearInterval(timer);timer=null;}
root.querySelector('.prev').addEventListener('click',()=>{show(i-1);start();});
root.querySelector('.next').addEventListener('click',()=>{show(i+1);start();});
dots.forEach((d,k)=>d.addEventListener('click',()=>{show(k);start();}));
root.addEventListener('mouseenter',()=>{paused=true;stop();});root.addEventListener('mouseleave',()=>{paused=false;start();});
root.querySelector('.cmp-stage').addEventListener('click',()=>{paused=!paused;paused?stop():start();});
document.addEventListener('visibilitychange',()=>document.hidden?stop():start());start();})();
'''
feedback_js += carousel_js
t('navCompare', 'Compare', '横向对比')

# ---------------------------------------------------------------- styles
css = (
    'a.draft{display:block}a.draft:hover{text-decoration:underline;text-underline-offset:3px}'
    '.whats-new{border-top:1px solid var(--line)}'
    '.news-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}'
    '.news-card{border:1px solid #d4dbd1;border-radius:6px;padding:26px;background:#fffefa}'
    '.news-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:20px}'
    '.news-card .feature-icon{width:39px;height:39px;display:grid;place-items:center;background:#e8eee5;border-radius:8px;color:var(--green);font-size:19px}'
    '.news-card h3{font-size:19px;margin-bottom:12px}.news-card p{font-size:14px}'
    '.status{font-size:10px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;padding:5px 9px;border-radius:3px;white-space:nowrap}'
    '.status.done{background:#dfeadf;color:#2b5440}.status.progress{background:#f6e7d8;color:#8a3a1e}.status.cloud{background:#1d2d39;color:#fffefa}'
    '.news-next{font-size:14px;margin-top:20px}.news-next strong{color:var(--ink)}'
    '.proof-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px;border-top:1px solid #aeb9b4;padding-top:22px}'
    '.proof-strip strong{display:block;font-family:var(--serif);font-weight:400;font-size:40px;color:var(--orange);letter-spacing:-.02em;line-height:1.1}'
    '.proof-strip span{font-size:13px;color:var(--muted)}'
    '.pricing{border-top:1px solid var(--line)}'
    '.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;align-items:stretch}'
    '.plan-card{border:1px solid #d4dbd1;border-radius:6px;padding:30px 28px;background:#fffefa;display:flex;flex-direction:column}'
    '.plan-head{display:flex;justify-content:space-between;align-items:center;gap:10px;min-height:30px}'
    '.plan-head h3{font-size:17px}'
    '.plan-badge{font-size:10px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;padding:5px 9px;border-radius:3px;background:var(--orange);color:#fffefa;white-space:nowrap}'
    '.plan-price{margin:22px 0 2px;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}'
    '.plan-price strong{font-family:var(--serif);font-weight:400;font-size:46px;letter-spacing:-.03em;color:var(--ink);line-height:1}'
    '.plan-price span{font-size:13px}.plan-tax{font-size:12px}'
    '.plan-card ul{list-style:none;padding:0;margin:22px 0 26px;border-top:1px solid var(--line);flex:1}'
    '.plan-card li{font-size:14px;color:var(--muted);padding:10px 0 10px 24px;border-bottom:1px solid var(--line);position:relative}'
    '.plan-card li:before{content:"✓";position:absolute;left:0;color:var(--green);font-weight:700}'
    '.plan-card .button{width:100%}'
    '.plan-card.featured{background:var(--ink);border-color:var(--ink)}'
    '.plan-card.featured h3,.plan-card.featured .plan-price strong{color:#fffefa}'
    '.plan-card.featured p,.plan-card.featured .plan-price span,.plan-card.featured li{color:#d0d9da}'
    '.plan-card.featured ul,.plan-card.featured li{border-color:#52616a}.plan-card.featured li:before{color:#f1c3a4}'
    '.dragon-lockup{display:flex;align-items:center;gap:14px}'
    '.hl-head{align-items:center}'
    '.hl-head{gap:44px}.hl-a{grid-template-columns:1.4fr auto 1fr}.hl-a .dragon-lockup{justify-self:center}.hl-a>p{justify-self:end;text-align:right}'
    '.hl-b{grid-template-columns:1.75fr 1fr auto}.hl-b .dragon-lockup{justify-self:end}'
    '@media(max-width:1000px){.hl-a,.hl-b{grid-template-columns:1fr auto}.hl-a>p,.hl-b>p{grid-column:1/-1;justify-self:start;text-align:left}.hl-b .dragon-lockup{grid-row:1;grid-column:2}}'
    '@media(max-width:760px){.hl-a,.hl-b{grid-template-columns:1fr}.hl-a .dragon-lockup,.hl-b .dragon-lockup{justify-self:start;grid-column:1;grid-row:auto}}'
    '.dragon-lockup img{width:78px;height:90px;object-fit:contain;filter:drop-shadow(0 6px 6px #1d2d3914)}'
    '.dragon-lockup strong{display:block;font-size:30px;letter-spacing:-.03em;line-height:1.1}'
    '.dragon-lockup strong em{font-style:normal;color:var(--orange)}'
    '.dragon-cn{display:block;font-size:14px;color:var(--green);font-weight:600}'
    '.downloads{border-top:1px solid var(--line)}'
    '.dl-list{display:grid;grid-template-columns:1fr 1fr;gap:0 40px;border-top:1px solid #aeb9b4}'
    '.dl-item{display:grid;grid-template-columns:40px 1fr auto;gap:16px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)}'
    '.dl-thumb{width:40px;height:56px;object-fit:cover;object-position:top;border:1px solid #d4dbd1;border-radius:3px;background:#fffefa}'
    '.dl-item h3{font-size:16px;margin-bottom:2px}.dl-meta{font-size:13px;line-height:1.45}'
    '.dl-links{display:flex;gap:8px}'
    '.dl-link{font-size:12px;font-weight:600;padding:6px 11px;border:1px solid #b4bcb9;border-radius:4px;white-space:nowrap}'
    '.dl-link:before{content:"↓ ";color:var(--orange)}a.dl-link:hover{border-color:var(--ink);background:#fffefa}'
    '.dl-link.soon{color:var(--muted);border-style:dashed;font-weight:400}.dl-link.soon:before{content:""}'
    '@media(max-width:1000px){.dl-list{grid-template-columns:1fr}}@media(max-width:760px){.dl-item{grid-template-columns:40px 1fr}.dl-links{grid-column:2}.dragon-lockup strong{font-size:26px}.dragon-lockup img{width:62px;height:72px}}'
    '.topbar{display:flex;justify-content:center;align-items:center;gap:28px;flex-wrap:wrap}'
    '.topbar a:hover{text-decoration:underline;text-underline-offset:3px}'
    '.topbar-feedback{color:#f1c3a4;font-weight:600;white-space:nowrap}'
    '.fb-dialog{width:min(620px,calc(100% - 32px));max-height:calc(100dvh - 40px);overflow:auto;border:0;border-radius:8px;padding:32px;background:var(--paper);color:var(--ink);box-shadow:0 30px 80px #1d2d3940}'
    '.fb-dialog::backdrop{background:#1d2d3999}'
    '.fb-close{position:absolute;top:12px;right:14px;border:0;background:none;font-size:28px;line-height:1;cursor:pointer;color:var(--muted)}.fb-close:hover{color:var(--ink)}'
    '.fb-head h2{font-size:32px;margin:12px 0 10px}.fb-head p{font-size:14px;margin-bottom:20px}'
    '.fb-form{display:grid;gap:16px}'
    '.fb-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}'
    '.fb-form label{display:grid;gap:6px;font-size:13px;font-weight:600}'
    '.fb-form select,.fb-form textarea,.fb-form input{font:inherit;font-size:14px;font-weight:400;color:var(--ink);background:var(--paper);border:1px solid #c6cec4;border-radius:4px;padding:10px 12px;width:100%}'
    '.fb-form textarea{resize:vertical;min-height:120px}'
    '.fb-form select:focus,.fb-form textarea:focus,.fb-form input:focus{outline:3px solid var(--peach);border-color:var(--orange)}'
    '.fb-form small{font-weight:400;font-size:12px;color:var(--muted)}'
    '.fb-form .button{justify-self:start;cursor:pointer}'
    '.fb-error{color:var(--orange)!important;font-size:13px}'
    '.fb-note{font-size:12px}.fb-note a{text-decoration:underline;text-underline-offset:3px}'
    '@media(max-width:760px){.fb-dialog{padding:24px 18px}.fb-head h2{font-size:27px}}'
    '@media(max-width:760px){.fb-row{grid-template-columns:1fr}.topbar{gap:4px 16px}.topbar-feedback{font-size:11px}}'
    '.compare{border-top:1px solid var(--line)}'
    '.cmp-carousel{position:relative;background:#fffefa;border:1px solid #d4dbd1;border-radius:6px;padding:14px 10px 14px;margin-top:30px}'
    '.cmp-stage{display:grid;cursor:pointer}'
    '.cmp-slide{grid-area:1/1;margin:0;opacity:0;visibility:hidden;transition:opacity .6s,visibility .6s}'
    '.cmp-slide.active{opacity:1;visibility:visible}'
    '.cmp-slide svg{display:block;width:100%;max-width:760px;height:auto;margin:auto}'
    '.cmp-slide svg text{font-size:21px;fill:#55616a;stroke:none;font-family:inherit}'
    '.cmp-slide .ring{fill:none;stroke:#e3e6df}.cmp-slide .axis{stroke:#e3e6df}'
    '.cmp-slide .other{fill:#7f97a833;stroke:#5f7a8c;stroke-width:2}.cmp-slide .other-dot{fill:#5f7a8c}'
    '.cmp-slide .dragon{fill:#b4432533;stroke:var(--orange);stroke-width:2.5}.cmp-slide .dragon-dot{fill:var(--orange)}'
    '.cmp-slide figcaption{text-align:center;margin-top:6px}'
    '.cmp-vs{display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:center;font-size:14px;font-weight:600}'
    '.cmp-vs strong{font-family:var(--serif);font-weight:400;font-size:22px;margin-right:4px}'
    '.cmp-sep{color:var(--muted);font-weight:400;margin:0 8px}'
    '.key{width:14px;height:14px;border-radius:3px;display:inline-block}.key.dragon{background:var(--orange)}.key.other{background:#5f7a8c}'
    '.cmp-note{display:block;font-size:12px;color:var(--muted);margin-top:2px}'
    '.cmp-nav{position:absolute;top:auto;bottom:10px;width:30px;height:30px;font-size:18px;border-radius:50%;border:1px solid #c6cec4;background:var(--paper);font-size:22px;line-height:1;cursor:pointer;color:var(--ink)}'
    '.cmp-nav.prev{left:12px}.cmp-nav.next{right:12px}.cmp-source{margin-top:12px}.cmp-nav:hover{border-color:var(--ink)}'
    '.cmp-dots{display:flex;justify-content:center;align-items:center;gap:8px;margin-top:10px;min-height:30px}'
    '.cmp-dot{width:9px;height:9px;border-radius:50%;border:0;padding:0;background:#cdd4ca;cursor:pointer}.cmp-dot.active{background:var(--orange);width:24px;border-radius:5px}'
    '@media(max-width:760px){.cmp-carousel{padding:12px 4px 12px}.cmp-slide svg text{font-size:24px}}'
    '@media(prefers-reduced-motion:reduce){.cmp-slide{transition:none}}'
    '.faq-layout{row-gap:0;align-items:start}.faq-layout>div:first-child{display:contents}'
    '.faq-layout>div:first-child>.eyebrow,#faq-title{grid-column:1/-1}#faq-title{margin-bottom:34px}'
    '.faq-layout .cmp-carousel{grid-column:1;margin-top:0}.faq-layout .cmp-source{grid-column:1}'
    '.faq-layout>.faq{grid-column:2;grid-row:3/span 2}'
    '@media(max-width:760px){.faq-layout>.faq{grid-column:1;grid-row:auto;margin-top:30px}}'
    '.experience{border-top:1px solid var(--line)}'
    '.xp-layout{display:grid;grid-template-columns:.9fr 1.4fr;gap:50px}'
    '.xp-layout h3{font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-weight:700;margin-bottom:16px}'
    '.xp-roles ul{list-style:none;margin:0;padding:0;border-top:1px solid #aeb9b4}'
    '.xp-roles li{padding:15px 0;border-bottom:1px solid var(--line)}'
    '.xp-roles li strong{display:block;font-size:15px;margin-bottom:3px}.xp-roles li span{font-size:13px;color:var(--muted)}'
    '.xp-langs{font-size:13px;margin-top:18px}'
    '.xp-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}'
    '.xp-card{border:1px solid #d4dbd1;border-radius:6px;padding:24px;background:#fffefa}'
    '.xp-client{display:inline-block;font-size:10px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--orange);margin-bottom:12px}'
    '.xp-card h3{font-size:18px;text-transform:none;letter-spacing:-.02em;color:var(--ink);font-weight:600;margin-bottom:10px}'
    '.xp-card p{font-size:14px}'
    '@media(max-width:1000px){.xp-layout{grid-template-columns:1fr;gap:35px}}'
    '@media(max-width:760px){.xp-grid{grid-template-columns:1fr}.xp-card{padding:22px}}'
    '.faq details p a{text-decoration:underline;text-underline-offset:3px}'
    '@media(max-width:1000px){.news-grid,.plan-grid{grid-template-columns:1fr 1fr}}'
    '@media(max-width:760px){.news-grid,.plan-grid,.proof-strip{grid-template-columns:1fr}.news-card,.plan-card{padding:23px}'
    '.proof-strip strong{font-size:34px}.plan-price strong{font-size:40px}}'
)
html = replace_once(html, '</style>', css + '</style>')

# ---------------------------------------------------------------- write
javascript = javascript[:offset] + json.dumps(translations, ensure_ascii=False, indent=2) + javascript[offset + length:] + feedback_js
(destination / 'index.html').write_text(html, encoding='utf-8')
(destination / 'bilingual.js').write_text(javascript, encoding='utf-8')
missing = [k for k in __import__('re').findall(r'data-i18n="([^"]+)"', html) if k not in translations]
if missing:
    raise RuntimeError(f'Missing translations: {missing}')
print(json.dumps({'output': str(destination), 'keys': len(translations)}))
