#!/usr/bin/env python3
"""
Export a QC_Param_Eval Markdown report to PDF.

Markdown -> standalone HTML (images embedded as base64) -> PDF via headless Google Chrome.
Needs the `markdown` package (system python3 has it) and google-chrome.

Usage:
    python3 md_to_pdf.py Report_Summary.md                 # A4 landscape (default)
    python3 md_to_pdf.py sec3_1_se_off_noise/Report_3_1_SE_OFF_Noise.md --portrait
    python3 md_to_pdf.py Report_Summary.md --combine       # also append every linked section report;
                                                            # the summary links jump inside the PDF
Output: same path with .pdf (the intermediate .html is kept next to it).
"""

import os
import re
import sys
import base64
import shutil
import subprocess
import markdown

CSS = """
@page { size: A4 %(orient)s; margin: 12mm 10mm; }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 9.5pt; line-height: 1.4; color: #222; }
h1 { font-size: 17pt; color: #1f3b5a; border-bottom: 2px solid #3b6ea5; padding-bottom: 4px; }
h2 { font-size: 13pt; color: #2b5c8a; border-bottom: 1px solid #c8d3df; padding-bottom: 2px; margin-top: 18px;
     page-break-after: avoid; }
h3 { font-size: 11pt; color: #333; margin-top: 14px; page-break-after: avoid; }
table { border-collapse: collapse; margin: 6px 0 10px 0; font-size: 8pt; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #c5ccd4; padding: 2px 5px; text-align: left; vertical-align: top; }
th { background: #e8eef5; }
tr:nth-child(even) td { background: #f7f9fb; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; background: #f1f3f5; padding: 0 2px; }
img { max-width: 100%%; max-height: 120mm; width: auto; height: auto; display: block; margin: 6px auto; page-break-inside: avoid; }
a { color: #2b5c8a; text-decoration: none; }
p.back { font-size: 8pt; margin: 0 0 4px 0; }
section .newpage { page-break-before: always; }
"""


def embed_images(html, base_dir):
    def repl(m):
        src = m.group(2)
        path = os.path.join(base_dir, src)
        if src.startswith(("http:", "https:", "data:")) or not os.path.exists(path):
            return m.group(0)
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        return f'{m.group(1)}data:image/png;base64,{data}{m.group(3)}'
    return re.sub(r'(<img[^>]*src=")([^"]+)(")', repl, html)


def md_to_html_body(md_path):
    with open(md_path, encoding='utf-8') as f:
        body = markdown.markdown(f.read(), extensions=['tables', 'fenced_code', 'sane_lists'])
    return embed_images(body, os.path.dirname(md_path))


def combine_linked_reports(body, base):
    """Append every linked local .md report to the document and turn the links into in-PDF jumps."""
    linked = []
    for href in re.findall(r'<a href="([^"#:]+\.md)"', body):
        if href not in linked and os.path.exists(os.path.join(base, href)):
            linked.append(href)
    parts = [f'<div id="top"></div>{body}']
    for href in linked:
        anchor = "report-" + re.sub(r'[^A-Za-z0-9]+', '-', os.path.splitext(os.path.basename(href))[0])
        body_sec = md_to_html_body(os.path.join(base, href))
        # one parameter per page: break before numbered parameter headings ("4.1 ..."); when such a
        # heading directly follows a chapter heading, break before the chapter heading instead
        body_sec = re.sub(r'<h2>(\d+\. [^<]*)</h2>(\s*<h3>\d+\.\d+ )', r'<h2 class="newpage">\1</h2>\2', body_sec)
        body_sec = re.sub(r'(</h2>\s*)?<h3>(\d+\.\d+ )',
                          lambda m: m.group(0) if m.group(1) else f'<h3 class="newpage">{m.group(2)}', body_sec)
        parts.append(f'<section id="{anchor}" style="page-break-before: always;">'
                     f'<p class="back"><a href="#top">&#8592; Back to summary</a></p>{body_sec}</section>')
        parts[0] = parts[0].replace(f'<a href="{href}">', f'<a href="#{anchor}">')
    return "".join(parts), len(linked)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    md_path = os.path.abspath(args[0])
    orient = "portrait" if "--portrait" in sys.argv else "landscape"
    base = os.path.dirname(md_path)

    body = md_to_html_body(md_path)
    if "--combine" in sys.argv:
        body, n = combine_linked_reports(body, base)
        print(f"Appended {n} linked report(s)")
    title = os.path.splitext(os.path.basename(md_path))[0]
    html = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{CSS % {"orient": orient}}</style></head><body>{body}</body></html>')

    html_path = os.path.splitext(md_path)[0] + ".html"
    pdf_path = os.path.splitext(md_path)[0] + ".pdf"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if not chrome:
        sys.exit("No Chrome/Chromium found; HTML written to " + html_path)
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf_path}", "file://" + html_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"PDF: {pdf_path}")


if __name__ == "__main__":
    main()
