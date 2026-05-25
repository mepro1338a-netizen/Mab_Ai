"""Stripe plan diagnostics — Admin Panel only (not Premium)."""
from __future__ import annotations

import streamlit as st

from services.stripe_verify import get_stripe_verify_cache, refresh_stripe_verify_cache


def render_stripe_admin_diagnostics() -> None:
    """Admin Panel: Stripe Price-ID status per checkout plan."""
    cache = get_stripe_verify_cache()
    broken = [k for k, v in cache.items() if v.get("price_id") and not v.get("ok")]

    st.markdown("#### Stripe Checkout (Abo-Pläne)")
    st.caption("Nur recurring `price_…` mit mode=subscription. One-off Prices werden abgelehnt.")

    for plan_key, row in cache.items():
        env = row.get("env", "")
        pid = row.get("price_id", "") or "—"
        if row.get("ok"):
            mode = "live" if row.get("livemode") else "test"
            interval = row.get("recurring_interval") or "recurring"
            short = pid if len(pid) <= 28 else f"{pid[:28]}…"
            st.markdown(
                f"✅ **{plan_key}** — `{env}` → `{short}` ({mode}, {interval})"
            )
        else:
            err = row.get("error") or "unbekannt"
            st.markdown(f"❌ **{plan_key}** — `{env}` → `{pid}` — {err}")

    if broken:
        st.warning(
            "Ungültige Pläne: " + ", ".join(broken) + " — in Stripe Recurring-Preise anlegen."
        )
    else:
        st.success("Alle Checkout-Pläne sind als Recurring-Preise gültig.")

    if st.button("Stripe erneut prüfen", key="admin_stripe_verify_refresh"):
        refresh_stripe_verify_cache()
        st.rerun()
