# Vendored Higgsfield Cursor plugin

Upstream: https://github.com/higgsfield-ai/cursor-plugin  
Marketplace: https://cursor.com/marketplace/higgsfield  
Pinned commit: `af1ae5a79611bb47b9e1db86c4afc13eb406ee07` (2026-05-21)

MIT License — see `LICENSE`.

To refresh from upstream:

```bash
git clone https://github.com/higgsfield-ai/cursor-plugin.git /tmp/higgsfield-cursor-plugin
cd /tmp/higgsfield-cursor-plugin && git pull
cp -r .cursor-plugin assets commands skills LICENSE mcp.json README.md \
  /path/to/proof-codex-ai/.cursor/plugins/higgsfield/
# Update this file with the new commit hash.
```

Owner setup: `docs/FOR_OWNER_HIGGSFIELD_SETUP.md`
