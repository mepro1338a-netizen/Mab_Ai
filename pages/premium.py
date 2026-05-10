import streamlit as st
from config import PLANS


def plan_card(plan_key):
    plan = PLANS[plan_key]

    with st.container(border=True):
        st.subheader(plan["name"])
        st.markdown(f"## {plan['price']}€ / Monat")
        st.markdown(f"**{plan['tokens']} Tokens inklusive**")

        st.divider()

        for feature in plan["features"]:
            st.write(f"✅ {feature}")

        st.divider()

        if st.button(f"Buy {plan['name']}", key=f"buy_{plan_key}", use_container_width=True):
            st.session_state.selected_plan = plan_key
            st.success(f"{plan['name']} ausgewählt. Stripe Checkout kann hier verbunden werden.")


def render_premium():
    st.markdown("## 💳 Premium")
    st.write("Upgrade deinen Account und schalte mehr AI Features frei.")

    col1, col2, col3 = st.columns(3)

    with col1:
        plan_card("pro")

    with col2:
        plan_card("grand")

    with col3:
        plan_card("elite")