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
    SUBSCRIPTION_CHECKOUT_MODE,
    checkout_base_url,
    stripe_checkout_cancel_url,
    stripe_checkout_success_url,
)
from services.stripe_verify import verify_all_checkout_plans


def main() -> None:
    print("STRIPE_SECRET_KEY:", "set" if os.getenv("STRIPE_SECRET_KEY") else "MISSING")
    print("APP_BASE_URL:", os.getenv("APP_BASE_URL", "(unset)"))
    print("STRIPE_SUCCESS_URL:", os.getenv("STRIPE_SUCCESS_URL", "(unset)"))
    print("checkout_base_url():", checkout_base_url())
    print("success_url:", stripe_checkout_success_url())
    print("cancel_url:", stripe_checkout_cancel_url())
    print("checkout mode:", SUBSCRIPTION_CHECKOUT_MODE, "(all Abo plans)")
    print()
    for key, row in verify_all_checkout_plans().items():
        mark = "OK" if row.get("ok") else "FAIL"
        err = row.get("error") or "-"
        pid = row.get("price_id") or "MISSING"
        ptype = row.get("price_type") or "-"
        interval = row.get("recurring_interval") or "-"
        print(
            f"  [{mark}] {key}: {row.get('env')} -> {pid} | "
            f"type={ptype} interval={interval} | {err}"
        )


if __name__ == "__main__":
    main()
