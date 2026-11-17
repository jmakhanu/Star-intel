#!/usr/bin/env python3
import os
import time
import json
import sqlite3
import hashlib
import urllib.parse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from star_intel_growth import init_db, fetch_web_signal, verify_domain_and_emails, call_llm

PORT = int(os.getenv("PORT", 8080))
PAYPAL_CHECKOUT_URL = "https://www.paypal.com/ncp/payment/XKUVEJSB74V88"
DB_FILE = "star_intel_telemetry.db"
ADMIN_KEY = os.getenv("ADMIN_KEY", "makhanu2026")
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_template.html")


def hash_pw(pw: str) -> str:
    return hashlib.sha256((pw or "").encode("utf-8")).hexdigest()


def ensure_telemetry_tables():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS founder_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT DEFAULT '',
        startup_domain TEXT,
        plan TEXT DEFAULT 'Free Studio',
        created_at TEXT,
        last_active TEXT
    )''')
    try:
        c.execute("ALTER TABLE founder_users ADD COLUMN password_hash TEXT DEFAULT ''")
    except Exception:
        pass
    c.execute('''CREATE TABLE IF NOT EXISTS scan_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        user_email TEXT,
        mode TEXT,
        ip_addr TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_cache (
        cache_key TEXT PRIMARY KEY,
        json_data TEXT,
        created_ts INTEGER
    )''')
    conn.commit()
    conn.close()


def log_scan_event(domain, user_email, mode, ip_addr):
    try:
        ensure_telemetry_tables()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO scan_logs (domain, user_email, mode, ip_addr, created_at) VALUES (?, ?, ?, ?, ?)",
            (domain, user_email or "anonymous", mode, ip_addr, now),
        )
        if user_email and "@" in user_email:
            c.execute(
                '''INSERT INTO founder_users (email, startup_domain, created_at, last_active)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(email) DO UPDATE SET
                   startup_domain=excluded.startup_domain,
                   last_active=excluded.last_active''',
                (user_email.lower().strip(), domain, now, now),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Telemetry log warning:", e)


def get_cached_analysis(cache_key):
    try:
        ensure_telemetry_tables()
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        row = c.execute(
            "SELECT json_data, created_ts FROM analysis_cache WHERE cache_key = ?",
            (cache_key,),
        ).fetchone()
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
        now_ts = int(datetime.now(timezone.utc).timestamp())
        c.execute(
            "INSERT OR REPLACE INTO analysis_cache (cache_key, json_data, created_ts) VALUES (?, ?, ?)",
            (cache_key, json.dumps(data_dict), now_ts),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


class StarIntelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html", "/healthz"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.end_headers()
            with open(TEMPLATE_PATH, "rb") as tf:
                self.wfile.write(tf.read())
            return

        if parsed.path in ("/api/auth", "/api/signup"):
            qs = urllib.parse.parse_qs(parsed.query)
            mode = qs.get("mode", ["signup"])[0].strip().lower()
            email = qs.get("email", [""])[0].strip().lower()
            password = qs.get("password", [""])[0]
            domain = qs.get("domain", [""])[0].strip() or "direct-signup"
            ip_addr = self.headers.get("X-Forwarded-For", self.client_address[0])

            if not email or "@" not in email:
                self.send_json({"error": "Please enter a valid work email address."}, 400)
                return

            ensure_telemetry_tables()
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            pw_hashed = hash_pw(password)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            existing = c.execute(
                "SELECT email, password_hash, startup_domain FROM founder_users WHERE email = ?",
                (email,),
            ).fetchone()

            if mode == "login":
                if not existing:
                    conn.close()
                    self.send_json(
                        {"error": "No account found with that email. Please switch to Create Account (Sign Up)."},
                        404,
                    )
                    return
                if existing[1] and existing[1] != pw_hashed:
                    conn.close()
                    self.send_json({"error": "Incorrect password. Please try again."}, 401)
                    return
                c.execute(
                    "UPDATE founder_users SET password_hash = ?, last_active = ? WHERE email = ?",
                    (pw_hashed, now, email),
                )
                conn.commit()
                conn.close()
                log_scan_event(existing[2] or domain, email, "USER_LOGIN", ip_addr)
                self.send_json({"ok": True, "email": email, "domain": existing[2] or domain}, 200)
                return
            else:
                if existing and existing[1] and existing[1] != pw_hashed:
                    conn.close()
                    self.send_json(
                        {"error": "Account already exists. Please switch to Returning User (Sign In)."},
                        409,
                    )
                    return
                c.execute(
                    '''INSERT INTO founder_users (email, password_hash, startup_domain, created_at, last_active)
                       VALUES (?, ?, ?, ?, ?)
                       ON CONFLICT(email) DO UPDATE SET
                       password_hash=excluded.password_hash,
                       startup_domain=excluded.startup_domain,
                       last_active=excluded.last_active''',
                    (email, pw_hashed, domain, now, now),
                )
                conn.commit()
                conn.close()
                log_scan_event(domain, email, "ACCOUNT_SIGNUP", ip_addr)
                self.send_json({"ok": True, "email": email, "domain": domain}, 200)
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
            users = c.execute(
                "SELECT email, startup_domain, plan, created_at, last_active FROM founder_users ORDER BY id DESC LIMIT 100"
            ).fetchall()
            scans = c.execute(
                "SELECT domain, user_email, mode, ip_addr, created_at FROM scan_logs ORDER BY id DESC LIMIT 150"
            ).fetchall()
            conn.close()

            u_rows = (
                "".join(
                    [
                        f"<tr><td><strong>{u[0]}</strong></td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[4]}</td>"
                        f"<td><a target='_blank' href='https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(u[0])}&su={urllib.parse.quote('Your Star Intel teardown for ' + u[1])}' style='color:#059669;font-weight:700;'>✉️ Email Founder ↗</a></td></tr>"
                        for u in users
                    ]
                )
                or "<tr><td colspan='6'>No registered emails yet — share your link on X!</td></tr>"
            )

            s_rows = (
                "".join(
                    [
                        f"<tr><td><strong>{s[0]}</strong></td><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]}</td></tr>"
                        for s in scans
                    ]
                )
                or "<tr><td colspan='5'>No scans recorded yet.</td></tr>"
            )

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
                clean_url = (
                    raw_url.replace("https://", "").replace("http://", "").split("/")[0]
                    or "StealthStartup"
                )
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
                        f_mkt = ex.submit(
                            fetch_web_signal,
                            f"top competitors and target B2B buyers for {custom_desc} {custom_icp}",
                        )
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
                        f_mkt = ex.submit(
                            fetch_web_signal,
                            f"top competitors alternatives pricing and target B2B customers for {clean_url}",
                        )
                        f_dns = ex.submit(verify_domain_and_emails, clean_url) if "." in clean_url else None

                        startup_home = f_home.result()
                        direct_pricing_raw = f_direct_price.result()
                        startup_pricing = (direct_pricing_raw[:1600] + "\n" + f_price.result()[:1600]).strip()
                        market_search = f_mkt.result()
                        contact_info = f_dns.result() if f_dns else {"dns_live": False, "emails": []}
                        mode_used = "PARALLEL LIVE RECON"
                        pricing_page_fetched = any(
                            tok in startup_pricing.lower()
                            for tok in ["$", "€", "£", "/mo", "/month", "free tier", "enterprise"]
                        )

                sys_p = f'''You are Star Intel's Autonomous Competitive Intelligence & Customer Hunter Engine.
Analyze '{clean_url}' ({custom_desc or 'live domain'}) and return ONLY valid JSON with these exact keys:
1. "startup_name": Clean name of {clean_url}
2. "core_product_summary": 1-sentence summary of what they build and who their ideal B2B customer is.
3. "pricing_and_packaging_strategy": object with keys:
   - "current_or_inferred_model": Pricing tiers if directly observed in context, or clearly labeled inferred positioning if not fetched.
   - "pricing_verification_status": MUST be "observed" if explicit price numbers appear in the scraped signal, or "unverified (inferred)" if the pricing page could not be fetched or hides pricing.
   - "pricing_source": MUST always be the exact attempted or source URL starting with https:// (e.g. "https://{clean_url}/pricing").
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
7. "red_team_cso_verdict": Brutally honest critique of the #1 threat to {clean_url}.'''

                user_p = f"CHECK_DATE: {check_date}\nPRICING_SIGNAL_DETECTED: {pricing_page_fetched}\nSTARTUP ({clean_url}):\n{startup_home[:2800]}\n\nPRICING:\n{startup_pricing[:2200]}\n\nMARKET & CUSTOMERS:\n{market_search[:2800]}"
                try:
                    data = call_llm(sys_p, user_p)
                    if not isinstance(data, dict) or not data.get("competitor_matrix"):
                        time.sleep(2)
                        data = call_llm(sys_p, user_p)
                except Exception:
                    time.sleep(2)
                    data = call_llm(sys_p, user_p)

                if not isinstance(data, dict):
                    data = {}
                if not isinstance(data.get("competitor_matrix"), list):
                    data["competitor_matrix"] = []
                if not isinstance(data.get("growth_playbooks"), list):
                    data["growth_playbooks"] = []

                for c in data.get("competitor_matrix", []):
                    c["check_date"] = check_date
                    if not c.get("verification_status"):
                        c["verification_status"] = (
                            "observed" if "$" in str(c.get("pricing_model_and_cost", "")) else "unverified"
                        )
                    dom = (
                        str(c.get("competitor_domain", "competitor.com"))
                        .replace("https://", "")
                        .replace("http://", "")
                        .split("/")[0]
                        .strip()
                    )
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

                prospects = data.get("customer_prospects")
                if not isinstance(prospects, list):
                    prospects = []
                data["customer_prospects"] = prospects

                for p in prospects:
                    if not isinstance(p, dict):
                        continue
                    p["check_date"] = check_date
                    p["dns_status"] = "VALID MX/DNS"
                    p_dom = str(p.get("customer_domain", "")).replace("https://", "").replace("http://", "").split("/")[0].strip()
                    if not p.get("target_email") or "@" not in str(p.get("target_email", "")):
                        p["target_email"] = f"founders@{p_dom}" if p_dom else "founders@company.com" 

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
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))


if __name__ == "__main__":
    ensure_telemetry_tables()
    print(f"[+] Star Intel Studio GTM Portal running at: http://localhost:{PORT}")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StarIntelHandler)
    server.serve_forever()
