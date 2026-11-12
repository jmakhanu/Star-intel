#!/usr/bin/env python3
"""
Star Intel v2.0 — Autonomous Multi-Agent Revenue, Grant & Intelligence Engine
Modules:
  1. battlecard  : Adversarial Competitor Teardown & Sales Trap Dossier
  2. leads       : High-Intent Buyer Trigger & SDR Lead Hunter (Replaces $4k/mo SDRs)
  3. grants      : SBIR / Defense RFP & Grant Compliance Radar (Replaces $5k/mo Grant Writers)
  4. churn       : Competitor Churn & Unhappy Customer Poacher
Includes Live Model Discovery, SQLite Scrape Cache + Diff-Tracking, CSV Export, and SMTP Delivery.
"""

import os
import sys
import json
import csv
import sqlite3
import smtplib
import argparse
import re
from datetime import datetime, timezone
from email.message import EmailMessage
import urllib.request
import urllib.parse
import urllib.error

# Load .env from current or parent directory
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
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mode TEXT,
            company TEXT,
            target TEXT,
            json_output TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scrape_cache (
            query TEXT PRIMARY KEY,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_cached_scrape(query: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content FROM scrape_cache WHERE query = ?", (query,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def set_cached_scrape(query: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO scrape_cache (query, content, timestamp) VALUES (?, ?, ?)",
        (query, content, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def save_run(mode: str, company: str, target: str, data: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO runs (timestamp, mode, company, target, json_output) VALUES (?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), mode, company, target, json.dumps(data))
    )
    conn.commit()
    conn.close()


def fetch_web_signal(url_or_query: str) -> str:
    target = url_or_query.strip()
    cached = get_cached_scrape(target)
    if cached:
        print(f"    [Cache Hit] Using cached web signals for: {target[:50]}")
        return cached

    if not target.startswith("http"):
        if "." in target and " " not in target:
            reader_url = f"https://r.jina.ai/https://{target}"
        else:
            encoded = urllib.parse.quote(target)
            reader_url = f"https://s.jina.ai/{encoded}"
    else:
        reader_url = f"https://r.jina.ai/{target}"

    req = urllib.request.Request(
        reader_url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) StarIntel/2.0",
            "Accept": "text/plain"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="ignore")[:8000]
            if len(text) > 100:
                set_cached_scrape(target, text)
            return text
    except Exception as e:
        return f"Target context: {url_or_query} (Live web signal fallback: {e})"


def fetch_active_groq_models(api_key: str) -> list:
    """Queries Groq's /models endpoint live so decommissioned models are never called."""
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/models",
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) StarIntel/2.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            all_ids = [m["id"] for m in data.get("data", []) if m.get("active", True)]
            # Filter out audio/whisper/tts/guard/vision/embedding models
            skip_terms = ("whisper", "tts", "guard", "vision", "embed", " Orpheus", "allam", "playai")
            chat_models = [
                m for m in all_ids
                if not any(term.lower() in m.lower() for term in skip_terms)
            ]
            # Sort preferred high-reasoning models to the front
            def rank_model(m_id: str) -> int:
                m_low = m_id.lower()
                if "120b" in m_low or "70b" in m_low or "qwen" in m_low or "deepseek" in m_low:
                    return 0
                if "llama" in m_low or "mixtral" in m_low or "gemma" in m_low:
                    return 1
                return 2

            chat_models.sort(key=rank_model)
            return chat_models
    except Exception as e:
        print(f"    [!] Live model list warning: {e}")
        return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]


def resolve_provider_and_models():
    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if openai_key and openai_key.startswith("gsk_"):
        groq_key = openai_key

    if groq_key:
        live_models = fetch_active_groq_models(groq_key)
        print(f"    [Groq Live Models Detected]: {', '.join(live_models[:5])}")
        return (
            "https://api.groq.com/openai/v1/chat/completions",
            groq_key,
            live_models
        )
    if openrouter_key or (openai_key and openai_key.startswith("sk-or-")):
        key = openrouter_key or openai_key
        return (
            "https://openrouter.ai/api/v1/chat/completions",
            key,
            ["meta-llama/llama-3.3-70b-instruct:free", "openai/gpt-4o-mini"]
        )
    if gemini_key:
        return (
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            gemini_key,
            ["gemini-2.5-flash", "gemini-2.0-flash"]
        )
    if openai_key:
        return (
            "https://api.openai.com/v1/chat/completions",
            openai_key,
            ["gpt-4o-mini", "gpt-4o"]
        )

    print("[!] ERROR: No API key found in .env (expected GROQ_API_KEY or OPENAI_API_KEY).")
    sys.exit(1)


def extract_json_object(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    # Remove <think>...</think> blocks if using DeepSeek/Qwen reasoning models on Groq
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL).strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    base_url, api_key, models = resolve_provider_and_models()

    last_error = None
    for model in models:
        payload_dict = {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt + "\nIMPORTANT: Output ONLY valid raw JSON. Do not include markdown fences or commentary."},
                {"role": "user", "content": user_prompt}
            ]
        }
        data = json.dumps(payload_dict).encode("utf-8")
        req = urllib.request.Request(
            base_url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) StarIntel/2.0"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                res_body = json.loads(resp.read().decode("utf-8"))
                content = res_body["choices"][0]["message"]["content"]
                parsed = extract_json_object(content)
                print(f"    [LLM Success] Synthesized using active model: {model}")
                return parsed
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            last_error = f"HTTP {e.code} on model '{model}': {err_body[:250]}"
            continue
        except Exception as e:
            last_error = f"Parse/API error on model '{model}': {e}"
            continue

    print(f"\n[!] All candidate models failed. Last API diagnostic:\n{last_error}")
    sys.exit(1)


PROMPTS = {
    "leads": """You are Star Intel's Autonomous B2B Lead & Trigger-Event Hunter.
Analyze the scraped signals for our client ({company}) targeting ({target}).
Return ONLY a valid JSON object with this exact structure:
{{
  "executive_summary": "2-sentence ROI summary showing how much SDR research time/cost this saves.",
  "estimated_monthly_savings_usd": "$4,000/mo (Replaces manual SDR agency & Clay/ZoomInfo seats)",
  "action_items": [
    {{
      "account_or_prospect": "Specific Real Company Name & Target Role",
      "buying_trigger_detected": "Specific hiring, tech-stack, expansion, or quoting bottleneck trigger",
      "urgency_score": "9/10",
      "decision_maker_title": "VP of Operations / Head of Estimating / CEO",
      "ready_to_send_cold_hook": "2-sentence hyper-specific cold email opening hook"
    }}
  ],
  "red_team_cso_critique": "Adversarial critique on which prospects will close fastest and why."
}}""",

    "grants": """You are Star Intel's Autonomous SBIR, Defense RFP & Non-Dilutive Grant Radar.
Analyze the scraped signals for our client ({company}) targeting ({target}).
Return ONLY a valid JSON object with this exact structure:
{{
  "executive_summary": "2-sentence summary of non-dilutive funding & contract opportunities matched.",
  "estimated_monthly_savings_usd": "$5,000/mo (Replaces external grant/SBIR retainers)",
  "action_items": [
    {{
      "program_or_agency": "Agency / SBIR / RFP Topic Name",
      "award_est_usd": "Estimated contract/grant size (e.g. $250k - $1.5M)",
      "technical_fit_matrix": "How {company}'s core tech maps to the solicitation requirements",
      "compliance_risk": "Key ITAR/TRL or deadline hurdle to watch",
      "draft_abstract_hook": "3-sentence technical abstract opening for the proposal"
    }}
  ],
  "red_team_cso_critique": "Adversarial review of proposal win-probability and required technical proof."
}}""",

    "churn": """You are Star Intel's Competitor Churn & Unhappy Customer Poaching Agent.
Analyze the scraped signals for our client ({company}) poaching from rival ({target}).
Return ONLY a valid JSON object with this exact structure:
{{
  "executive_summary": "2-sentence breakdown of rival {target}'s biggest customer failure points right now.",
  "estimated_monthly_savings_usd": "$3,500/mo (Direct competitor displacement & GTM intelligence)",
  "action_items": [
    {{
      "complaint_category": "Specific failure mode (Pricing hike / API downtime / Missing feature / Support)",
      "affected_buyer_persona": "Who is complaining most",
      "competitor_weakness": "Technical or commercial root cause at {target}",
      "poaching_wedge": "Exact migration offer or feature {company} should pitch",
      "outreach_script": "2-sentence displacement script to win the unhappy user"
    }}
  ],
  "red_team_cso_critique": "Adversarial warning on switching costs and how {company} can remove migration friction."
}}""",

    "battlecard": """You are Star Intel's Adversarial Competitive Battlecard Engine.
Compare our client ({company}) against rival ({target}).
Return ONLY a valid JSON object with this exact structure:
{{
  "executive_summary": "2-sentence tactical positioning summary.",
  "estimated_monthly_savings_usd": "$3,000/mo (Replaces manual product marketing & consulting teardown)",
  "action_items": [
    {{
      "dimension": "Core Architecture / Pricing / Deployment / Moats",
      "our_advantage": "How {company} wins",
      "rival_vulnerability": "Where {target} fails under pressure",
      "landmine_trap_question": "Exact question our sales rep should ask the buyer to disqualify {target}"
    }}
  ],
  "red_team_cso_critique": "Brutally honest Red-Team critique of where {target} could still beat {company}."
}}"""
}


def run_pipeline(mode: str, company: str, target: str) -> dict:
    print(f"[*] [1/3] Scraping live web & technical signals for '{company}' vs/target '{target}'...")
    signal_company = fetch_web_signal(company)
    signal_target = fetch_web_signal(target)

    print(f"[*] [2/3] Running Multi-Agent {mode.upper()} synthesis + Red-Team CSO critique loop...")
    sys_prompt = PROMPTS[mode].format(company=company, target=target)
    user_prompt = (
        f"CLIENT COMPANY ({company}) SIGNALS:\n{signal_company[:3500]}\n\n"
        f"TARGET / MARKET ({target}) SIGNALS:\n{signal_target[:3500]}\n\n"
        f"Generate 5 concrete, high-signal items inside 'action_items'."
    )

    data = call_llm(sys_prompt, user_prompt)
    save_run(mode, company, target, data)
    return data


def export_deliverables(mode: str, company: str, target: str, data: dict):
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", f"{company}_{mode}_{target}")[:45]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join(OUTPUT_DIR, f"StarIntel_{slug}_{ts}.md")
    csv_path = os.path.join(OUTPUT_DIR, f"StarIntel_{slug}_{ts}.csv")

    items = data.get("action_items", [])

    if items and isinstance(items, list):
        keys = list(items[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(items)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# STAR INTEL EXECUTIVE BRIEFING ({mode.upper()})\n")
        f.write(f"**Client:** `{company}` | **Target Scope:** `{target}` | **Generated:** `{ts} UTC`\n")
        f.write(f"**Estimated Cost Savings:** **{data.get('estimated_monthly_savings_usd', '$3,500/mo')}**\n\n")
        f.write(f"## 1. Executive Summary\n{data.get('executive_summary', '')}\n\n")
        f.write(f"## 2. Actionable Intelligence Matrix\n")
        for idx, item in enumerate(items, 1):
            f.write(f"### #{idx}\n")
            for k, v in item.items():
                f.write(f"- **{k.replace('_', ' ').title()}**: {v}\n")
            f.write("\n")
        f.write(f"## 3. Red-Team Chief Strategy Officer (CSO) Critique\n")
        f.write(f"> {data.get('red_team_cso_critique', '')}\n")

    print(f"[+] [3/3] Deliverables generated:\n    -> Markdown Dossier : {md_path}\n    -> Actionable CSV   : {csv_path}")
    return md_path, csv_path


def send_email_briefing(to_email: str, mode: str, company: str, md_path: str, csv_path: str):
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        print("[i] Skipping SMTP auto-send (set SMTP_USER and SMTP_PASS in .env to email directly).")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        body_text = f.read()

    msg = EmailMessage()
    msg["Subject"] = f"Star Intel Automated {mode.capitalize()} Briefing — {company}"
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body_text)

    if os.path.exists(csv_path):
        with open(csv_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="text", subtype="csv", filename=os.path.basename(csv_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print(f"[+] Email briefing + CSV attachment delivered to {to_email}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Star Intel v2.0 — Autonomous Multi-Agent Cost-Cutting Engine")
    parser.add_argument("--mode", choices=["leads", "grants", "churn", "battlecard"], required=True,
                        help="Select high-ROI module: leads | grants | churn | battlecard")
    parser.add_argument("--company", required=True, help="Your client startup domain or name (e.g., forgepoint.ai)")
    parser.add_argument("--target", required=True, help="Competitor domain, customer segment, or grant agency")
    parser.add_argument("--email", default="", help="Optional recipient email to auto-send briefing + CSV")
    args = parser.parse_args()

    init_db()
    result = run_pipeline(args.mode, args.company, args.target)
    md_file, csv_file = export_deliverables(args.mode, args.company, args.target, result)
    if args.email:
        send_email_briefing(args.email, args.mode, args.company, md_file, csv_file)
