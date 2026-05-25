"""Legal pages — Impressum, Datenschutz, AGB, Cookies, Refund, Premium Terms."""
from __future__ import annotations

import html

import streamlit as st

from ui.premium_foundation import premium_foundation_css, render_page_hero
from ui_core import require_login


LEGAL_PAGES = {
    "impressum": ("Impressum", "Anbieterkennzeichnung"),
    "privacy": ("Datenschutz", "DSGVO-konforme Informationen"),
    "terms": ("AGB", "Allgemeine Geschäftsbedingungen"),
    "cookies": ("Cookie-Hinweis", "Technisch notwendige Cookies"),
    "refund": ("Refund Policy", "Erstattungen & Kündigung"),
    "premium_terms": ("Premium Terms", "Abonnements & Leistungsbeschreibung"),
}


def _legal_css() -> None:
    premium_foundation_css(900, 88, """
.legal-doc h3 { color: #ffe7a3 !important; font-size: 18px; margin-top: 18px; }
.legal-doc p, .legal-doc li { color: #94a3b8 !important; font-size: 14px; line-height: 1.6; }
.legal-doc ul { padding-left: 20px; }
.legal-footer { margin-top: 28px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,.08); }
""")


def _block(content: str) -> None:
    st.markdown(f'<div class="legal-doc">{content}</div>', unsafe_allow_html=True)


def render_impressum() -> None:
    _block("""
    <h3>Anbieter</h3>
    <p>MaByte / Mab AI — Betreiber gemäß Impressumspflicht.<br>
    Kontakt: support@mabyte.de (Platzhalter — bitte vor Launch ersetzen)</p>
    <h3>Verantwortlich für Inhalte</h3>
    <p>Verantwortlich nach § 18 Abs. 2 MStV: [Name, Anschrift eintragen]</p>
    <h3>Umsatzsteuer-ID</h3>
    <p>[USt-IdNr. falls vorhanden]</p>
    """)


def render_privacy() -> None:
    _block("""
    <h3>1. Verantwortlicher</h3>
    <p>Verarbeitung personenbezogener Daten erfolgt DSGVO-konform. Kontakt: Datenschutzanfragen an support@mabyte.de.</p>
    <h3>2. Welche Daten</h3>
    <ul>
    <li>Account: Username, E-Mail, gehashtes Passwort</li>
    <li>Nutzung: Workspace-Logs, Token-Verbrauch, Support-Tickets</li>
    <li>Zahlung: Stripe (Zahlungsdaten direkt bei Stripe)</li>
    <li>OAuth: Provider-ID über Google/Meta/TikTok — kein Klartext-Passwort</li>
    </ul>
    <h3>3. Zweck & Rechtsgrundlage</h3>
    <p>Vertragserfüllung (Art. 6 Abs. 1 lit. b), berechtigtes Interesse an Sicherheit und Betrieb (lit. f).</p>
    <h3>4. Speicherdauer</h3>
    <p>Accountdaten bis Löschung; Logs rotierend; Backups nach interner Policy.</p>
    <h3>5. Ihre Rechte</h3>
    <p>Auskunft, Berichtigung, Löschung, Einschränkung, Widerspruch — per Support-Ticket.</p>
    """)


def render_terms() -> None:
    _block("""
    <h3>1. Geltungsbereich</h3>
    <p>Diese AGB gelten für die Nutzung der MaByte SaaS-Plattform (Mab AI).</p>
    <h3>2. Leistung</h3>
    <p>AI-Workspaces, Football Intelligence, Media Studios — Verfügbarkeit im Beta-Best-Effort.</p>
    <h3>3. Pflichten Nutzer</h3>
    <p>Keine illegalen Inhalte, kein Missbrauch von APIs, keine Weitergabe von Zugangsdaten.</p>
    <h3>4. Haftung</h3>
    <p>Haftung bei Vorsatz und grober Fahrlässigkeit; Football/Odds nur analytisch, keine Wettberatung.</p>
    <h3>5. Schluss</h3>
    <p>Es gilt deutsches Recht. Gerichtsstand nach gesetzlichen Vorgaben für Verbraucher.</p>
    """)


def render_cookies() -> None:
    _block("""
    <h3>Technisch notwendige Cookies</h3>
    <p>Streamlit-Session-Cookies für Login und Sicherheit (XSRF). Kein Tracking-Marketing ohne Einwilligung.</p>
    <h3>Speicherdauer</h3>
    <p>Session-Cookies bis Logout bzw. Ablauf der Browser-Session.</p>
    <h3>Deaktivierung</h3>
    <p>Ohne Session-Cookies ist die Anmeldung nicht möglich.</p>
    """)


def render_refund() -> None:
    _block("""
    <h3>Abonnements</h3>
    <p>Über Stripe abgerechnet. Kündigung zum Periodenende über Stripe Customer Portal (wenn aktiviert) oder Support.</p>
    <h3>Erstattungen</h3>
    <p>14-Tage-Widerruf für Verbraucher wo anwendbar; anteilige Erstattung nach Prüfung bei technischen Ausfällen.</p>
    <h3>Tokens</h3>
    <p>Verbrauchte Token-Pakete sind nach Nutzung grundsätzlich nicht erstattbar.</p>
    """)


def render_premium_terms() -> None:
    _block("""
    <h3>Pläne</h3>
    <p>MaByte: Free, Pro, Grand, Elite. Football: Starter, Pro, Elite — jeweils eigene Feature-Matrix.</p>
    <h3>Tokens</h3>
    <p>1€ ≈ 100 Tokens (konfigurierbar). Verbrauch je Workspace laut App-Anzeige.</p>
    <h3>Upgrades</h3>
    <p>Upgrades wirken nach erfolgreicher Stripe-Zahlung. Downgrades zum nächsten Abrechnungszeitraum.</p>
    <h3>Fair Use</h3>
    <p>API- und AI-Limits pro Plan; Missbrauch kann zur Sperre führen.</p>
    """)


RENDERERS = {
    "impressum": render_impressum,
    "privacy": render_privacy,
    "terms": render_terms,
    "cookies": render_cookies,
    "refund": render_refund,
    "premium_terms": render_premium_terms,
}


def render_legal(page_key: str = "legal", *, public: bool = False) -> None:
    if not public:
        require_login()
    _legal_css()

    if page_key == "legal":
        render_page_hero("Legal Center", "Rechtliches", "Impressum, Datenschutz, AGB und Premium-Bedingungen.")
        cols = st.columns(2)
        keys = list(LEGAL_PAGES.keys())
        for i, key in enumerate(keys):
            title, sub = LEGAL_PAGES[key]
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{html.escape(title)}**")
                    st.caption(sub)
                    if st.button("Öffnen", key=f"legal_go_{key}", width="stretch"):
                        st.session_state.page = key
                        st.rerun()
        return

    title, sub = LEGAL_PAGES.get(page_key, ("Legal", ""))
    render_page_hero(title, "MaByte Legal", sub)
    fn = RENDERERS.get(page_key)
    if fn:
        fn()
    st.markdown('<div class="legal-footer">', unsafe_allow_html=True)
    if st.button("← Legal Center" if not public else "← Zur Anmeldung", width="stretch"):
        st.session_state.page = "legal" if not public else "auth"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
