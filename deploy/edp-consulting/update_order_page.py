"""Update the maintained root website with the agreed activation policy and intake form."""
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[2]
html_path = root / 'index.html'
js_path = root / 'bilingual.js'
html = html_path.read_text(encoding='utf-8-sig')
javascript = js_path.read_text(encoding='utf-8-sig')
prefix = 'const translations = '
offset = javascript.index(prefix) + len(prefix)
translations, size = json.JSONDecoder().raw_decode(javascript[offset:])
pairs = {
    'planMonthly2': ('Monthly only: three calendar months of trial after payment-method verification and opening', '仅月付：付款方式验证并开通后，可试用三个自然月'),
    'planYearly0': ('Cloud hosting, a separate database and encrypted backups', '云托管、独立数据库与加密备份'),
    'planYearly1': ('No free trial; payment must be confirmed before opening', '不提供免费试用；确认年费到账后开通'),
    'planYearly2': ('Pay once a year; about 17% less than 12 monthly payments', '一年付一次，比按月付 12 个月约省 17%'),
    'planLicence3': ('No free trial; pay before activation. Installation, migration and support quoted separately', '不提供免费试用，付款后开通；安装、迁移与支持另行报价'),
    'ctaSubscribe': ('Prepare monthly order <span aria-hidden="true">↗</span>', '填写月付开通资料 <span aria-hidden="true">↗</span>'),
    'ctaSubscribeYearly': ('Prepare yearly order <span aria-hidden="true">↗</span>', '填写年付开通资料 <span aria-hidden="true">↗</span>'),
    'ctaBuy': ('Prepare licence order <span aria-hidden="true">↗</span>', '填写买断开通资料 <span aria-hidden="true">↗</span>'),
    'pricingNote': ('Prepare the opening details below before confirming your order. Orders and payment arrangements are currently confirmed with you by email; this page does not collect payment or automatically deploy a system. Installation and migration are quoted separately. Final amounts are confirmed with your order.', '请先填写下方开通资料，再确认订单。目前订单与付款安排仍由我们通过邮件与您确认；本页不收取款项，也不会自动部署系统。安装与迁移另行报价，最终金额以确认订单为准。'),
    'a4': ('Choose a monthly, yearly or on-premises plan, complete the opening details, then review and email the prepared request. We confirm your order, payment or trial eligibility, and opening arrangements. Only monthly subscriptions include a three-month trial; yearly subscriptions and on-premises licences require confirmed payment.', '选择月付、年付或本地买断方案，填写开通资料，核对后通过邮件提交。我们与您确认订单、付款或试用资格及开通安排。仅月付有三个月试用；年付与买断均须确认付款后开通。'),
    'activationTitle': ('Opening and activation', '开通与激活规则'),
    'activationMonthly': ('Only the monthly plan includes a three-calendar-month trial, starting when the system is opened and the payment method has been verified.', '仅月付提供三个自然月试用，自付款方式验证通过且系统开通后起算。'),
    'activationPaid': ('Yearly subscriptions and on-premises licences have no three-month free trial. Opening requires confirmed payment and complete setup details.', '年付和本地买断不享有三个月免费试用；确认付款且开通资料齐备后安排开通。'),
    'activationWait': ('If capacity is unavailable, the maximum wait is three days from meeting the opening conditions. We will contact you before any further arrangement; the wait is not extended automatically.', '如资源不足，自满足开通条件起最多等待三天；超过三天须与您确认后续安排，不自动无限延长等待。'),
    'activationFinancial': ('If order accounting confirmation is delayed, provisional access may be provided first. The final activation code is issued only after that confirmation is complete. Yearly and on-premises orders still require payment first; provisional access does not create a free trial.', '如订单账务确认延迟，可先提供临时使用权限；确认完成后才发放正式激活码。年付与买断仍须先付款，临时使用不等于三个月免费试用。'),
    'orderEye': ('Before you order', '下单前 · 准备开通资料'),
    'orderTitle': ('Ready to open.<br><em>Start with the details.</em>', '资料齐备。<br><em>开通更顺畅。</em>'),
    'orderIntro': ('Tell us who will own the system, what your business needs and where it will run. Required fields are marked *. Review the details before sending them to Philip for order confirmation.', '请先明确系统负责人、企业信息与运行环境。标有 * 的项目为必填；核对资料后发送给 Philip，由我们确认订单与开通安排。'),
    'orderPlanLegend': ('1. Your plan', '1. 选择方案'),
    'orderPlanLabel': ('Plan *', '方案 *'),
    'orderUsersLabel': ('Contract users *', '合同使用人数 *'),
    'orderCloudUsersHelp': ('1–50 users. Cloud pricing rounds up to blocks of five users.', '1–50 人，云订阅按每五人一档向上计费。'),
    'orderBuyoutUsersHelp': ('The licence includes 20 users; additional users are A$18 each, excluding GST.', '买断包含 20 人，超过部分每人 A$18（未含 GST）。'),
    'orderMonthlyTitle': ('Monthly: three-month trial', '月付：三个自然月试用'),
    'orderMonthlyPolicy': ('A verified payment method and complete opening details are required. The three-calendar-month trial starts when the system is opened; monthly subscription charges follow the trial.', '须验证有效付款方式并提交完整开通资料。系统开通后开始三个自然月试用，试用结束后按月计费。'),
    'orderYearlyTitle': ('Yearly: pay before opening', '年付：先付款，再开通'),
    'orderYearlyPolicy': ('No three-month free trial. Confirm the annual payment and complete setup details before opening.', '不提供三个月免费试用。确认年费到账且开通资料齐备后开通。'),
    'orderBuyoutTitle': ('On-premises: pay before activation', '本地买断：先付款，再开通'),
    'orderBuyoutPolicy': ('No three-month free trial. Confirm the software payment and have the agreed server environment ready before activation. Installation, migration and support are quoted separately.', '不提供三个月免费试用。确认软件款到账，且约定的服务器环境与资料已准备好后开通；安装、迁移与支持另行报价。'),
    'orderCompanyLegend': ('2. Company and billing', '2. 企业与账单信息'),
    'orderCompanyLabel': ('Company / legal business name *', '企业／法定经营名称 *'),
    'orderCountryLabel': ('Billing country *', '账单国家／地区 *'),
    'orderChoose': ('Please select', '请选择'),
    'orderAU': ('Australia', '澳大利亚'),
    'orderNZ': ('New Zealand', '新西兰'),
    'orderOther': ('Other — scope and quote to be confirmed', '其他 — 服务范围及报价需确认'),
    'orderRegistrationLabel': ('ABN / business registration number (if applicable)', 'ABN／企业登记号（如适用）'),
    'orderAddressLabel': ('Full billing address, including country and postcode *', '完整账单地址（含国家／地区及邮编）*'),
    'orderOwnerLegend': ('3. Contact and first administrator', '3. 联系人与首位管理员'),
    'orderContactLabel': ('Contact full name *', '联系人姓名 *'),
    'orderOwnerNameLabel': ('First administrator (owner) full name *', '首位管理员（owner）姓名 *'),
    'orderOwnerEmailLabel': ('Owner login and activation email *', 'owner 登录及激活邮箱 *'),
    'orderConfirmEmailLabel': ('Confirm owner email *', '再次确认 owner 邮箱 *'),
    'orderBillingEmailLabel': ('Billing email *', '账单接收邮箱 *'),
    'orderBillingEmailHelp': ('This can be the same as the owner email.', '可与 owner 邮箱相同。'),
    'orderOwnerHelp': ('The owner email will be verified during order confirmation and used to deliver the secure account-setup link.', '订单确认时会验证 owner 邮箱，并通过该邮箱安全交付账号设置链接。'),
    'orderSetupLegend': ('4. Setup requirements', '4. 开通配置'),
    'orderScopeLabel': ('Initial system scope *', '初始使用范围 *'),
    'orderFullERP': ('ERP business workflows', 'ERP 业务流程'),
    'orderStockOnly': ('Start with inventory only', '先使用库存管理'),
    'orderLanguageLabel': ('Initial system language *', '系统初始语言 *'),
    'orderTimezoneLabel': ('Business time zone *', '业务时区 *'),
    'orderHostingLabel': ('Preferred hosting country *', '期望托管地区 *'),
    'orderHostingHelp': ('Availability is confirmed with your order.', '可用地区与容量在订单确认时核实。'),
    'orderServerLabel': ('Server operating system, version and architecture *', '服务器操作系统、版本及架构 *'),
    'orderServerHelp': ('Describe the environment only. Installation access is arranged separately through a secure channel.', '此处只填写运行环境；安装访问通过另行约定的安全渠道安排。'),
    'orderServerReady': ('The agreed server environment is ready, and I can arrange authorised installation access securely.', '约定的服务器运行环境已准备好，并可通过安全方式安排经授权的安装访问。'),
    'orderStartHelp': ('Requested opening: as soon as payment or trial eligibility and setup details are confirmed. If capacity is unavailable, the maximum wait is three days.', '期望开通时间：付款或试用资格与开通资料确认后尽快开通；资源不足最多等待三天。'),
    'orderConsent': ('I confirm these details are accurate and have read the trial/payment, three-day capacity wait, provisional access and final activation conditions above.', '我确认以上资料准确，已阅读上述试用／付款、三天资源等待、临时使用及正式激活条件。'),
    'orderReview': ('Review opening details', '核对开通资料'),
    'orderPreviewTitle': ('Your opening request', '开通资料摘要'),
    'orderEmpty': ('Your checked details and plan conditions will appear here after you complete the form and select Review.', '填写表格并点击“核对开通资料”后，将在这里显示资料与方案条件。'),
    'orderPrepared': ('Details prepared — not yet submitted or paid', '资料已整理 — 尚未提交，尚未付款'),
    'orderEmailAction': ('Open email to submit details', '打开邮件提交开通资料'),
    'orderDownloadAction': ('Download the details checklist', '下载开通资料清单'),
    'orderSubmitHelp': ('The email button opens your own mail app with the reviewed details. Send that email to submit your request. A saved checklist is not an order confirmation, payment receipt or activation code.', '邮件按钮会打开您自己的邮件应用并填入核对后的资料，发送该邮件后才算提交资料。下载清单不代表订单已确认、付款成功或已取得激活码。'),
    'orderPrivacy': ('Details remain in this page until you choose to email or download them. Do not enter payment-card details or passwords.', '在您选择邮件提交或下载前，资料仅保留在本页。请勿填写银行卡信息或密码。'),
    'orderCalculator': ('Open the existing cloud price calculator ↗', '打开现有云服务价格计算器 ↗'),
    'orderEmailMismatch': ('The two owner email addresses must match.', '两次填写的 owner 邮箱必须一致。'),
    'orderRequiredDetail': ('Please enter this required detail, not just spaces.', '请填写此项必需资料，不能只输入空格。'),
    'orderInvalidUsers': ('Enter a whole number of users; cloud plans support 1–50 users.', '请填写有效的整数人数；云订阅支持 1–50 人。'),
    'orderBillableUsers': ('billable users', '计费人数'),
    'orderActivationLabel': ('Trial / opening conditions', '试用／开通条件'),
    'orderCapacityLabel': ('Capacity wait', '资源等待'),
    'orderCapacityPolicy': ('Maximum three days after opening conditions are met; further arrangements require customer confirmation.', '满足开通条件后最多等待三天；后续安排须与客户确认。'),
    'orderFormalLabel': ('Final activation', '正式激活'),
    'orderFormalPolicy': ('Provisional access may precede accounting confirmation. The final activation code follows completed financial confirmation. Yearly and on-premises plans still require payment first.', '账务确认延迟时可先临时使用，财务确认完成后才发正式激活码；年付与买断仍须先付款。'),
    'orderMonthlyEstimate': ('Estimated monthly amount including GST after the three-month trial. No subscription fee is collected on this page; final quote to be confirmed.', '三个月试用结束后的含 GST 月费估算。本页不收取订阅费，最终金额以确认报价为准。'),
    'orderYearlyEstimate': ('Estimated annual amount including GST, payable before opening. No free trial; final quote to be confirmed.', '开通前应付的含 GST 年费估算。不提供免费试用，最终金额以确认报价为准。'),
    'orderBuyoutEstimate': ('Estimated one-off software amount including GST, payable before activation. Installation, migration and support are separate; final quote to be confirmed.', '开通前应付的一次性软件款含 GST 估算。安装、迁移与支持另计，最终金额以确认报价为准。'),
    'orderMailIntro': ('Please review these opening details and confirm the DragonERP order and payment or trial arrangements.', '请审核以下开通资料，并与我确认 DragonERP 订单、付款或试用安排。'),
    'orderQuoteLabel': ('Displayed estimate including GST', '页面显示的含 GST 估算'),
    'orderNoPayment': ('This is an opening-details request, not payment confirmation or proof of activation.', '这是开通资料申请，不是付款确认或已激活证明。'),
    'orderRequestSubject': ('Opening-details request', '开通资料申请'),
}
for key, (en, zh) in pairs.items():
    translations[key] = {'en': en, 'zh': zh}

html = re.sub(r'<!-- ORDER-INTAKE-START -->.*?<!-- ORDER-INTAKE-END -->', '', html, flags=re.S)
html = re.sub(r'<!-- ACTIVATION-POLICY-START -->.*?<!-- ACTIVATION-POLICY-END -->', '', html, flags=re.S)
policy = '<!-- ACTIVATION-POLICY-START --><div class="activation-policy" id="activation-rules"><h3 data-i18n="activationTitle"></h3><ul>' + ''.join('<li data-i18n="' + key + '"></li>' for key in ['activationMonthly', 'activationPaid', 'activationWait', 'activationFinancial']) + '</ul></div><!-- ACTIVATION-POLICY-END -->'
pattern = r'(<section\b[^>]*id="pricing".*?)(</section>)'
html, count = re.subn(pattern, lambda match: match[1] + policy + match[2] + '<!-- ORDER-INTAKE-START -->' + (root / 'deploy/edp-consulting/order-form.html').read_text(encoding='utf-8') + '<!-- ORDER-INTAKE-END -->', html, count=1, flags=re.S)
if count != 1:
    raise RuntimeError('Pricing section not found')
for key, plan in [('ctaSubscribe', 'monthly'), ('ctaSubscribeYearly', 'yearly'), ('ctaBuy', 'buyout')]:
    pattern = r'<a\b[^>]*data-i18n="' + key + r'"[^>]*>'
    def update_link(match):
        tag = re.sub(r'\s(?:href|target|rel|data-order-plan)="[^"]*"', '', match[0])
        return tag[:-1] + ' href="#order" data-order-plan="' + plan + '">'
    html, count = re.subn(pattern, update_link, html)
    if count != 1:
        raise RuntimeError('Expected one plan link: ' + key)
for key in pairs.keys() | {'planMonthlyName', 'planYearlyName', 'planLicenceName'}:
    pattern = r'(<(?P<tag>[a-z][a-z0-9]*)\b[^>]*data-i18n="' + re.escape(key) + r'"[^>]*>).*?(</(?P=tag)>)'
    html = re.sub(pattern, lambda match: match[1] + translations[key]['en'] + match[3], html, flags=re.S)
if 'href="order.css"' not in html:
    html = html.replace('</head>', '<link rel="stylesheet" href="order.css"></head>', 1)
if 'src="order.js"' not in html:
    html = html.replace('<script src="bilingual.js"></script>', '<script src="bilingual.js"></script><script src="order.js"></script>', 1)
javascript = javascript[:offset] + json.dumps(translations, ensure_ascii=False, indent=2) + javascript[offset + size:]
if "new CustomEvent('site-language-change'" not in javascript:
    javascript = javascript.replace('  if(remember)', "  document.dispatchEvent(new CustomEvent('site-language-change',{detail:{lang}}));\n  if(remember)", 1)
html_path.write_text(html.rstrip() + '\n', encoding='utf-8')
js_path.write_text(javascript.rstrip() + '\n', encoding='utf-8')
missing = sorted(set(re.findall(r'data-i18n="([^"]+)"', html)) - translations.keys())
if missing:
    raise RuntimeError('Missing translations: ' + ', '.join(missing))
print(json.dumps({'policy_version': '2026-11-24', 'translation_count': len(translations), 'missing_translations': missing}))
