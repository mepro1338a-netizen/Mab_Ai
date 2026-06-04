"""Football AI V2 — page CSS."""
from __future__ import annotations

FOOTBALL_CSS = """
.fb2 { max-width: 1100px; margin: 0 auto; padding-bottom: 40px; }
.fb2-hero { margin-bottom: 20px; }
.fb2-hero h1 { margin: 0; font-size: 24px; font-weight: 800; color: #fafafa; letter-spacing: -.02em; }
.fb2-hero p { margin: 6px 0 0; font-size: 13px; color: #94a3b8; }
.fb2-nav { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
.fb2-chip {
  display: inline-flex; align-items: center; padding: 8px 14px; border-radius: 10px;
  font-size: 12px; font-weight: 600; text-decoration: none !important;
  color: #a1a1aa !important; background: rgba(24,24,27,.9);
  border: 1px solid rgba(255,255,255,.08); transition: all .12s ease;
}
.fb2-chip:hover { color: #e4e4e7 !important; border-color: rgba(139,92,246,.35); }
.fb2-chip.on {
  color: #fff !important; background: rgba(124,58,237,.22);
  border-color: rgba(139,92,246,.5); box-shadow: 0 0 0 1px rgba(139,92,246,.25);
}
.fb2-chip.live.on { border-color: rgba(34,197,94,.5); background: rgba(34,197,94,.12); }
.fb2-subnav { margin-bottom: 16px; }
.fb2-banner {
  font-size: 12px; color: #a78bfa; padding: 10px 14px; margin-bottom: 14px;
  border-radius: 10px; background: rgba(139,92,246,.08); border: 1px solid rgba(139,92,246,.2);
}
.fb2-empty {
  padding: 32px 20px; text-align: center; border-radius: 14px;
  border: 1px dashed rgba(255,255,255,.1); color: #94a3b8; font-size: 14px;
}
.fb2-gate {
  padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08);
  color: #94a3b8; font-size: 14px; line-height: 1.5;
}
.fb2-match {
  padding: 16px 18px; margin-bottom: 10px; border-radius: 14px;
  background: linear-gradient(155deg, rgba(24,24,27,.95), rgba(12,12,16,.98));
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 8px 24px rgba(0,0,0,.2);
}
.fb2-match.is-live { border-left: 4px solid #22c55e; }
.fb2-match-meta { font-size: 11px; color: #71717a; margin-bottom: 10px; }
.fb2-match-meta .lg { color: #a78bfa; font-weight: 600; }
.fb2-teams {
  display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center;
  margin-bottom: 10px;
}
.fb2-team { font-size: 15px; font-weight: 700; color: #f4f4f5; line-height: 1.25; }
.fb2-team.away { text-align: right; }
.fb2-vs { font-size: 12px; font-weight: 800; color: #52525b; text-align: center; }
.fb2-score { font-size: 18px; font-weight: 800; color: #fafafa; text-align: center; }
.fb2-row {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: 8px; margin-top: 8px;
}
.fb2-status {
  font-size: 10px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  padding: 4px 10px; border-radius: 999px; background: rgba(113,113,122,.2); color: #d4d4d8;
}
.fb2-status.live { background: rgba(34,197,94,.15); color: #4ade80; }
.fb2-odds { font-size: 12px; color: #94a3b8; font-weight: 500; }
.fb2-back {
  display: inline-flex; align-items: center; gap: 6px; margin-bottom: 16px;
  font-size: 13px; color: #a78bfa !important; cursor: pointer;
}
.fb2-analysis {
  border-radius: 16px; padding: 22px 20px; margin-bottom: 20px;
  background: linear-gradient(160deg, rgba(20,18,32,.98), rgba(9,9,11,.99));
  border: 1px solid rgba(139,92,246,.28);
  box-shadow: 0 16px 48px rgba(0,0,0,.35);
}
.fb2-analysis h2 { margin: 0 0 4px; font-size: 20px; color: #fafafa; font-weight: 800; }
.fb2-analysis .sub { font-size: 12px; color: #71717a; margin-bottom: 18px; }
.fb2-block { margin-bottom: 20px; }
.fb2-block h3 {
  font-size: 10px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase;
  color: #a78bfa; margin: 0 0 10px;
}
.fb2-prob { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
@media (max-width: 600px) { .fb2-prob { grid-template-columns: 1fr; } }
.fb2-prob-item { padding: 12px; border-radius: 10px; background: rgba(0,0,0,.25); border: 1px solid rgba(255,255,255,.06); }
.fb2-prob-item .lbl { font-size: 10px; color: #94a3b8; text-transform: uppercase; }
.fb2-prob-item .pct { font-size: 22px; font-weight: 800; color: #fafafa; margin-top: 4px; }
.fb2-bar { height: 4px; border-radius: 4px; background: rgba(255,255,255,.08); margin-top: 8px; overflow: hidden; }
.fb2-bar > span { display: block; height: 100%; background: linear-gradient(90deg, #7c3aed, #8b5cf6); border-radius: 4px; }
.fb2-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 700px) { .fb2-grid2 { grid-template-columns: 1fr; } }
.fb2-statbox {
  padding: 12px 14px; border-radius: 10px; background: rgba(0,0,0,.2);
  border: 1px solid rgba(255,255,255,.06); font-size: 13px; color: #e4e4e7;
}
.fb2-statbox .t { font-weight: 700; color: #fafafa; margin-bottom: 6px; }
.fb2-list { margin: 0; padding: 0; list-style: none; }
.fb2-list li {
  padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.05);
  font-size: 12px; color: #cbd5e1;
}
.fb2-list li:last-child { border-bottom: none; }
.fb2-summary {
  padding: 14px 16px; border-radius: 12px; background: rgba(124,58,237,.1);
  border: 1px solid rgba(139,92,246,.22); font-size: 13px; color: #e4e4e7; line-height: 1.55;
}
.fb2-summary p { margin: 0 0 10px; }
.fb2-summary p:last-child { margin: 0; }
.fb2-warn {
  padding: 16px; border-radius: 12px; background: rgba(39,39,42,.6);
  border: 1px solid rgba(255,255,255,.08); color: #94a3b8; font-size: 14px; line-height: 1.5;
}
"""
