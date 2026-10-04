# -*- coding: utf-8 -*-
"""The single definition of how the CV looks.

`make_reference.py` turns this into `reference.docx`, whose named styles are what
`cv.qmd` addresses through Pandoc's `custom-style`. Change a number here and both
the Word and the PDF output follow, because the PDF is produced from the Word file.
"""

# Palette: the site's --gold darkened for print, plus a warm near-black.
INK    = "1A1712"   # body text
MUTED  = "5A5347"   # secondary text
FAINT  = "7A7263"   # dates, notes
BRONZE = "8A6520"   # section headings, accents, links
RULE   = "C9B98E"   # hairline under section headings

SERIF, SANS = "Georgia", "Calibri"

PAGE = dict(width=8.27, height=11.69,           # A4, inches
            left=0.72, right=0.72, top=0.6, bottom=0.6, footer=0.35)

GUTTER = 1.30       # date column on entries
LABEL  = 1.55       # wider gutter for skills / service, whose labels are longer
BULLET = 0.16       # bullet hanging indent, added to GUTTER
PUBIND = 0.34       # hanging indent on numbered publications

# name -> paragraph style. Sizes in pt, indents in inches, spacing in pt.
PARAGRAPH_STYLES = {
    "CVName":     dict(font=SERIF, size=19,  bold=True,  color=INK,    after=1,  spacing=1.6, caps=True),
    "CVTitle":    dict(font=SERIF, size=10,  italic=True, color=BRONZE, after=3),
    "CVAffil":    dict(font=SANS,  size=8.8, color=MUTED, after=2),
    "CVContact":  dict(font=SANS,  size=8.6, color=MUTED, after=1),
    "CVLinks":    dict(font=SANS,  size=8.6, color=MUTED, after=0, border_bottom=(BRONZE, 10, 6)),
    "CVSection":  dict(font=SERIF, size=9.8, bold=True,  color=BRONZE, caps=True, spacing=1.1,
                       before=11, after=4, keep_next=True, border_bottom=(RULE, 4, 2)),
    "CVProfile":  dict(font=SANS,  size=9.5, color=INK,   line=1.08),
    "CVMetrics":  dict(font=SANS,  size=8.4, color=MUTED, before=7),
    "CVNote":     dict(font=SANS,  size=8,   italic=True, color=FAINT, before=2),
    "CVPubNote":  dict(font=SANS,  size=8.2, italic=True, color=FAINT, after=5, keep_next=True),
    "CVLead":     dict(font=SANS,  size=8.8, italic=True, color=MUTED, after=3),
    "CVSubhead":  dict(font=SANS,  size=9.4, bold=True,  color=INK, before=9, after=1, keep_next=True),
    "CVEntry":    dict(font=SANS,  size=9.8, bold=True,  color=INK, before=6,
                       left=GUTTER, hanging=GUTTER, tab=GUTTER, keep_next=True),
    "CVMeta":     dict(font=SANS,  size=9,   italic=True, color=MUTED, left=GUTTER),
    "CVBody":     dict(font=SANS,  size=9.3, color=INK,   left=GUTTER, before=1),
    "CVBullet":   dict(font=SANS,  size=9.3, color=INK,   before=1.5,
                       left=GUTTER + BULLET, hanging=BULLET, tab=GUTTER + BULLET),
    "CVPub":      dict(font=SANS,  size=9.3, color=INK,   before=3.5, line=1.03,
                       left=PUBIND, hanging=PUBIND, tab=PUBIND),
    "CVLabel":    dict(font=SANS,  size=9.3, color=INK,   before=3, line=1.05,
                       left=LABEL, hanging=LABEL, tab=LABEL),
    "CVLabelNote":dict(font=SANS,  size=8.7, color=MUTED, before=2, left=LABEL, line=1.05),
    "CVRefName":  dict(font=SANS,  size=9.6, bold=True,  color=INK, before=5, keep_next=True),
    "CVRefOrg":   dict(font=SANS,  size=9,   italic=True, color=MUTED, keep_next=True),
}

# name -> character style, for spans inside a paragraph.
CHARACTER_STYLES = {
    "CVDate":   dict(font=SANS,  size=8.8,  bold=True, color=FAINT),
    "CVMe":     dict(bold=True),                     # Kenneth's name in an author list
    "CVTaxon":  dict(italic=True),                   # genus / species names
    "CVBig":    dict(font=SERIF, size=10.3, bold=True, color=BRONZE),   # metric figures
    "CVSep":    dict(color="C0B6A0"),                # the "·" between items
    "CVMuted":  dict(color=MUTED, bold=False),
    "CVFaint":  dict(color=FAINT),
    "CVNum":    dict(font=SANS,  size=9.3,  bold=True, color=FAINT),    # publication numbers
    "CVLink":   dict(font=SANS,  size=8.6,  color=BRONZE),
}

FOOTER = "Kenneth Otieno Onditi  ·  Curriculum Vitae  ·  "
