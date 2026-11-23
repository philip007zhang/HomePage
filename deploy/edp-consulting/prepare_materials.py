"""Prepare downloadable DragonERP materials and the DragonERP logo for the homepage.

Copies the latest one-pager / double-sided PDFs to materials/downloads with web-safe names,
renders a first-page thumbnail for each, and makes a small DragonERP logo.
Needs PyMuPDF + Pillow (run with PYTHONPATH pointing at a folder where they are installed).
"""
from pathlib import Path
import shutil

import fitz
from PIL import Image

here = Path(__file__).parent
marketing = Path('D:/Projects/dgERP/docs/Marketing/OnePager')
out = here / 'materials'
(out / 'downloads').mkdir(parents=True, exist_ok=True)
(out / 'thumbs').mkdir(parents=True, exist_ok=True)

files = {
    'DragonERP-One-Pager-EN.pdf': 'DragonERP-One-Pager-EN-2026-11-21.pdf',
    'DragonERP-One-Pager-ZH.pdf': 'DragonERP-一页介绍-中文-2026-11-21.pdf',
    'DragonERP-Double-sided-Overview-EN.pdf': 'DragonERP-Double-sided-Overview-EN.pdf',
    'DragonERP-Group-Consolidation-EN.pdf': 'Dragon-ERP-Group-Consolidation-OnePager-EN.pdf',
    'DragonERP-White-Paper-EN.pdf': '../WhitePaper/DragonERP-Product-White-Paper-2026-11-12-EN.pdf',
    'DragonERP-White-Paper-ZH.pdf': '../WhitePaper/DragonERP-产品白皮书-2026-11-12.pdf',
}
for target, source in files.items():
    pdf = out / 'downloads' / target
    shutil.copy2(marketing / source, pdf)
    doc = fitz.open(pdf)
    page = doc[0]
    zoom = 160 / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    img.save(out / 'thumbs' / (pdf.stem + '.jpg'), quality=82, optimize=True)
    print(target, doc.page_count, 'pages', pdf.stat().st_size // 1024, 'KB')

logo = Image.open('D:/Projects/HomePage/assets/dragonerp-logo.png')
logo.thumbnail((260, 300))
logo.save(out / 'dragonerp-logo.png', optimize=True)
print('logo', logo.size)
