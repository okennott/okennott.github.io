# kennott.github.io

Personal academic website of **Kenneth Otieno Onditi** — mammal ecologist and evolutionary biologist specialising in the systematics, phylogeography, and conservation biology of African small mammals.

🌐 **Live site:** [kennott.github.io](https://kennott.github.io)

---

## About

This is a single-file static website (`index.html`) built with vanilla HTML, CSS, and JavaScript — no frameworks, no build tools, no dependencies beyond Google Fonts. It is designed to be lightweight, fast, and deployable directly via GitHub Pages.

The site covers six sections:

| Page | Contents |
|---|---|
| **Home** | Research overview, key metrics, selected publications |
| **Research** | Thematic research programmes with context and key taxa |
| **Publications** | All peer-reviewed works with live DOI links |
| **Fieldwork** | Field expedition records with specimen counts and site descriptions |
| **CV** | Curriculum vitae — education, appointments, grants, awards, mentorship |
| **Contact** | Email, institutional affiliations, collaborator directory |

---

## Repository Structure

```
kennott.github.io/
└── index.html       # Entire site — all pages, styles, and scripts in one file
└── README.md        # This file
```

---

## Deployment

The site is deployed automatically via **GitHub Pages** from the `main` branch root.

To update the site, edit `index.html` and push to `main`:

```bash
git add index.html
git commit -m "Update [section] — [brief description]"
git push origin main
```

Changes are typically live within 1–2 minutes.

---

## Tech Stack

- **HTML5 / CSS3 / vanilla JS** — no frameworks
- **Fonts:** EB Garamond, DM Mono, Bitter (Google Fonts)
- **Navigation:** client-side single-page app with CSS `animation` transitions
- **Scroll reveals:** `IntersectionObserver` API
- **Hosting:** GitHub Pages (static, free tier)

---

## Content Updates

### Adding a new publication

Find the relevant year block in the `Publications` page section of `index.html` and prepend a new `.pub-entry` div, incrementing the number:

```html
<div class="pub-entry">
  <span class="pub-num">33</span>
  <div>
    <div class="pub-authors"><strong>Onditi, K. O.</strong>, Co-author, A. B., ...</div>
    <div class="pub-title">Title of the paper</div>
    <div class="pub-venue">Journal Name, Volume(Issue), pages · 
      <a href="https://doi.org/10.xxxx/xxxxx" target="_blank">doi:10.xxxx/xxxxx</a>
    </div>
  </div>
</div>
```

Also update the publication count in the hero stats on the Home page:

```html
<span class="stat-num">33</span>  <!-- was 32 -->
```

### Updating citation count

In the Home page hero section, update:

```html
<span class="stat-num">200<sup ...>+</sup></span>
```

---

## Local Preview

No build step required. Open the file directly in any browser:

```bash
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

Or serve locally with Python:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

---

## Contact

**Kenneth Otieno Onditi**  
kenotieno@hotmail.com  
+254 722 620075  
Nairobi, Kenya

[Google Scholar](https://scholar.google.com/citations?user=qnHYvIIAAAAJ&hl=en) · [ResearchGate](https://www.researchgate.net/profile/Kenneth-Onditi)
