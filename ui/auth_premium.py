"""Auth premium UI — DISABLED (emergency). Layout lives in pages/auth.py only."""
from __future__ import annotations


def auth_styles_bundle() -> str:
    return ""


def auth_grid_marker_html() -> str:
    return ""


def login_card_marker_html() -> str:
    return ""


def page_open_html(mode_class: str = "") -> str:
    return ""


def page_close_html() -> str:
    return ""


def panel_close_html() -> str:
    return ""


def panel_shell_html(*, register: bool) -> str:
    return ""


def hero_html() -> str:
    return ""


def forgot_password_html() -> str:
    return ""


def oauth_divider_html() -> str:
    return ""


def notice_html(level: str, message: str) -> str:
    return ""


def auth_page_marker_html() -> str:
    return ""


# Legacy aliases
auth_page_open = page_open_html
auth_page_close = page_close_html
oauth_divider_html = oauth_divider_html
forgot_password_html = forgot_password_html
login_card_marker_html = login_card_marker_html
panel_close_html = panel_close_html
hero_html = hero_html
auth_grid_marker_html = auth_grid_marker_html
auth_card_marker_html = login_card_marker_html
auth_card_header_html = panel_shell_html
auth_divider_html = oauth_divider_html
auth_forgot_link_html = forgot_password_html
auth_label_html = lambda text: ""
auth_notice_html = notice_html
auth_switch_note_html = lambda *, register: ""
brand_panel_html = hero_html
