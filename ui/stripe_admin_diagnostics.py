"""Stripe plan diagnostics — Admin Panel only (not Premium)."""
from __future__ import annotations

import streamlit as st

try:
    from services.stripe_verify import get_stripe_verify_cache, refresh_stripe_verify_cache
except ImportError:
    def get_stripe_verify_cache() -> dict:
        return {}

    def refresh_stripe_verify_cache() -> None:
        return None


def render_stripe_admin_diagnostics() -> None:
    """Admin Panel: Stripe Price-ID status per checkout plan."""
    cache = get_stripe_verify_cache()
    if not cache:
        st.info("Stripe-Diagnose ist derzeit nicht verfügbar.")
        return
    broken = [k for k, v in cache.items() if v.get("price_id") and not v.get("ok")]

    st.markdown("#### Stripe Checkout (Abo-Pl├ñne)")
    st.caption("Nur recurring `price_ÔÇª` mit mode=subscription. One-off Prices werden abgelehnt.")

    for plan_key, row in cache.items():
        env = row.get("env", "")
        pid = row.get("price_id", "") or "ÔÇö"
        if row.get("ok"):
            mode = "live" if row.get("livemode") else "test"
            interval = row.get("recurring_interval") or "recurring"
            short = pid if len(pid) <= 28 else f"{pid[:28]}ÔÇª"
            st.markdown(
                f"Ô£à **{plan_key}** ÔÇö `{env}` ÔåÆ `{short}` ({mode}, {interval})"
            )
        else:
            err = row.get("error") or "unbekannt"
            st.markdown(f"ÔØî **{plan_key}** ÔÇö `{env}` ÔåÆ `{pid}` ÔÇö {err}")

    if broken:
        st.warning(
            "Ung├╝ltige Pl├ñne: " + ", ".join(broken) + " ÔÇö in Stripe Recurring-Preise anlegen."
        )
    else:
        st.success("Alle Checkout-Pl├ñne sind als Recurring-Preise g├╝ltig.")

    if st.button("Stripe erneut pr├╝fen", key="admin_stripe_verify_refresh"):
        refresh_stripe_verify_cache()
        st.rerun()
