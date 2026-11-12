#!/usr/bin/env python3
"""
Star Intel Web SaaS Platform
Self-serve web portal with custom SVG vector graphics, architecture pipeline,
ROI bento cards, Founding Test User conversion flow, and live teardown engine.
"""

import os
import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from star_intel_growth import init_db, fetch_web_signal, verify_domain_and_emails, call_llm

PORT = int(os.getenv("PORT", 8080))

LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Star Intel — Autonomous Market, Pricing & Competitive Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #050811;
    --panel: rgba(15, 23, 42, 0.75);
    --panel-solid: #0f172a;
    --border: rgba(56, 189, 248, 0.16);
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
      radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 35%),
      radial-gradient(circle at 85% 25%, rgba(16, 185, 129, 0.07) 0%, transparent 35%),
      linear-gradient(rgba(148, 163, 184, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(148, 163, 184, 0.03) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    margin: 0;
    padding: 0;
    line-height: 1.5;
  }
  .mono { font-family: 'JetBrains Mono', monospace; }

  /* NAVBAR */
  .nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1220px;
    margin: 0 auto;
    padding: 20px 24px;
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
    letter-spacing: 1.5px;
    color: var(--text);
  }
  .nav-pills { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .status-pill {
    display: flex;
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
  .beta-cta-nav {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid var(--border);
    color: var(--cyan);
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    text-decoration: none;
    transition: 0.2s;
  }
  .beta-cta-nav:hover { background: var(--cyan); color: #050811; }
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

  /* HERO SECTION */
  .hero-wrap {
    max-width: 1220px;
    margin: 48px auto 32px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: 1.25fr 0.75fr;
    gap: 36px;
    align-items: center;
  }
  @media (max-width: 920px) {
    .hero-wrap { grid-template-columns: 1fr; }
  }
  .eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--cyan);
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid var(--border);
    padding: 6px 12px;
    border-radius: 6px;
    margin-bottom: 18px;
    font-weight: 600;
  }
  h1 {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.12;
    margin: 0 0 18px;
    letter-spacing: -0.02em;
  }
  h1 span {
    background: linear-gradient(95deg, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-sub {
    color: var(--muted);
    font-size: 16.5px;
    margin: 0 0 28px;
    max-width: 620px;
  }

  /* COMMAND SEARCH BAR */
  .cmd-box {
    display: flex;
    gap: 10px;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 8px;
    border-radius: 12px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.55), 0 0 25px rgba(56, 189, 248, 0.08);
  }
  .cmd-input-wrap {
    display: flex;
    align-items: center;
    flex: 1;
    padding-left: 12px;
    gap: 10px;
  }
  .cmd-box input {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--text);
    font-size: 15.5px;
    outline: none;
    font-family: 'JetBrains Mono', monospace;
  }
  .cmd-btn {
    background: linear-gradient(135deg, #38bdf8, #0284c7);
    color: #040711;
    border: none;
    padding: 13px 24px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 14.5px;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .cmd-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35); }
  .cmd-btn:disabled { background: #334155; color: #94a3b8; cursor: wait; }

  .quick-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    margin-top: 14px;
    font-size: 12.5px;
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
    font-size: 12px;
    transition: 0.15s;
  }
  .pill-btn:hover { border-color: var(--cyan); color: var(--cyan); }

  /* HERO RIGHT: ORBITAL TELEMETRY GRAPHIC CARD */
  .telemetry-card {
    background: var(--panel);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px;
    position: relative;
    overflow: hidden;
  }
  .telemetry-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11px;
    color: var(--muted);
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 10px;
    margin-bottom: 14px;
  }
  .radar-wrap {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 16px;
  }
  .kpi-mini-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .kpi-mini {
    background: rgba(2, 6, 23, 0.65);
    border: 1px solid var(--border-subtle);
    padding: 10px;
    border-radius: 8px;
  }
  .kpi-mini .val { font-size: 17px; font-weight: 800; color: var(--text); }
  .kpi-mini .lbl { font-size: 11px; color: var(--muted); }

  /* SECTION HEADERS */
  .section {
    max-width: 1220px;
    margin: 48px auto;
    padding: 0 24px;
  }
  .section-title {
    font-size: 13px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--cyan);
    font-weight: 700;
    margin-bottom: 6px;
  }
  .section-heading {
    font-size: 26px;
    font-weight: 800;
    margin: 0 0 24px;
  }

  /* 4-PILLAR BENTO GRID */
  .bento-4 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(265px, 1fr));
    gap: 18px;
  }
  .bento-card {
    background: var(--panel);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 22px;
    transition: border-color 0.2s, transform 0.2s;
  }
  .bento-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
    transform: translateY(-2px);
  }
  .icon-box {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid var(--border);
    margin-bottom: 14px;
  }
  .bento-card h3 { margin: 0 0 8px; font-size: 17px; }
  .bento-card p { margin: 0 0 14px; color: var(--muted); font-size: 13.8px; }
  .benefit-tag {
    display: inline-block;
    font-size: 11.5px;
    font-weight: 600;
    color: #34d399;
    background: rgba(16, 185, 129, 0.1);
    padding: 4px 10px;
    border-radius: 6px;
  }

  /* ARCHITECTURE PIPELINE STRIP */
  .pipeline-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px;
  }
  .pipe-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }
  .step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: var(--cyan);
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid var(--border);
    padding: 4px 8px;
    border-radius: 6px;
  }

  /* EARLY ADOPTER / TEST USER PILOT BANNER */
  .pilot-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(6, 78, 59, 0.35));
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 14px;
    padding: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
  }
  .pilot-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  .btn-pilot-primary {
    background: #10b981;
    color: #04130e;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 14px;
    text-decoration: none;
    transition: 0.2s;
  }
  .btn-pilot-primary:hover { opacity: 0.9; transform: translateY(-1px); }
  .btn-pilot-secondary {
    background: rgba(30, 41, 59, 0.85);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    text-decoration: none;
  }

  /* LOADER & RESULTS */
  .loader-box {
    display: none;
    max-width: 680px;
    margin: 24px auto;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid var(--cyan);
    border-radius: 10px;
    padding: 16px 20px;
    color: var(--cyan);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13.5px;
  }
  #results {
    max-width: 1220px;
    margin: 36px auto 80px;
    padding: 0 24px;
    display: none;
  }
  .res-banner {
    background: linear-gradient(90deg, rgba(15,23,42,0.95), rgba(6,78,59,0.35));
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 24px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    background: var(--panel-solid);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border-subtle);
    margin-bottom: 28px;
  }
  th {
    background: #1e293b;
    color: var(--muted);
    text-align: left;
    padding: 14px;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }
  td {
    padding: 15px 14px;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 13.8px;
    vertical-align: top;
  }
  .gap { color: var(--rose); }
  .wedge { color: #34d399; }
  .email-box {
    background: #090d16;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
    white-space: pre-wrap;
    font-size: 13px;
    color: #e2e8f0;
  }
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
  .footer {
    border-top: 1px solid var(--border-subtle);
    padding: 32px 24px;
    text-align: center;
    color: var(--muted);
    font-size: 13.5px;
    margin-top: 60px;
  }
  .footer a { color: var(--cyan); text-decoration: none; }
</style>
</head>
<body>

  <!-- TOP NAVIGATION -->
  <nav class="nav">
    <div class="brand">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2">
        <circle cx="12" cy="12" r="9"/>
        <circle cx="12" cy="12" r="3" fill="#38bdf8"/>
        <path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>
      </svg>
      STAR INTEL
    </div>
    <div class="nav-pills">
      <div class="status-pill"><span class="pulse-dot"></span> Autonomous Multi-Agent Engine Online</div>
      <a href="#pilot" class="beta-cta-nav">Join Founding Test Cohort →</a>
    </div>
  </nav>

  <!-- HERO + TELEMETRY GRAPHIC -->
  <section class="hero-wrap">
    <div>
      <div class="eyebrow mono">⚡ AUTONOMOUS B2B COMPETITIVE, PRICING & GROWTH RADAR</div>
      <h1>Stop Guessing Your Market.<br><span>Tear Down Any Competitor</span> in 28 Seconds.</h1>
      <p class="hero-sub">
        Enterprise competitive intelligence tools like Klue and Crayon charge <strong>$15,000+/year</strong>.
        Paste your startup's URL below and Star Intel's multi-agent pipeline scrapes live market pricing, exposes rival product gaps, verifies domain DNS, and builds your sales displacement playbook.
      </p>

      <form class="cmd-box" onsubmit="runAnalysis(event)">
        <div class="cmd-input-wrap">
          <svg width="18" height="18" fill="none" stroke="#38bdf8" stroke-width="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <input type="text" id="urlInput" placeholder="Enter startup domain (e.g., mintlify.com, linear.app)" required />
        </div>
        <button type="submit" class="cmd-btn" id="runBtn">Run Live Teardown →</button>
      </form>

      <div class="quick-pills">
        <span>Instant 1-click test:</span>
        <button type="button" class="pill-btn" onclick="fillAndRun('mintlify.com')">mintlify.com</button>
        <button type="button" class="pill-btn" onclick="fillAndRun('linear.app')">linear.app</button>
        <button type="button" class="pill-btn" onclick="fillAndRun('forgepoint.ai')">forgepoint.ai</button>
        <button type="button" class="pill-btn" onclick="fillAndRun('resend.com')">resend.com</button>
      </div>

      <div class="loader-box" id="loader">
        [1/3] Scraping live product & pricing signals via Jina Reader...<br>
        [2/3] Running Multi-Agent Competitor Matrix + Red-Team CSO Loop...<br>
        [3/3] Verifying live DNS & rendering executive battlecard (~25s)...
      </div>
    </div>

    <!-- RIGHT GRAPHIC: ORBITAL RADAR & COST BENCHMARK -->
    <div class="telemetry-card">
      <div class="telemetry-header mono">
        <span>SIGNAL TELEMETRY // LIVE BENCHMARK</span>
        <span style="color:#34d399">● ACTIVE</span>
      </div>
      <div class="radar-wrap">
        <svg width="115" height="115" viewBox="0 0 120 120" style="flex-shrink:0">
          <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(56,189,248,0.2)" stroke-width="1.5"/>
          <circle cx="60" cy="60" r="36" fill="none" stroke="rgba(56,189,248,0.25)" stroke-dasharray="4 4" stroke-width="1.5"/>
          <circle cx="60" cy="60" r="18" fill="none" stroke="rgba(16,185,129,0.35)" stroke-width="1.5"/>
          <line x1="60" y1="6" x2="60" y2="114" stroke="rgba(56,189,248,0.15)"/>
          <line x1="6" y1="60" x2="114" y2="60" stroke="rgba(56,189,248,0.15)"/>
          <polygon points="60,60 98,24 108,48" fill="rgba(56,189,248,0.22)"/>
          <circle cx="82" cy="38" r="4" fill="#34d399"/>
          <circle cx="42" cy="78" r="3.5" fill="#fb7185"/>
          <circle cx="75" cy="82" r="3" fill="#38bdf8"/>
          <circle cx="60" cy="60" r="4.5" fill="#38bdf8"/>
        </svg>
        <div>
          <div style="font-size:13px;font-weight:700;color:#f8fafc;margin-bottom:6px;">Adversarial Multi-Agent Core</div>
          <div style="font-size:12.5px;color:#94a3b8;line-height:1.45;">
            Unlike generic ChatGPT prompts, Star Intel chains live web-scraping agents with a <strong>Red-Team Chief Strategy Officer (CSO)</strong> critic to expose real pricing tiers and sales traps.
          </div>
        </div>
      </div>
      <div class="kpi-mini-grid">
        <div class="kpi-mini">
          <div class="val" style="color:#34d399">$15,000/yr</div>
          <div class="lbl">CI Spend Saved</div>
        </div>
        <div class="kpi-mini">
          <div class="val" style="color:#38bdf8">~28 Sec</div>
          <div class="lbl">Dossier Speed</div>
        </div>
        <div class="kpi-mini">
          <div class="val" style="color:#f59e0b">CSV + MD</div>
          <div class="lbl">Instant Export</div>
        </div>
      </div>
    </div>
  </section>

  <!-- DYNAMIC RESULTS INJECTED HERE -->
  <div id="results"></div>

  <!-- WHAT STAR INTEL DOES & FOUNDER BENEFITS -->
  <section class="section">
    <div class="section-title mono">WHY FOUNDERS & GTM TEAMS USE STAR INTEL</div>
    <h2 class="section-heading">Built to Cut Consulting Spend & Win Competitive Deals</h2>

    <div class="bento-4">
      <div class="bento-card">
        <div class="icon-box">
          <svg width="22" height="22" fill="none" stroke="#38bdf8" stroke-width="2" viewBox="0 0 24 24">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
        </div>
        <h3>1. Live Pricing & Tier Arbitrage</h3>
        <p>Automatically benchmarks what your top 4 competitors charge (per-seat, usage-based, or enterprise) and recommends an exact pricing wedge to undercut them.</p>
        <span class="benefit-tag">Replaces $5k Pricing Consultants</span>
      </div>

      <div class="bento-card">
        <div class="icon-box">
          <svg width="22" height="22" fill="none" stroke="#34d399" stroke-width="2" viewBox="0 0 24 24">
            <polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>
          </svg>
        </div>
        <h3>2. Exploitable Product Gap Matrix</h3>
        <p>Maps rival technical bottlenecks, missing integrations, and deployment friction so your engineering and sales teams know exactly which features win deals.</p>
        <span class="benefit-tag">Replaces $15k/yr Klue / Crayon</span>
      </div>

      <div class="bento-card">
        <div class="icon-box">
          <svg width="22" height="22" fill="none" stroke="#fb7185" stroke-width="2" viewBox="0 0 24 24">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <h3>3. Red-Team CSO Stress-Test</h3>
        <p>Every dossier passes through an adversarial Chief Strategy Officer critique loop that warns you where competitors can still beat you and how to neutralize them.</p>
        <span class="benefit-tag">Zero Fluff / Board-Ready</span>
      </div>

      <div class="bento-card">
        <div class="icon-box">
          <svg width="22" height="22" fill="none" stroke="#f59e0b" stroke-width="2" viewBox="0 0 24 24">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
          </svg>
        </div>
        <h3>4. Verified DNS & Outbound Hooks</h3>
        <p>Verifies live domain DNS records, extracts published contact emails, and generates a 100-word First-Customer cold email ready to paste into your outbound sequence.</p>
        <span class="benefit-tag">Replaces $4k/mo SDR Agencies</span>
      </div>
    </div>
  </section>

  <!-- HOW THE MULTI-AGENT PIPELINE WORKS -->
  <section class="section">
    <div class="section-title mono">UNDER THE HOOD</div>
    <h2 class="section-heading">4-Stage Autonomous Agent Architecture</h2>
    <div class="pipeline-strip">
      <div class="pipe-step">
        <span class="step-num">01</span>
        <div>
          <strong>Signal Harvester</strong>
          <div style="font-size:13px;color:var(--muted);">Scrapes target homepage, pricing docs, and market alternatives with SQLite caching.</div>
        </div>
      </div>
      <div class="pipe-step">
        <span class="step-num">02</span>
        <div>
          <strong>DNS & Mail Verifier</strong>
          <div style="font-size:13px;color:var(--muted);">Resolves live socket DNS records and extracts verified @domain contacts.</div>
        </div>
      </div>
      <div class="pipe-step">
        <span class="step-num">03</span>
        <div>
          <strong>Multi-Agent + Red-Team</strong>
          <div style="font-size:13px;color:var(--muted);">Synthesizes competitor matrix and runs adversarial CSO vulnerability checks.</div>
        </div>
      </div>
      <div class="pipe-step">
        <span class="step-num">04</span>
        <div>
          <strong>CSV & Battlecard Export</strong>
          <div style="font-size:13px;color:var(--muted);">Renders interactive executive battlecard and 1-click spreadsheet export.</div>
        </div>
      </div>
    </div>
  </section>

  <!-- FOUNDING TEST USER / EARLY ACCESS COHORT -->
  <section class="section" id="pilot">
    <div class="pilot-card">
      <div style="max-width:680px;">
        <div class="section-title mono" style="color:#34d399;">FOUNDING DESIGN PARTNER PROGRAM</div>
        <h2 style="margin:6px 0 10px;font-size:24px;">Want Automated Weekly Competitor, Pricing & Lead Briefings?</h2>
        <p style="margin:0;color:#cbd5e1;font-size:14.5px;">
          We are onboarding <strong>founding test startups</strong> to receive custom weekly competitor price-drop alerts, SBIR/grant matches, and 50 high-intent buyer leads delivered straight to your inbox. Test the full automated pipeline with us and help shape our roadmap.
        </p>
      </div>
      <div class="pilot-actions">
        <a class="btn-pilot-primary" href="mailto:jmakhanuh@gmail.com?subject=Star%20Intel%20Founding%20Test%20User%20Request&body=Hi%20Idriss%2C%0A%0AWe%20tested%20Star%20Intel%20and%20would%20love%20to%20join%20the%20Founding%20Test%20Cohort%20for%20weekly%20competitor%20and%20lead%20briefings.%0A%0AOur%20Startup%20URL%3A%20%0ATop%20Competitors%20to%20Track%3A%20">
          ✉ Request Custom Pilot (Email)
        </a>
        <a class="btn-pilot-secondary" href="https://wa.me/254790758050?text=Hi%20Idriss%2C%20I%20just%20tested%20Star%20Intel%20and%20want%20to%20try%20the%20Founding%20Test%20User%20weekly%20briefings." target="_blank">
          💬 WhatsApp / Call (+254790758050)
        </a>
      </div>
    </div>
  </section>

  <footer class="footer">
    Built by <strong>Idriss</strong> &nbsp;|&nbsp;
    Email: <a href="mailto:jmakhanuh@gmail.com">jmakhanuh@gmail.com</a> &nbsp;|&nbsp;
    Phone / WhatsApp: <a href="tel:+254790758050">+254790758050</a> &nbsp;|&nbsp;
    <a href="https://github.com/jmakhanu/Star-intel" target="_blank">GitHub</a>
  </footer>

<script>
let lastData = null;

function fillAndRun(domain) {
  document.getElementById('urlInput').value = domain;
  document.getElementById('runBtn').click();
}

async function runAnalysis(e) {
  e.preventDefault();
  const url = document.getElementById('urlInput').value.trim();
  const btn = document.getElementById('runBtn');
  const loader = document.getElementById('loader');
  const resDiv = document.getElementById('results');

  btn.disabled = true;
  btn.innerText = "Synthesizing...";
  loader.style.display = "block";
  resDiv.style.display = "none";

  try {
    const resp = await fetch('/api/analyze?url=' + encodeURIComponent(url));
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    lastData = data;
    renderDashboard(data);
    resDiv.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert("Analysis error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = "Run Live Teardown →";
    loader.style.display = "none";
  }
}

function downloadCSV() {
  if (!lastData || !lastData.competitor_matrix) return;
  const rows = lastData.competitor_matrix;
  const keys = Object.keys(rows[0]);
  const csv = [keys.join(','), ...rows.map(r => keys.map(k => '"' + String(r[k]||'').replace(/"/g,'""') + '"').join(','))].join('\\n');
  const blob = new Blob([csv], {type: 'text/csv'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'StarIntel_' + (lastData.startup_name || 'Competitors') + '.csv';
  a.click();
}

function renderDashboard(d) {
  const p = d.pricing_and_packaging_strategy || {};
  const comps = d.competitor_matrix || [];
  const plays = d.growth_playbooks || [];
  const em = d.ready_to_send_customer_email || {};
  const domainName = encodeURIComponent(d.domain || '');

  let rowsHtml = comps.map(c => `
    <tr>
      <td><strong>${c.competitor_name||''}</strong><br><span class="mono" style="color:#64748b;font-size:12px">${c.competitor_domain||''}</span></td>
      <td><span class="mono" style="background:#1e293b;padding:4px 8px;border-radius:4px;font-size:12px;">${c.pricing_model_and_cost||''}</span></td>
      <td>${c.core_product_strength||''}</td>
      <td class="gap">${c.exploitable_product_gap||''}</td>
      <td class="wedge">${c.sales_displacement_wedge||''}</td>
    </tr>`).join('');

  let playsHtml = plays.map(pl => `
    <div class="bento-card">
      <div class="section-title mono">${pl.growth_channel||''}</div>
      <p style="color:#f8fafc;margin-top:6px;">${pl.tactical_action||''}</p>
      <div class="benefit-tag">Expected ROI: ${pl.expected_roi||''}</div>
    </div>`).join('');

  const resDiv = document.getElementById('results');
  resDiv.innerHTML = `
    <div class="res-banner">
      <div>
        <div class="section-title mono">LIVE INTELLIGENCE DOSSIER GENERATED</div>
        <h2 style="margin:4px 0;">${d.startup_name || d.domain} — Growth, Pricing & Competitor Matrix</h2>
        <div style="font-size:13.5px;color:#cbd5e1;margin-top:4px;">${d.core_product_summary||''}</div>
        <div class="mono" style="font-size:12px;color:#38bdf8;margin-top:6px;">
          DNS Verified: ${d.dns_live ? 'ONLINE' : 'UNVERIFIED'} | Published Site Contacts: ${(d.verified_emails||[]).join(', ') || 'Protected / Use Contact Form'}
        </div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn-dl" onclick="downloadCSV()">⬇ Export Competitor Matrix (.CSV)</button>
        <a class="btn-pilot-primary" href="mailto:jmakhanuh@gmail.com?subject=Custom%20Weekly%20Radar%20for%20${domainName}&body=Hi%20Idriss%2C%0A%0AI%20just%20ran%20a%20live%20teardown%20for%20${domainName}%20on%20Star%20Intel.%20I%27d%20like%20to%20test%20the%20automated%20weekly%20competitor%20%26%20buyer-lead%20briefings.">
          ⚡ Activate Weekly Radar for ${d.domain}
        </a>
      </div>
    </div>

    <h3 style="margin-bottom:12px;">1. Pricing & Packaging Arbitrage</h3>
    <div class="grid-3">
      <div class="bento-card"><div class="section-title mono">Current / Inferred Model</div><p style="color:#f8fafc">${p.current_or_inferred_model||''}</p></div>
      <div class="bento-card"><div class="section-title mono">Market Pricing Benchmark</div><p style="color:#f8fafc">${p.market_pricing_benchmark||''}</p></div>
      <div class="bento-card"><div class="section-title mono">Recommended Pricing Wedge</div><p style="color:#34d399">${p.recommended_pricing_wedge||''}</p></div>
    </div>

    <h3 style="margin-bottom:12px;">2. Competitor Product, Pricing & Displacement Matrix</h3>
    <table>
      <thead><tr><th>Competitor</th><th>Pricing & Tiers</th><th>Core Strength</th><th>Exploitable Product Gap</th><th>Sales Displacement Wedge</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>

    <h3 style="margin-bottom:12px;">3. Startup Growth Playbooks</h3>
    <div class="grid-3">${playsHtml}</div>

    <h3 style="margin-bottom:12px;">4. Red-Team Chief Strategy Officer (CSO) Verdict</h3>
    <div class="bento-card" style="border-color:#fb7185;background:rgba(127,29,29,0.2);color:#fecdd3;margin-bottom:28px;">
      ${d.red_team_cso_verdict||''}
    </div>

    <h3 style="margin-bottom:12px;">5. Ready-to-Send Outbound Pitch Email</h3>
    <div class="email-box">Subject: ${em.subject||''}\n\n${em.body||''}</div>
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
            if not raw_url:
                self.send_json({"error": "Missing url parameter"}, 400)
                return
            try:
                init_db()
                clean_url = raw_url.replace("https://", "").replace("http://", "").split("/")[0]
                startup_home = fetch_web_signal(clean_url)
                startup_pricing = fetch_web_signal(f"{clean_url} pricing products features competitors")
                market_search = fetch_web_signal(f"top competitors alternatives and pricing for {clean_url}")
                contact_info = verify_domain_and_emails(clean_url)

                sys_p = f"""You are Star Intel's Autonomous Startup Growth, Pricing & Competitive Intelligence Engine.
Analyze {clean_url} and return ONLY valid JSON with keys:
startup_name, core_product_summary, annual_consulting_cost_saved,
pricing_and_packaging_strategy (keys: current_or_inferred_model, market_pricing_benchmark, recommended_pricing_wedge),
competitor_matrix (list of 4 objects with keys: competitor_name, competitor_domain, pricing_model_and_cost, core_product_strength, exploitable_product_gap, sales_displacement_wedge),
growth_playbooks (list of 3 objects with keys: growth_channel, tactical_action, expected_roi),
red_team_cso_verdict,
ready_to_send_customer_email (keys: subject, body)."""
                user_p = f"STARTUP ({clean_url}):\n{startup_home[:3000]}\n\nPRICING:\n{startup_pricing[:2500]}\n\nCOMPETITORS:\n{market_search[:3000]}"
                data = call_llm(sys_p, user_p)
                data["domain"] = clean_url
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
    print(f"[+] Star Intel Web Portal running at: http://localhost:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StarIntelHandler)
    server.serve_forever()
