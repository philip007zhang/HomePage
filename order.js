(() => {
  const form = document.getElementById('order-form');
  if (!form) return;
  const planInput = form.elements.plan;
  const usersInput = form.elements.users;
  let reviewed = null;
  let usersEdited = false;
  const lang = () => document.documentElement.lang === 'zh-Hans' ? 'zh' : 'en';
  const t = key => translations[key]?.[lang()] || key;
  const money = cents => new Intl.NumberFormat(lang() === 'zh' ? 'zh-CN' : 'en-AU', {style: 'currency', currency: 'AUD'}).format(cents / 100);
  const planLabel = plan => t({monthly: 'planMonthlyName', yearly: 'planYearlyName', buyout: 'planLicenceName'}[plan]);
  const summary = document.getElementById('order-summary');
  const empty = document.getElementById('order-empty');
  const error = document.getElementById('order-error');

  function invalidate() {
    reviewed = null;
    summary.hidden = true;
    empty.hidden = false;
    document.getElementById('order-email').removeAttribute('href');
  }

  function updatePlan(resetUsers = false) {
    const buyout = planInput.value === 'buyout';
    if (resetUsers && !usersEdited) usersInput.value = buyout ? '20' : '5';
    if (buyout) usersInput.removeAttribute('max');
    else usersInput.max = '50';
    usersInput.setAttribute('aria-describedby', 'order-users-help');
    document.getElementById('order-users-help').textContent = t(buyout ? 'orderBuyoutUsersHelp' : 'orderCloudUsersHelp');
    document.getElementById('order-hosting-field').hidden = buyout;
    form.elements.hosting_region.disabled = buyout;
    document.getElementById('order-server-field').hidden = !buyout;
    document.getElementById('order-server-ready-field').hidden = !buyout;
    for (const name of ['server_environment', 'server_ready']) {
      form.elements[name].disabled = !buyout;
      form.elements[name].required = buyout;
    }
    const policy = planInput.value === 'monthly' ? 'orderMonthly' : (buyout ? 'orderBuyout' : 'orderYearly');
    document.getElementById('order-policy-title').textContent = t(policy + 'Title');
    document.getElementById('order-policy-body').textContent = t(policy + 'Policy');
    if (reviewed) renderSummary();
  }

  function checkEmails() {
    for (const name of ['company', 'billing_address', 'contact', 'owner_name', 'server_environment']) {
      const input = form.elements[name];
      input.setCustomValidity(!input.disabled && input.required && !input.value.trim() ? t('orderRequiredDetail') : '');
    }
    const same = form.elements.owner_email.value.trim().toLowerCase() === form.elements.confirm_email.value.trim().toLowerCase();
    form.elements.confirm_email.setCustomValidity(same ? '' : t('orderEmailMismatch'));
  }

  function makeRequest() {
    const data = new FormData(form);
    const value = key => String(data.get(key) || '').trim();
    const plan = value('plan');
    const users = Number(value('users'));
    if (!Number.isSafeInteger(users) || users < 1 || (plan !== 'buyout' && users > 50)) throw new Error(t('orderInvalidUsers'));
    const slots = plan === 'buyout' ? null : Math.ceil(users / 5);
    const subtotal = plan === 'buyout' ? 188800 + Math.max(0, users - 20) * 1800 : slots * (plan === 'monthly' ? 4888 : 48800);
    if (!Number.isSafeInteger(subtotal)) throw new Error(t('orderInvalidUsers'));
    const gst = Math.round(subtotal / 10);
    return {
      schema_version: 1,
      policy_version: '2026-11-24',
      source: 'edp-company-website',
      request_status: 'prepared_not_submitted',
      prepared_at: new Date().toISOString(),
      plan,
      product: 'DragonERP',
      users,
      billable_users: plan === 'buyout' ? Math.max(20, users) : slots * 5,
      company: {name: value('company'), country: value('country'), registration: value('registration'), billing_address: value('billing_address')},
      contact_name: value('contact'),
      owner: {name: value('owner_name'), email: value('owner_email')},
      billing_email: value('billing_email'),
      setup: {scope: value('scope'), language: value('system_language'), timezone: value('timezone'), hosting_region: plan === 'buyout' ? null : value('hosting_region'), server_environment: plan === 'buyout' ? value('server_environment') : null, customer_server_ready: plan === 'buyout' ? data.get('server_ready') === 'on' : null},
      estimate: {currency: 'AUD', subtotal_cents: subtotal, gst_cents: gst, total_cents: subtotal + gst, final_quote_required: true},
      activation: {requested: 'as_soon_as_eligible', trial_calendar_months: plan === 'monthly' ? 3 : 0, payment_before_activation: plan !== 'monthly', max_capacity_wait_days: 3, provisional_access_if_finance_sync_pending: true, final_activation_code_requires_finance_sync: true},
      details_and_activation_policy_confirmed: true
    };
  }

  function rows(request) {
    return [
      [t('orderPlanLabel'), planLabel(request.plan)],
      [t('orderCompanyLabel'), request.company.name],
      [t('orderUsersLabel'), String(request.users) + (request.plan === 'buyout' ? '' : ' / ' + request.billable_users + ' ' + t('orderBillableUsers'))],
      [t('orderContactLabel'), request.contact_name],
      [t('orderOwnerNameLabel'), request.owner.name],
      [t('orderOwnerEmailLabel'), request.owner.email],
      [t('orderBillingEmailLabel'), request.billing_email],
      [t('orderCountryLabel'), request.company.country === 'AU' ? t('orderAU') : request.company.country === 'NZ' ? t('orderNZ') : t('orderOther')],
      [t('orderRegistrationLabel'), request.company.registration || '—'],
      [t('orderAddressLabel'), request.company.billing_address],
      [t('orderScopeLabel'), t(request.setup.scope === 'stock' ? 'orderStockOnly' : 'orderFullERP')],
      [t('orderLanguageLabel'), request.setup.language === 'zh' ? '中文' : 'English'],
      [t('orderTimezoneLabel'), request.setup.timezone],
      [t(request.plan === 'buyout' ? 'orderServerLabel' : 'orderHostingLabel'), request.plan === 'buyout' ? request.setup.server_environment : t(request.setup.hosting_region === 'NZ' ? 'orderNZ' : 'orderAU')],
      [t('orderActivationLabel'), t(request.plan === 'monthly' ? 'orderMonthlyPolicy' : request.plan === 'yearly' ? 'orderYearlyPolicy' : 'orderBuyoutPolicy')],
      [t('orderCapacityLabel'), t('orderCapacityPolicy')],
      [t('orderFormalLabel'), t('orderFormalPolicy')]
    ];
  }

  function renderSummary() {
    if (!reviewed) return;
    const list = document.getElementById('order-summary-list');
    list.replaceChildren();
    const details = rows(reviewed);
    for (const [label, value] of details) {
      const row = document.createElement('div');
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      dt.textContent = label;
      dd.textContent = value;
      row.append(dt, dd);
      list.append(row);
    }
    const estimate = money(reviewed.estimate.total_cents);
    document.getElementById('order-estimate').textContent = estimate;
    document.getElementById('order-estimate-note').textContent = t(reviewed.plan === 'monthly' ? 'orderMonthlyEstimate' : reviewed.plan === 'yearly' ? 'orderYearlyEstimate' : 'orderBuyoutEstimate');
    const body = [t('orderMailIntro'), '', ...details.map(([key, value]) => key + ': ' + value), '', t('orderQuoteLabel') + ': ' + estimate, t('orderNoPayment'), '', 'Policy: ' + reviewed.policy_version].join('\n');
    document.getElementById('order-email').href = 'mailto:philip.zhang@edp-consulting.au?subject=' + encodeURIComponent('[DragonERP] ' + planLabel(reviewed.plan) + ' — ' + t('orderRequestSubject')) + '&body=' + encodeURIComponent(body);
    summary.hidden = false;
    empty.hidden = true;
  }

  form.addEventListener('input', event => {
    if (event.target === usersInput) usersEdited = true;
    checkEmails();
    error.hidden = true;
    invalidate();
  });
  planInput.addEventListener('change', () => { invalidate(); updatePlan(true); });
  form.addEventListener('submit', event => {
    event.preventDefault();
    checkEmails();
    if (!form.reportValidity()) return;
    try {
      reviewed = makeRequest();
      error.hidden = true;
      renderSummary();
      document.getElementById('order-preview-title').scrollIntoView({behavior: 'smooth', block: 'start'});
    } catch (failure) {
      error.textContent = failure.message;
      error.hidden = false;
    }
  });
  document.getElementById('order-download').addEventListener('click', () => {
    if (!reviewed) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(reviewed, null, 2)], {type: 'application/json'}));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'DragonERP-opening-request-' + reviewed.plan + '.json';
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  document.querySelectorAll('[data-order-plan]').forEach(link => link.addEventListener('click', () => {
    const plan = link.dataset.orderPlan;
    if (!['monthly', 'yearly', 'buyout'].includes(plan)) return;
    planInput.value = plan;
    invalidate();
    updatePlan(true);
  }));
  document.addEventListener('site-language-change', () => { checkEmails(); updatePlan(); });
  updatePlan();
  document.getElementById('order-review').disabled = false;
})();
