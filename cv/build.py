# -*- coding: utf-8 -*-
"""Render the CV.

    python build.py              # reference.docx -> cv.docx -> OKOnditi_CV_2026.{docx,pdf}
    python build.py --no-pdf     # Word only

The PDF is produced from the Word file rather than through LaTeX, so the two can
never disagree: there is one design (design.py -> reference.docx) and one render.

Fonts: the CV asks for Georgia and Calibri. Linux has neither, so a Linux
LibreOffice substitutes Noto Serif and Carlito and the PDF will not look like what
Word shows. This script therefore prefers the Windows LibreOffice, which has the
real fonts, and warns when it has to fall back.
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCX = os.path.join(HERE, "OKOnditi_CV_2026.docx")
PDF = os.path.join(HERE, "OKOnditi_CV_2026.pdf")
WIN_SOFFICE = "/mnt/c/Program Files/LibreOffice/program/soffice.exe"


def run(cmd, **kw):
    result = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, **kw)
    if result.returncode != 0:
        sys.exit(f"failed: {' '.join(str(c) for c in cmd)}\n{result.stdout}\n{result.stderr}")
    return result


def set_properties(path):
    from docx import Document
    doc = Document(path)
    doc.core_properties.title = "Kenneth Otieno Onditi — Curriculum Vitae"
    doc.core_properties.author = "Kenneth Otieno Onditi"
    doc.core_properties.comments = "Generated from cv.qmd; see cv/README.md"
    doc.save(path)


def to_pdf(docx_path):
    """Convert with the Windows LibreOffice when available, for the real fonts."""
    if os.path.exists(WIN_SOFFICE):
        win = subprocess.run(["wslpath", "-w", HERE], capture_output=True, text=True).stdout.strip()
        win_doc = subprocess.run(["wslpath", "-w", docx_path],
                                 capture_output=True, text=True).stdout.strip()
        proc = subprocess.run([WIN_SOFFICE, "--headless", "--convert-to", "pdf",
                               "--outdir", win, win_doc], capture_output=True, text=True)
        produced = os.path.splitext(docx_path)[0] + ".pdf"
        if proc.returncode == 0 and os.path.exists(produced):
            return produced, "Windows LibreOffice (Georgia / Calibri)"
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit("no LibreOffice found; run with --no-pdf or install it")
    run([soffice, "--headless", "--convert-to", "pdf", "--outdir", HERE, docx_path])
    return os.path.splitext(docx_path)[0] + ".pdf", \
        "Linux LibreOffice — WARNING: Georgia/Calibri substituted, layout may shift"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    args = ap.parse_args()

    run([sys.executable, "make_reference.py"])
    run(["quarto", "render", "cv.qmd", "--to", "docx"])

    shutil.move(os.path.join(HERE, "cv.docx"), DOCX)
    set_properties(DOCX)
    print(f"wrote {os.path.basename(DOCX)}")

    if not args.no_pdf:
        produced, how = to_pdf(DOCX)
        if produced != PDF:
            shutil.move(produced, PDF)
        print(f"wrote {os.path.basename(PDF)} via {how}")


if __name__ == "__main__":
    main()
