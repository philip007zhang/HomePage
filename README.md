# EDP Consulting website

Live site: https://edp-consulting.au/

This is a buildless static website. The current page uses `index.html`, `bilingual.js`, `order.js`, `order.css`, and the referenced files under `assets/` and `downloads/`. English and Chinese content are maintained together in `bilingual.js`; the HTML provides the initial English content.

To preview locally, serve this directory with any static HTTP server, for example `python -m http.server 8000`.

The public contact is Philip Zhang at philip.zhang@edp-consulting.au. No telephone field is displayed. Update both the visible email and its `mailto:` link when changing contact details.

Publish the static page, language script, referenced assets, `robots.txt`, and `sitemap.xml` together. Mailbox credentials and server private configuration are not website assets.

## Opening-details form and policy

Only monthly subscriptions include a three-calendar-month trial. Yearly subscriptions and on-premises licences require payment before opening and do not receive that trial. Capacity waits are limited to three days after eligibility; provisional access may precede financial confirmation, but the final activation code requires completed financial confirmation. Provisional access does not waive payment for yearly or on-premises orders.

The form collects company, billing, contact, owner and setup details and prepares a reviewable request. Customers explicitly choose to open an email draft or download a JSON checklist. No order, payment, deployment or activation is claimed to have completed on this page. The existing cloud calculator remains linked separately. Automatic ERP/payment/provisioning integrations are outside this static-page increment.

The maintained live page is in the root files. To reapply the intake markup and translations after editing `deploy/edp-consulting/order-form.html` or its policy strings, run `python deploy/edp-consulting/update_order_page.py`. This updater is idempotent. Earlier preview generators are historical inputs, not the source of the current published root page.

`node deploy/edp-consulting/verify-order-flow.cjs` runs browser checks with synthetic data only. It checks required fields, matching owner emails, conditional on-premises readiness, all three plan policies, estimates, language switching, safe text rendering and mobile layout; it does not send email or submit payments. Set `EDP_SITE_URL` to verify a deployed site. Screenshots and results are written outside the checkout by default.
