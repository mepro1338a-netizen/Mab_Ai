#!/usr/bin/env python3
"""Print per-plan Stripe checkout readiness (run locally with .env loaded)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from services.billing_plans import (
    AI_CHECKOUT_KEYS,
    FOOTBALL_CHECKOUT_KEYS,
    checkout_plans_status,
    plan_checkout_ready,
    resolve_stripe_price_id,
)


def main() -> None:
    print("STRIPE_SECRET_KEY:", "set" if os.getenv("STRIPE_SECRET_KEY") else "MISSING")
    print()
    for key in (*AI_CHECKOUT_KEYS, *FOOTBALL_CHECKOUT_KEYS):
        ready, reason = plan_checkout_ready(key)
        price_id, env = resolve_stripe_price_id(key)
        mark = "OK" if ready else "FAIL"
        print(f"  [{mark}] {key}: env={env} price_id={'set' if price_id else 'MISSING'} reason={reason or '-'}")
    print()
    status = checkout_plans_status()
    if status["missing_envs"]:
        print("Missing Railway variables:", ", ".join(status["missing_envs"]))


if __name__ == "__main__":
    main()
