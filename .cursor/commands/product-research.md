---
name: product-research
description: Module 3 FastMoss product picks and ranked affiliate shortlist. Use when the owner wants fresh products or products.json refresh.
---

# /product-research

Invoke the **Product Researcher** — Module 3 **FastMoss** research (replaces EchoTik).

**Launch path A:** owner picks in FastMoss app → paste names to agent.  
**Launch path B:** API scout when `FASTMOSS_*` secrets configured.

## Examples

```
/product-research
I picked 8 products in FastMoss — here are the names: ...

/product-research
Run middle core scout when API is wired — top picks for this week
```

## What you get

- Products saved or confirmed in `data/tiktok_shop/products.json`
- Plain-English top picks with commission, GMV, creators (when data available)
- Reminder to eyeball top 3 in FastMoss before batch clip day

## CEO orchestration

Or just ask in chat: *"Help me lock 8–10 FastMoss products while you prep clips"* — CEO delegates in **background**.

Full doc: `data/research/course/PRODUCT_RESEARCH.md` · Setup: `docs/FOR_OWNER_FASTMOSS_SETUP.md`
