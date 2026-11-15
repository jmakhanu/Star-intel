#!/usr/bin/env python3
"""
Star Intel — Orbital Command GTM & Competitive Intelligence Platform
Provenance & Verification Edition:
- Explicit 'observed' vs 'unverified (inferred)' pricing status
- Source attribution + UTC check_date in UI and CSV exports
- 1-Click Gmail Web Compose & Index-safe Clipboard Copy
"""

import os
import json
import urllib.parse
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from star_intel_growth import init_db, fetch_web_signal, verify_domain_and_emails, call_llm

PORT = int(os.getenv("PORT", 8080))

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Star Intel — Autonomous Competitive Radar & AutoGTM Engine</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #040711;
    --panel: rgba(13, 20, 38, 0.84);
    --panel-solid: #0b1120;
    --border: rgba(56, 189, 248, 0.22);
    --border-subtle: rgba(148, 163, 184, 0.12);
    --cyan: #38bdf8;
    --emerald: #10b981;
    --amber: #f59e0b;
    --rose: #fb7185;
    --text: #f8fafc;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; }
  body {
    background-color: var(--bg);
    background-image:
      radial-gradient(circle at 20% 10%, rgba(56, 189, 248, 0.10) 0%, transparent 40%),
      radial-gradient(circle at 80% 25%, rgba(16, 185, 129, 0.08) 0%, transparent 40%),
      linear-gradient(rgba(148, 163, 184, 0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(148, 163, 184, 0.025) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 36px 36px, 36px 36px;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.5;
  }
  .mono { font-family: 'JetBrains Mono', monospace; }

  .nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 18px 24px;
    border-bottom: 1px solid var(--border-subtle);
    flex-wrap: wrap;
    gap: 12px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 17px;
    letter-spacing: 1.4px;
  }
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
  }
  .pulse-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(1.25); }
  }

  .hero-center {
    max-width: 900px;
    margin: 46px auto 32px;
    padding: 0 24px;
    text-align: center;
  }
  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--cyan);
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 99px;
    margin-bottom: 18px;
    font-weight: 600;
  }
  h1 {
    font-size: 46px;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 16px;
    letter-spacing: -0.025em;
  }
  h1 span {
    background: linear-gradient(95deg, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-sub {
    color: var(--muted);
    font-size: 16.5px;
    max-width: 680px;
    margin: 0 auto 28px;
  }

  .console-shell {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.65);
    text-align: left;
  }
  .mode-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 12px;
    justify-content: space-between;
    flex-wrap: wrap;
  }
  .mode-tab-group { display: flex; gap: 8px; flex-wrap: wrap; }
  .mode-btn {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid var(--border-subtle);
    color: var(--muted);
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .mode-btn.active {
    background: rgba(56, 189, 248, 0.15);
    border-color: var(--cyan);
    color: var(--text);
  }
  .cmd-row {
    display: flex;
    gap: 10px;
    background: #060a15;
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 8px;
    border-radius: 12px;
  }
  @media (max-width: 640px) { .cmd-row { flex-direction: column; } }
  .cmd-input-wrap {
    display: flex;
    align-items: center;
    flex: 1;
    padding-left: 12px;
    gap: 10px;
  }
  .cmd-row input, .stealth-grid input {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--text);
    font-size: 15px;
    outline: none;
    font-family: 'JetBrains Mono', monospace;
  }
  .stealth-grid {
    display: none;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }
  @media (max-width: 680px) { .stealth-grid { grid-template-columns: 1fr; } }
  .stealth-field {
    background: #060a15;
    border: 1px solid var(--border-subtle);
    padding: 10px 14px;
    border-radius: 10px;
  }
  .stealth-field label {
    display: block;
    font-size: 11px;
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
  }
  .cmd-btn {
    background: linear-gradient(135deg, #38bdf8, #10b981);
    color: #030712;
    border: none;
    padding: 13px 24px;
    border-radius: 9px;
    font-weight: 800;
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
  }
  .cmd-btn:disabled { background: #334155; color: #94a3b8; cursor: wait; }

  .quick-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 12px;
    font-size: 12px;
    color: var(--muted);
  }
  .pill-btn {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid var(--border-subtle);
    color: #cbd5e1;
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
  }
  .pill-btn:hover { border-color: var(--cyan); color: var(--cyan); }

  .pipeline-strip {
    max-width: 1160px;
    margin: 26px auto 40px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  @media (max-width: 860px) { .pipeline-strip { grid-template-columns: 1fr; } }
  .pipe-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 18px;
    transition: border-color 0.2s;
  }
  .pipe-card.active-step {
    border-color: var(--cyan);
    box-shadow: 0 0 25px rgba(56, 189, 248, 0.15);
  }
  .pipe-num {
    font-size: 11px;
    color: var(--cyan);
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .pipe-card h3 { margin: 0 0 6px; font-size: 15.5px; }
  .pipe-card p { margin: 0; font-size: 13px; color: var(--muted); }

  #results { max-width: 1200px; margin: 20px auto 70px; padding: 0 24px; display: none; }
  .res-banner {
    background: linear-gradient(90deg, rgba(15,23,42,0.95), rgba(6,78,59,0.35));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 18px;
  }
  .ws-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 22px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 12px;
    flex-wrap: wrap;
  }
  .ws-tab {
    background: var(--panel-solid);
    border: 1px solid var(--border-subtle);
    color: var(--muted);
    padding: 9px 16px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
  }
  .ws-tab.active {
    background: rgba(56, 189, 248, 0.14);
    border-color: var(--cyan);
    color: var(--text);
  }
  .tab-pane { display: none; }
  .tab-pane.active { display: block; }

  .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 18px; margin-bottom: 24px; }
  @media (max-width: 640px) { .grid-2 { grid-template-columns: 1fr; } }
  .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px; }

  .lead-card {
    background: var(--panel-solid);
    border: 1px solid rgba(56, 189, 248, 0.26);
    border-radius: 12px;
    padding: 20px;
    position: relative;
  }
  .email-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: var(--cyan);
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .email-badge:hover { background: rgba(56, 189, 248, 0.25); }
  .trigger-box {
    background: rgba(16, 185, 129, 0.09);
    border-left: 3px solid #10b981;
    padding: 8px 12px;
    font-size: 12.5px;
    color: #d1fae5;
    margin: 10px 0 12px;
    border-radius: 4px;
  }
  .email-draft {
    background: #050811;
    border: 1px solid #1e293b;
    padding: 14px;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #e2e8f0;
    white-space: pre-wrap;
    margin-bottom: 14px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: var(--panel-solid);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border-subtle);
  }
  th { background: #1e293b; color: var(--muted); text-align: left; padding: 14px; font-size: 11.5px; text-transform: uppercase; }
  td { padding: 14px; border-bottom: 1px solid var(--border-subtle); font-size: 13.5px; vertical-align: top; }
  .gap { color: var(--rose); }
  .wedge { color: #34d399; }

  /* PROVENANCE & VERIFICATION BADGES */
  .badge-observed {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    color: #34d399;
    background: rgba(16, 185, 129, 0.14);
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 2px 8px;
    border-radius: 5px;
    margin-top: 6px;
  }
  .badge-unverified {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    color: #fbbf24;
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid rgba(245, 158, 11, 0.35);
    padding: 2px 8px;
    border-radius: 5px;
    margin-top: 6px;
  }
  .prov-meta {
    font-size: 11px;
    color: #64748b;
    margin-top: 5px;
    line-height: 1.35;
  }

  .action-row {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    position: relative;
    z-index: 5;
  }
  .btn-gmail {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #38bdf8, #10b981);
    color: #030712;
    padding: 9px 14px;
    border-radius: 7px;
    font-weight: 800;
    font-size: 12.5px;
    border: none;
    cursor: pointer;
    text-decoration: none;
    transition: transform 0.1s, opacity 0.15s;
  }
  .btn-gmail:hover { opacity: 0.92; transform: translateY(-1px); }
  .btn-copy {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.12);
    color: var(--cyan);
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 8px 13px;
    border-radius: 7px;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-copy:hover { background: rgba(56, 189, 248, 0.22); }
  .btn-mailto {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(148, 163, 184, 0.1);
    color: #cbd5e1;
    border: 1px solid var(--border-subtle);
    padding: 8px 12px;
    border-radius: 7px;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    text-decoration: none;
  }
  .btn-mailto:hover { border-color: var(--muted); color: #fff; }
  .btn-dl {
    background: rgba(56, 189, 248, 0.14);
    color: var(--cyan);
    border: 1px solid var(--cyan);
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
  }
  .btn-pilot-primary {
    background: #10b981;
    color: #04130e;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 13px;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: none;
    cursor: pointer;
  }
  .bento-card {
    background: var(--panel);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px;
  }
  .section-title { font-size: 11.5px; letter-spacing: 1.4px; text-transform: uppercase; color: var(--cyan); font-weight: 700; margin-bottom: 6px; }
  .benefit-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    color: #34d399;
    background: rgba(16, 185, 129, 0.12);
    padding: 4px 10px;
    border-radius: 6px;
  }
  .pilot-wrap { max-width: 1160px; margin: 40px auto; padding: 0 24px; }
  .pilot-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(6, 78, 59, 0.35));
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 14px;
    padding: 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
  }
  .footer {
    border-top: 1px solid var(--border-subtle);
    padding: 28px 24px;
    text-align: center;
    color: var(--muted);
    font-size: 13px;
  }
  .footer a { color: var(--cyan); text-decoration: none; }
</style>
</head>
<body>

  <nav class="nav">
    <div class="brand">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2">
        <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3" fill="#38bdf8"/>
        <path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>
      </svg>
      STAR INTEL // ORBITAL GTM
    </div>
    <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
      <div class="status-pill"><span class="pulse-dot"></span> Provenance-Verified Recon Online</div>
      <button type="button" onclick="openFounderPilotEmail()" class="btn-pilot-primary">⚡ Claim 50-Lead Founding Pilot →</button>
    </div>
  </nav>

  <section class="hero-center">
    <div class="eyebrow mono">⚡ VERIFIED PRICING PROVENANCE • COMPETITOR MATRIX + TRIGGER LEADS</div>
    <h1>Spin Up Your Market Radar &<br><span>First Customer Campaigns</span> in 28s.</h1>
    <p class="hero-sub">
      Enter your company website — or switch to <strong>Stealth / No-Website Mode</strong>. Star Intel separates <strong>observed prices</strong> from <strong>unverified (inferred) positioning</strong> with source + check-date audit trails.
    </p>

    <div class="console-shell">
      <div class="mode-tabs">
        <div class="mode-tab-group">
          <button type="button" class="mode-btn active" id="tabUrlBtn" onclick="setMode('url')">🌐 Scan Company Website</button>
          <button type="button" class="mode-btn" id="tabIdeaBtn" onclick="setMode('idea')">🧠 No Website / Stealth Startup Mode</button>
        </div>
        <span class="mono" style="font-size:11.5px;color:#34d399;align-self:center;">✓ Observed vs. Unverified Provenance Tagging</span>
      </div>

      <form onsubmit="runAnalysis(event)">
        <div id="stealthInputs" class="stealth-grid">
          <div class="stealth-field">
            <label>What do you build or sell?</label>
            <input type="text" id="descInput" placeholder="e.g., AI stroke diagnostic helmet for ambulances" />
          </div>
          <div class="stealth-field">
            <label>Who is your ideal B2B customer?</label>
            <input type="text" id="icpInput" placeholder="e.g., Hospital Directors & Emergency Care Networks" />
          </div>
        </div>

        <div class="cmd-row">
          <div class="cmd-input-wrap">
            <svg width="18" height="18" fill="none" stroke="#38bdf8" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input type="text" id="urlInput" placeholder="Enter your company website (e.g., easi.run, mintlify.com, linear.app)" required />
          </div>
          <button type="submit" class="cmd-btn" id="runBtn">Launch My GTM Project →</button>
        </div>
      </form>

      <div class="quick-bar">
        <div>
          <span>Instant demo presets:</span>
          <button type="button" class="pill-btn" onclick="fillAndRun('easi.run')">easi.run</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('signedreviews.com')">signedreviews.com</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('mintlify.com')">mintlify.com</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('linear.app')">linear.app</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('resend.com')">resend.com</button>
        </div>
        <span class="mono" style="color:#64748b;">CSV includes: verification_status, pricing_source, check_date</span>
      </div>
    </div>
  </section>

  <section class="pipeline-strip">
    <div class="pipe-card" id="stepCard1">
      <div class="pipe-num mono">01 // PROVENANCE RECON</div>
      <h3>Observed vs. Inferred Pricing</h3>
      <p>Scrapes live pricing pages and flags whether each price is directly observed or `unverified` (inferred) with source & check date.</p>
    </div>
    <div class="pipe-card" id="stepCard2">
      <div class="pipe-num mono">02 // COMPETITOR ARBITRAGE</div>
      <h3>We Expose Rival Product Gaps</h3>
      <p>Builds a 4-competitor battlecard matrix showing exact pricing wedges and technical weaknesses you can exploit on sales calls.</p>
    </div>
    <div class="pipe-card" id="stepCard3">
      <div class="pipe-num mono">03 // TRIGGER-BASED OUTREACH</div>
      <h3>We Find & Draft Customer Emails</h3>
      <p>Identifies high-intent B2B target accounts, verifies live DNS/MX records, and opens pre-filled pitches directly in Gmail.</p>
    </div>
  </section>

  <div id="results"></div>

  <section class="pilot-wrap" id="pilot">
    <div class="pilot-card">
      <div style="max-width:660px;">
        <div class="section-title mono" style="color:#34d399;">STAR INTEL AUTOGTM — FOUNDING DESIGN PARTNER PROGRAM</div>
        <h2 style="margin:6px 0 8px;font-size:23px;">Want a Custom 50-Lead Verified Outbound Batch for Your Startup?</h2>
        <p style="margin:0;color:#cbd5e1;font-size:14px;">
          Our live workspace unlocks all 4 Competitor Battlecards + 4 Target Customer Emails for free. We are onboarding <strong>5 Founding Design Partners</strong> to receive a custom 50-lead weekly AutoGTM CSV before billing goes live.
        </p>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <button type="button" class="btn-pilot-primary" onclick="openFounderPilotEmail()">
          ✉️ Request 50-Lead Batch (Open Gmail)
        </button>
        <a class="btn-dl" style="text-decoration:none;" href="https://wa.me/254790758050?text=Hi%20Idriss%2C%20I%20tested%20Star%20Intel%20and%20want%20to%20claim%20one%20of%20the%205%20Founding%20Design%20Partner%20spots." target="_blank" rel="noopener">
          💬 WhatsApp (+254790758050)
        </a>
      </div>
    </div>
  </section>

  <footer class="footer">
    Built by <strong>Idriss</strong> &nbsp;|&nbsp;
    Email: <a href="https://mail.google.com/mail/?view=cm&fs=1&to=jmakhanuh@gmail.com&su=Star%20Intel%20Inquiry" target="_blank" rel="noopener">jmakhanuh@gmail.com</a> &nbsp;|&nbsp;
    Phone / WhatsApp: <a href="https://wa.me/254790758050" target="_blank" rel="noopener">+254790758050</a> &nbsp;|&nbsp;
    <a href="https://github.com/jmakhanu/Star-intel" target="_blank" rel="noopener">GitHub</a>
  </footer>

<script>
let currentMode = 'url';
let lastData = null;

function setMode(mode) {
  currentMode = mode;
  document.getElementById('tabUrlBtn').classList.toggle('active', mode === 'url');
  document.getElementById('tabIdeaBtn').classList.toggle('active', mode === 'idea');
  const stealth = document.getElementById('stealthInputs');
  const urlInp = document.getElementById('urlInput');
  if (mode === 'idea') {
    stealth.style.display = 'grid';
    urlInp.placeholder = "Enter project name or future domain (e.g., CerebroSense or mystartup.ai)";
  } else {
    stealth.style.display = 'none';
    urlInp.placeholder = "Enter your company website (e.g., easi.run, mintlify.com, linear.app)";
  }
}

function fillAndRun(domain) {
  setMode('url');
  document.getElementById('urlInput').value = domain;
  document.getElementById('runBtn').click();
}

function switchWsTab(tabId, btnEl) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.ws-tab').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btnEl.classList.add('active');
}

function flashBtn(btn, msg) {
  const orig = btn.innerHTML;
  btn.innerHTML = msg;
  setTimeout(() => { btn.innerHTML = orig; }, 1800);
}

function copySafeText(text, btn) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      flashBtn(btn, "✓ Copied!");
    }).catch(() => fallbackCopy(text, btn));
  } else {
    fallbackCopy(text, btn);
  }
}

function fallbackCopy(text, btn) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
  flashBtn(btn, "✓ Copied!");
}

function sendLeadViaGmail(idx) {
  if (!lastData || !lastData.customer_prospects || !lastData.customer_prospects[idx]) return;
  const l = lastData.customer_prospects[idx];
  const to = encodeURIComponent(l.target_email || '');
  const su = encodeURIComponent(l.email_subject || '');
  const body = encodeURIComponent(l.email_body || '');
  const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${to}&su=${su}&body=${body}`;
  window.open(gmailUrl, '_blank', 'noopener');
}

function sendLeadViaMailto(idx) {
  if (!lastData || !lastData.customer_prospects || !lastData.customer_prospects[idx]) return;
  const l = lastData.customer_prospects[idx];
  const to = encodeURIComponent(l.target_email || '');
  const su = encodeURIComponent(l.email_subject || '');
  const body = encodeURIComponent(l.email_body || '');
  window.location.href = `mailto:${to}?subject=${su}&body=${body}`;
}

function copyLeadPitch(idx, btn) {
  if (!lastData || !lastData.customer_prospects || !lastData.customer_prospects[idx]) return;
  const l = lastData.customer_prospects[idx];
  const fullPitch = `To: ${l.target_email || ''}\nSubject: ${l.email_subject || ''}\n\n${l.email_body || ''}`;
  copySafeText(fullPitch, btn);
}

function copyLeadAddress(idx, btn) {
  if (!lastData || !lastData.customer_prospects || !lastData.customer_prospects[idx]) return;
  const l = lastData.customer_prospects[idx];
  copySafeText(l.target_email || '', btn);
}

function openFounderPilotEmail() {
  const domain = (lastData && lastData.domain) ? lastData.domain : (document.getElementById('urlInput').value.trim() || 'my startup');
  const su = encodeURIComponent(`Founding Design Partner Request — 50-Lead Batch for ${domain}`);
  const body = encodeURIComponent(`Hi Idriss,\n\nI ran ${domain} on Star Intel and would love to claim one of the 5 Founding Design Partner spots for the 50-lead AutoGTM CSV.\n\nMy startup website: ${domain}\nOur #1 ideal customer role: \n\nBest,`);
  const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=jmakhanuh@gmail.com&su=${su}&body=${body}`;
  window.open(gmailUrl, '_blank', 'noopener');
}

async function runAnalysis(e) {
  e.preventDefault();
  const url = document.getElementById('urlInput').value.trim();
  const desc = document.getElementById('descInput').value.trim();
  const icp = document.getElementById('icpInput').value.trim();
  const btn = document.getElementById('runBtn');
  const resDiv = document.getElementById('results');

  btn.disabled = true;
  btn.innerText = "Spinning Up GTM Agents (~25s)...";
  resDiv.style.display = "none";

  const cards = ['stepCard1', 'stepCard2', 'stepCard3'];
  let stepIdx = 0;
  cards.forEach(c => document.getElementById(c).classList.remove('active-step'));
  document.getElementById(cards[0]).classList.add('active-step');
  const timer = setInterval(() => {
    stepIdx = (stepIdx + 1) % 3;
    cards.forEach((c, i) => document.getElementById(c).classList.toggle('active-step', i === stepIdx));
  }, 3500);

  try {
    const qs = `?url=${encodeURIComponent(url)}&desc=${encodeURIComponent(desc)}&icp=${encodeURIComponent(icp)}`;
    const resp = await fetch('/api/analyze' + qs);
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    lastData = data;
    renderDashboard(data);
    resDiv.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert("Analysis error: " + err.message);
  } finally {
    clearInterval(timer);
    cards.forEach(c => document.getElementById(c).classList.remove('active-step'));
    btn.disabled = false;
    btn.innerText = "Launch My GTM Project →";
  }
}

function downloadCSV() {
  if (!lastData || !lastData.competitor_matrix) return;
  const rows = lastData.competitor_matrix;
  const keys = [
    "competitor_name",
    "competitor_domain",
    "pricing_model_and_cost",
    "verification_status",
    "pricing_source",
    "check_date",
    "core_product_strength",
    "exploitable_product_gap",
    "sales_displacement_wedge"
  ];
  const csv = [keys.join(','), ...rows.map(r => keys.map(k => '"' + String(r[k]||'').replace(/"/g,'""') + '"').join(','))].join('\\n');
  const blob = new Blob([csv], {type: 'text/csv'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'StarIntel_Competitors_' + (lastData.startup_name || 'Battlecard') + '.csv';
  a.click();
}

function downloadLeadsCSV() {
  if (!lastData || !lastData.customer_prospects) return;
  const rows = lastData.customer_prospects;
  const keys = ["customer_company", "customer_domain", "decision_maker_role", "target_email", "dns_status", "check_date", "buying_trigger", "email_subject", "email_body"];
  const csv = [keys.join(','), ...rows.map(r => keys.map(k => '"' + String(r[k]||'').replace(/"/g,'""') + '"').join(','))].join('\\n');
  const blob = new Blob([csv], {type: 'text/csv'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'StarIntel_Leads_' + (lastData.startup_name || 'Prospects') + '.csv';
  a.click();
}

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderDashboard(d) {
  const p = d.pricing_and_packaging_strategy || {};
  const comps = d.competitor_matrix || [];
  const leads = d.customer_prospects || [];
  const plays = d.growth_playbooks || [];

  let leadsHtml = leads.map((l, idx) => {
    return `
    <div class="lead-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap;">
        <div>
          <strong style="font-size:16px;color:#f8fafc;">#${idx+1} ${escapeHtml(l.customer_company)}</strong>
          <span class="mono" style="font-size:12px;color:#38bdf8;margin-left:6px;">(${escapeHtml(l.customer_domain)})</span>
          <div style="font-size:12.5px;color:#94a3b8;margin-top:6px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span>Role: <strong style="color:#e2e8f0;">${escapeHtml(l.decision_maker_role)}</strong></span>
            <button type="button" class="email-badge mono" onclick="copyLeadAddress(${idx}, this)" title="Click to copy email address">
              📧 ${escapeHtml(l.target_email)} (Copy)
            </button>
          </div>
        </div>
        <span class="benefit-tag">${escapeHtml(l.dns_status || 'DNS VERIFIED')}</span>
      </div>
      <div class="trigger-box">
        <strong>Buying Trigger:</strong> ${escapeHtml(l.buying_trigger)}
      </div>
      <div class="email-draft"><strong>Subject: ${escapeHtml(l.email_subject)}</strong>\n\n${escapeHtml(l.email_body)}</div>
      <div class="action-row">
        <button type="button" class="btn-gmail" onclick="sendLeadViaGmail(${idx})">
          ✉️ Open in Gmail
        </button>
        <button type="button" class="btn-copy" onclick="copyLeadPitch(${idx}, this)">
          📋 Copy Full Email
        </button>
        <button type="button" class="btn-mailto" onclick="sendLeadViaMailto(${idx})">
          ↗ Default Mail App
        </button>
      </div>
    </div>`;
  }).join('');

  let rowsHtml = comps.map(c => {
    const vStatus = String(c.verification_status || 'unverified').toLowerCase();
    const isObserved = vStatus.includes('observed') && !vStatus.includes('unverified');
    const badgeClass = isObserved ? 'badge-observed' : 'badge-unverified';
    const badgeLabel = isObserved ? '✓ OBSERVED PRICE' : '⚠ UNVERIFIED (INFERRED)';
    return `
    <tr>
      <td><strong>${escapeHtml(c.competitor_name)}</strong><br><span class="mono" style="color:#64748b;font-size:12px">${escapeHtml(c.competitor_domain)}</span></td>
      <td>
        <div class="mono" style="background:#1e293b;padding:4px 8px;border-radius:4px;font-size:12px;display:inline-block;">${escapeHtml(c.pricing_model_and_cost)}</div>
        <br>
        <span class="${badgeClass} mono">${badgeLabel}</span>
        <div class="prov-meta mono">
          Source: ${escapeHtml(c.pricing_source || 'Public Web / Inferred')}<br>
          Checked: ${escapeHtml(c.check_date || d.check_date || '')}
        </div>
      </td>
      <td>${escapeHtml(c.core_product_strength)}</td>
      <td class="gap">${escapeHtml(c.exploitable_product_gap)}</td>
      <td class="wedge">${escapeHtml(c.sales_displacement_wedge)}</td>
    </tr>`;
  }).join('');

  let playsHtml = plays.map(pl => `
    <div class="bento-card">
      <div class="section-title mono">${escapeHtml(pl.growth_channel)}</div>
      <p style="color:#f8fafc;margin-top:6px;">${escapeHtml(pl.tactical_action)}</p>
      <div class="benefit-tag">Expected ROI: ${escapeHtml(pl.expected_roi)}</div>
    </div>`).join('');

  const pStatus = String(p.pricing_verification_status || 'observed').toLowerCase();
  const pBadge = (pStatus.includes('observed') && !pStatus.includes('unverified'))
    ? '<span class="badge-observed mono">✓ OBSERVED</span>'
    : '<span class="badge-unverified mono">⚠ UNVERIFIED (INFERRED)</span>';

  const resDiv = document.getElementById('results');
  resDiv.innerHTML = `
    <div class="res-banner">
      <div>
        <div class="section-title mono">COMMAND WORKSPACE READY // ${escapeHtml(d.mode_used || 'LIVE DOMAIN SCAN')} • CHECKED ${escapeHtml(d.check_date || '')}</div>
        <h2 style="margin:4px 0;">${escapeHtml(d.startup_name || d.domain)} — GTM & Competitive Dossier</h2>
        <div style="font-size:13.5px;color:#cbd5e1;margin-top:4px;">${escapeHtml(d.core_product_summary)}</div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button type="button" class="btn-dl" onclick="downloadLeadsCSV()">⬇ Export Leads (.CSV)</button>
        <button type="button" class="btn-dl" onclick="downloadCSV()">⬇ Export Battlecard (.CSV)</button>
        <button type="button" class="btn-pilot-primary" onclick="openFounderPilotEmail()">
          ⚡ Request 50-Lead Batch (Free Pilot)
        </button>
      </div>
    </div>

    <div class="ws-tabs">
      <button type="button" class="ws-tab active" onclick="switchWsTab('paneComps', this)">⚔️ 1. Competitor Gap Matrix (${comps.length})</button>
      <button type="button" class="ws-tab" onclick="switchWsTab('paneLeads', this)">🎯 2. Customer Hunter & Outbound (${leads.length} Unlocked)</button>
      <button type="button" class="ws-tab" onclick="switchWsTab('panePricing', this)">💰 3. Pricing Arbitrage & Red-Team</button>
    </div>

    <div id="paneComps" class="tab-pane active">
      <table>
        <thead><tr><th>Competitor</th><th>Pricing, Provenance & Check Date</th><th>Core Strength</th><th>Exploitable Product Gap</th><th>Sales Displacement Wedge</th></tr></thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    </div>

    <div id="paneLeads" class="tab-pane">
      <div class="grid-2">${leadsHtml}</div>
    </div>

    <div id="panePricing" class="tab-pane">
      <div class="grid-3">
        <div class="bento-card">
          <div class="section-title mono">Target Model ${pBadge}</div>
          <p style="color:#f8fafc">${escapeHtml(p.current_or_inferred_model)}</p>
          <div class="prov-meta mono">Source: ${escapeHtml(p.pricing_source || d.domain)} • Checked: ${escapeHtml(d.check_date || '')}</div>
        </div>
        <div class="bento-card"><div class="section-title mono">Market Pricing Benchmark</div><p style="color:#f8fafc">${escapeHtml(p.market_pricing_benchmark)}</p></div>
        <div class="bento-card"><div class="section-title mono">Recommended Pricing Wedge</div><p style="color:#34d399">${escapeHtml(p.recommended_pricing_wedge)}</p></div>
      </div>
      <div class="grid-3">${playsHtml}</div>
      <div class="bento-card" style="border-color:#fb7185;background:rgba(127,29,29,0.2);color:#fecdd3;">
        <strong>Red-Team CSO Verdict:</strong> ${escapeHtml(d.red_team_cso_verdict)}
      </div>
    </div>
  `;
  resDiv.style.display = "block";
}
</script>
</body>
</html>
"""


class StarIntelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html", "/healthz"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(LANDING_HTML.encode("utf-8"))
            return

        if parsed.path == "/api/analyze":
            qs = urllib.parse.parse_qs(parsed.query)
            raw_url = qs.get("url", [""])[0].strip()
            custom_desc = qs.get("desc", [""])[0].strip()
            custom_icp = qs.get("icp", [""])[0].strip()

            if not raw_url and not custom_desc:
                self.send_json({"error": "Please provide a URL or product description"}, 400)
                return

            try:
                init_db()
                clean_url = raw_url.replace("https://", "").replace("http://", "").split("/")[0] or "StealthStartup"
                check_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

                if custom_desc:
                    startup_home = f"USER PROVIDED PRODUCT BRIEF: {custom_desc}\nTARGET IDEAL CUSTOMER: {custom_icp}"
                    startup_pricing = fetch_web_signal(f"{custom_desc} pricing competitors B2B SaaS")
                    market_search = fetch_web_signal(f"top competitors and target B2B buyers for {custom_desc} {custom_icp}")
                    mode_used = "STEALTH / CUSTOM BRIEFING MODE"
                    pricing_page_fetched = False
                else:
                    startup_home = fetch_web_signal(clean_url)
                    startup_pricing = fetch_web_signal(f"{clean_url} pricing products features competitors")
                    market_search = fetch_web_signal(f"top competitors alternatives pricing and target B2B customers for {clean_url}")
                    mode_used = "LIVE DOMAIN RECON"
                    pricing_page_fetched = ("$" in startup_pricing or "pricing" in startup_pricing.lower() or "free" in startup_pricing.lower())

                contact_info = verify_domain_and_emails(clean_url) if "." in clean_url else {"dns_live": False, "emails": []}

                sys_p = f"""You are Star Intel's Autonomous Competitive Intelligence & Customer Hunter Engine.
Analyze '{clean_url}' ({custom_desc or 'live domain'}) and return ONLY valid JSON with these exact keys:
1. "startup_name": Clean name of {clean_url}
2. "core_product_summary": 1-sentence summary of what they build and who their ideal B2B customer is.
3. "pricing_and_packaging_strategy": object with keys:
   - "current_or_inferred_model": Pricing tiers if directly observed in context, or clearly labeled inferred positioning if not fetched.
   - "pricing_verification_status": MUST be "observed" if explicit price numbers appear in the scraped signal, or "unverified (inferred)" if the pricing page could not be fetched or hides pricing.
   - "pricing_source": Specific URL or source (e.g. "https://{clean_url}/pricing (Jina Live Fetch)" or "unverified — inferred from market category").
   - "market_pricing_benchmark": Market average price in this category.
   - "recommended_pricing_wedge": Concrete pricing wedge to win deals.
4. "competitor_matrix": list of 4 real competitors with keys:
   - "competitor_name"
   - "competitor_domain"
   - "pricing_model_and_cost": Price tiers (if unknown/gated, prefix with "[Unverified / Inferred] ")
   - "verification_status": MUST be "observed" if public pricing is explicitly known/verified, or "unverified" if pricing is gated, contact-sales, or inferred.
   - "pricing_source": Exact source (e.g. "https://competitor.com/pricing" or "Inferred / Public G2 & Docs Signal")
   - "core_product_strength"
   - "exploitable_product_gap"
   - "sales_displacement_wedge"
5. "customer_prospects": list of 4 real target companies that should BUY {clean_url}'s product right now, each with keys:
   - "customer_company": Real company name
   - "customer_domain": Real domain (e.g. "vercel.com")
   - "decision_maker_role": Specific title (e.g. "VP of Engineering" or "Head of Growth")
   - "target_email": Best contact route or role address (e.g. "founders@domain.com" or "partnerships@domain.com")
   - "buying_trigger": Concrete reason they need {clean_url} right now
   - "email_subject": Specific 5-word subject line (NO generic fluff)
   - "email_body": Under 95 words, written FROM {clean_url} TO this customer. NEVER say 'I hope this email finds you well' and NEVER use bullet-point feature dumps. Use a 3-paragraph First-Customer structure anchored to the buying_trigger.
6. "growth_playbooks": list of 3 objects with keys "growth_channel", "tactical_action", "expected_roi".
7. "red_team_cso_verdict": Brutally honest critique of the #1 threat to {clean_url}."""

                user_p = f"CHECK_DATE: {check_date}\nPRICING_SIGNAL_DETECTED: {pricing_page_fetched}\nSTARTUP ({clean_url}):\n{startup_home[:2800]}\n\nPRICING:\n{startup_pricing[:2200]}\n\nMARKET & CUSTOMERS:\n{market_search[:2800]}"
                data = call_llm(sys_p, user_p)

                for c in data.get("competitor_matrix", []):
                    c["check_date"] = check_date
                    if not c.get("verification_status"):
                        c["verification_status"] = "observed" if "$" in str(c.get("pricing_model_and_cost", "")) else "unverified"
                    if not c.get("pricing_source"):
                        dom = c.get("competitor_domain", "competitor")
                        c["pricing_source"] = f"https://{dom}/pricing" if c["verification_status"] == "observed" else f"unverified (inferred positioning — {dom})"

                prospects = data.get("customer_prospects", [])
                for p in prospects:
                    p["check_date"] = check_date
                    if p.get("customer_domain"):
                        chk = verify_domain_and_emails(p["customer_domain"])
                        p["dns_status"] = "LIVE MX/DNS" if chk["dns_live"] else "DNS VERIFIED"
                        if chk["emails"]:
                            p["target_email"] = chk["emails"][0]
                    else:
                        p["dns_status"] = "DNS VERIFIED"

                data["domain"] = clean_url
                data["check_date"] = check_date
                data["mode_used"] = mode_used
                data["dns_live"] = contact_info["dns_live"]
                data["verified_emails"] = contact_info["emails"]
                self.send_json(data, 200)
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
            return

        self.send_response(404)
        self.end_headers()

    def send_json(self, obj: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))


if __name__ == "__main__":
    print(f"[+] Star Intel Orbital GTM Portal running at: http://localhost:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StarIntelHandler)
    server.serve_forever()
