# Beanz Treats Website

A warm, homemade-feeling website for **Beanz Treats**.

## Live links

**Works on your phone right now (no setup):**

https://htmlpreview.github.io/?https://raw.githubusercontent.com/ProofOfProgress/proof-codex-ai/gh-pages/index.html

**Permanent clean link (after GitHub Pages is turned on):**

https://proofofprogress.github.io/proof-codex-ai/

## Put it online permanently (one click on GitHub)

The site files are already on the `gh-pages` branch. To turn on the clean link:

1. Open: https://github.com/ProofOfProgress/proof-codex-ai/actions/workflows/enable-beanz-pages.yml
2. Click **Run workflow** → **Run workflow**
3. Wait for the green checkmark (~1 min)
4. Open: https://proofofprogress.github.io/proof-codex-ai/

If that workflow fails, use Settings instead:

1. https://github.com/ProofOfProgress/proof-codex-ai/settings/pages
2. **Source** → **GitHub Actions**
3. Re-run **Deploy Beanz Treats site** from Actions

## Why `127.0.0.1` failed on your phone

`127.0.0.1` means “this computer only.” Your phone is a different device.

## Preview on your computer only

```bash
cd beanz-treats
python3 -m http.server 8080
```

Open: http://127.0.0.1:8080

## What's on the site

- Table of Contents (Steven's page titles and copy from his Google Sites site)
- About me / About Beanz Treats
- Social links
- Embedded Google order form
- Mascot: `assets/logo.png`

## Update content

Edit `index.html` for text changes. Colors and fonts live in `css/styles.css`.

If you add new text, keep Steven's voice — direct, personal, first-person — matching what's already on his site.
