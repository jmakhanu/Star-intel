#!/usr/bin/env python3
"""
Star Intel — Executive Studio GTM & Competitive Intelligence Platform
Live USD Checkout Edition:
- Direct PayPal + International Card Checkout (XKUVEJSB74V88)
- Post-checkout auto-return celebration banner (?checkout=success)
- Observed vs. Unverified pricing provenance + check_date in UI & CSV
- 1-Click Gmail Web Compose & Index-safe Clipboard Copy
"""

import os
import json
import urllib.parse
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from star_intel_growth import init_db, fetch_web_signal, verify_domain_and_emails, call_llm

PORT = int(os.getenv("PORT", 8080))
PAYPAL_CHECKOUT_URL = "https://www.paypal.com/ncp/payment/XKUVEJSB74V88"

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Star Intel — Autonomous Competitive Radar & AutoGTM Engine</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F8F9FA;
    --surface: #FFFFFF;
    --surface-subtle: #F3F4F6;
    --border: #E5E7EB;
    --border-strong: #D1D5DB;
    --obsidian: #111827;
    --obsidian-hover: #1F2937;
    --emerald: #059669;
    --emerald-bg: #ECFDF5;
    --emerald-border: #A7F3D0;
    --amber: #D97706;
    --amber-bg: #FFFBEB;
    --amber-border: #FDE68A;
    --rose: #E11D48;
    --rose-bg: #FFF1F2;
    --text: #111827;
    --text-secondary: #4B5563;
    --muted: #6B7280;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
    --shadow-md: 0 10px 30px -5px rgba(0, 0, 0, 0.05), 0 4px 12px -2px rgba(0, 0, 0, 0.03);
    --shadow-lg: 0 20px 45px -10px rgba(0, 0, 0, 0.07), 0 8px 18px -4px rgba(0, 0, 0, 0.04);
  }
  * { box-sizing: border-box; }
  body {
    background-color: var(--bg);
    background-image: radial-gradient(#E5E7EB 1px, transparent 1px);
    background-size: 24px 24px;
    color: var(--text);
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }
  .mono { font-family: 'JetBrains Mono', monospace; }

  /* POST-CHECKOUT SUCCESS BANNER */
  #checkoutBanner {
    display: none;
    background: var(--obsidian);
    color: #FFFFFF;
    padding: 16px 24px;
    text-align: center;
    border-bottom: 2px solid var(--emerald);
  }
  #checkoutBanner a {
    color: #34D399;
    font-weight: 700;
    text-decoration: underline;
    margin-left: 8px;
  }

  /* TOP NAVIGATION */
  .nav-wrap {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 40;
  }
  .nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 14px 24px;
    flex-wrap: wrap;
    gap: 12px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 16.5px;
    letter-spacing: -0.02em;
    color: var(--obsidian);
  }
  .brand-mark {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: var(--obsidian);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 14px;
  }
  .status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--emerald-bg);
    border: 1px solid var(--emerald-border);
    color: var(--emerald);
    padding: 5px 13px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
  }
  .pulse-dot {
    width: 7px;
    height: 7px;
    background: var(--emerald);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.45; transform: scale(1.25); }
  }

  /* STEPPER RIBBON */
  .stepper-ribbon {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 99px;
    box-shadow: var(--shadow-sm);
    margin-bottom: 20px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .step-dot {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
  }
  .step-dot span {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--obsidian);
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
  }
  .step-line { width: 18px; height: 1px; background: var(--border-strong); }
  .step-ready {
    background: var(--emerald-bg);
    border: 1px solid var(--emerald-border);
    color: var(--emerald);
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 11.5px;
    font-weight: 700;
  }

  /* HERO CENTER */
  .hero-center {
    max-width: 880px;
    margin: 42px auto 30px;
    padding: 0 24px;
    text-align: center;
  }
  h1 {
    font-size: 46px;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 16px;
    letter-spacing: -0.03em;
    color: var(--obsidian);
  }
  h1 span {
    color: var(--emerald);
    text-decoration: underline;
    text-decoration-color: rgba(5, 150, 105, 0.28);
    text-underline-offset: 6px;
  }
  .hero-sub {
    color: var(--text-secondary);
    font-size: 16.5px;
    max-width: 660px;
    margin: 0 auto 28px;
    font-weight: 400;
  }

  /* COMMAND CONSOLE CARD */
  .console-shell {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 20px;
    box-shadow: var(--shadow-lg);
    text-align: left;
  }
  .mode-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
    justify-content: space-between;
    flex-wrap: wrap;
  }
  .mode-tab-group {
    display: inline-flex;
    background: var(--surface-subtle);
    padding: 4px;
    border-radius: 99px;
    border: 1px solid var(--border);
    gap: 4px;
  }
  .mode-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .mode-btn.active {
    background: var(--obsidian);
    color: #FFFFFF;
    box-shadow: var(--shadow-sm);
  }
  .cmd-row {
    display: flex;
    gap: 10px;
    background: var(--bg);
    border: 1.5px solid var(--border-strong);
    padding: 7px;
    border-radius: 12px;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .cmd-row:focus-within {
    border-color: var(--obsidian);
    background: #fff;
    box-shadow: 0 0 0 4px rgba(17, 24, 39, 0.06);
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
    color: var(--obsidian);
    font-size: 15px;
    outline: none;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }
  .stealth-grid {
    display: none;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }
  @media (max-width: 680px) { .stealth-grid { grid-template-columns: 1fr; } }
  .stealth-field {
    background: var(--bg);
    border: 1px solid var(--border-strong);
    padding: 10px 14px;
    border-radius: 10px;
  }
  .stealth-field label {
    display: block;
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
    font-weight: 700;
  }
  .cmd-btn {
    background: var(--emerald);
    color: #FFFFFF;
    border: none;
    padding: 13px 24px;
    border-radius: 9px;
    font-weight: 700;
    font-size: 14px;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s, transform 0.1s;
    box-shadow: 0 2px 6px rgba(5, 150, 105, 0.25);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .cmd-btn:hover { background: #047857; transform: translateY(-1px); }
  .cmd-btn:disabled { background: #9CA3AF; color: #F3F4F6; cursor: wait; box-shadow: none; }

  .quick-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 14px;
    font-size: 12px;
    color: var(--muted);
  }
  .pill-btn {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    color: var(--obsidian);
    padding: 4px 11px;
    border-radius: 99px;
    cursor: pointer;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    font-weight: 500;
    transition: all 0.15s;
  }
  .pill-btn:hover {
    border-color: var(--obsidian);
    background: var(--obsidian);
    color: #fff;
  }

  /* 3-PILLAR PIPELINE CARDS */
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
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
  }
  .pipe-card.active-step {
    border-color: var(--emerald);
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
  }
  .pipe-num {
    display: inline-block;
    font-size: 11px;
    color: var(--emerald);
    background: var(--emerald-bg);
    border: 1px solid var(--emerald-border);
    padding: 2px 8px;
    border-radius: 6px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  .pipe-card h3 { margin: 0 0 6px; font-size: 16px; color: var(--obsidian); }
  .pipe-card p { margin: 0; font-size: 13.5px; color: var(--text-secondary); }

  /* WORKSPACE RESULTS & PILL SWITCHER */
  #results { max-width: 1200px; margin: 20px auto 70px; padding: 0 24px; display: none; }
  .res-banner {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-md);
  }
  .ws-tabs {
    display: inline-flex;
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    padding: 5px;
    border-radius: 99px;
    gap: 6px;
    margin-bottom: 22px;
    flex-wrap: wrap;
  }
  .ws-tab {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 8px 18px;
    border-radius: 99px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .ws-tab.active {
    background: var(--obsidian);
    color: #FFFFFF;
    box-shadow: var(--shadow-sm);
  }
  .tab-pane { display: none; }
  .tab-pane.active { display: block; }

  .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 18px; margin-bottom: 24px; }
  @media (max-width: 640px) { .grid-2 { grid-template-columns: 1fr; } }
  .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 24px; }

  .lead-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px;
    position: relative;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .lead-card:hover {
    border-color: var(--border-strong);
    box-shadow: var(--shadow-md);
  }
  .avatar-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--surface-subtle);
    border: 1px solid var(--border-strong);
    color: var(--obsidian);
    font-weight: 700;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .email-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface-subtle);
    border: 1px solid var(--border-strong);
    color: var(--obsidian);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }
  .email-badge:hover { background: var(--obsidian); color: #fff; }
  .trigger-box {
    background: var(--emerald-bg);
    border-left: 3px solid var(--emerald);
    padding: 9px 13px;
    font-size: 12.5px;
    color: #065F46;
    margin: 12px 0 14px;
    border-radius: 6px;
  }
  .email-draft {
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 15px;
    border-radius: 10px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 13.5px;
    color: var(--obsidian);
    white-space: pre-wrap;
    margin-bottom: 14px;
    line-height: 1.6;
  }

  /* TABLE STYLING */
  .table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th {
    background: var(--surface-subtle);
    color: var(--text-secondary);
    text-align: left;
    padding: 14px 16px;
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border);
  }
  td {
    padding: 16px;
    border-bottom: 1px solid var(--border);
    font-size: 13.5px;
    vertical-align: top;
    color: var(--text);
  }
  tr:last-child td { border-bottom: none; }
  .gap { color: var(--rose); font-weight: 500; }
  .wedge { color: var(--emerald); font-weight: 600; }

  /* PROVENANCE & VERIFICATION BADGES */
  .badge-observed {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    color: var(--emerald);
    background: var(--emerald-bg);
    border: 1px solid var(--emerald-border);
    padding: 2px 8px;
    border-radius: 6px;
    margin-top: 6px;
  }
  .badge-unverified {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 700;
    color: var(--amber);
    background: var(--amber-bg);
    border: 1px solid var(--amber-border);
    padding: 2px 8px;
    border-radius: 6px;
    margin-top: 6px;
  }
  .prov-meta {
    font-size: 11px;
    color: var(--muted);
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
    background: var(--emerald);
    color: #FFFFFF;
    padding: 9px 15px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 12.5px;
    border: none;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.15s, transform 0.1s;
  }
  .btn-gmail:hover { background: #047857; transform: translateY(-1px); }
  .btn-copy {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--obsidian);
    color: #FFFFFF;
    border: 1px solid var(--obsidian);
    padding: 8px 13px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-copy:hover { background: var(--obsidian-hover); }
  .btn-mailto {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--surface);
    color: var(--text-secondary);
    border: 1px solid var(--border-strong);
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 12px;
    cursor: pointer;
    text-decoration: none;
  }
  .btn-mailto:hover { border-color: var(--obsidian); color: var(--obsidian); }
  .btn-dl {
    background: var(--surface);
    color: var(--obsidian);
    border: 1px solid var(--border-strong);
    padding: 10px 16px;
    border-radius: 9px;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-dl:hover { border-color: var(--obsidian); background: var(--surface-subtle); }
  .btn-pilot-primary {
    background: var(--obsidian);
    color: #FFFFFF;
    padding: 10px 18px;
    border-radius: 99px;
    font-weight: 700;
    font-size: 13px;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: none;
    cursor: pointer;
    transition: background 0.15s;
  }
  .btn-pilot-primary:hover { background: var(--obsidian-hover); }

  .bento-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: var(--shadow-sm);
  }
  .section-title { font-size: 11px; letter-spacing: 1.1px; text-transform: uppercase; color: var(--muted); font-weight: 700; margin-bottom: 6px; }
  .benefit-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    color: var(--emerald);
    background: var(--emerald-bg);
    border: 1px solid var(--emerald-border);
    padding: 3px 10px;
    border-radius: 99px;
  }
  .pilot-wrap { max-width: 1160px; margin: 40px auto; padding: 0 24px; }
  .pilot-card {
    background: var(--surface);
    border: 1.5px solid var(--obsidian);
    border-radius: 18px;
    padding: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    box-shadow: var(--shadow-md);
  }
  .price-strike {
    text-decoration: line-through;
    color: var(--muted);
    font-weight: 500;
    margin-right: 4px;
  }
  .footer {
    border-top: 1px solid var(--border);
    background: var(--surface);
    padding: 28px 24px;
    text-align: center;
    color: var(--muted);
    font-size: 13px;
  }
  .footer a { color: var(--obsidian); font-weight: 600; text-decoration: none; }
  .footer a:hover { color: var(--emerald); }
</style>
</head>
<body>

  <div id="checkoutBanner">
    🎉 <strong>Welcome to Star Intel AutoGTM Pro (Founding Member)!</strong> Your payment is confirmed.
    <a href="https://mail.google.com/mail/?view=cm&fs=1&to=jmakhanuh@gmail.com&su=AutoGTM%20Pro%2050-Lead%20Onboarding&body=Hi%20Idriss%2C%20I%20just%20completed%20my%20Founding%20Member%20checkout.%20Here%20is%20my%20domain%20and%20target%20buyer%20role%3A%20" target="_blank" rel="noopener">Click here to confirm your domain for your first 50-lead CSV →</a>
  </div>

  <div class="nav-wrap">
    <nav class="nav">
      <div class="brand">
        <span class="brand-mark">SI</span>
        Star Intel
        <span class="mono" style="font-size:11px;color:var(--muted);font-weight:500;">// AutoGTM Studio</span>
      </div>
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
        <div class="status-pill"><span class="pulse-dot"></span> Provenance-Verified Recon Online</div>
        <a href="https://www.paypal.com/ncp/payment/XKUVEJSB74V88" target="_blank" rel="noopener" class="btn-pilot-primary">
          💳 Unlock AutoGTM Pro (<span class="price-strike" style="color:#9CA3AF;">$49</span> $19/mo) →
        </a>
      </div>
    </nav>
  </div>

  <section class="hero-center">
    <div class="stepper-ribbon">
      <div class="step-dot"><span>1</span> Map Market & Prices</div>
      <div class="step-line"></div>
      <div class="step-dot"><span>2</span> Expose Rival Gaps</div>
      <div class="step-line"></div>
      <div class="step-dot"><span>3</span> Verify Buyers</div>
      <div class="step-line"></div>
      <div class="step-ready">● Outreach Ready</div>
    </div>

    <h1>Your AI Go-To-Market &<br><span>Competitive Teardown</span> Studio.</h1>
    <p class="hero-sub">
      Enter your company website — or switch to <strong>Stealth Startup Mode</strong>. Star Intel separates <strong>observed prices</strong> from <strong>unverified (inferred) positioning</strong> with source + check-date audit trails and ready-to-send buyer emails.
    </p>

    <div class="console-shell">
      <div class="mode-tabs">
        <div class="mode-tab-group">
          <button type="button" class="mode-btn active" id="tabUrlBtn" onclick="setMode('url')">🌐 Company Website</button>
          <button type="button" class="mode-btn" id="tabIdeaBtn" onclick="setMode('idea')">🧠 No Website / Stealth Mode</button>
        </div>
        <span class="mono" style="font-size:11.5px;color:var(--emerald);font-weight:600;align-self:center;">✓ Observed vs. Unverified Provenance Tagging</span>
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
            <svg width="18" height="18" fill="none" stroke="#111827" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input type="text" id="urlInput" placeholder="Enter your company website (e.g., easi.run, signedreviews.com, linear.app)" required />
          </div>
          <button type="submit" class="cmd-btn" id="runBtn">Create My GTM Project →</button>
        </div>
      </form>

      <div class="quick-bar">
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
          <span style="font-weight:600;color:var(--text-secondary);">Live presets:</span>
          <button type="button" class="pill-btn" onclick="fillAndRun('easi.run')">easi.run ↗</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('signedreviews.com')">signedreviews.com ↗</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('mintlify.com')">mintlify.com ↗</button>
          <button type="button" class="pill-btn" onclick="fillAndRun('linear.app')">linear.app ↗</button>
        </div>
        <span class="mono" style="color:var(--muted);">CSV includes: verification_status, pricing_source, check_date</span>
      </div>
    </div>
  </section>

  <section class="pipeline-strip">
    <div class="pipe-card" id="stepCard1">
      <div class="pipe-num mono">STEP 01 // PROVENANCE RECON</div>
      <h3>Observed vs. Inferred Pricing</h3>
      <p>Scrapes live pricing pages and flags whether each price is directly observed or `unverified` (inferred) with source & check date.</p>
    </div>
    <div class="pipe-card" id="stepCard2">
      <div class="pipe-num mono">STEP 02 // COMPETITOR ARBITRAGE</div>
      <h3>Expose Rival Product Gaps</h3>
      <p>Builds a 4-competitor battlecard matrix showing exact pricing wedges and technical weaknesses you can exploit on sales calls.</p>
    </div>
    <div class="pipe-card" id="stepCard3">
      <div class="pipe-num mono">STEP 03 // TRIGGER-BASED OUTREACH</div>
      <h3>Verified Buyers & Cold Emails</h3>
      <p>Identifies high-intent B2B target accounts, verifies live DNS/MX records, and opens pre-filled pitches directly in Gmail.</p>
    </div>
  </section>

  <div id="results"></div>

  <section class="pilot-wrap" id="pilot">
    <div class="pilot-card">
      <div style="max-width:650px;">
        <div class="benefit-tag mono" style="margin-bottom:8px;">FIRST 10 FOUNDING MEMBERS • 60% EARLY-BIRD LOCK-IN</div>
        <h2 style="margin:4px 0 8px;font-size:23px;color:var(--obsidian);">
          Get Your Weekly 50-Lead AutoGTM Pack — <span class="price-strike">$49/mo</span> <span style="color:var(--emerald);">$19/mo USD</span>
        </h2>
        <p style="margin:0;color:var(--text-secondary);font-size:14.5px;">
          Our live studio unlocks all 4 Competitor Battlecards + 4 Target Customer Emails for free. Upgrade to <strong>AutoGTM Pro ($19/mo via PayPal or Debit/Credit Card)</strong> to receive 50 verified decision-maker leads & custom outbound sequences every week.
        </p>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
        <a class="cmd-btn" href="https://www.paypal.com/ncp/payment/XKUVEJSB74V88" target="_blank" rel="noopener">
          💳 Checkout $19 USD (PayPal / Card) →
        </a>
        <button type="button" class="btn-dl" onclick="openFounderPilotEmail()">
          ✉️ Ask a Question (Gmail)
        </button>
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
const PAYPAL_URL = "https://www.paypal.com/ncp/payment/XKUVEJSB74V88";
let currentMode = 'url';
let lastData = null;

if (window.location.search.includes("checkout=success")) {
  document.getElementById("checkoutBanner").style.display = "block";
}

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
    urlInp.placeholder = "Enter your company website (e.g., easi.run, signedreviews.com, linear.app)";
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
  const su = encodeURIComponent(`Star Intel AutoGTM Pro — 50-Lead Batch for ${domain}`);
  const body = encodeURIComponent(`Hi Idriss,\n\nI ran ${domain} on Star Intel and have a quick question about the 50-lead AutoGTM CSV:\n\nMy startup website: ${domain}\nOur #1 ideal customer role: \n\nBest,`);
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
  btn.innerText = "Building GTM Project (~25s)...";
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
    btn.innerText = "Create My GTM Project →";
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
    const initials = String(l.customer_company || 'CO').slice(0, 2).toUpperCase();
    return `
    <div class="lead-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap;">
        <div style="display:flex;gap:12px;align-items:center;">
          <div class="avatar-circle">${escapeHtml(initials)}</div>
          <div>
            <strong style="font-size:16px;color:var(--obsidian);">${escapeHtml(l.customer_company)}</strong>
            <span class="mono" style="font-size:12px;color:var(--muted);margin-left:6px;">· ${escapeHtml(l.customer_domain)}</span>
            <div style="font-size:12.5px;color:var(--text-secondary);margin-top:4px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span>${escapeHtml(l.decision_maker_role)}</span>
              <button type="button" class="email-badge mono" onclick="copyLeadAddress(${idx}, this)" title="Click to copy email address">
                ✉ ${escapeHtml(l.target_email)}
              </button>
            </div>
          </div>
        </div>
        <span class="benefit-tag mono">● ${escapeHtml(l.dns_status || 'VALID')}</span>
      </div>
      <div class="trigger-box">
        <strong>Buying Trigger:</strong> ${escapeHtml(l.buying_trigger)}
      </div>
      <div class="email-draft"><strong>Subject: ${escapeHtml(l.email_subject)}</strong>\n\n${escapeHtml(l.email_body)}</div>
      <div class="action-row">
        <button type="button" class="btn-gmail" onclick="sendLeadViaGmail(${idx})">
          ✉️ Send via Gmail
        </button>
        <button type="button" class="btn-copy" onclick="copyLeadPitch(${idx}, this)">
          📋 Copy Email
        </button>
        <button type="button" class="btn-mailto" onclick="sendLeadViaMailto(${idx})">
          ↗ Mail App
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
      <td><strong style="color:var(--obsidian);">${escapeHtml(c.competitor_name)}</strong><br><span class="mono" style="color:var(--muted);font-size:12px">${escapeHtml(c.competitor_domain)}</span></td>
      <td>
        <div class="mono" style="background:var(--surface-subtle);border:1px solid var(--border);padding:4px 8px;border-radius:6px;font-size:12px;display:inline-block;color:var(--obsidian);font-weight:600;">${escapeHtml(c.pricing_model_and_cost)}</div>
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
      <p style="color:var(--obsidian);margin-top:6px;font-weight:500;">${escapeHtml(pl.tactical_action)}</p>
      <div class="benefit-tag">ROI: ${escapeHtml(pl.expected_roi)}</div>
    </div>`).join('');

  const pStatus = String(p.pricing_verification_status || 'observed').toLowerCase();
  const pBadge = (pStatus.includes('observed') && !pStatus.includes('unverified'))
    ? '<span class="badge-observed mono">✓ OBSERVED</span>'
    : '<span class="badge-unverified mono">⚠ UNVERIFIED (INFERRED)</span>';

  const resDiv = document.getElementById('results');
  resDiv.innerHTML = `
    <div class="res-banner">
      <div>
        <div class="section-title mono" style="color:var(--emerald);">● OUTREACH & BATTLECARD READY • CHECKED ${escapeHtml(d.check_date || '')}</div>
        <h2 style="margin:4px 0;color:var(--obsidian);">${escapeHtml(d.startup_name || d.domain)} — GTM & Competitive Dossier</h2>
        <div style="font-size:14px;color:var(--text-secondary);margin-top:4px;">${escapeHtml(d.core_product_summary)}</div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button type="button" class="btn-dl" onclick="downloadLeadsCSV()">⬇ Export Leads (.CSV)</button>
        <button type="button" class="btn-dl" onclick="downloadCSV()">⬇ Export Battlecard (.CSV)</button>
        <a class="cmd-btn" href="${PAYPAL_URL}" target="_blank" rel="noopener">
          💳 Unlock 50-Lead Pack ($19 USD) →
        </a>
      </div>
    </div>

    <div class="ws-tabs">
      <button type="button" class="ws-tab active" onclick="switchWsTab('paneComps', this)">🏢 Companies & Matrix (${comps.length})</button>
      <button type="button" class="ws-tab" onclick="switchWsTab('paneLeads', this)">✉️ Buyer Emails (${leads.length} Valid)</button>
      <button type="button" class="ws-tab" onclick="switchWsTab('panePricing', this)">📊 Pricing & Strategy</button>
    </div>

    <div id="paneComps" class="tab-pane active">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Competitor</th><th>Pricing, Provenance & Check Date</th><th>Core Strength</th><th>Exploitable Product Gap</th><th>Sales Displacement Wedge</th></tr></thead>
          <tbody>${rowsHtml}</tbody>
        </table>
      </div>
    </div>

    <div id="paneLeads" class="tab-pane">
      <div class="grid-2">${leadsHtml}</div>
    </div>

    <div id="panePricing" class="tab-pane">
      <div class="grid-3">
        <div class="bento-card">
          <div class="section-title mono">Target Model ${pBadge}</div>
          <p style="color:var(--obsidian);font-weight:500;">${escapeHtml(p.current_or_inferred_model)}</p>
          <div class="prov-meta mono">Source: ${escapeHtml(p.pricing_source || d.domain)} • Checked: ${escapeHtml(d.check_date || '')}</div>
        </div>
        <div class="bento-card"><div class="section-title mono">Market Pricing Benchmark</div><p style="color:var(--obsidian);font-weight:500;">${escapeHtml(p.market_pricing_benchmark)}</p></div>
        <div class="bento-card"><div class="section-title mono">Recommended Pricing Wedge</div><p style="color:var(--emerald);font-weight:600;">${escapeHtml(p.recommended_pricing_wedge)}</p></div>
      </div>
      <div class="grid-3">${playsHtml}</div>
      <div class="bento-card" style="border-color:#FECDD3;background:var(--rose-bg);color:#9F1239;">
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
   - "pricing_source": Specific URL or source (e.g. "https://{clean_url}/pricing (Live Fetch)" or "unverified — inferred from market category").
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
                        p["dns_status"] = "VALID MX/DNS" if chk["dns_live"] else "VALID"
                        if chk["emails"]:
                            p["target_email"] = chk["emails"][0]
                    else:
                        p["dns_status"] = "VALID"

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
    print(f"[+] Star Intel Studio GTM Portal running at: http://localhost:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StarIntelHandler)
    server.serve_forever()
