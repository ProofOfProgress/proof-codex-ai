# Beanz Treats Website

A warm, homemade-feeling website for **Beanz Treats**.

## Put it online (free)

After the site is merged to `main`, GitHub Pages publishes it automatically.

**Your link will be:**

https://proofofprogress.github.io/proof-codex-ai/

That works on phones, laptops, anywhere — not just your computer.

### One-time setup (if Pages is not enabled yet)

1. Open: https://github.com/ProofOfProgress/proof-codex-ai/settings/pages
2. Under **Build and deployment → Source**, choose **GitHub Actions**
3. Wait 1–2 minutes, then open the link above

### Why `127.0.0.1` failed on your phone

`127.0.0.1` means “this computer only.” Your phone is a different device, so it cannot see a server running on your laptop.

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
