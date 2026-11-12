#!/usr/bin/env python3
"""
Star Intel Web SaaS Platform (v4.0)
Self-serve web portal: Users paste a startup URL in the browser ->
Live scrapes product, pricing & competitors -> Renders interactive dashboard + CSV download.
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
<title>Star Intel — Autonomous Startup Growth, Pricing & Competitor SaaS</title>
<style>
  :root { --bg:#070a12; --panel:#111827; --border:#1e293b; --accent:#38bdf8; --green:#34d399; --text:#f8fafc; --muted:#94a3b8; }
  * { box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:'Inter',system-ui,sans-serif; margin:0; padding:0; }
  .nav { display:flex; justify-content:space-between; align-items:center; padding:20px 40px; border-bottom:1px solid var(--border); }
  .logo { font-weight:800; letter-spacing:2px; color:var(--accent); font-size:15px; }
  .badge-top { background:#064e3b; color:var(--green); padding:6px 12px; border-radius:99px; font-size:12px; font-weight:600; border:1px solid #059669; }
  .hero { max-width:900px; margin:60px auto 30px; text-align:center; padding:0 20px; }
  h1 { font-size:42px; line-height:1.15; margin-bottom:16px; background:linear-gradient(90deg,#fff,#38bdf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  p.sub { color:var(--muted); font-size:18px; max-width:680px; margin:0 auto 32px; line-height:1.5; }
  .search-box { display:flex; gap:12px; max-width:680px; margin:0 auto; background:var(--panel); padding:10px; border-radius:12px; border:1px solid var(--border); box-shadow:0 10px 30px rgba(0,0,0,0.5); }
  input { flex:1; background:transparent; border:none; color:#fff; font-size:16px; padding:12px 16px; outline:none; }
  button { background:var(--accent); color:#070a12; border:none; padding:14px 28px; border-radius:8px; font-weight:700; font-size:15px; cursor:pointer; transition:0.2s; }
  button:hover { opacity:0.9; transform:translateY(-1px); }
  button:disabled { background:#475569; cursor:wait; }
  .loader { display:none; margin:28px auto; color:var(--accent); font-weight:600; font-size:15px; }
  #results { max-width:1150px; margin:40px auto; padding:0 24px 80px; display:none; }
  .grid-3 { display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; margin-bottom:28px; }
  .card { background:var(--panel); border:1px solid var(--border); padding:20px; border-radius:10px; }
  .card-title { color:var(--accent); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
  table { width:100%; border-collapse:collapse; background:var(--panel); border-radius:10px; overflow:hidden; border:1px solid var(--border); margin-bottom:28px; }
  th { background:#1e293b; color:var(--muted); text-align:left; padding:14px; font-size:12px; text-transform:uppercase; }
  td { padding:14px; border-bottom:1px solid var(--border); font-size:14px; vertical-align:top; }
  .gap { color:#fca5a5; }
  .wedge { color:var(--green); }
  .email-box { background:#0f172a; border:1px solid #334155; padding:18px; border-radius:8px; font-family:monospace; white-space:pre-wrap; font-size:13.5px; color:#e2e8f0; }
  .btn-secondary { background:#1e293b; color:#fff; border:1px solid #334155; padding:10px 18px; border-radius:6px; cursor:pointer; font-size:13px; font-weight:600; margin-bottom:16px; }
</style>
</head>
<body>
  <div class="nav">
    <div class="logo">STAR INTEL // AUTONOMOUS GROWTH & PRICING ENGINE</div>
    <div class="badge-top">Replaces $15,000/yr Klue & Market Consulting Spend</div>
  </div>

  <div class="hero">
    <h1>Paste Any Startup URL.<br>Get Live Competitor Pricing, Product Gaps & Growth Playbooks.</h1>
    <p class="sub">Autonomous multi-agent LangGraph & 120B LLM engine that tears down your rivals' pricing tiers, exposes product weaknesses, and writes high-converting outbound hooks in 30 seconds.</p>
    <form class="search-box" onsubmit="runAnalysis(event)">
      <input type="text" id="urlInput" placeholder="Enter startup domain (e.g., mintlify.com, forgepoint.ai, linear.app)" required />
      <button type="submit" id="runBtn">Generate Growth Dossier</button>
    </form>
    <div class="loader" id="loader">[⚡] Scraping live pricing pages, running 120B multi-agent teardown & verifying DNS... (takes ~25s)</div>
  </div>

  <div id="results"></div>

<script>
let lastData = null;

async function runAnalysis(e) {
  e.preventDefault();
  const url = document.getElementById('urlInput').value.trim();
  const btn = document.getElementById('runBtn');
  const loader = document.getElementById('loader');
  const resDiv = document.getElementById('results');

  btn.disabled = true;
  btn.innerText = "Running Agents...";
  loader.style.display = "block";
  resDiv.style.display = "none";

  try {
    const resp = await fetch('/api/analyze?url=' + encodeURIComponent(url));
    const data = await resp.json();
    if (data.error) throw new Error(data.error);
    lastData = data;
    renderDashboard(data);
  } catch (err) {
    alert("Analysis error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = "Generate Growth Dossier";
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

  let rowsHtml = comps.map(c => `
    <tr>
      <td><strong>${c.competitor_name||''}</strong><br><span style="color:#64748b;font-size:12px">${c.competitor_domain||''}</span></td>
      <td><strong>${c.pricing_model_and_cost||''}</strong></td>
      <td>${c.core_product_strength||''}</td>
      <td class="gap">${c.exploitable_product_gap||''}</td>
      <td class="wedge">${c.sales_displacement_wedge||''}</td>
    </tr>`).join('');

  let playsHtml = plays.map(pl => `
    <div class="card">
      <div class="card-title">${pl.growth_channel||''}</div>
      <p>${pl.tactical_action||''}</p>
      <div style="color:#34d399;font-size:12px;font-weight:600">ROI: ${pl.expected_roi||''}</div>
    </div>`).join('');

  const resDiv = document.getElementById('results');
  resDiv.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h2>${d.startup_name || d.domain} — Executive Growth & Pricing Dossier</h2>
      <button class="btn-secondary" onclick="downloadCSV()">⬇ Download Competitor & Pricing CSV</button>
    </div>
    <div class="card" style="margin-bottom:24px;border-left:4px solid #38bdf8;">
      <strong>Product & ICP Summary:</strong> ${d.core_product_summary||''} <br>
      <span style="color:#94a3b8;font-size:13px">DNS Live: ${d.dns_live} | Published Site Emails: ${(d.verified_emails||[]).join(', ') || 'None listed on home page'}</span>
    </div>

    <h3>1. Pricing & Packaging Strategy</h3>
    <div class="grid-3">
      <div class="card"><div class="card-title">Current / Inferred Model</div><p>${p.current_or_inferred_model||''}</p></div>
      <div class="card"><div class="card-title">Market Pricing Benchmark</div><p>${p.market_pricing_benchmark||''}</p></div>
      <div class="card"><div class="card-title">Recommended Pricing Wedge</div><p>${p.recommended_pricing_wedge||''}</p></div>
    </div>

    <h3>2. Competitor Product, Pricing & Displacement Matrix</h3>
    <table>
      <thead><tr><th>Competitor</th><th>Pricing & Tiers</th><th>Core Strength</th><th>Exploitable Product Gap</th><th>Sales Displacement Wedge</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
    </table>

    <h3>3. Startup Growth Playbooks</h3>
    <div class="grid-3">${playsHtml}</div>

    <h3>4. Red-Team CSO Verdict</h3>
    <div class="card" style="border-color:#7f1d1d;background:#1f1215;color:#fecaca;margin-bottom:28px;">${d.red_team_cso_verdict||''}</div>

    <h3>5. Auto-Generated Outbound Pitch Email</h3>
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
        if parsed.path == "/" or parsed.path == "/index.html":
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

                from star_intel_growth import run_startup_growth_engine
                # Call LLM directly for JSON response
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
    print(f"[+] Star Intel SaaS Web Portal running at: http://localhost:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StarIntelHandler)
    server.serve_forever()
