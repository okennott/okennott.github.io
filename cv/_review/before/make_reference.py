# -*- coding: utf-8 -*-
"""Build `reference.docx` — the style sheet Pandoc applies when rendering cv.qmd.

Pandoc looks styles up by name, so every name in design.PARAGRAPH_STYLES /
CHARACTER_STYLES is what `custom-style="..."` in the .qmd refers to. Page size,
margins and the page-number footer come from here too, because Pandoc copies the
reference document's section properties.

    python make_reference.py
"""
import sys
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import design as D


def rgb(hexstr):
    return RGBColor(int(hexstr[0:2], 16), int(hexstr[2:4], 16), int(hexstr[4:6], 16))


def set_fonts(rpr_owner, name):
    """python-docx only sets w:ascii; Word also consults hAnsi and cs."""
    rpr = rpr_owner.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(attr), name)


def apply_run_props(style, spec):
    f = style.font
    if spec.get("font"):
        f.name = spec["font"]
        set_fonts(style.element, spec["font"])
    if spec.get("size"):    f.size = Pt(spec["size"])
    if spec.get("bold") is not None: f.bold = spec["bold"]
    if spec.get("italic"):  f.italic = True
    if spec.get("caps"):    f.all_caps = True
    if spec.get("color"):   f.color.rgb = rgb(spec["color"])
    if spec.get("spacing") is not None:
        el = OxmlElement("w:spacing")
        el.set(qn("w:val"), str(int(spec["spacing"] * 20)))
        style.element.get_or_add_rPr().append(el)


def apply_para_props(style, spec):
    pf = style.paragraph_format
    pf.space_before = Pt(spec.get("before", 0))
    pf.space_after = Pt(spec.get("after", 0))
    pf.line_spacing = spec.get("line", 1.0)
    if spec.get("left"):    pf.left_indent = Inches(spec["left"])
    if spec.get("hanging"): pf.first_line_indent = Inches(-spec["hanging"])
    if spec.get("tab"):     pf.tab_stops.add_tab_stop(Inches(spec["tab"]), WD_TAB_ALIGNMENT.LEFT)
    pf.keep_together = True
    pf.widow_control = True
    if spec.get("keep_next"): pf.keep_with_next = True
    if spec.get("border_bottom"):
        color, size, space = spec["border_bottom"]
        ppr = style.element.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), str(size))
        bottom.set(qn("w:space"), str(space))
        bottom.set(qn("w:color"), color)
        bdr.append(bottom)
        ppr.append(bdr)


def page_field(paragraph, code):
    """A Word field, e.g. PAGE or NUMPAGES."""
    for kind in ("begin", "instr", "end"):
        r = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        rf = OxmlElement("w:rFonts")
        for a in ("w:ascii", "w:hAnsi"):
            rf.set(qn(a), D.SANS)
        rpr.append(rf)
        sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "16"); rpr.append(sz)
        col = OxmlElement("w:color"); col.set(qn("w:val"), D.FAINT); rpr.append(col)
        r.append(rpr)
        if kind == "instr":
            t = OxmlElement("w:instrText")
            t.text = code
            t.set(qn("xml:space"), "preserve")
            r.append(t)
        else:
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), kind)
            r.append(fc)
        paragraph._element.append(r)


def build(path="reference.docx"):
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(D.PAGE["width"]), Inches(D.PAGE["height"])
    sec.left_margin, sec.right_margin = Inches(D.PAGE["left"]), Inches(D.PAGE["right"])
    sec.top_margin, sec.bottom_margin = Inches(D.PAGE["top"]), Inches(D.PAGE["bottom"])
    sec.footer_distance = Inches(D.PAGE["footer"])

    normal = doc.styles["Normal"]
    normal.font.name = D.SANS
    normal.font.size = Pt(9.5)
    set_fonts(normal.element, D.SANS)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing = 1.0

    # Pandoc routes body text through "Body Text"; keep it identical to Normal so
    # anything not wrapped in a custom-style div still looks right.
    for name in ("Body Text", "First Paragraph", "Compact"):
        try:
            st = doc.styles[name]
        except KeyError:
            st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st.font.name = D.SANS
        st.font.size = Pt(9.5)
        set_fonts(st.element, D.SANS)
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(0)
        st.paragraph_format.line_spacing = 1.0

    for name, spec in D.PARAGRAPH_STYLES.items():
        style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles["Normal"]
        style.quick_style = True
        apply_run_props(style, spec)
        apply_para_props(style, spec)

    for name, spec in D.CHARACTER_STYLES.items():
        style = doc.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
        style.quick_style = True
        apply_run_props(style, spec)

    # Hyperlinks: Pandoc uses the built-in "Hyperlink" character style.
    try:
        link = doc.styles["Hyperlink"]
    except KeyError:
        link = doc.styles.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
    link.font.color.rgb = rgb(D.BRONZE)
    link.font.size = Pt(8.6)
    link.font.underline = False
    set_fonts(link.element, D.SANS)

    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.space_before = fp.paragraph_format.space_after = Pt(0)
    r = fp.add_run(D.FOOTER)
    r.font.name = D.SANS; set_fonts(r._element, D.SANS)
    r.font.size = Pt(8); r.font.color.rgb = rgb(D.FAINT)
    page_field(fp, "PAGE")
    r = fp.add_run(" of ")
    r.font.name = D.SANS; set_fonts(r._element, D.SANS)
    r.font.size = Pt(8); r.font.color.rgb = rgb(D.FAINT)
    page_field(fp, "NUMPAGES")

    # Pandoc replaces the body, but an empty one confuses some readers.
    doc.add_paragraph("")
    doc.save(path)
    return path


if __name__ == "__main__":
    out = build(sys.argv[1] if len(sys.argv) > 1 else "reference.docx")
    print(f"wrote {out}: {len(D.PARAGRAPH_STYLES)} paragraph + "
          f"{len(D.CHARACTER_STYLES)} character styles")
