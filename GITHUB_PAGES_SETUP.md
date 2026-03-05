# GitHub Pages URL Fix — Issue 2

## Current situation

| URL | Status |
|-----|--------|
| `https://kennott.github.io/` | ❌ 404 |
| `https://okennott.github.io/` | ❌ 404 |
| `https://okennott.github.io/kennott.github.io/` | ✅ Works |

**Why:** Your GitHub username is `okennott` and your repo is named `kennott.github.io`.
GitHub Pages serves a *user site* at `https://<username>.github.io/` from a repo named `<username>.github.io`.
Since the names don't match (`okennott` ≠ `kennott`), GitHub treats it as a *project site* at `/kennott.github.io/`.

---

## Option A — Rename your GitHub username to `kennott` (Best option)

This makes `https://kennott.github.io/` work instantly, with **no other changes needed**.

1. Check that `kennott` is available at https://github.com/kennott
2. On GitHub: **Settings → Account → Change username → `kennott`**
3. GitHub will automatically redirect `okennott` links to `kennott` for a period.
4. Your site URL becomes: **`https://kennott.github.io/`** ✅

> The repo is already named `kennott.github.io`, so once the username matches, it becomes a proper user site served from root.

---

## Option B — Rename the repo to match your current username

If `kennott` is taken and you want a stable URL under `okennott`:

1. On GitHub: open the repo → **Settings → Rename → `okennott.github.io`**
2. Your site URL becomes: **`https://okennott.github.io/`** ✅
3. All internal links in the HTML files use relative paths (`href="research.html"`) so they will continue to work.

---

## Option C — Custom domain (Most professional)

If you have or acquire a domain (e.g. `kennetonditi.com` or `onditi.ac.ke`):

1. In the repo root, create a file named `CNAME` containing just your domain:
   ```
   kennetonditi.com
   ```
2. In your domain registrar's DNS settings, add:
   - An **A record** pointing to GitHub's IPs: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - Or a **CNAME record** pointing `www` to `okennott.github.io`
3. On GitHub: repo **Settings → Pages → Custom domain** → enter your domain → Save
4. Enable **Enforce HTTPS** once the certificate is issued (usually within 24 h).

---

## Deploying the new multi-page site

The website now has separate HTML files. Push everything to the `main` (or `gh-pages`) branch:

```bash
git add .
git commit -m "Redesign: multi-page site with publications, fieldwork, CV pages"
git push origin main
```

Make sure GitHub Pages is set to serve from:
**Settings → Pages → Source → Deploy from a branch → `main` / `root`**

---

## Adding PDF author copies

1. Export your papers from your EndNote library as PDFs.
2. Rename them following the convention in `pdfs/README.txt`.
3. Place them in the `pdfs/` folder.
4. Commit and push — the "Author Copy (PDF)" buttons on the publications page will then work.

For open-access papers (BMC, Frontiers, MDPI, Scientific Reports, ZooKeys),
the publisher PDF is freely available via the DOI link, so no author copy is strictly needed.
