#!/usr/bin/env python3
"""DEPRECATED — use scripts/hub_kalodata_apply_method.py (verify-before-submit gates)."""

from __future__ import annotations

import sys

print(
    "ERROR: cloud_kalodata_grind.py is deprecated — blind clicks caused misclicks on product detail.\n"
    "Use: python3 scripts/hub_kalodata_apply_method.py --method middle_core --category Furniture --cleanup-tabs",
    file=sys.stderr,
)
raise SystemExit(2)
