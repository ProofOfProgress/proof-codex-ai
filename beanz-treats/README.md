# Beanz Treats Website

A warm, homemade-feeling website for **Beanz Treats**.

## Preview locally

From this folder:

```bash
cd beanz-treats
python3 -m http.server 8080
```

Open: http://127.0.0.1:8080

## Add the real logo

Save Steven's updated logo image as:

`beanz-treats/assets/logo.png`

Recommended: PNG with transparent background, at least 512×512 px.

The site tries `logo.png` first and falls back to `logo.svg` until the PNG is added.

## Publish for free (GitHub Pages)

1. Push this repo to GitHub.
2. On GitHub: **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Branch: `main`, folder: `/beanz-treats`.
5. Save. GitHub gives you a link like `https://yourusername.github.io/repo-name/`.

## What's on the site

- Hero with brand story
- About Me (Steven)
- About Beanz Treats (business story)
- Social links (TikTok, Instagram, Facebook, YouTube)
- Embedded Google order form

## Update content

Edit `index.html` for text changes. Colors and fonts live in `css/styles.css`.
