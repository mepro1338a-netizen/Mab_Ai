from pathlib import Path

p = Path(r"c:\mab_upload\pages\auth.py")
text = p.read_text(encoding="utf-8")

start = text.index("def render_mode_switch() -> str:")
end = text.index("\n\n\ndef oauth_button", start)
new_fn = '''def render_mode_switch() -> str:
    mode = st.session_state.get("auth_mode", "login")
    tab_login, tab_register = st.columns(2, gap="small")

    with tab_login:
        if st.button("Anmelden", key="auth_tab_login", width="stretch", type="primary" if mode == "login" else "tertiary"):
            st.session_state.auth_mode = "login"
            st.rerun()

    with tab_register:
        if st.button("Registrieren", key="auth_tab_register", width="stretch", type="primary" if mode == "register" else "tertiary"):
            st.session_state.auth_mode = "register"
            st.rerun()

    return mode
'''

text = text[:start] + new_fn + text[end:]
p.write_text(text, encoding="utf-8")
print("render_mode_switch patched")
