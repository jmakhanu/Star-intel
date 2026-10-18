import time
import requests
import argparse
import json
import sqlite3
import hashlib
import os
import re
import warnings
from datetime import datetime
from typing import TypedDict, Dict, Any
from urllib.parse import urlparse

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from markdown_pdf import MarkdownPdf, Section

os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")

# Ensure clean directory architecture exists
os.makedirs("reports", exist_ok=True)
os.makedirs("vault", exist_ok=True)
os.makedirs("logs", exist_ok=True)

DATABASE_PATH = "vault/intel_vault.db"
# Load secret webhook from local .env file
if os.path.exists(".env"):
    with open(".env") as _f:
        for _line in _f:
            if "=" in _line and not _line.startswith("#"):
                _k, _v = _line.strip().split("=", 1)
                os.environ[_k] = _v.strip('"\'')
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitor_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            url TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            pricing_model TEXT,
            key_features TEXT,
            vulnerabilities TEXT,
            red_team_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intelligence_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            critique TEXT,
            iterations INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def send_slack_alert(domain: str, client_domain: str, score: str, pricing: str, vulns: list, pdf_path: str):
    print("\n[*] 7. Pushing intelligence summary to Star Intel Slack channel...")
    vuln_text = "\n".join([f"• {v}" for v in vulns[:5]]) if vulns else "• See full PDF dossier for tactical breakdown."
    
    slack_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 STAR INTEL ALERT: {domain.upper()}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Protected Client:*\n`{client_domain}`"},
                    {"type": "mrkdwn", "text": f"*Target Competitor:*\n`{domain}`"},
                    {"type": "mrkdwn", "text": f"*Red Team Threat Score:*\n*{score}/10*"},
                    {"type": "mrkdwn", "text": f"*Pricing Architecture:*\n{pricing}"}
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Key Exploitable Vulnerabilities:*\n{vuln_text}\n\n📄 *Dossier Vaulted:* `{pdf_path}`"
                }
            }
        ]
    }
    
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=slack_payload, timeout=10)
        if resp.status_code == 200:
            print("[+] Slack push successful! Alert delivered to workspace.")
        else:
            print(f"[!] Slack rejected payload (HTTP {resp.status_code}): {resp.text}")
    except Exception as e:
        print(f"[!] Slack connection error: {e}")

class PipelineState(TypedDict):
    client_url: str
    client_domain: str
    client_context: str
    target_url: str
    target_domain: str
    raw_markdown: str
    content_hash: str
    draft_report: str
    extracted_json: Dict[str, Any]
    critique: str
    revision_count: int
    final_report: str

def scrape_client(state: PipelineState):
    c_domain = urlparse(state["client_url"]).netloc.replace("www.", "")
    print(f"\n[*] 0. Building deep context on OUR CLIENT: {c_domain} ({state['client_url']})")
    try:
        response = requests.get(f"https://r.jina.ai/{state['client_url']}", timeout=20)
        response.raise_for_status()
        context = response.text[:3000]
        print(f"    [+] Ingested {len(context)} chars of client baseline data.")
    except Exception as e:
        context = f"Client scrape failed for {c_domain}: {e}"
        print(f"    [!] {context}")
    return {"client_context": context, "client_domain": c_domain}

def scrape_and_hash(state: PipelineState):
    domain = urlparse(state["target_url"]).netloc.replace("www.", "")
    print(f"[*] 1. Infiltrating TARGET COMPETITOR: {domain} ({state['target_url']})")
    
    try:
        response = requests.get(f"https://r.jina.ai/{state['target_url']}", timeout=20)
        response.raise_for_status()
        raw_text = response.text[:3800]
        print(f"    [+] Ingested {len(raw_text)} chars of competitor intelligence.")
    except Exception as e:
        raw_text = f"Scrape failed for {domain}: {e}"
        print(f"    [!] {raw_text}")

    c_hash = hashlib.sha256(raw_text.encode()).hexdigest()
    return {
        "target_domain": domain,
        "raw_markdown": raw_text,
        "content_hash": c_hash,
        "revision_count": 0
    }

def primary_analyst(state: PipelineState):
    print("[*] 2. Primary Analyst: Synthesizing deep technical intelligence...")
    
    llm_json = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    json_prompt = f"""
    Analyze this competitor data for {state['target_domain']}:
    {state['raw_markdown']}
    
    Output ONLY a valid JSON object with EXACTLY these keys:
    "pricing_model": (string describing their pricing structure, enterprise gating, or contract style),
    "key_features": (list of 4-5 specific technical capabilities or claims),
    "vulnerabilities": (list of 3-4 specific weaknesses, bottlenecks, or gaps compared to {state['client_domain']}).
    """
    try:
        res_json = llm_json.invoke([HumanMessage(content=json_prompt)])
        raw_j = re.sub(r"<think>.*?</think>", "", res_json.content, flags=re.DOTALL)
        m_j = re.search(r"\{.*\}", raw_j, re.DOTALL)
        extracted_dict = json.loads(m_j.group(0)) if m_j else json.loads(raw_j)
    except Exception:
        extracted_dict = {"pricing_model": "Opaque / Enterprise Quote", "key_features": [], "vulnerabilities": []}

    llm_text = ChatGroq(model="openai/gpt-oss-120b", temperature=0.1, max_tokens=3000, reasoning_effort="low")
    text_prompt = f"""
    You are Lead Defense & Enterprise Strategist at Star Intel. 
    You work EXCLUSIVELY FOR OUR CLIENT ({state['client_domain']}) to defeat TARGET COMPETITOR ({state['target_domain']}).

    OUR CLIENT'S CAPABILITIES ({state['client_domain']}):
    {state['client_context']}

    TARGET COMPETITOR'S DATA ({state['target_domain']}):
    {state['raw_markdown']}

    Write a detailed, exhaustive, multi-section Markdown intelligence dossier.
    CRITICAL FORMATTING & GROUNDING RULES:
    1. DO NOT USE MARKDOWN TABLES (| col | col |). Wide tables break the PDF renderer. Use structured ### subheadings and bold bullet points instead.
    2. ZERO HALLUCINATION POLICY: Only cite metrics, specs, and claims explicitly supported by the scraped text. NEVER invent unverified hardware specs (like fake CPU models, fake satellite masses, or fake AWS instance types). If a spec is undisclosed on their site, explicitly flag its opacity as a competitive blind spot.

    Include these exact sections:
    ## 1. Executive Threat Summary & Market Posture
    (Analyze how {state['target_domain']} positions itself, who they target, and where they clash with {state['client_domain']}.)

    ## 2. Technical Architecture & Capability Breakdown
    (Dissect their specific hardware/software claims, latency, resolution, deployment speed, or operational specs.)

    ## 3. Commercial & Pricing Architecture
    (Analyze their contract structure, pricing opacity, capex/opex burden, and buyer friction.)

    ## 4. Exploitable Vulnerability Matrix
    (Detail 4 specific technical, operational, or commercial blind spots in {state['target_domain']}'s offering.)

    ## 5. High-Conversion Sales Battlecard (For {state['client_domain']} Reps)
    (Provide 4 concrete attack vectors, including exact trap-setting questions our sales team should ask prospects to disqualify {state['target_domain']}, and direct rebuttals to their claims.)
    """
    res_text = llm_text.invoke([HumanMessage(content=text_prompt)])

    return {
        "draft_report": res_text.content,
        "extracted_json": extracted_dict
    }

def red_team_critic(state: PipelineState):
    print("[*] 3. Red Team Adversary: Stress-testing dossier for weak assumptions...")
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

    critic_prompt = f"""
    You are the Chief Strategy Officer of {state['target_domain']}. You intercepted a competitive dossier written for your rival ({state['client_domain']}).
    Dissect this report. Point out where the analyst was too generic, missed specific technical details from the raw data, or wrote weak sales attack vectors.

    DRAFT REPORT:
    {state['draft_report']}

    Keep your critique under 200 words. End your response on a new line with this exact tag:
    SEVERITY_SCORE: X
    (where X is an integer from 1 to 10 rating how dangerous this competitor is to {state['client_domain']}).
    """
    res = llm.invoke([HumanMessage(content=critic_prompt)])
    return {"critique": res.content}

def should_refine(state: PipelineState):
    if state["revision_count"] < 1:
        print("[!] Red Team flagged areas for deeper tactical rigor. Routing to Lead Strategist...")
        return "refine"
    return "commit"

def analyst_refine(state: PipelineState):
    print("[*] 4. Lead Strategist: Cooling down Groq TPM window (35s) then hardening final brief...")
    time.sleep(35)
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.1, max_tokens=3600, reasoning_effort="low")

    refine_prompt = f"""
    You are the Lead Strategist at Star Intel working EXCLUSIVELY FOR {state['client_domain']} to defeat {state['target_domain']}.
    Rewrite and expand the draft dossier below to address the Red Team critique. 
    Make the analysis thorough, highly technical, and ruthless.
    CRITICAL RULES:
    1. DO NOT USE MARKDOWN TABLES (| col | col |)—use clean bulleted lists and bold labels so the PDF renders cleanly.
    2. STRICT LENGTH & GROUNDING: Keep Sections 1, 2, 3, and 4 concise (maximum 150 words per section) so you have plenty of space to write Section 5 in complete detail. NEVER invent external citations (no fake FCC/ESA filings, no fake NRO audits, no invented $/km2 prices). End the report with "--- END OF DOSSIER ---" after completing all 4 trap questions and rebuttals in Section 5.

    DRAFT DOSSIER:
    {state['draft_report']}

    RED TEAM CRITIQUE TO ADDRESS:
    {state['critique']}

    Output ONLY the comprehensive Markdown report using these exact ## headings:
    ## 1. Executive Threat Summary & Market Posture
    ## 2. Technical Architecture & Capability Comparison
    ## 3. Verified Pricing & Contract Architecture
    ## 4. Hardened Vulnerability Matrix (Their Blind Spots)
    ## 5. Field Sales Battlecard: Disqualifying {state['target_domain']} (Trap Questions & Rebuttals)
    """
    res = llm.invoke([HumanMessage(content=refine_prompt)])
    return {
        "final_report": res.content,
        "revision_count": state["revision_count"] + 1
    }

def commit_to_vault(state: PipelineState):
    print("[*] 5. Committing structured intelligence to local Data Moat (vault/intel_vault.db)...")
    
    score = 7
    match = re.search(r'SEVERITY_SCORE:\s*([0-9]+)', state["critique"])
    if match:
        score = int(match.group(1))

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO competitor_records (
            domain, url, content_hash, pricing_model, key_features, vulnerabilities, red_team_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        state["target_domain"],
        state["target_url"],
        state["content_hash"],
        state["extracted_json"].get("pricing_model", "N/A"),
        json.dumps(state["extracted_json"].get("key_features", [])),
        json.dumps(state["extracted_json"].get("vulnerabilities", [])),
        score
    ))

    cursor.execute("""
        INSERT INTO intelligence_logs (domain, critique, iterations)
        VALUES (?, ?, ?)
    """, (
        state["target_domain"],
        state["critique"],
        state["revision_count"]
    ))

    conn.commit()
    conn.close()
    return {}

init_db()

builder = StateGraph(PipelineState)
builder.add_node("scrape_client", scrape_client)
builder.add_node("scrape_and_hash", scrape_and_hash)
builder.add_node("primary_analyst", primary_analyst)
builder.add_node("red_team_critic", red_team_critic)
builder.add_node("analyst_refine", analyst_refine)
builder.add_node("commit_to_vault", commit_to_vault)

builder.add_edge(START, "scrape_client")
builder.add_edge("scrape_client", "scrape_and_hash")
builder.add_edge("scrape_and_hash", "primary_analyst")
builder.add_edge("primary_analyst", "red_team_critic")
builder.add_conditional_edges(
    "red_team_critic",
    should_refine,
    {
        "refine": "analyst_refine",
        "commit": "commit_to_vault"
    }
)
builder.add_edge("analyst_refine", "commit_to_vault")
builder.add_edge("commit_to_vault", END)

app = builder.compile()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Star Intel Autonomous CI Engine")
    parser.add_argument("--target", required=False, help="Competitor URL to analyze")
    parser.add_argument("--client_url", required=False, help="Our Client's URL for baseline context")
    parser.add_argument("--test_slack", action="store_true", help="Send an immediate test ping to Slack without running the LLM")
    args = parser.parse_args()

    if args.test_slack:
        print("[*] Running standalone Slack Webhook diagnostic...")
        send_slack_alert(
            domain="iceye.com (DIAGNOSTIC TEST)",
            client_domain="capellaspace.com",
            score="8",
            pricing="Enterprise Gated / Sovereign Fleet Contracts",
            vulns=[
                "3-hour data delivery window creates latency gaps for tactical maritime tracking",
                "Opaque pricing tiers create procurement friction for commercial mid-market buyers",
                "Limited US-sovereign ground station footprint compared to domestic primes"
            ],
            pdf_path="reports/Hardened_Intel_iceye.com_TEST.pdf"
        )
        exit(0)

    if not args.target or not args.client_url:
        parser.error("Both --target and --client_url are required unless running --test_slack")

    init_state = {
        "client_url": args.client_url,
        "client_domain": "",
        "client_context": "",
        "target_url": args.target,
        "target_domain": "",
        "raw_markdown": "",
        "content_hash": "",
        "draft_report": "",
        "extracted_json": {},
        "critique": "",
        "revision_count": 0,
        "final_report": ""
    }

    result = app.invoke(init_state)

    domain = result["target_domain"]
    client_domain = result["client_domain"]
    raw_report = result["final_report"] if result["final_report"] else result["draft_report"]
    
    # Strip any top-level H1 generated by the LLM so our Star Intel header is always #1
    raw_report = re.sub(r"<think>.*?</think>", "", raw_report, flags=re.DOTALL)
    cleaned_body = re.sub(r"^#\s+.*\n+", "", raw_report.strip())
    
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    file_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"reports/StarIntel_Dossier_{domain}_{file_ts}.pdf"

    score_match = re.search(r'SEVERITY_SCORE:\s*([0-9]+)', result["critique"])
    score_val = score_match.group(1) if score_match else "7"

    branded_markdown = (
        f"# ✦ STAR INTEL: TACTICAL DOSSIER\n\n"
        f"**Prepared Exclusively For:** `{client_domain}`  \n"
        f"**Target Adversary:** `{domain}`  \n"
        f"**Red Team Threat Rating:** `{score_val}/10`  \n"
        f"**Timestamp:** `{timestamp_str}`  \n"
        f"**Clearance:** `CONFIDENTIAL // EXECUTIVE & SALES LEADERSHIP ONLY`\n\n"
        f"---\n\n"
        f"{cleaned_body}\n"
    )

    print(f"\n[*] 6. Rendering branded deliverable: {pdf_filename}...")
    try:
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(branded_markdown))
        pdf.save(pdf_filename)
        print(f"[+] Done. Branded PDF saved: {pdf_filename}")
        print(f"[+] Database record saved in: {DATABASE_PATH}")
    except Exception as e:
        print(f"[!] PDF generation error: {e}")

    if SLACK_WEBHOOK_URL:
        pricing = result["extracted_json"].get("pricing_model", "Enterprise Gated / Custom Quote")
        vulns = result["extracted_json"].get("vulnerabilities", [])
        send_slack_alert(domain, client_domain, score_val, pricing, vulns, pdf_filename)
