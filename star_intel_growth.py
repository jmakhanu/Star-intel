#!/usr/bin/env python3
"""
Star Intel Growth Engine (v3.5)
Paste ONE Startup URL -> Automatically discovers top competitors, scrapes market pricing
& product features, identifies growth wedges, checks live DNS/emails, and outputs:
  1. Eye-catching Dark-Mode HTML Growth & Pricing Dashboard (.html)
  2. Actionable Pricing & Competitor Matrix (.csv)
  3. Executive Markdown Brief + 100-word Outbound Pitch (.md)
"""

import os
import sys
import json
import csv
import re
import socket
import sqlite3
import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.parse
import urllib.error

# Load .env
for env_file in [".env", "../.env"]:
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

DB_PATH = "star_intel_v2.db"
OUTPUT_DIR = "briefings"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scrape_cache (
            query TEXT PRIMARY KEY,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def fetch_web_signal(url_or_query: str) -> str:
    target = url_or_query.strip()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content FROM scrape_cache WHERE query = ?", (target,))
    row = c.fetchone()
    conn.close()
    if row:
        print(f"    [Cache Hit] {target[:55]}")
        return row[0]

    if not target.startswith("http"):
        if "." in target and " " not in target:
            reader_url = f"https://r.jina.ai/https://{target}"
        else:
            reader_url = f"https://s.jina.ai/{urllib.parse.quote(target)}"
    else:
        reader_url = f"https://r.jina.ai/{target}"

    req = urllib.request.Request(
        reader_url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) StarIntel/3.5",
            "Accept": "text/plain"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="ignore")[:8500]
            if len(text) > 100:
                conn = sqlite3.connect(DB_PATH)
                conn.execute(
                    "INSERT OR REPLACE INTO scrape_cache (query, content, timestamp) VALUES (?, ?, ?)",
                    (target, text, datetime.now(timezone.utc).isoformat())
                )
                conn.commit()
                conn.close()
            return text
    except Exception as e:
        return f"Context for {url_or_query}: {e}"


def verify_domain_and_emails(domain_or_url: str) -> dict:
    clean_domain = re.sub(r"^https?://", "", domain_or_url.strip()).split("/")[0].replace("www.", "")
    dns_live = False
    try:
        socket.gethostbyname(clean_domain)
        dns_live = True
    except Exception:
        dns_live = False

    emails = set()
    if dns_live:
        for path in [clean_domain, f"{clean_domain}/contact", f"{clean_domain}/about"]:
            raw = fetch_web_signal(path)
            found = re.findall(r"[a-zA-Z0-9._%+-]+@" + re.escape(clean_domain), raw, re.IGNORECASE)
            for addr in found:
                emails.add(addr.lower())
            if emails:
                break
    return {"domain": clean_domain, "dns_live": dns_live, "emails": list(emails)[:5]}


def fetch_active_groq_models(api_key: str) -> list:
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "StarIntel/3.5"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            all_ids = [m["id"] for m in data.get("data", []) if m.get("active", True)]
            skip = ("whisper", "tts", "guard", "vision", "embed", "orpheus", "allam", "playai")
            chat = [m for m in all_ids if not any(s in m.lower() for s in skip)]
            chat.sort(key=lambda m: 0 if any(k in m.lower() for k in ("120b", "70b", "qwen", "llama-3.3")) else 1)
            return chat
    except Exception:
        return ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[!] ERROR: Missing GROQ_API_KEY in .env")
        sys.exit(1)

    models = fetch_active_groq_models(api_key)
    for model in models:
        payload = json.dumps({
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt + "\nIMPORTANT: Output ONLY valid raw JSON."},
                {"role": "user", "content": user_prompt}
            ]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "StarIntel/3.5"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                content = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]
                cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned)
                s, e = cleaned.find("{"), cleaned.rfind("}")
                parsed = json.loads(cleaned[s:e+1])
                print(f"    [LLM Success] Synthesized using active model: {model}")
                return parsed
        except Exception:
            continue
    raise RuntimeError("All active LLM models failed.")


def run_startup_growth_engine(startup_url: str):
    init_db()
    clean_url = re.sub(r"^https?://", "", startup_url.strip()).split("/")[0]
    print(f"[*] [1/4] Scraping Startup Product, Positioning & Pricing: {clean_url} ...")
    startup_home = fetch_web_signal(clean_url)
    startup_pricing = fetch_web_signal(f"{clean_url} pricing products features competitors")
    contact_info = verify_domain_and_emails(clean_url)

    print(f"[*] [2/4] Researching Market Competitors, Pricing Benchmarks & Product Gaps...")
    market_search = fetch_web_signal(f"top competitors alternatives and pricing for {clean_url}")

    sys_prompt = """You are Star Intel's Autonomous Startup Growth, Pricing & Competitive Intelligence Engine.
Analyze the target startup ({startup}) and its market signals.
Return ONLY a valid JSON object with this exact structure:
{{
  "startup_name": "Clean Company Name",
  "core_product_summary": "1-sentence summary of what they build and who they sell to.",
  "annual_consulting_cost_saved": "$15,000/yr (Replaces Klue/Crayon enterprise CI & manual pricing consultants)",
  "pricing_and_packaging_strategy": {{
    "current_or_inferred_model": "How the startup currently prices or sells",
    "market_pricing_benchmark": "What competitors charge (exact $ tiers or enterprise contract averages)",
    "recommended_pricing_wedge": "Specific pricing/packaging move to undercut rivals and expand ACV"
  }},
  "competitor_matrix": [
    {{
      "competitor_name": "Real Competitor Name",
      "competitor_domain": "competitor.com",
      "pricing_model_and_cost": "Exact or estimated pricing tiers (e.g. $49/mo or $25k/yr)",
      "core_product_strength": "What they do well",
      "exploitable_product_gap": "Specific feature, latency, or pricing weakness where {startup} wins",
      "sales_displacement_wedge": "1-sentence pitch for {startup} to steal their customers"
    }}
  ],
  "growth_playbooks": [
    {{
      "growth_channel": "Product-Led / Outbound Wedge / Pricing Arbitrage / Ecosystem Integration",
      "tactical_action": "Concrete step {startup} can execute this week to win market share",
      "expected_roi": "High-impact revenue or conversion outcome"
    }}
  ],
  "red_team_cso_verdict": "Brutally honest Chief Strategy Officer critique on the biggest threat to {startup}'s growth and how to neutralize it.",
  "ready_to_send_customer_email": {{
    "subject": "Short 5-word subject line",
    "body": "Under 110 words following the First-Customer Outreach template: introduce Idriss (Founder of Star Intel), show a specific competitor/pricing insight we just uncovered for {startup}, explain how Star Intel saves $15k/yr on Klue/market consulting, and offer to send the full HTML/CSV teardown."
  }}
}}"""

    user_prompt = (
        f"STARTUP ({clean_url}) SIGNALS:\n{startup_home[:3000]}\n\n"
        f"PRICING & PRODUCT SIGNALS:\n{startup_pricing[:2500]}\n\n"
        f"COMPETITOR & MARKET SIGNALS:\n{market_search[:3000]}\n\n"
        f"Include 4 real competitors in 'competitor_matrix' and 3 concrete items in 'growth_playbooks'."
    )

    print(f"[*] [3/4] Synthesizing Competitor Pricing Matrix, Product Gaps & Growth Playbook...")
    data = call_llm(sys_prompt.format(startup=clean_url), user_prompt)
    export_all(clean_url, contact_info, data)


def export_all(clean_url: str, contact_info: dict, data: dict):
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", clean_url)[:35]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join(OUTPUT_DIR, f"StarIntel_Growth_{slug}_{ts}.md")
    csv_path = os.path.join(OUTPUT_DIR, f"StarIntel_Growth_{slug}_{ts}.csv")
    html_path = os.path.join(OUTPUT_DIR, f"StarIntel_Dashboard_{slug}_{ts}.html")

    comps = data.get("competitor_matrix", [])
    pricing = data.get("pricing_and_packaging_strategy", {})
    playbooks = data.get("growth_playbooks", [])
    email_pitch = data.get("ready_to_send_customer_email", {})

    # 1. CSV Export
    if comps and isinstance(comps, list):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(comps[0].keys()))
            writer.writeheader()
            writer.writerows(comps)

    # 2. Markdown Export
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# STAR INTEL GROWTH, PRICING & COMPETITOR DOSSIER: {data.get('startup_name', clean_url)}\n")
        f.write(f"**Domain:** `{clean_url}` | **DNS Live:** `{contact_info['dns_live']}` | **Verified Site Emails:** `{', '.join(contact_info['emails']) or 'None published on home/contact'}`\n")
        f.write(f"**Estimated Savings:** **{data.get('annual_consulting_cost_saved', '$15,000/yr')}**\n\n")
        f.write(f"## 1. Product & Market Positioning\n{data.get('core_product_summary', '')}\n\n")
        f.write(f"## 2. Pricing & Packaging Intelligence\n")
        f.write(f"- **Current/Inferred Model:** {pricing.get('current_or_inferred_model', '')}\n")
        f.write(f"- **Market Pricing Benchmark:** {pricing.get('market_pricing_benchmark', '')}\n")
        f.write(f"- **Recommended Pricing Wedge:** {pricing.get('recommended_pricing_wedge', '')}\n\n")
        f.write(f"## 3. Competitor Product & Pricing Matrix\n")
        for c in comps:
            f.write(f"### {c.get('competitor_name')} (`{c.get('competitor_domain')}`)\n")
            f.write(f"- **Pricing & Tiers:** {c.get('pricing_model_and_cost')}\n")
            f.write(f"- **Core Strength:** {c.get('core_product_strength')}\n")
            f.write(f"- **Exploitable Product Gap:** {c.get('exploitable_product_gap')}\n")
            f.write(f"- **Sales Displacement Wedge:** {c.get('sales_displacement_wedge')}\n\n")
        f.write(f"## 4. Startup Growth Playbooks\n")
        for p in playbooks:
            f.write(f"- **{p.get('growth_channel')}**: {p.get('tactical_action')} *(ROI: {p.get('expected_roi')})*\n")
        f.write(f"\n## 5. Red-Team CSO Verdict\n> {data.get('red_team_cso_verdict', '')}\n\n")
        f.write(f"## 6. Ready-to-Send First Customer Outreach Email\n")
        f.write(f"**Subject:** `{email_pitch.get('subject', '')}`\n\n")
        f.write(f"```text\n{email_pitch.get('body', '')}\n```\n")

    # 3. Eye-Catching Dark-Mode HTML Dashboard Export
    rows_html = ""
    for c in comps:
        rows_html += f"""
        <tr>
            <td><strong>{c.get('competitor_name', '')}</strong><br><span class="muted">{c.get('competitor_domain', '')}</span></td>
            <td><span class="badge">{c.get('pricing_model_and_cost', '')}</span></td>
            <td>{c.get('core_product_strength', '')}</td>
            <td class="gap">{c.get('exploitable_product_gap', '')}</td>
            <td class="wedge">{c.get('sales_displacement_wedge', '')}</td>
        </tr>"""

    plays_html = ""
    for p in playbooks:
        plays_html += f"""
        <div class="card">
            <div class="card-title">{p.get('growth_channel', '')}</div>
            <p>{p.get('tactical_action', '')}</p>
            <div class="roi">Expected ROI: {p.get('expected_roi', '')}</div>
        </div>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Star Intel Growth & Pricing Dossier — {data.get('startup_name', clean_url)}</title>
<style>
  body {{ background:#0b0f19; color:#e2e8f0; font-family:'Inter',system-ui,sans-serif; margin:0; padding:32px; }}
  .container {{ max-width:1150px; margin:0 auto; }}
  .header {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:20px; margin-bottom:24px; }}
  .brand {{ font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#38bdf8; font-weight:700; }}
  h1 {{ margin:6px 0 0 0; font-size:28px; color:#f8fafc; }}
  .savings {{ background:#064e3b; color:#34d399; padding:8px 14px; border-radius:6px; font-weight:600; font-size:13px; border:1px solid #059669; }}
  .summary-box {{ background:#111827; border:1px solid #1f2937; border-left:4px solid #38bdf8; padding:18px; border-radius:8px; margin-bottom:24px; }}
  .grid-3 {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-bottom:28px; }}
  .card {{ background:#111827; border:1px solid #1e293b; padding:18px; border-radius:8px; }}
  .card-title {{ color:#38bdf8; font-weight:700; font-size:13px; text-transform:uppercase; margin-bottom:8px; }}
  .roi {{ color:#34d399; font-size:12px; font-weight:600; margin-top:10px; }}
  table {{ width:100%; border-collapse:collapse; background:#111827; border-radius:8px; overflow:hidden; border:1px solid #1e293b; margin-bottom:28px; }}
  th {{ background:#1e293b; color:#94a3b8; text-align:left; padding:12px 14px; font-size:12px; text-transform:uppercase; }}
  td {{ padding:14px; border-bottom:1px solid #1e293b; font-size:13.5px; vertical-align:top; }}
  .muted {{ color:#64748b; font-size:12px; }}
  .badge {{ background:#1e293b; color:#f8fafc; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:600; }}
  .gap {{ color:#fca5a5; }}
  .wedge {{ color:#6ee7b7; }}
  .redteam {{ background:#1f1215; border:1px solid #7f1d1d; padding:18px; border-radius:8px; color:#fecaca; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <div class="brand">STAR INTEL // AUTONOMOUS MARKET, PRICING & COMPETITOR ENGINE</div>
      <h1>{data.get('startup_name', clean_url)} — Growth & Competitive Dossier</h1>
    </div>
    <div class="savings">Replaces {data.get('annual_consulting_cost_saved', '$15,000/yr')} CI & Pricing Spend</div>
  </div>

  <div class="summary-box">
    <strong>Core Product & ICP:</strong> {data.get('core_product_summary', '')}
  </div>

  <h2>1. Pricing & Packaging Arbitrage</h2>
  <div class="grid-3">
    <div class="card"><div class="card-title">Current / Inferred Model</div><p>{pricing.get('current_or_inferred_model', '')}</p></div>
    <div class="card"><div class="card-title">Competitor Pricing Benchmark</div><p>{pricing.get('market_pricing_benchmark', '')}</p></div>
    <div class="card"><div class="card-title">Recommended Pricing Wedge</div><p>{pricing.get('recommended_pricing_wedge', '')}</p></div>
  </div>

  <h2>2. Live Competitor Product, Pricing & Displacement Matrix</h2>
  <table>
    <thead>
      <tr>
        <th>Competitor</th>
        <th>Pricing & Tiers</th>
        <th>Core Strength</th>
        <th>Exploitable Product Gap</th>
        <th>Sales Displacement Wedge</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>

  <h2>3. Tactical Startup Growth Playbooks</h2>
  <div class="grid-3">{plays_html}</div>

  <h2>4. Red-Team Chief Strategy Officer (CSO) Verdict</h2>
  <div class="redteam">{data.get('red_team_cso_verdict', '')}</div>
</div>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] [4/4] Startup Growth & Pricing Pack Generated:")
    print(f"    -> Visual HTML Dashboard : {html_path}  (Open in browser or screenshot for founder!)")
    print(f"    -> Competitor & Price CSV: {csv_path}")
    print(f"    -> Executive MD + Email  : {md_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Star Intel v3.5 — Startup Growth, Competitor & Pricing Engine")
    parser.add_argument("--url", required=True, help="Paste ANY startup domain (e.g., mintlify.com, forgepoint.ai)")
    args = parser.parse_args()
    run_startup_growth_engine(args.url)
