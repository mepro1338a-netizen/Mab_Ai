"""Futuristic Football UI — HTML cards, discovery hub, less Streamlit look."""
from __future__ import annotations

import html
import re
from typing import Any

import streamlit as st

from ui.styles import inject_css

POPULAR_LEAGUES: list[dict[str, Any]] = [
    {"id": 39, "name": "Premier League", "country": "England"},
    {"id": 140, "name": "La Liga", "country": "Spain"},
    {"id": 78, "name": "Bundesliga", "country": "Germany"},
    {"id": 135, "name": "Serie A", "country": "Italy"},
    {"id": 61, "name": "Ligue 1", "country": "France"},
    {"id": 2, "name": "Champions League", "country": "Europe"},
    {"id": 3, "name": "Europa League", "country": "Europe"},
    {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
]

FOOTBALL_UI_CSS = """
.fb-command-hero {
    border-radius: 32px;
    padding: 32px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 92% 8%, rgba(34,197,94,.22), transparent 38%),
        radial-gradient(circle at 6% 0%, rgba(168,85,247,.28), transparent 40%),
        linear-gradient(135deg, rgba(8,14,32,.98), rgba(4,18,14,.96));
    border: 1px solid rgba(134,239,172,.16);
    box-shadow: 0 32px 80px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.06);
}
.fb-command-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 48px,
        rgba(255,255,255,.015) 48px,
        rgba(255,255,255,.015) 49px
    );
    pointer-events: none;
}
.fb-scanline {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .28em;
    text-transform: uppercase;
}
.fb-command-title {
    color: #f0fdf4 !important;
    font-size: 42px;
    font-weight: 1000;
    letter-spacing: -2px;
    line-height: 1;
    margin-top: 10px;
}
.fb-command-sub {
    color: #94a3b8 !important;
    font-size: 15px;
    line-height: 1.6;
    max-width: 720px;
    margin-top: 12px;
}
.fb-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin: 18px 0 22px 0;
}
@media (max-width: 1100px) {
    .fb-stat-grid { grid-template-columns: repeat(2, 1fr); }
}
.fb-stat-card {
    border-radius: 20px;
    padding: 18px 20px;
    background: linear-gradient(145deg, rgba(12,20,38,.92), rgba(6,12,10,.96));
    border: 1px solid rgba(134,239,172,.14);
    box-shadow: 0 12px 32px rgba(0,0,0,.22);
}
.fb-stat-card .lbl {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .14em;
    text-transform: uppercase;
}
.fb-stat-card .val {
    color: #f0fdf4 !important;
    font-size: 26px;
    font-weight: 1000;
    margin-top: 8px;
    letter-spacing: -.5px;
}
.fb-stat-card .hint {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 6px;
}
.fb-panel {
    border-radius: 24px;
    padding: 22px 24px;
    margin-bottom: 18px;
    background: linear-gradient(160deg, rgba(14,18,36,.94), rgba(8,12,22,.98));
    border: 1px solid rgba(168,85,247,.14);
    box-shadow: 0 18px 48px rgba(0,0,0,.26);
}
.fb-panel-title {
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
    margin: 0 0 4px 0;
}
.fb-panel-sub {
    color: #64748b !important;
    font-size: 12px;
    margin: 0 0 16px 0;
}
.fb-chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
}
.fb-league-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(15,23,42,.75);
    border: 1px solid rgba(168,85,247,.22);
    color: #e2e8f0 !important;
    font-size: 12px;
    font-weight: 800;
}
.fb-league-chip small {
    color: #64748b !important;
    font-weight: 700;
}
.fb-fixture-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
    margin-top: 12px;
}
.fb-fixture-card {
    border-radius: 18px;
    padding: 16px 18px;
    background: linear-gradient(145deg, rgba(18,24,44,.9), rgba(10,14,28,.95));
    border: 1px solid rgba(255,255,255,.07);
    transition: border-color .2s;
}
.fb-fixture-card.live {
    border-color: rgba(34,197,94,.45);
    box-shadow: 0 0 24px rgba(34,197,94,.12);
}
.fb-fixture-league {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .12em;
    text-transform: uppercase;
}
.fb-fixture-date {
    color: #64748b !important;
    font-size: 11px;
    float: right;
}
.fb-fixture-teams {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-top: 14px;
}
.fb-team {
    flex: 1;
    text-align: center;
    color: #f8fafc !important;
    font-size: 13px;
    font-weight: 900;
    line-height: 1.25;
}
.fb-score {
    flex: 0 0 auto;
    min-width: 64px;
    text-align: center;
    padding: 8px 12px;
    border-radius: 14px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(255,231,163,.12);
    color: #ffe7a3 !important;
    font-size: 20px;
    font-weight: 1000;
}
.fb-status-pill {
    display: inline-block;
    margin-top: 10px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .08em;
    text-transform: uppercase;
}
.fb-status-pill.live { background: rgba(34,197,94,.2); color: #86efac !important; }
.fb-status-pill.ns { background: rgba(100,116,139,.2); color: #cbd5e1 !important; }
.fb-status-pill.ft { background: rgba(59,130,246,.18); color: #93c5fd !important; }
.fb-team-pick {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 16px;
    margin-bottom: 8px;
    background: rgba(15,23,42,.55);
    border: 1px solid rgba(255,255,255,.06);
}
.fb-team-pick img {
    width: 36px;
    height: 36px;
    object-fit: contain;
}
.fb-team-pick .name {
    color: #f8fafc !important;
    font-size: 14px;
    font-weight: 900;
}
.fb-team-pick .meta {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 2px;
}
.fb-standings-wrap {
    overflow-x: auto;
    margin-top: 12px;
}
.fb-standings {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
.fb-standings th {
    color: #86efac !important;
    text-align: left;
    padding: 10px 8px;
    border-bottom: 1px solid rgba(134,239,172,.2);
    font-weight: 1000;
    letter-spacing: .06em;
    text-transform: uppercase;
    font-size: 10px;
}
.fb-standings td {
    color: #e2e8f0 !important;
    padding: 10px 8px;
    border-bottom: 1px solid rgba(255,255,255,.04);
}
.fb-standings tr:hover td {
    background: rgba(168,85,247,.08);
}
.fb-empty {
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    border: 1px dashed rgba(134,239,172,.2);
    color: #94a3b8 !important;
    font-size: 14px;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: rgba(8,12,24,.6) !important;
    border-radius: 16px !important;
    padding: 6px !important;
    border: 1px solid rgba(168,85,247,.12) !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 900 !important;
    color: #94a3b8 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(22,101,52,.5), rgba(76,29,149,.4)) !important;
    color: #f0fdf4 !important;
}
.fb-page .stTextInput input, .fb-page .stNumberInput input {
    border-radius: 14px !important;
    background: rgba(8,12,24,.85) !important;
    border: 1px solid rgba(134,239,172,.18) !important;
    color: #f8fafc !important;
}
.fb-page .stButton > button {
    border-radius: 14px !important;
    background: linear-gradient(135deg, rgba(22,101,52,.85), rgba(76,29,149,.75)) !important;
    border: 1px solid rgba(134,239,172,.28) !important;
    color: #f0fdf4 !important;
    font-weight: 1000 !important;
}
.fb-page [data-testid="metric-container"] {
    background: linear-gradient(145deg, rgba(12,18,32,.9), rgba(6,14,10,.95)) !important;
    border: 1px solid rgba(134,239,172,.14) !important;
    border-radius: 18px !important;
}
.fb-ai-studio {
    border-radius: 26px;
    padding: 22px 24px;
    margin-bottom: 20px;
    background: linear-gradient(160deg, rgba(14,12,32,.94), rgba(8,14,24,.98));
    border: 1px solid rgba(168,85,247,.16);
    box-shadow: 0 20px 50px rgba(0,0,0,.28);
}
.fb-match-banner {
    border-radius: 24px;
    padding: 24px 28px;
    margin: 16px 0 20px 0;
    text-align: center;
    background:
        radial-gradient(circle at 50% 0%, rgba(168,85,247,.22), transparent 55%),
        linear-gradient(135deg, rgba(10,16,36,.96), rgba(6,20,14,.94));
    border: 1px solid rgba(255,231,163,.14);
}
.fb-match-banner .vs {
    color: #64748b !important;
    font-size: 14px;
    font-weight: 1000;
    margin: 0 12px;
}
.fb-match-banner .club {
    color: #f0fdf4 !important;
    font-size: 28px;
    font-weight: 1000;
    letter-spacing: -.5px;
}
.fb-match-banner .meta {
    margin-top: 12px;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
}
.fb-module-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
}
.fb-module-chip {
    border-radius: 14px;
    padding: 12px 14px;
    background: rgba(12,16,32,.7);
    border: 1px solid rgba(255,255,255,.06);
}
.fb-module-chip .ico {
    font-size: 18px;
    margin-bottom: 4px;
}
.fb-module-chip .nm {
    color: #e2e8f0 !important;
    font-size: 12px;
    font-weight: 900;
}
.fb-content-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin: 16px 0;
}
@media (max-width: 900px) {
    .fb-content-grid { grid-template-columns: 1fr; }
}
.fb-content-card {
    border-radius: 20px;
    padding: 18px 20px;
    background: linear-gradient(145deg, rgba(16,20,40,.92), rgba(10,12,26,.96));
    border: 1px solid rgba(255,255,255,.07);
    min-height: 120px;
}
.fb-content-card.focus {
    border-color: rgba(134,239,172,.35);
    box-shadow: 0 0 32px rgba(34,197,94,.1);
    grid-column: 1 / -1;
}
.fb-content-card .head {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.fb-content-card .tag {
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
    padding: 4px 8px;
    border-radius: 8px;
    color: #f0fdf4 !important;
}
.fb-content-card .title {
    color: #ffe7a3 !important;
    font-size: 15px;
    font-weight: 1000;
}
.fb-content-card .body {
    color: #cbd5e1 !important;
    font-size: 13px;
    line-height: 1.65;
    max-height: 280px;
    overflow-y: auto;
}
.fb-content-card.focus .body {
    max-height: none;
    font-size: 14px;
}
.fb-viral-panel {
    display: flex;
    gap: 24px;
    align-items: center;
    flex-wrap: wrap;
    border-radius: 22px;
    padding: 22px 26px;
    margin: 18px 0;
    background: linear-gradient(135deg, rgba(22,16,48,.9), rgba(8,20,16,.92));
    border: 1px solid rgba(168,85,247,.2);
}
.fb-viral-ring-wrap {
    position: relative;
    width: 128px;
    height: 128px;
    flex-shrink: 0;
}
.fb-viral-ring {
    width: 128px;
    height: 128px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 40px rgba(34,197,94,.15);
}
.fb-viral-ring .inner {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    background: rgba(8,12,24,.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.fb-viral-ring .score {
    color: #86efac !important;
    font-size: 32px;
    font-weight: 1000;
    line-height: 1;
}
.fb-viral-ring .lbl {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-top: 4px;
}
.fb-viral-feedback {
    flex: 1;
    min-width: 220px;
}
.fb-viral-feedback h4 {
    color: #ffe7a3 !important;
    margin: 0 0 10px 0;
    font-size: 16px;
    font-weight: 1000;
}
.fb-viral-feedback .fb-body {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.6;
}
.fb-thumb-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 12px;
    margin-top: 14px;
}
.fb-thumb-card {
    border-radius: 18px;
    padding: 16px 18px;
    background: rgba(12,16,32,.8);
    border: 1px solid rgba(255,231,163,.12);
}
.fb-thumb-card .t {
    color: #ffe7a3 !important;
    font-size: 13px;
    font-weight: 1000;
    margin-bottom: 10px;
}
.fb-thumb-card .b {
    color: #94a3b8 !important;
    font-size: 12px;
    line-height: 1.55;
}
.fb-summary-card {
    border-radius: 22px;
    padding: 24px 28px;
    margin: 16px 0;
    background: linear-gradient(145deg, rgba(12,20,38,.95), rgba(8,16,12,.96));
    border: 1px solid rgba(134,239,172,.2);
}
.fb-summary-card .fb-body {
    color: #e2e8f0 !important;
    font-size: 15px;
    line-height: 1.7;
}
.fb-export-bar {
    border-radius: 18px;
    padding: 16px 20px;
    margin: 12px 0;
    background: rgba(15,23,42,.6);
    border: 1px dashed rgba(168,85,247,.25);
    text-align: center;
}
.fb-export-bar .t {
    color: #c084fc !important;
    font-size: 12px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.fb-mesh-intro {
    border-radius: 22px;
    padding: 20px 24px;
    margin-bottom: 18px;
    background: linear-gradient(135deg, rgba(12,18,38,.92), rgba(8,14,28,.96));
    border: 1px solid rgba(168,85,247,.14);
}
.fb-usage-bar {
    height: 8px;
    border-radius: 999px;
    background: rgba(255,255,255,.08);
    overflow: hidden;
    margin-top: 10px;
}
.fb-usage-bar > span {
    display: block;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #22c55e, #a855f7);
}
.fb-workflow {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 14px 0 20px 0;
}
.fb-workflow-step {
    flex: 1;
    min-width: 120px;
    border-radius: 14px;
    padding: 12px 14px;
    background: rgba(12,16,32,.65);
    border: 1px solid rgba(255,255,255,.06);
    text-align: center;
}
.fb-workflow-step.done {
    border-color: rgba(34,197,94,.35);
    background: rgba(6,78,59,.2);
}
.fb-workflow-step.active {
    border-color: rgba(168,85,247,.4);
    box-shadow: 0 0 20px rgba(168,85,247,.15);
}
.fb-workflow-step .num {
    color: #64748b !important;
    font-size: 10px;
    font-weight: 1000;
}
.fb-workflow-step .lbl {
    color: #e2e8f0 !important;
    font-size: 12px;
    font-weight: 900;
    margin-top: 4px;
}
.fb-output-zone {
    border-radius: 26px;
    padding: 8px 4px 24px 4px;
    margin-top: 8px;
    border: 1px solid rgba(134,239,172,.1);
    background: rgba(6,10,20,.35);
}
.fb-odds-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 18px 0;
}
@media (max-width: 1000px) {
    .fb-odds-grid { grid-template-columns: repeat(2, 1fr); }
}
.fb-odds-metric {
    border-radius: 18px;
    padding: 16px 18px;
    background: linear-gradient(145deg, rgba(14,18,36,.95), rgba(8,12,24,.98));
    border: 1px solid rgba(255,255,255,.07);
}
.fb-odds-metric.highlight {
    border-color: rgba(34,197,94,.4);
    box-shadow: 0 0 28px rgba(34,197,94,.12);
}
.fb-odds-metric.warn {
    border-color: rgba(234,179,8,.35);
}
.fb-odds-metric .k {
    color: #86efac !important;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .1em;
    text-transform: uppercase;
}
.fb-odds-metric .v {
    color: #f0fdf4 !important;
    font-size: 22px;
    font-weight: 1000;
    margin-top: 8px;
}
.fb-odds-metric .s {
    color: #64748b !important;
    font-size: 11px;
    margin-top: 4px;
}
.fb-odds-verdict {
    border-radius: 20px;
    padding: 18px 22px;
    margin: 12px 0;
    font-size: 14px;
    font-weight: 800;
    line-height: 1.5;
}
.fb-odds-verdict.positive {
    background: rgba(6,78,59,.35);
    border: 1px solid rgba(34,197,94,.35);
    color: #86efac !important;
}
.fb-odds-verdict.neutral {
    background: rgba(30,27,75,.4);
    border: 1px solid rgba(168,85,247,.25);
    color: #c4b5fd !important;
}
.fb-odds-market-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-top: 10px;
}
.fb-odds-market-table th {
    color: #c084fc !important;
    text-align: left;
    padding: 8px;
    border-bottom: 1px solid rgba(168,85,247,.2);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: .08em;
}
.fb-odds-market-table td {
    color: #e2e8f0 !important;
    padding: 10px 8px;
    border-bottom: 1px solid rgba(255,255,255,.04);
}
.fb-odds-market-table tr:hover td {
    background: rgba(168,85,247,.08);
}
.fb-prediction-card {
    border-radius: 20px;
    padding: 20px 22px;
    margin-bottom: 16px;
    background: linear-gradient(135deg, rgba(22,16,48,.9), rgba(10,20,16,.92));
    border: 1px solid rgba(255,231,163,.14);
}
.fb-pred-bars {
    display: flex;
    gap: 10px;
    margin-top: 14px;
}
.fb-pred-bar {
    flex: 1;
    text-align: center;
}
.fb-pred-bar .bar {
    height: 6px;
    border-radius: 999px;
    background: rgba(255,255,255,.1);
    margin-top: 8px;
    overflow: hidden;
}
.fb-pred-bar .fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #6366f1, #22c55e);
}
.fb-pred-bar .pct {
    color: #ffe7a3 !important;
    font-size: 18px;
    font-weight: 1000;
}
.fb-pred-bar .nm {
    color: #94a3b8 !important;
    font-size: 11px;
    font-weight: 800;
    margin-top: 4px;
}
.fb-legal {
    border-radius: 14px;
    padding: 12px 16px;
    margin: 12px 0;
    background: rgba(15,23,42,.5);
    border: 1px solid rgba(148,163,184,.15);
    color: #94a3b8 !important;
    font-size: 12px;
    line-height: 1.5;
}
.fb-plan-current-banner {
    border-radius: 24px;
    padding: 22px 26px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, rgba(22,101,52,.35), rgba(76,29,149,.25));
    border: 1px solid rgba(134,239,172,.28);
    box-shadow: 0 20px 50px rgba(0,0,0,.25);
}
.fb-plan-current-banner .plan-name {
    color: #f0fdf4 !important;
    font-size: 28px;
    font-weight: 1000;
}
.fb-plan-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin: 18px 0;
}
@media (max-width: 1000px) {
    .fb-plan-grid { grid-template-columns: 1fr; }
}
.fb-plan-card {
    border-radius: 24px;
    padding: 22px 22px 18px 22px;
    min-height: 340px;
    display: flex;
    flex-direction: column;
    background: linear-gradient(160deg, rgba(14,16,36,.95), rgba(8,10,24,.98));
    border: 1px solid rgba(255,255,255,.08);
    position: relative;
}
.fb-plan-card.current {
    border-color: rgba(34,197,94,.45);
    box-shadow: 0 0 40px rgba(34,197,94,.12);
}
.fb-plan-card.recommended {
    border-color: rgba(168,85,247,.45);
    box-shadow: 0 0 36px rgba(168,85,247,.18);
}
.fb-plan-card .tier-badge {
    display: inline-flex;
    padding: 5px 11px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 1000;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.fb-plan-card.starter .tier-badge {
    background: rgba(59,130,246,.25);
    color: #93c5fd !important;
}
.fb-plan-card.pro .tier-badge {
    background: rgba(168,85,247,.3);
    color: #e9d5ff !important;
}
.fb-plan-card.elite .tier-badge {
    background: rgba(255,231,163,.15);
    color: #ffe7a3 !important;
}
.fb-plan-card .price {
    color: #f0fdf4 !important;
    font-size: 26px;
    font-weight: 1000;
    letter-spacing: -.5px;
}
.fb-plan-card .desc {
    color: #94a3b8 !important;
    font-size: 13px;
    line-height: 1.55;
    margin: 10px 0 14px 0;
    flex: 1;
}
.fb-plan-limits {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}
.fb-plan-limits span {
    font-size: 11px;
    font-weight: 800;
}
.fb-plan-highlights {
    list-style: none;
    padding: 0;
    margin: 0 0 8px 0;
}
.fb-plan-highlights li {
    color: #cbd5e1 !important;
    font-size: 12px;
    font-weight: 700;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,.04);
}
.fb-plan-highlights li::before {
    content: "✓ ";
    color: #86efac !important;
    font-weight: 1000;
}
.fb-plan-ribbon {
    position: absolute;
    top: 14px;
    right: 14px;
    padding: 4px 10px;
    border-radius: 8px;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: #fff !important;
    font-size: 10px;
    font-weight: 1000;
}
"""


def inject_football_ui_css() -> None:
    inject_css(FOOTBALL_UI_CSS)


def render_command_hero(title: str, subtitle: str, plan_label: str, api_line: str) -> None:
    st.markdown(
        f"""
<div class="fb-command-hero">
    <div class="fb-scanline">Football Intelligence · Live Data Mesh</div>
    <div class="fb-command-title">{html.escape(title)}</div>
    <div class="fb-command-sub">{html.escape(subtitle)}</div>
    <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap;">
        <span class="fb-league-chip">Plan <strong>{html.escape(plan_label)}</strong></span>
        <span class="fb-league-chip">{html.escape(api_line)}</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_row(stats: list[tuple[str, str, str]]) -> None:
    cards = []
    for label, value, hint in stats:
        cards.append(
            f"""
<div class="fb-stat-card">
    <div class="lbl">{html.escape(label)}</div>
    <div class="val">{html.escape(value)}</div>
    <div class="hint">{html.escape(hint)}</div>
</div>
            """
        )
    st.markdown(
        f'<div class="fb-stat-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str = "") -> None:
    sub = f'<p class="fb-panel-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
<div class="fb-panel" style="padding-bottom:8px;margin-bottom:12px;">
    <div class="fb-panel-title">{html.escape(title)}</div>
    {sub}
</div>
        """,
        unsafe_allow_html=True,
    )


def parse_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    teams = fixture.get("teams") or {}
    goals = fixture.get("goals") or {}
    meta = fixture.get("fixture") or {}
    league = fixture.get("league") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    status = (meta.get("status") or {}).get("short") or "NS"
    home_goals = goals.get("home")
    away_goals = goals.get("away")
    if home_goals is not None and away_goals is not None:
        score = f"{home_goals} : {away_goals}"
    elif status in ("NS", "TBD"):
        score = "vs"
    else:
        score = status
    date_raw = str(meta.get("date") or "")
    date_show = date_raw[11:16] if "T" in date_raw else date_raw[:10]
    if date_raw and "T" in date_raw:
        date_show = f"{date_raw[:10]} · {date_raw[11:16]}"
    return {
        "fixture_id": meta.get("id"),
        "home": home.get("name") or "Home",
        "away": away.get("name") or "Away",
        "home_logo": home.get("logo") or "",
        "away_logo": away.get("logo") or "",
        "score": score,
        "status": status,
        "league": league.get("name") or "",
        "country": league.get("country") or "",
        "date": date_show,
        "live": status in ("1H", "2H", "HT", "ET", "P", "LIVE"),
    }


def _status_class(status: str) -> str:
    if status in ("1H", "2H", "HT", "ET", "P", "LIVE"):
        return "live"
    if status == "FT":
        return "ft"
    return "ns"


def render_fixture_cards(fixtures: list[dict[str, Any]], *, empty_msg: str = "Keine Spiele geladen.") -> None:
    if not fixtures:
        st.markdown(f'<div class="fb-empty">{html.escape(empty_msg)}</div>', unsafe_allow_html=True)
        return
    cards = []
    for raw in fixtures:
        f = parse_fixture(raw)
        live_cls = " live" if f["live"] else ""
        st_cls = _status_class(f["status"])
        cards.append(
            f"""
<div class="fb-fixture-card{live_cls}">
    <div class="fb-fixture-league">{html.escape(f['league'] or 'Match')}
        <span class="fb-fixture-date">{html.escape(f['date'])}</span>
    </div>
    <div class="fb-fixture-teams">
        <div class="fb-team">{html.escape(f['home'])}</div>
        <div class="fb-score">{html.escape(str(f['score']))}</div>
        <div class="fb-team">{html.escape(f['away'])}</div>
    </div>
    <span class="fb-status-pill {st_cls}">{html.escape(f['status'])}</span>
</div>
            """
        )
    st.markdown(
        f'<div class="fb-fixture-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_team_results(teams: list[dict[str, Any]]) -> None:
    if not teams:
        return
    blocks = []
    for row in teams[:12]:
        team = row.get("team") or {}
        name = team.get("name") or "Team"
        country = row.get("country") or team.get("country") or ""
        logo = team.get("logo") or ""
        tid = team.get("id") or ""
        logo_html = (
            f'<img src="{html.escape(logo)}" alt="" />' if logo else "<div style='width:36px'></div>"
        )
        blocks.append(
            f"""
<div class="fb-team-pick">
    {logo_html}
    <div>
        <div class="name">{html.escape(name)}</div>
        <div class="meta">ID {html.escape(str(tid))} · {html.escape(str(country))}</div>
    </div>
</div>
            """
        )
    st.markdown("".join(blocks), unsafe_allow_html=True)


def render_league_results(leagues: list[dict[str, Any]]) -> None:
    if not leagues:
        return
    chips = []
    for row in leagues[:12]:
        league = row.get("league") or {}
        lid = league.get("id") or ""
        name = league.get("name") or "Liga"
        country = league.get("country") or ""
        chips.append(
            f'<span class="fb-league-chip"><strong>{html.escape(name)}</strong>'
            f' <small>{html.escape(str(country))}</small></span>'
        )
    st.markdown(f'<div class="fb-chip-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_popular_leagues() -> None:
    chips = []
    for lg in POPULAR_LEAGUES:
        chips.append(
            f'<span class="fb-league-chip"><strong>{html.escape(lg["name"])}</strong>'
            f' <small>{html.escape(lg["country"])}</small></span>'
        )
    st.markdown(f'<div class="fb-chip-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_standings_table(standings_payload: list[dict[str, Any]], *, limit: int = 15) -> None:
    if not standings_payload:
        st.markdown('<div class="fb-empty">Keine Tabellendaten.</div>', unsafe_allow_html=True)
        return
    try:
        groups = (standings_payload[0].get("league") or {}).get("standings") or []
        rows = groups[0] if groups else []
    except (IndexError, TypeError, KeyError):
        st.markdown('<div class="fb-empty">Tabellenformat nicht lesbar.</div>', unsafe_allow_html=True)
        return
    if not rows:
        st.markdown('<div class="fb-empty">Leere Tabelle.</div>', unsafe_allow_html=True)
        return

    trs = []
    for entry in rows[:limit]:
        team = (entry.get("team") or {}).get("name") or "—"
        pts = entry.get("points", 0)
        played = (entry.get("all") or {}).get("played", 0)
        rank = entry.get("rank", "")
        trs.append(
            f"<tr><td>{html.escape(str(rank))}</td>"
            f"<td>{html.escape(team)}</td>"
            f"<td>{html.escape(str(played))}</td>"
            f"<td><strong>{html.escape(str(pts))}</strong></td></tr>"
        )
    st.markdown(
        f"""
<div class="fb-standings-wrap">
<table class="fb-standings">
<thead><tr><th>#</th><th>Team</th><th>Sp</th><th>Pkt</th></tr></thead>
<tbody>{"".join(trs)}</tbody>
</table>
</div>
        """,
        unsafe_allow_html=True,
    )


# --- AI Content Engine ---

PACKAGE_MODULES: list[dict[str, str]] = [
    {"title": "TikTok Hook", "icon": "⚡", "tag": "TikTok", "color": "#fe2c55"},
    {"title": "TikTok Caption", "icon": "🎬", "tag": "TikTok", "color": "#fe2c55"},
    {"title": "Instagram Caption", "icon": "📸", "tag": "Instagram", "color": "#e1306c"},
    {"title": "Twitter Thread", "icon": "𝕏", "tag": "X", "color": "#38bdf8"},
    {"title": "YouTube Title", "icon": "▶", "tag": "YouTube", "color": "#ef4444"},
    {"title": "YouTube Description", "icon": "📝", "tag": "YouTube", "color": "#ef4444"},
    {"title": "Thumbnail Prompt", "icon": "🖼", "tag": "Visual", "color": "#a855f7"},
    {"title": "Hashtags", "icon": "#", "tag": "Reach", "color": "#22c55e"},
    {"title": "CTA", "icon": "🎯", "tag": "Convert", "color": "#f59e0b"},
    {"title": "Posting Strategy", "icon": "📅", "tag": "Strategy", "color": "#6366f1"},
]

_MODULE_LOOKUP = {m["title"]: m for m in PACKAGE_MODULES}


def rich_text_html(text: str, *, max_len: int | None = None) -> str:
    raw = (text or "").strip()
    if not raw:
        return '<span style="color:#64748b">Kein Inhalt generiert.</span>'
    if max_len and len(raw) > max_len:
        raw = raw[: max_len - 1].rsplit(" ", 1)[0] + "…"
    escaped = html.escape(raw)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return escaped.replace("\n\n", "<br><br>").replace("\n", "<br>")


def split_markdown_sections(text: str) -> dict[str, str]:
    """Split AI output by ## headers (thumbnails etc.)."""
    sections: dict[str, str] = {}
    current_title = "Overview"
    current_lines: list[str] = []

    for line in (text or "").splitlines():
        if line.strip().startswith("##"):
            if current_lines:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line.strip().lstrip("#").strip() or "Section"
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_title] = "\n".join(current_lines).strip()
    if not sections and text:
        sections["Overview"] = text.strip()
    return sections


def render_ai_module_preview() -> None:
    chips = []
    for mod in PACKAGE_MODULES:
        chips.append(
            f'<div class="fb-module-chip">'
            f'<div class="ico">{html.escape(mod["icon"])}</div>'
            f'<div class="nm">{html.escape(mod["title"])}</div></div>'
        )
    st.markdown(
        f"""
<div class="fb-panel-title" style="margin-bottom:12px;">Content Matrix</div>
<p class="fb-panel-sub">10+ Module pro Matchday Package</p>
<div class="fb-module-grid">{"".join(chips)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_match_banner(
    club: str,
    opponent: str,
    platform: str,
    tone: str,
    *,
    badge: str = "Matchday Package",
) -> None:
    st.markdown(
        f"""
<div class="fb-match-banner">
    <div class="fb-scanline">{html.escape(badge)}</div>
    <div style="margin-top:14px;">
        <span class="club">{html.escape(club)}</span>
        <span class="vs">VS</span>
        <span class="club">{html.escape(opponent)}</span>
    </div>
    <div class="meta">
        <span class="fb-league-chip">{html.escape(platform)}</span>
        <span class="fb-league-chip">Tone · <strong>{html.escape(tone)}</strong></span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_output(text: str, club: str, opponent: str) -> None:
    render_match_banner(club, opponent, "Summary", "Starter", badge="AI Match Summary")
    st.markdown(
        f"""
<div class="fb-summary-card">
    <div class="fb-scanline" style="margin-bottom:12px;">Kurzfassung · Starter</div>
    <div class="fb-body">{rich_text_html(text)}</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _content_card_html(
    title: str,
    body: str,
    *,
    focus: bool = False,
    preview_len: int | None = None,
) -> str:
    meta = _MODULE_LOOKUP.get(title, {"icon": "✦", "tag": "Content", "color": "#a855f7"})
    cls = "fb-content-card focus" if focus else "fb-content-card"
    body_html = rich_text_html(body, max_len=preview_len if not focus else None)
    return f"""
<div class="{cls}">
    <div class="head">
        <span class="tag" style="background:{html.escape(meta['color'])}33;
            border:1px solid {html.escape(meta['color'])}55">{html.escape(meta['tag'])}</span>
        <span class="title">{html.escape(meta['icon'])} {html.escape(title)}</span>
    </div>
    <div class="body">{body_html}</div>
</div>
    """


def render_content_package(
    sections: dict[str, str],
    *,
    key_prefix: str = "fb_pkg",
) -> None:
    filled = {k: v.strip() for k, v in sections.items() if (v or "").strip()}
    if not filled:
        st.markdown('<div class="fb-empty">Keine Inhalte im Package.</div>', unsafe_allow_html=True)
        return

    titles = list(filled.keys())
    default_focus = titles[0]
    focus = st.selectbox(
        "Fokus-Modul",
        titles,
        key=f"{key_prefix}_focus",
        label_visibility="collapsed",
    )

    cards = [_content_card_html(focus, filled[focus], focus=True)]
    for title in titles:
        if title == focus:
            continue
        cards.append(_content_card_html(title, filled[title], preview_len=220))

    st.markdown(f'<div class="fb-content-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="fb-scanline" style="margin:14px 0 8px 0;">Einzeldownloads</div>', unsafe_allow_html=True)
    cols = st.columns(min(3, len(titles)))
    for i, title in enumerate(titles):
        with cols[i % len(cols)]:
            content = filled[title]
            st.download_button(
                f"↓ {title}",
                data=content.encode("utf-8"),
                file_name=f"mabyte_{title.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"{key_prefix}_dl_{title}",
                width="stretch",
            )


def render_viral_intelligence(score: int, feedback: str) -> None:
    score = max(0, min(100, int(score)))
    ring_color = (
        "#22c55e" if score >= 75 else "#eab308" if score >= 50 else "#ef4444"
    )
    st.markdown(
        f"""
<div class="fb-viral-panel">
    <div class="fb-viral-ring-wrap">
        <div class="fb-viral-ring" style="background:conic-gradient(
            {ring_color} {score}%,
            rgba(255,255,255,.08) 0
        );">
            <div class="inner">
                <div class="score">{score}</div>
                <div class="lbl">Viral</div>
            </div>
        </div>
    </div>
    <div class="fb-viral-feedback">
        <h4>Viral Intelligence</h4>
        <div class="fb-body">{rich_text_html(feedback)}</div>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100.0)


def render_thumbnail_package(text: str) -> None:
    render_section_header("Thumbnail Intelligence", "YouTube · TikTok · Instagram Covers")
    parts = split_markdown_sections(text)
    if len(parts) <= 1 and "Overview" in parts:
        parts = split_markdown_sections(
            text.replace("## YouTube Thumbnail", "\n## YouTube\n").replace(
                "## TikTok Cover", "\n## TikTok\n"
            )
        )
    cards = []
    for title, body in parts.items():
        if not body.strip():
            continue
        cards.append(
            f"""
<div class="fb-thumb-card">
    <div class="t">{html.escape(title)}</div>
    <div class="b">{rich_text_html(body, max_len=600)}</div>
</div>
            """
        )
    if cards:
        st.markdown(f'<div class="fb-thumb-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="fb-summary-card"><div class="fb-body">{rich_text_html(text)}</div></div>',
            unsafe_allow_html=True,
        )


def render_export_bar(title: str = "Full Package Export") -> None:
    st.markdown(
        f"""
<div class="fb-export-bar">
    <div class="t">{html.escape(title)}</div>
    <div style="color:#64748b;font-size:12px;">Komplettes Paket als .txt</div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_mesh_usage_bar(used: int, limit: int) -> None:
    pct = min(100, int((used / limit) * 100)) if limit > 0 else 0
    st.markdown(
        f"""
<div class="fb-mesh-intro">
    <div class="fb-scanline">MaByte Data Layer</div>
    <div class="fb-panel-title" style="margin-top:8px;">Live Intelligence</div>
    <p class="fb-panel-sub">Datenabfragen heute · {used:,} / {limit:,} · intelligent gecacht</p>
    <div class="fb-usage-bar"><span style="width:{pct}%"></span></div>
</div>
        """.replace(",", "."),
        unsafe_allow_html=True,
    )


def render_workflow_pipeline(steps: list[tuple[str, str]]) -> None:
    """steps: (label, status) status in done|active|pending"""
    blocks = []
    for i, (label, status) in enumerate(steps, 1):
        cls = status if status in ("done", "active") else ""
        blocks.append(
            f'<div class="fb-workflow-step {cls}">'
            f'<div class="num">Schritt {i}</div>'
            f'<div class="lbl">{html.escape(label)}</div></div>'
        )
    st.markdown(f'<div class="fb-workflow">{"".join(blocks)}</div>', unsafe_allow_html=True)


def render_saas_legal(text: str) -> None:
    st.markdown(
        f'<div class="fb-legal">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def render_output_zone_start() -> None:
    st.markdown('<div class="fb-output-zone">', unsafe_allow_html=True)


def render_output_zone_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_odds_dashboard(result: dict[str, Any], note: str = "") -> None:
    value_cls = "positive" if result.get("is_value_bet") else "neutral"
    verdict = (
        "Positiver mathematischer Edge erkannt — keine Wettempfehlung."
        if result.get("is_value_bet")
        else "Kein klarer Value Bet bei dieser Schätzung."
    )
    metrics = [
        ("Möglicher Gewinn", f"{result['profit']:.2f}", ""),
        ("Auszahlung", f"{result['payout']:.2f}", "bei Sieg"),
        ("Break-even", f"{result['break_even_probability_pct']:.1f}%", "Mindest-Wahrscheinlichkeit"),
        ("Implizite Quote", f"{result['implied_probability_pct']:.1f}%", "vom Markt"),
        ("Edge", f"{result['edge_pct']:+.2f}%", "deine Schätzung vs. Markt"),
        ("Erwartungswert", f"{result['expected_value']:+.2f}", "EV pro Einsatz"),
        ("Value Bet", "Ja" if result.get("is_value_bet") else "Nein", ""),
        ("Risiko", str(result.get("risk_level", "—")), "Modell"),
    ]
    cards = []
    for i, (k, v, s) in enumerate(metrics):
        extra = " highlight" if k == "Value Bet" and result.get("is_value_bet") else ""
        extra = extra or (" warn" if k == "Risiko" and result.get("risk_level") == "Hoch" else "")
        cards.append(
            f'<div class="fb-odds-metric{extra}">'
            f'<div class="k">{html.escape(k)}</div>'
            f'<div class="v">{html.escape(v)}</div>'
            f'<div class="s">{html.escape(s)}</div></div>'
        )
    st.markdown(f'<div class="fb-odds-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="fb-odds-verdict {value_cls}">{html.escape(verdict)}</div>',
        unsafe_allow_html=True,
    )
    if note.strip():
        st.markdown(
            f'<span class="fb-league-chip">Match · <strong>{html.escape(note.strip())}</strong></span>',
            unsafe_allow_html=True,
        )


def render_odds_market_table(markets: list[dict[str, Any]], *, max_rows: int = 16) -> None:
    if not markets:
        st.markdown(
            '<div class="fb-empty">Keine Live-Marktdaten für dieses Spiel verfügbar.</div>',
            unsafe_allow_html=True,
        )
        return
    rows = []
    for m in markets[:max_rows]:
        rows.append(
            f"<tr><td>{html.escape(m.get('bookmaker', ''))}</td>"
            f"<td>{html.escape(m.get('market', ''))}</td>"
            f"<td>{html.escape(m.get('selection', ''))}</td>"
            f"<td><strong>{m.get('odd', 0):.2f}</strong></td></tr>"
        )
    st.markdown(
        f"""
<div class="fb-panel" style="margin-top:12px;">
    <div class="fb-panel-title">Live Marktquoten</div>
    <p class="fb-panel-sub">Elite Data Feed · zur Analyse</p>
    <table class="fb-odds-market-table">
    <thead><tr><th>Anbieter</th><th>Markt</th><th>Auswahl</th><th>Quote</th></tr></thead>
    <tbody>{"".join(rows)}</tbody>
    </table>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_prediction_card(insights: dict[str, Any]) -> None:
    home = insights.get("home") or "Home"
    away = insights.get("away") or "Away"
    h = insights.get("home_pct")
    d = insights.get("draw_pct")
    a = insights.get("away_pct")

    def _bar(label: str, pct: float | None) -> str:
        w = int(pct or 0)
        return f"""
<div class="fb-pred-bar">
    <div class="nm">{html.escape(label)}</div>
    <div class="pct">{html.escape(str(pct) if pct is not None else "—")}{"%" if pct is not None else ""}</div>
    <div class="bar"><div class="fill" style="width:{w}%"></div></div>
</div>
        """

    advice = insights.get("advice") or ""
    comment = insights.get("winner_comment") or ""
    st.markdown(
        f"""
<div class="fb-prediction-card">
    <div class="fb-scanline">Elite Match Intelligence</div>
    <div class="fb-panel-title" style="margin-top:8px;">{html.escape(home)} vs {html.escape(away)}</div>
    <div class="fb-pred-bars">{_bar("Heim", h)}{_bar("Unentschieden", d)}{_bar("Auswärts", a)}</div>
    {"<p class='fb-panel-sub' style='margin-top:14px'>" + html.escape(advice) + "</p>" if advice else ""}
    {"<p class='fb-panel-sub'>" + html.escape(comment) + "</p>" if comment else ""}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_pipeline_header() -> None:
    render_workflow_pipeline([
        ("Match Setup", "done"),
        ("AI Generierung", "done"),
        ("Viral Score", "active"),
        ("Export", "pending"),
    ])


def _plan_tier_class(plan_key: str) -> str:
    if "elite" in plan_key:
        return "elite"
    if "pro" in plan_key:
        return "pro"
    return "starter"


def render_current_plan_banner(
    plan_label: str,
    plan_key: str,
    *,
    ai_used: int,
    ai_limit: str | int,
    api_used: int,
    api_limit: int,
    live_api: bool,
) -> None:
    ai_txt = f"{ai_used} / {ai_limit}"
    api_txt = (
        f"{api_used:,} / {api_limit:,} Datenabfragen heute".replace(",", ".")
        if live_api
        else "Live-Daten nach Upgrade"
    )
    st.markdown(
        f"""
<div class="fb-plan-current-banner">
    <div class="fb-scanline">Dein Abonnement</div>
    <div class="plan-name" style="margin-top:10px;">{html.escape(plan_label)}</div>
    <div class="meta" style="margin-top:12px;">
        <span class="fb-league-chip">AI · <strong>{html.escape(ai_txt)}</strong></span>
        <span class="fb-league-chip">{html.escape(api_txt)}</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_plan_card_html(
    plan_key: str,
    label: str,
    price: str,
    badge: str,
    description: str,
    highlights: list[str],
    *,
    daily_ai: int,
    daily_api: int,
    is_current: bool = False,
    recommended: bool = False,
) -> None:
    tier = _plan_tier_class(plan_key)
    classes = f"fb-plan-card {tier}"
    if is_current:
        classes += " current"
    if recommended and not is_current:
        classes += " recommended"
    ribbon = '<div class="fb-plan-ribbon">Empfohlen</div>' if recommended and not is_current else ""
    if is_current:
        ribbon = '<div class="fb-plan-ribbon" style="background:linear-gradient(135deg,#166534,#15803d)">Aktiv</div>'

    ai_show = f"{daily_ai:,}".replace(",", ".") if daily_ai < 9999 else "Unbegrenzt"
    api_show = f"{daily_api:,}".replace(",", ".")
    lim_chips = (
        f'<div class="fb-plan-limits">'
        f'<span class="fb-league-chip">{ai_show} AI / Tag</span>'
        f'<span class="fb-league-chip">{api_show} Daten / Tag</span>'
        f'</div>'
    )
    items = "".join(
        f"<li>{html.escape(str(h))}</li>" for h in (highlights or [])[:6]
    )
    st.markdown(
        f"""
<div class="{classes}">
    {ribbon}
    <span class="tier-badge">{html.escape(badge)}</span>
    <div class="price">{html.escape(label)}</div>
    <div style="color:#c084fc;font-size:14px;font-weight:1000;margin-top:4px;">{html.escape(price)}</div>
    <p class="desc">{html.escape(description)}</p>
    {lim_chips}
    <ul class="fb-plan-highlights">{items}</ul>
</div>
        """,
        unsafe_allow_html=True,
    )
