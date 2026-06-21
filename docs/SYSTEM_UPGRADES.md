# System upgrades — plain English

**You asked to upgrade the system a ton.** Here is what is in the repo now, what still needs you, and what we skipped on purpose.

---

## Upgraded (no verification from you)

| Upgrade | What it does |
|---------|----------------|
| **Mem0** | Remembers hooks, failures, lessons (`data/mem0/`) |
| **TextGrad** | Rewrites hook templates when analytics punish |
| **Product queue (15)** | `data/product_queue.json` — topics + hooks + verdict hints ready |
| **Script QC** | Scores brief before InVideo — don’t burn credits on bad scripts |
| **Run telemetry** | Every daily tick logged to `data/telemetry/runs.jsonl` |
| **Owner signals** | Say “framing was wonky” in chat → Mem0 + avoid rules |
| **Render retries** | InVideo download tries twice before giving up |
| **Phase 2 purge** | ~8k lines of homemade horror/render code deleted |

---

## Still blocked (needs phone / pay / verify)

| Item | Why |
|------|-----|
| InVideo Generate on cloud | Credits + payment + 2FA |
| Daily loop timer | Paused until credits |
| TikTok cross-post | Phone OAuth |
| Google Drive MCP on cloud | Google verify |
| Full EvoAgentX install | Huge; TextGrad covers evolution |

---

## Laptop-only ship (free Drive)

1. Export MP4 on laptop InVideo  
2. Upload to Google Drive (free) → share link  
3. Paste link to agent → `fetch_url_cli` → YouTube upload  

No paid Drive. No cloud verify.

---

## Inspect

```bash
python3 -m shorts_bot.learning.workflow_cli status
python3 -m shorts_bot.production.product_queue_cli   # if added
cat data/telemetry/runs.jsonl | tail -3
```

---

## When phone is back

1. InVideo credits  
2. Resume daily loop OR laptop `/loop`  
3. Analytics → Mem0/TextGrad start learning for real  

Until then the **brain keeps getting smarter**; the **hands** wait for credits.
