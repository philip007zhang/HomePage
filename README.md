# EDP Consulting website

Live site: https://edp-consulting.au/

This is a buildless static website. The current page uses `index.html`, `bilingual.js`, and `assets/edp-logo.png`. English and Chinese content are maintained together in `bilingual.js`; the HTML provides the initial English content.

To preview locally, serve this directory with any static HTTP server, for example `python -m http.server 8000`.

The public contact is Philip Zhang at philip.zhang@edp-consulting.au. No telephone field is displayed. Update both the visible email and its `mailto:` link when changing contact details.

Publish the static page, language script, referenced assets, `robots.txt`, and `sitemap.xml` together. Mailbox credentials and server private configuration are not website assets.
