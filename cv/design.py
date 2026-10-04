# -*- coding: utf-8 -*-
"""The single definition of how the CV looks.

`make_reference.py` turns this into `reference.docx`, whose named styles are what
`cv.qmd` addresses through Pandoc's `custom-style`. Change a number here and both
the Word and the PDF output follow, because the PDF is produced from the Word file.

Fonts are Cambria (headings) and Calibri (text). Both ship with Word, and both have
metric-compatible open substitutes (Caladea, Carlito) on Linux, so a Linux
LibreOffice lays the PDF out exactly as Word does.
"""

# Palette: the site's --gold darkened for print, plus a warm near-black.
INK    = "1A1712"   # body text
MUTED  = "4F493E"   # secondary text (affiliations, meta lines)
FAINT  = "6E6757"   # dates, notes, footer
BRONZE = "8A6520"   # section headings, accents, links
RULE   = "D2C49C"   # hairlines
BAND   = "F8F4E8"   # key-figures band

SERIF, SANS = "Cambria", "Calibri"

PAGE = dict(width=8.27, height=11.69,           # A4, inches
            left=0.75, right=0.75, top=0.65, bottom=0.75, footer=0.4)
TEXT_WIDTH = PAGE["width"] - PAGE["left"] - PAGE["right"]

GUTTER = 1.35       # date column on entries
LABEL  = 1.60       # wider gutter for skills / service, whose labels are longer
BULLET = 0.16       # bullet hanging indent, added to GUTTER
PUBIND = 0.36       # hanging indent on numbered publications

# name -> paragraph style. Sizes in pt, indents in inches, spacing in pt.
PARAGRAPH_STYLES = {
    "CVName":     dict(font=SERIF, size=24,  bold=True,  color=INK,    after=1,  spacing=1.4, caps=True),
    "CVTitle":    dict(font=SERIF, size=11,  italic=True, color=BRONZE, after=4),
    "CVAffil":    dict(font=SANS,  size=9.5, color=MUTED, after=2),
    "CVContact":  dict(font=SANS,  size=9.2, color=MUTED, after=1),
    "CVLinks":    dict(font=SANS,  size=9.2, color=MUTED, after=0, border_bottom=(BRONZE, 8, 7)),
    "CVSection":  dict(font=SERIF, size=10.5, bold=True, color=BRONZE, caps=True, spacing=1.2,
                       before=14, after=5, keep_next=True, border_bottom=(RULE, 4, 2)),
    "CVProfile":  dict(font=SANS,  size=10,  color=INK,   line=1.12, before=2, after=7),
    "CVNote":     dict(font=SANS,  size=8.3, italic=True, color=FAINT, before=4),
    "CVPubNote":  dict(font=SANS,  size=8.6, italic=True, color=FAINT, after=4, keep_next=True),
    "CVLead":     dict(font=SANS,  size=9.4, italic=True, color=MUTED, after=3, line=1.06),
    "CVSubhead":  dict(font=SANS,  size=10,  bold=True,  color=INK, before=10, after=2, keep_next=True),
    "CVEntry":    dict(font=SANS,  size=10.2, bold=True, color=INK, before=7,
                       left=GUTTER, hanging=GUTTER, tab=GUTTER, keep_next=True),
    # A title-only entry: same look, but not chained to the next paragraph.
    "CVEntryEnd": dict(font=SANS,  size=10.2, bold=True, color=INK, before=7,
                       left=GUTTER, hanging=GUTTER, tab=GUTTER),
    "CVMeta":     dict(font=SANS,  size=9.4, italic=True, color=MUTED, left=GUTTER, keep_next=True),
    # The last line of an entry that has no body text: same look, but it must not
    # chain the entry to whatever follows.
    "CVMetaEnd":  dict(font=SANS,  size=9.4, italic=True, color=MUTED, left=GUTTER),
    "CVBody":     dict(font=SANS,  size=9.8, color=INK,   left=GUTTER, before=1.5, line=1.06),
    "CVBullet":   dict(font=SANS,  size=9.8, color=INK,   before=2, line=1.06,
                       left=GUTTER + BULLET, hanging=BULLET, tab=GUTTER + BULLET),
    "CVPub":      dict(font=SANS,  size=9.5, color=INK,   before=4, line=1.04,
                       left=PUBIND, hanging=PUBIND, tab=PUBIND),
    "CVLabel":    dict(font=SANS,  size=9.8, color=INK,   before=4, line=1.06,
                       left=LABEL, hanging=LABEL, tab=LABEL),
    "CVLabelNote":dict(font=SANS,  size=9.2, color=MUTED, before=2, left=LABEL, line=1.05),
    "CVRefName":  dict(font=SANS,  size=10,  bold=True,  color=INK, before=6, keep_next=True),
    "CVRefOrg":   dict(font=SANS,  size=9.4, italic=True, color=MUTED, keep_next=True),
}

# name -> character style, for spans inside a paragraph.
CHARACTER_STYLES = {
    "CVDate":   dict(font=SANS,  size=9.2,  bold=True, color=FAINT),
    "CVMe":     dict(bold=True),                     # Kenneth's name in an author list
    "CVTaxon":  dict(italic=True),                   # genus / species names
    "CVSep":    dict(color="B9AE94"),                # the "·" between items
    "CVMuted":  dict(color=MUTED, bold=False),
    "CVFaint":  dict(color=FAINT),
    "CVNum":    dict(font=SANS,  size=9.5,  bold=True, color=FAINT),    # publication numbers
    "CVLink":   dict(font=SANS,  size=9.2,  color=BRONZE),
}

FOOTER = "Kenneth Otieno Onditi  ·  Curriculum Vitae"
