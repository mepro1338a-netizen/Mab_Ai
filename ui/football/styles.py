"""Football AI V2 — page CSS."""
from __future__ import annotations

FOOTBALL_CSS = """
.fb2 {
  max-width: 1100px; width: 100%; margin: 0 auto; padding-bottom: 40px;
  overflow-x: hidden; box-sizing: border-box;
}
.fb2-hero { margin-bottom: 20px; }
.fb2-hero h1 { margin: 0; font-size: 24px; font-weight: 800; color: #fafafa; letter-spacing: -.02em; }
.fb2-hero p { margin: 6px 0 0; font-size: 13px; color: #94a3b8; }
.fb2-nav { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.fb2-subnav { margin-bottom: 16px; }
.fb2-banner {
  font-size: 12px; color: #a78bfa; padding: 10px 14px; margin-bottom: 14px;
  border-radius: 10px; background: rgba(139,92,246,.08); border: 1px solid rgba(139,92,246,.2);
}
.fb2-empty-note {
  font-size: 14px; color: #94a3b8; text-align: center; margin-bottom: 10px; line-height: 1.5;
}
.fb2-empty {
  padding: 32px 20px; text-align: center; border-radius: 14px;
  border: 1px dashed rgba(255,255,255,.1); color: #94a3b8; font-size: 14px; line-height: 1.5;
}
.fb2-gate {
  padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08);
  color: #94a3b8; font-size: 14px; line-height: 1.5;
}

.fb2-card-wrap { width: 100%; max-width: 100%; overflow: hidden; box-sizing: border-box; }
.fb2-match {
  padding: 14px 16px; border-radius: 14px;
  background: linear-gradient(155deg, rgba(24,24,27,.95), rgba(12,12,16,.98));
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 8px 24px rgba(0,0,0,.2);
  overflow: hidden; box-sizing: border-box;
}
.fb2-match.is-live {
  border-left: 4px solid #ef4444;
  background: linear-gradient(155deg, rgba(48,10,10,.55), rgba(12,12,16,.98));
  box-shadow: 0 0 0 1px rgba(239,68,68,.12), 0 8px 24px rgba(0,0,0,.25);
}
.fb2-match.is-ft { border-left: 4px solid #71717a; }

.fb2-match-meta { margin-bottom: 10px; min-width: 0; }
.fb2-league-meta {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 11px; color: #71717a; max-width: 100%; min-width: 0;
}
.fb2-league-meta .lg {
  color: #a78bfa; font-weight: 600;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.fb2-logo-box--sm { width: 18px; height: 18px; }
.fb2-logo-box--sm .fb2-league-logo {
  width: 16px; height: 16px; max-width: 16px; max-height: 16px;
}

.fb2-teams {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 8px; align-items: start; margin-bottom: 8px;
}
.fb2-team { min-width: 0; font-size: 14px; color: #f4f4f5; line-height: 1.25; }
.fb2-team.away { text-align: right; }
.fb2-team-head {
  display: flex; align-items: flex-start; gap: 7px; margin-bottom: 5px; min-width: 0;
}
.fb2-team.away .fb2-team-head { flex-direction: row-reverse; justify-content: flex-end; }
.fb2-logo-box {
  width: 32px; height: 32px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.fb2-logo {
  width: 28px; height: 28px; max-width: 28px; max-height: 28px;
  object-fit: contain; display: block;
}
.fb2-team-name {
  font-size: 13px; font-weight: 700; line-height: 1.3;
  overflow-wrap: anywhere; word-break: break-word; hyphens: auto; min-width: 0;
}
.fb2-stand-chip {
  display: inline-block; min-width: 118px; min-height: 20px; padding: 2px 8px;
  font-size: 10px; color: #94a3b8; font-weight: 600; margin-top: 2px;
  border-radius: 6px; background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06); box-sizing: border-box;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.fb2-stand-chip.away { margin-left: auto; text-align: right; }
.fb2-stand-chip.is-empty { visibility: hidden; border-color: transparent; background: transparent; }
.fb2-form-line {
  font-size: 10px; color: #71717a; letter-spacing: .06em; margin-top: 4px;
  min-height: 14px; line-height: 1.35; overflow-wrap: anywhere;
}
.fb2-form-line.is-empty { visibility: hidden; }

.fb2-mid {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 3px; min-width: 68px; max-width: 88px; padding: 0 2px; flex-shrink: 0;
}
.fb2-live-badge {
  font-size: 9px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase;
  color: #fecaca; background: rgba(239,68,68,.22);
  border: 1px solid rgba(239,68,68,.5); padding: 3px 9px; border-radius: 999px;
  line-height: 1;
}
.fb2-minute {
  font-size: 30px; font-weight: 900; color: #ef4444; line-height: 1;
  letter-spacing: -.02em;
}
.fb2-ft {
  font-size: 11px; font-weight: 800; letter-spacing: .14em;
  color: #fafafa; background: rgba(113,113,122,.35);
  padding: 3px 10px; border-radius: 6px; line-height: 1;
}
.fb2-kickoff {
  font-size: 22px; font-weight: 900; color: #fafafa; text-align: center; line-height: 1.1;
}
.fb2-kickoff--muted { font-size: 18px; color: #52525b; font-weight: 700; }
.fb2-score {
  font-size: 16px; font-weight: 800; color: #fafafa; text-align: center;
  white-space: nowrap; line-height: 1.2;
}
.fb2-score--live { font-size: 15px; font-weight: 800; color: #fecaca; }
.fb2-score--ft { font-size: 21px; font-weight: 900; color: #fafafa; letter-spacing: .04em; }

.fb2-row {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 8px; min-height: 22px; margin-top: 4px;
}
.fb2-status {
  font-size: 9px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  padding: 4px 10px; border-radius: 999px; background: rgba(113,113,122,.2); color: #d4d4d8;
}
.fb2-odds {
  font-size: 11px; color: #94a3b8; font-weight: 500;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%;
  text-align: right; flex: 1 1 auto; min-width: 0;
}

.fb2-card-actions {
  min-height: 44px; margin: 6px 0 14px; width: 100%; box-sizing: border-box;
}
.fb2-no-analysis {
  min-height: 44px; width: 100%; box-sizing: border-box;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: #52525b; font-weight: 500;
  border: 1px dashed rgba(255,255,255,.08); border-radius: 10px;
  background: rgba(0,0,0,.15);
}

.fb2-analysis {
  border-radius: 16px; padding: 22px 20px; margin-bottom: 20px;
  background: linear-gradient(160deg, rgba(20,18,32,.98), rgba(9,9,11,.99));
  border: 1px solid rgba(139,92,246,.28);
  box-shadow: 0 16px 48px rgba(0,0,0,.35);
  overflow-x: hidden; box-sizing: border-box; max-width: 100%;
}
.fb2-analysis h2 {
  margin: 0 0 6px; font-size: 20px; color: #fafafa; font-weight: 800;
  overflow-wrap: anywhere; word-break: break-word; line-height: 1.25;
}
.fb2-analysis .sub {
  font-size: 12px; color: #71717a; margin-bottom: 20px; line-height: 1.5;
  overflow-wrap: anywhere;
}
.fb2-block { margin-bottom: 22px; }
.fb2-block:last-child { margin-bottom: 0; }
.fb2-block h3 {
  font-size: 10px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
  color: #a78bfa; margin: 0 0 12px;
}
.fb2-prob { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.fb2-prob-item {
  padding: 12px; border-radius: 10px; background: rgba(0,0,0,.25);
  border: 1px solid rgba(255,255,255,.06); min-width: 0;
}
.fb2-prob-item .lbl { font-size: 10px; color: #94a3b8; text-transform: uppercase; }
.fb2-prob-item .pct { font-size: 22px; font-weight: 800; color: #fafafa; margin-top: 4px; }
.fb2-bar { height: 4px; border-radius: 4px; background: rgba(255,255,255,.08); margin-top: 8px; overflow: hidden; }
.fb2-bar > span { display: block; height: 100%; background: linear-gradient(90deg, #7c3aed, #8b5cf6); border-radius: 4px; }
.fb2-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.fb2-statbox {
  padding: 12px 14px; border-radius: 10px; background: rgba(0,0,0,.2);
  border: 1px solid rgba(255,255,255,.06); font-size: 13px; color: #e4e4e7;
  min-width: 0; overflow-wrap: anywhere;
}
.fb2-statbox .t { font-weight: 700; color: #fafafa; margin-bottom: 6px; }
.fb2-list { margin: 0; padding: 0; list-style: none; }
.fb2-list li {
  padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.05);
  font-size: 12px; color: #cbd5e1; overflow-wrap: anywhere;
}
.fb2-list li:last-child { border-bottom: none; }
.fb2-summary {
  padding: 14px 16px; border-radius: 12px; background: rgba(124,58,237,.1);
  border: 1px solid rgba(139,92,246,.22); font-size: 13px; color: #e4e4e7; line-height: 1.55;
  overflow-wrap: anywhere;
}
.fb2-summary p { margin: 0 0 10px; }
.fb2-summary p:last-child { margin: 0; }
.fb2-warn {
  padding: 16px; border-radius: 12px; background: rgba(39,39,42,.6);
  border: 1px solid rgba(255,255,255,.08); color: #94a3b8; font-size: 14px; line-height: 1.5;
}

@media (max-width: 600px) { .fb2-prob { grid-template-columns: 1fr; } }
@media (max-width: 700px) { .fb2-grid2 { grid-template-columns: 1fr; } }
@media (max-width: 430px) {
  .fb2-match { padding: 12px 12px; }
  .fb2-teams { gap: 6px; grid-template-columns: minmax(0, 1fr) 62px minmax(0, 1fr); }
  .fb2-mid { min-width: 58px; max-width: 62px; }
  .fb2-team-name { font-size: 12px; }
  .fb2-logo-box { width: 28px; height: 28px; }
  .fb2-logo { width: 24px; height: 24px; max-width: 24px; max-height: 24px; }
  .fb2-stand-chip { min-width: 96px; font-size: 9px; padding: 2px 6px; }
  .fb2-form-line { font-size: 9px; letter-spacing: .03em; }
  .fb2-minute { font-size: 26px; }
  .fb2-kickoff { font-size: 19px; }
  .fb2-score--ft { font-size: 18px; }
  .fb2-odds { font-size: 10px; white-space: normal; text-align: left; }
  .fb2-row { flex-direction: column; align-items: flex-start; }
  .fb2-analysis { padding: 16px 14px; border-radius: 12px; }
  .fb2-analysis h2 { font-size: 17px; }
}
@media (max-width: 375px) {
  .fb2-stand-chip { min-width: 88px; }
  .fb2-team-head { gap: 5px; }
}
@media (max-width: 320px) {
  .fb2-teams { grid-template-columns: minmax(0, 1fr) 54px minmax(0, 1fr); }
  .fb2-mid { min-width: 50px; max-width: 54px; }
  .fb2-minute { font-size: 22px; }
  .fb2-kickoff { font-size: 17px; }
  .fb2-stand-chip { min-width: 80px; }
}
"""
