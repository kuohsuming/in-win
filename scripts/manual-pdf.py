"""操作說明書轉 PDF（含截圖）：Markdown → HTML → Chrome 無頭列印。

需要 python-markdown（不放進 App 套件）：
  .venv/bin/pip install --target /tmp/mdlib markdown
  PYTHONPATH=/tmp/mdlib python3 scripts/manual-pdf.py [快速安裝指南.md]
預設轉 docs/manual/操作說明書.md；輸出同名 .pdf。
"""
import re
import subprocess
import sys
from pathlib import Path

import markdown

DIR = Path(__file__).resolve().parents[1] / "docs" / "manual"
TMP = DIR / ".manual.html"
CSS = """
@page { size: A4; margin: 16mm 14mm 18mm 14mm; @bottom-center { content: counter(page); } }
body { font-family: 'Noto Sans CJK TC','Noto Sans TC',sans-serif; font-size: 10.5pt; line-height: 1.6; color:#222; }
h1 { font-size: 22pt; border-bottom: 3px solid #1f4e79; padding-bottom: 6px; color:#1f4e79; }
h2 { font-size: 16pt; color:#1f4e79; border-bottom: 1px solid #9db3cc; margin-top: 1.6em; break-before: page; }
h2:first-of-type { break-before: auto; }
h3 { font-size: 12.5pt; color:#2e5f8a; margin-top: 1.3em; break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: .6em 0; font-size: 9.5pt; }
tr { break-inside: avoid; }
th, td { border: 1px solid #b8c4d0; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #e8eef5; }
code { font-family: 'Noto Sans Mono CJK TC', monospace; background:#f2f4f7; padding: 0 3px; border-radius: 3px; font-size: 9pt; }
pre { background:#f2f4f7; padding: 8px 10px; border-radius: 4px; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; }
figure { margin: .8em 0; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 120mm; border: 1px solid #999; }
figcaption { font-size: 9pt; color:#555; margin-top: 4px; }
blockquote { border-left: 4px solid #e0a800; background:#fff8e1; margin: .6em 0; padding: 4px 10px; }
"""


def main() -> int:
    src = DIR / (sys.argv[1] if len(sys.argv) > 1 else "操作說明書.md")
    out = src.with_suffix(".pdf")
    slug = lambda v, _s: re.sub(r"[^\w\-]", "", v.strip().lower().replace(" ", "-"))
    body = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "toc", "sane_lists"],
                             extension_configs={"toc": {"slugify": slug}})
    body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" ?/?></p>',
                  r'<figure><img src="\2"><figcaption>圖：\1</figcaption></figure>', body)
    TMP.write_text(f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>表面平整檢查系統 {src.stem}</title>'
                   f'<style>{CSS}</style></head><body>{body}</body></html>', encoding="utf-8")
    try:
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", TMP.as_uri()], check=True, capture_output=True)
    finally:
        TMP.unlink(missing_ok=True)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
