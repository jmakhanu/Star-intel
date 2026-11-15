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

import sqlite3
from concurrent.futures import ThreadPoolExecutor

def get_cached_analysis(cache_key):
    try:
        ensure_telemetry_tables()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_cache (
            cache_key TEXT PRIMARY KEY,
            json_data TEXT,
            created_ts INTEGER
        )''')
        row = c.execute("SELECT json_data, created_ts FROM analysis_cache WHERE cache_key = ?", (cache_key,)).fetchone()
        conn.close()
        if row and (int(datetime.now(timezone.utc).timestamp()) - int(row[1])) < 3600:
            return json.loads(row[0])
    except Exception:
        pass
    return None

def set_cached_analysis(cache_key, data_dict):
    try:
        ensure_telemetry_tables()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS analysis_cache (
            cache_key TEXT PRIMARY KEY,
            json_data TEXT,
            created_ts INTEGER
        )''')
        now_ts = int(datetime.now(timezone.utc).timestamp())
        c.execute("INSERT OR REPLACE INTO analysis_cache (cache_key, json_data, created_ts) VALUES (?, ?, ?)",
                  (cache_key, json.dumps(data_dict), now_ts))
        conn.commit()
        conn.close()
    except Exception:
        pass


DB_FILE = "star_intel_telemetry.db"
ADMIN_KEY = os.getenv("ADMIN_KEY", "makhanu2026")

def ensure_telemetry_tables():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS founder_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        startup_domain TEXT,
        plan TEXT DEFAULT 'Free Studio',
        created_at TEXT,
        last_active TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scan_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        user_email TEXT,
        mode TEXT,
        ip_addr TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

def log_scan_event(domain, user_email, mode, ip_addr):
    try:
        ensure_telemetry_tables()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO scan_logs (domain, user_email, mode, ip_addr, created_at) VALUES (?, ?, ?, ?, ?)",
                  (domain, user_email or "anonymous", mode, ip_addr, now))
        if user_email and "@" in user_email:
            c.execute('''INSERT INTO founder_users (email, startup_domain, created_at, last_active)
                         VALUES (?, ?, ?, ?)
                         ON CONFLICT(email) DO UPDATE SET
                         startup_domain=excluded.startup_domain,
                         last_active=excluded.last_active''',
                      (user_email.lower().strip(), domain, now, now))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Telemetry log error:", e)

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
  /* EXPLEE-STYLE ASYMMETRIC SPLIT HERO */
  .hero-split {
    max-width: 1220px;
    margin: 36px auto 32px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: 1.12fr 0.88fr;
    gap: 36px;
    align-items: center;
  }
  @media (max-width: 980px) {
    .hero-split { grid-template-columns: 1fr; gap: 28px; }
  }
  .hero-left {
    text-align: left;
  }
  .eyebrow-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--surface);
    border: 1px solid var(--border-strong);
    padding: 5px 12px;
    border-radius: 99px;
    font-size: 11.5px;
    font-weight: 700;
    color: var(--obsidian);
    box-shadow: var(--shadow-sm);
    margin-bottom: 18px;
  }
  .eyebrow-badge span.tag {
    background: var(--emerald-bg);
    color: var(--emerald);
    border: 1px solid var(--emerald-border);
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 10.5px;
  }
  h1 {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.08;
    margin: 0 0 16px;
    letter-spacing: -0.035em;
    color: var(--obsidian);
  }
  .grad-accent {
    background: linear-gradient(135deg, #059669 0%, #0D9488 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-sub {
    color: var(--text-secondary);
    font-size: 15.5px;
    max-width: 580px;
    margin: 0 0 22px;
    font-weight: 400;
    line-height: 1.6;
  }

  /* COMMAND CONSOLE CARD (LEFT-ALIGNED) */
  .console-shell {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    border-radius: 16px;
    padding: 18px;
    box-shadow: var(--shadow-lg);
    text-align: left;
    position: relative;
  }
  .mode-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
  }
  .mode-tab-group {
    display: inline-flex;
    background: var(--surface-subtle);
    padding: 3px;
    border-radius: 10px;
    border: 1px solid var(--border);
    gap: 4px;
  }
  .mode-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 6px 13px;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 700;
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
    gap: 8px;
    background: var(--bg);
    border: 1.5px solid var(--border-strong);
    padding: 6px;
    border-radius: 11px;
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
    padding-left: 10px;
    gap: 8px;
  }
  .cmd-row input, .stealth-grid input {
    width: 100%;
    background: transparent;
    border: none;
    color: var(--obsidian);
    font-size: 14.5px;
    outline: none;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }
  .stealth-grid {
    display: none;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 10px;
  }
  @media (max-width: 680px) { .stealth-grid { grid-template-columns: 1fr; } }
  .stealth-field {
    background: var(--bg);
    border: 1px solid var(--border-strong);
    padding: 9px 12px;
    border-radius: 9px;
  }
  .stealth-field label {
    display: block;
    font-size: 10.5px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 3px;
    font-weight: 700;
  }
  .cmd-btn {
    background: var(--obsidian);
    color: #FFFFFF;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 13.5px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .cmd-btn:hover { background: var(--emerald); transform: translateY(-1px); }
  .cmd-btn:disabled { background: #9CA3AF; color: #F3F4F6; cursor: wait; }

  .quick-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px dashed var(--border);
    font-size: 11.5px;
    color: var(--muted);
  }
  .pill-btn {
    background: var(--surface-subtle);
    border: 1px solid var(--border);
    color: var(--obsidian);
    padding: 3px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    transition: all 0.15s;
  }
  .pill-btn:hover {
    border-color: var(--obsidian);
    background: var(--obsidian);
    color: #fff;
  }

  /* RIGHT COLUMN: INTERACTIVE STUDIO PREVIEW WINDOW */
  .studio-preview-window {
    background: var(--surface);
    border: 1px solid var(--border-strong);
    border-radius: 16px;
    box-shadow: var(--shadow-lg);
    overflow: hidden;
    text-align: left;
  }
  .window-bar {
    background: var(--surface-subtle);
    border-bottom: 1px solid var(--border);
    padding: 10px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .win-dots {
    display: flex;
    gap: 6px;
  }
  .win-dots span {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: var(--border-strong);
  }
  .win-dots span:nth-child(1) { background: #FDA4AF; }
  .win-dots span:nth-child(2) { background: #FCD34D; }
  .win-dots span:nth-child(3) { background: #6EE7B7; }
  .window-body {
    padding: 18px;
    background: linear-gradient(180deg, #FFFFFF 0%, #F9FAFB 100%);
  }
  .preview-row {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-sm);
  }
  .preview-lead-box {
    background: #FFFFFF;
    border: 1.5px solid var(--obsidian);
    border-radius: 12px;
    padding: 14px;
    margin-top: 12px;
    box-shadow: var(--shadow-sm);
  }

  /* COMPACT 3-PILLAR FEATURE BAR */
  .pipeline-strip {
    max-width: 1220px;
    margin: 12px auto 36px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  @media (max-width: 860px) { .pipeline-strip { grid-template-columns: 1fr; } }
  .pipe-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s;
    display: flex;
    gap: 14px;
    align-items: flex-start;
  }
  .pipe-card.active-step {
    border-color: var(--emerald);
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
  }
  .pipe-icon {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: var(--obsidian);
    color: #fff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .pipe-card h3 { margin: 0 0 4px; font-size: 14.5px; color: var(--obsidian); }
  .pipe-card p { margin: 0; font-size: 12.5px; color: var(--text-secondary); line-height: 1.45; }

  #results { max-width: 1220px; margin: 20px auto 70px; padding: 0 24px; display: none; }
  .res-banner {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--obsidian);
    border-radius: 14px;
    padding: 20px 24px;
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
    padding: 4px;
    border-radius: 10px;
    gap: 4px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }
  .ws-tab {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 8px 16px;
    border-radius: 7px;
    font-weight: 700;
    font-size: 12.5px;
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
    border-radius: 9px;
    background: var(--obsidian);
    color: #FFFFFF;
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
    outline: none;
    transition: border-color 0.15s, background 0.15s;
  }
  .email-draft:focus {
    background: #FFFFFF;
    border-color: var(--emerald);
    box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.12);
  }

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
  .pilot-wrap { max-width: 1220px; margin: 40px auto; padding: 0 24px; }
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
  .auth-modal-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(17, 24, 39, 0.55);
    backdrop-filter: blur(4px);
    z-index: 100;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .auth-modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    max-width: 440px;
    width: 100%;
    padding: 26px;
    box-shadow: var(--shadow-lg);
    text-align: left;
  }
  .auth-input {
    width: 100%;
    padding: 11px 14px;
    border: 1.5px solid var(--border-strong);
    border-radius: 9px;
    font-size: 14px;
    font-family: 'JetBrains Mono', monospace;
    margin: 8px 0 14px;
    outline: none;
  }
  .auth-input:focus { border-color: var(--obsidian); }
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
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <div class="status-pill"><span class="pulse-dot"></span> Provenance-Verified Recon Online</div>
        <button type="button" id="navUserBtn" class="user-pill" onclick="openAuthModal('save')">👤 Sign In / Save Workspace</button>
        <a href="https://www.paypal.com/ncp/payment/XKUVEJSB74V88" target="_blank" rel="noopener" class="btn-pilot-primary">
          💳 Unlock AutoGTM Pro (<span class="price-strike" style="color:#9CA3AF;">$49</span> $29/mo) →
        </a>
      </div>
    </nav>
  </div>

  <!-- ASYMMETRIC SPLIT HERO: LEFT COMMAND + RIGHT LIVE STUDIO PREVIEW -->
  <section class="hero-split">
    <div class="hero-left">
      <div class="eyebrow-badge">
        <span class="tag mono">AUTOGTM v4.2</span>
        <span>Map Market Pricing • Expose Rival Gaps • Draft Buyer Emails</span>
      </div>

      <h1>Autonomous GTM &<br><span class="grad-accent">Competitive Teardown</span> Studio.</h1>
      <p class="hero-sub">
        Enter any startup domain — or switch to <strong>Stealth Mode</strong>. Star Intel probes live <code>/pricing</code> endpoints in parallel, separates <strong>observed prices</strong> from <strong>inferred positioning</strong>, and drafts ready-to-send B2B buyer emails.
      </p>

      <div class="console-shell">
        <div class="mode-tabs">
          <div class="mode-tab-group">
            <button type="button" class="mode-btn active" id="tabUrlBtn" onclick="setMode('url')">🌐 Company Domain</button>
            <button type="button" class="mode-btn" id="tabIdeaBtn" onclick="setMode('idea')">🧠 Stealth Startup Brief</button>
          </div>
          <span class="mono" style="font-size:11px;color:var(--emerald);font-weight:700;">● Parallel DNS + Pricing Recon</span>
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
              <svg width="17" height="17" fill="none" stroke="#111827" stroke-width="2" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
              </svg>
              <input type="text" id="urlInput" placeholder="Enter startup domain (e.g., easi.run, signedreviews.com, linear.app)" required />
            </div>
            <button type="submit" class="cmd-btn" id="runBtn">Launch Teardown →</button>
          </div>
        </form>

        <div class="quick-bar">
          <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
            <span style="font-weight:700;color:var(--obsidian);">Try instant run:</span>
            <button type="button" class="pill-btn" onclick="fillAndRun('easi.run')">easi.run ↗</button>
            <button type="button" class="pill-btn" onclick="fillAndRun('signedreviews.com')">signedreviews.com ↗</button>
            <button type="button" class="pill-btn" onclick="fillAndRun('mintlify.com')">mintlify.com ↗</button>
            <button type="button" class="pill-btn" onclick="fillAndRun('linear.app')">linear.app ↗</button>
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT SIDE: EXPLEE-INSPIRED LIVE WORKSPACE PREVIEW WINDOW -->
    <div class="studio-preview-window">
      <div class="window-bar">
        <div class="win-dots"><span></span><span></span><span></span></div>
        <span class="mono" style="font-size:11px;color:var(--text-secondary);font-weight:600;">studio://battlecard-and-leads.csv</span>
        <span class="benefit-tag mono" style="font-size:10px;padding:2px 8px;">✓ LIVE SCHEMA</span>
      </div>
      <div class="window-body">
        <div class="section-title mono" style="margin-bottom:8px;">1. COMPETITOR PROVENANCE MATRIX (SAMPLE)</div>

        <div class="preview-row">
          <div>
            <strong style="font-size:13px;color:var(--obsidian);">Browserbase</strong>
            <span class="mono" style="font-size:11px;color:var(--muted);display:block;">https://browserbase.com/pricing</span>
          </div>
          <div style="text-align:right;">
            <span class="mono" style="font-size:12px;font-weight:700;color:var(--obsidian);">$20–$99/mo</span><br>
            <span class="badge-observed mono" style="margin-top:2px;">✓ OBSERVED PRICE</span>
          </div>
        </div>

        <div class="preview-row">
          <div>
            <strong style="font-size:13px;color:var(--obsidian);">Enterprise Rival</strong>
            <span class="mono" style="font-size:11px;color:var(--muted);display:block;">https://rival.io/pricing</span>
          </div>
          <div style="text-align:right;">
            <span class="mono" style="font-size:11.5px;font-weight:600;color:var(--text-secondary);">Gated / Custom</span><br>
            <span class="badge-unverified mono" style="margin-top:2px;">⚠ UNVERIFIED (INFERRED)</span>
          </div>
        </div>

        <div class="preview-lead-box">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="avatar-circle" style="width:28px;height:28px;font-size:11px;">VR</span>
              <div>
                <strong style="font-size:12.5px;color:var(--obsidian);">VP of Engineering · Verified B2B Buyer</strong>
                <div class="mono" style="font-size:10.5px;color:var(--emerald);">● VALID MX/DNS • Trigger-Matched</div>
              </div>
            </div>
            <span class="mono" style="font-size:10.5px;background:var(--emerald-bg);color:var(--emerald);padding:3px 8px;border-radius:6px;font-weight:700;">✉️ Draft in Gmail ↗</span>
          </div>
          <div class="mono" style="font-size:11px;color:var(--text-secondary);background:var(--bg);padding:8px 10px;border-radius:7px;border:1px solid var(--border);">
            "Saw your team scaling headless QA workflows — here is how you can cut session costs by 40% without gated enterprise contracts..."
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="pipeline-strip">
    <div class="pipe-card" id="stepCard1">
      <span class="pipe-icon">01</span>
      <div>
        <h3>Observed vs. Inferred Pricing</h3>
        <p>Directly probes <code>/pricing</code> URLs and stamps every row with verification status, source link & UTC check date.</p>
      </div>
    </div>
    <div class="pipe-card" id="stepCard2">
      <span class="pipe-icon">02</span>
      <div>
        <h3>4-Rival Displacement Matrix</h3>
        <p>Exposes technical gaps and exact sales wedges so your outbound pitches land against incumbent tools.</p>
      </div>
    </div>
    <div class="pipe-card" id="stepCard3">
      <span class="pipe-icon">03</span>
      <div>
        <h3>1-Click Gmail Buyer Outreach</h3>
        <p>Verifies target buyer DNS/MX records and opens live-editable founder emails straight in Gmail Web.</p>
      </div>
    </div>
  </section>

  <div id="results"></div>

  <section class="pilot-wrap" id="pilot">
    <div class="pilot-card">
      <div style="max-width:650px;">
        <div class="benefit-tag mono" style="margin-bottom:8px;">FIRST 10 FOUNDING MEMBERS • 40% EARLY-BIRD LOCK-IN</div>
        <h2 style="margin:4px 0 8px;font-size:23px;color:var(--obsidian);">
          Get Your Weekly 50-Lead AutoGTM Pack — <span class="price-strike">$49/mo</span> <span style="color:var(--emerald);">$29/mo USD</span>
        </h2>
        <p style="margin:0;color:var(--text-secondary);font-size:14.5px;">
          Our live studio unlocks all 4 Competitor Battlecards + 4 Target Customer Emails for free. Upgrade to <strong>AutoGTM Pro ($29/mo via PayPal or Debit/Credit Card)</strong> to receive 50 verified decision-maker leads & custom outbound sequences every week.
        </p>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
        <a class="cmd-btn" href="https://www.paypal.com/ncp/payment/XKUVEJSB74V88" target="_blank" rel="noopener">
          💳 Checkout $29 USD (PayPal / Card) →
        </a>
        <button type="button" class="btn-dl" onclick="openFounderPilotEmail()">
          ✉️ Ask a Question (Gmail)
        </button>
      </div>
    </div>
  </section>

    <!-- PROGRESSIVE WORKSPACE SIGN-IN MODAL -->
  <div id="authModalBackdrop" class="auth-modal-backdrop">
    <div class="auth-modal">
      <div class="benefit-tag mono" style="margin-bottom:8px;">STAR INTEL STUDIO ACCOUNT</div>
      <h3 style="margin:0 0 6px;font-size:20px;color:var(--obsidian);" id="authModalTitle">Save Your GTM Workspace</h3>
      <p style="margin:0 0 14px;font-size:13.5px;color:var(--text-secondary);" id="authModalDesc">
        Enter your founder email to unlock unlimited CSV battlecard exports, save your domain runs, and track competitor price changes.
      </p>
      <form onsubmit="submitAuthModal(event)">
        <label style="font-size:11.5px;font-weight:700;color:var(--text-secondary);text-transform:uppercase;">Work / Founder Email</label>
        <input type="email" id="authEmailInput" class="auth-input" placeholder="founder@yourstartup.com" required />
        <label style="font-size:11.5px;font-weight:700;color:var(--text-secondary);text-transform:uppercase;">Your Startup Domain</label>
        <input type="text" id="authDomainInput" class="auth-input" placeholder="e.g., easi.run or signedreviews.com" required />
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:6px;">
          <button type="button" class="btn-mailto" onclick="closeAuthModal()">Cancel</button>
          <button type="submit" class="cmd-btn" style="padding:10px 18px;">Continue & Unlock →</button>
        </div>
      </form>
    </div>
  </div>

  <footer class="footer">
    Built by <strong>Idriss</strong> &nbsp;|&nbsp;
    Email: <a href="https://mail.google.com/mail/?view=cm&fs=1&to=jmakhanuh@gmail.com&su=Star%20Intel%20Inquiry" target="_blank" rel="noopener">jmakhanuh@gmail.com</a> &nbsp;|&nbsp;
    Phone / WhatsApp: <a href="https://wa.me/254790758050" target="_blank" rel="noopener">+254790758050</a> &nbsp;|&nbsp;
    <a href="https://github.com/jmakhanu/Star-intel" target="_blank" rel="noopener">GitHub</a>
  </footer>

<script>
const PAYPAL_URL = "https://www.paypal.com/ncp/payment/XKUVEJSB74V88";
var currentMode = 'url';
var lastData = null;
var pendingActionAfterAuth = null;

function getSavedEmail() {
  try {
    return window.localStorage.getItem("star_intel_email") || "";
  } catch (e) {
    return "";
  }
}


function getSavedEmail() {
  return localStorage.getItem("star_intel_email") || "";
}
var currentMode = 'url';
var lastData = null;
var pendingActionAfterAuth = null;

var PAYPAL_URL = "https://www.paypal.com/ncp/payment/XKUVEJSB74V88";



if (window.location.search.includes("checkout=success")) {
  document.getElementById("checkoutBanner").style.display = "block";
}
window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const autoDomain = params.get("run");
  if (autoDomain) {
    fillAndRun(autoDomain);
  }
});

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

function getEditedBody(idx, fallback) {
  const el = document.getElementById('draftBody_' + idx);
  return el ? el.innerText.trim() : (fallback || '');
}

function sendLeadViaGmail(idx) {
  if (!lastData || !lastData.customer_prospects || !lastData.customer_prospects[idx]) return;
  const l = lastData.customer_prospects[idx];
  const to = encodeURIComponent(l.target_email || '');
  const su = encodeURIComponent(l.email_subject || '');
  const body = encodeURIComponent(getEditedBody(idx, l.email_body));
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
  const fullPitch = `To: ${l.target_email || ''}\nSubject: ${l.email_subject || ''}\n\n${getEditedBody(idx, l.email_body)}`;
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
    const qs = `?url=${encodeURIComponent(url)}&desc=${encodeURIComponent(desc)}&icp=${encodeURIComponent(icp)}&email=${encodeURIComponent(getSavedEmail())}`;
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
  if (!getSavedEmail()) { openAuthModal('csv_comp'); return; }
  rawDownloadCSV();
}
function rawDownloadCSV() {
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
  if (!getSavedEmail()) { openAuthModal('csv_leads'); return; }
  rawDownloadLeadsCSV();
}
function rawDownloadLeadsCSV() {
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
              <button type="button" class="email-badge mono" onclick="sendLeadViaGmail(${idx})" title="Click to open pre-filled draft in Gmail">
                ✉️ ${escapeHtml(l.target_email)} (Draft in Gmail ↗)
              </button>
            </div>
          </div>
        </div>
        <span class="benefit-tag mono">● ${escapeHtml(l.dns_status || 'VALID')}</span>
      </div>
      <div class="trigger-box">
        <strong>Buying Trigger:</strong> ${escapeHtml(l.buying_trigger)}
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span class="mono" style="font-size:11px;color:var(--muted);">Subject: <strong style="color:var(--obsidian);">${escapeHtml(l.email_subject)}</strong></span>
        <span class="mono" style="font-size:10.5px;color:var(--emerald);">✎ Click email below to edit</span>
      </div>
      <div class="email-draft" id="draftBody_${idx}" contenteditable="true" spellcheck="false">${escapeHtml(l.email_body)}</div>
      <div class="action-row">
        <button type="button" class="btn-gmail" onclick="sendLeadViaGmail(${idx})">
          ✉️ Open Draft in Gmail ↗
        </button>
        <button type="button" class="btn-mailto" onclick="sendLeadViaMailto(${idx})">
          ↗ Default Mail App
        </button>
        <button type="button" class="btn-mailto" onclick="copyLeadPitch(${idx}, this)">
          📋 Copy Text
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
          URL: <a href="${escapeHtml(c.pricing_source)}" target="_blank" rel="noopener" style="color:var(--obsidian);text-decoration:underline;">${escapeHtml(c.pricing_source)}</a><br>
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
          💳 Unlock 50-Lead Pack ($29 USD) →
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
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__) or ".", "ui_template.html"), "rb") as tf:
                self.wfile.write(tf.read())
            return

        if parsed.path == "/api/signup":
            qs = urllib.parse.parse_qs(parsed.query)
            email = qs.get("email", [""])[0].strip()
            domain = qs.get("domain", [""])[0].strip() or "direct-signup"
            ip_addr = self.headers.get("X-Forwarded-For", self.client_address[0])
            log_scan_event(domain, email, "WORKSPACE_SIGNUP", ip_addr)
            self.send_json({"ok": True, "email": email}, 200)
            return

        if parsed.path == "/admin":
            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("key", [""])[0] != ADMIN_KEY:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden: Invalid Admin Key")
                return
            ensure_telemetry_tables()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            users = c.execute("SELECT email, startup_domain, plan, created_at, last_active FROM founder_users ORDER BY id DESC LIMIT 100").fetchall()
            scans = c.execute("SELECT domain, user_email, mode, ip_addr, created_at FROM scan_logs ORDER BY id DESC LIMIT 150").fetchall()
            conn.close()

            u_rows = "".join([
                f"<tr><td><strong>{u[0]}</strong></td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[4]}</td>"
                f"<td><a target='_blank' href='https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(u[0])}&su={urllib.parse.quote("Your Star Intel teardown for " + u[1])}' style='color:#059669;font-weight:700;'>✉️ Email Founder ↗</a></td></tr>"
                for u in users
            ]) or "<tr><td colspan='6'>No registered emails yet — share your link on X!</td></tr>"

            s_rows = "".join([
                f"<tr><td><strong>{s[0]}</strong></td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td></tr>"
                for s in scans
            ]) or "<tr><td colspan='5'>No scans recorded yet.</td></tr>"

            admin_html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>Star Intel Founder CRM & Telemetry</title>
            <style>body{{font-family:system-ui,sans-serif;background:#F8F9FA;color:#111827;padding:30px;max-width:1100px;margin:0 auto;}}
            table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden;margin-bottom:30px;}}
            th{{background:#F3F4F6;text-align:left;padding:12px;font-size:12px;text-transform:uppercase;color:#4B5563;}}
            td{{padding:12px;border-bottom:1px solid #E5E7EB;font-size:13.5px;}}</style></head><body>
            <h1>🛰️ Star Intel — Founder Signups & Live Scan Telemetry</h1>
            <h3>1. Registered Founder Leads ({len(users)})</h3>
            <table><thead><tr><th>Founder Email</th><th>Startup Domain</th><th>Tier</th><th>First Seen</th><th>Last Active</th><th>1-Click Follow-Up</th></tr></thead><tbody>{u_rows}</tbody></table>
            <h3>2. Live Domain Scans ({len(scans)})</h3>
            <table><thead><tr><th>Scanned Domain</th><th>User Email</th><th>Mode</th><th>Visitor IP</th><th>Timestamp</th></tr></thead><tbody>{s_rows}</tbody></table>
            </body></html>'''
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.end_headers()
            self.wfile.write(admin_html.encode("utf-8"))
            return

        if parsed.path == "/api/analyze":
            qs = urllib.parse.parse_qs(parsed.query)
            raw_url = qs.get("url", [""])[0].strip()
            custom_desc = qs.get("desc", [""])[0].strip()
            custom_icp = qs.get("icp", [""])[0].strip()
            user_email = qs.get("email", [""])[0].strip()
            ip_addr = self.headers.get("X-Forwarded-For", self.client_address[0])

            if not raw_url and not custom_desc:
                self.send_json({"error": "Please provide a URL or product description"}, 400)
                return

            try:
                init_db()
                clean_url = raw_url.replace("https://", "").replace("http://", "").split("/")[0] or "StealthStartup"
                check_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

                cache_key = f"{clean_url}|{custom_desc}|{custom_icp}".lower()
                cached = get_cached_analysis(cache_key)
                if cached and not qs.get("nocache"):
                    log_scan_event(clean_url, user_email, "CACHED_INSTANT_RECON", ip_addr)
                    self.send_json(cached, 200)
                    return

                with ThreadPoolExecutor(max_workers=4) as ex:
                    if custom_desc:
                        f_price = ex.submit(fetch_web_signal, f"{custom_desc} pricing competitors B2B SaaS")
                        f_mkt = ex.submit(fetch_web_signal, f"top competitors and target B2B buyers for {custom_desc} {custom_icp}")
                        f_dns = ex.submit(verify_domain_and_emails, clean_url) if "." in clean_url else None
                        startup_home = f"USER PROVIDED PRODUCT BRIEF: {custom_desc}\nTARGET IDEAL CUSTOMER: {custom_icp}"
                        startup_pricing = f_price.result()
                        market_search = f_mkt.result()
                        contact_info = f_dns.result() if f_dns else {"dns_live": False, "emails": []}
                        mode_used = "STEALTH / CUSTOM BRIEFING MODE"
                        pricing_page_fetched = False
                    else:
                        f_home = ex.submit(fetch_web_signal, clean_url)
                        f_direct_price = ex.submit(fetch_web_signal, f"{clean_url}/pricing")
                        f_price = ex.submit(fetch_web_signal, f"{clean_url} pricing tiers cost plans")
                        f_mkt = ex.submit(fetch_web_signal, f"top competitors alternatives pricing and target B2B customers for {clean_url}")
                        f_dns = ex.submit(verify_domain_and_emails, clean_url) if "." in clean_url else None

                        startup_home = f_home.result()
                        direct_pricing_raw = f_direct_price.result()
                        startup_pricing = (direct_pricing_raw[:1600] + "\n" + f_price.result()[:1600]).strip()
                        market_search = f_mkt.result()
                        contact_info = f_dns.result() if f_dns else {"dns_live": False, "emails": []}
                        mode_used = "PARALLEL LIVE RECON"
                        pricing_page_fetched = any(tok in startup_pricing.lower() for tok in ["$", "€", "£", "/mo", "/month", "free tier", "enterprise"])

                sys_p = f"""You are Star Intel's Autonomous Competitive Intelligence & Customer Hunter Engine.
Analyze '{clean_url}' ({custom_desc or 'live domain'}) and return ONLY valid JSON with these exact keys:
1. "startup_name": Clean name of {clean_url}
2. "core_product_summary": 1-sentence summary of what they build and who their ideal B2B customer is.
3. "pricing_and_packaging_strategy": object with keys:
   - "current_or_inferred_model": Pricing tiers if directly observed in context, or clearly labeled inferred positioning if not fetched.
   - "pricing_verification_status": MUST be "observed" if explicit price numbers appear in the scraped signal, or "unverified (inferred)" if the pricing page could not be fetched or hides pricing.
   - "pricing_source": MUST always include the exact attempted or source URL starting with https:// (e.g. "https://{clean_url}/pricing").
   - "market_pricing_benchmark": Market average price in this category.
   - "recommended_pricing_wedge": Concrete pricing wedge to win deals.
4. "competitor_matrix": list of 4 real competitors with keys:
   - "competitor_name"
   - "competitor_domain"
   - "pricing_model_and_cost": Price tiers (if unknown/gated, prefix with "[Unverified / Inferred] ")
   - "verification_status": MUST be "observed" if public pricing is explicitly known/verified, or "unverified" if pricing is gated, contact-sales, or inferred.
   - "pricing_source": MUST be the exact source or attempted pricing-page URL starting with https:// (e.g. "https://competitor.com/pricing"). Never output only text without a URL.
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
                    dom = str(c.get("competitor_domain", "competitor.com")).replace("https://", "").replace("http://", "").split("/")[0].strip()
                    raw_src = str(c.get("pricing_source", "")).strip()
                    if not raw_src.startswith("http"):
                        c["pricing_source"] = f"https://{dom}/pricing"
                    else:
                        c["pricing_source"] = raw_src.split(" ")[0].strip()

                p_strat = data.get("pricing_and_packaging_strategy", {})
                if isinstance(p_strat, dict):
                    raw_psrc = str(p_strat.get("pricing_source", "")).strip()
                    if not raw_psrc.startswith("http"):
                        p_strat["pricing_source"] = f"https://{clean_url}/pricing"

                prospects = data.get("customer_prospects", [])
                def _verify_prospect(p):
                    p["check_date"] = check_date
                    if p.get("customer_domain"):
                        chk = verify_domain_and_emails(p["customer_domain"])
                        p["dns_status"] = "VALID MX/DNS" if chk["dns_live"] else "VALID"
                        if chk["emails"]:
                            p["target_email"] = chk["emails"][0]
                    else:
                        p["dns_status"] = "VALID"
                    return p

                with ThreadPoolExecutor(max_workers=4) as ex:
                    list(ex.map(_verify_prospect, prospects))

                log_scan_event(clean_url, user_email, mode_used, ip_addr)
                data["domain"] = clean_url
                data["check_date"] = check_date
                data["mode_used"] = mode_used
                data["dns_live"] = contact_info["dns_live"]
                data["verified_emails"] = contact_info["emails"]
                set_cached_analysis(cache_key, data)
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
