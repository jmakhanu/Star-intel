# 🛰️ Star Intel — Autonomous Competitive Intelligence & AutoGTM Studio

**Live Studio Web Portal:** [https://star-intel.onrender.com](https://star-intel.onrender.com)  
**Instant Demo Runs:** [`easi.run`](https://star-intel.onrender.com/?run=easi.run) • [`signedreviews.com`](https://star-intel.onrender.com/?run=signedreviews.com) • [`linear.app`](https://star-intel.onrender.com/?run=linear.app)

Star Intel is an autonomous B2B Competitive Intelligence and Go-To-Market (AutoGTM) engine designed for early-stage SaaS founders and GTM engineers. Give it any company domain—or a 2-line Stealth Startup brief—and it executes a parallel multi-agent reconnaissance pipeline in under 20 seconds.

---

## ⚡ Core Capabilities & Provenance Architecture

1. **Pricing Provenance & Audit Trails (`OBSERVED` vs. `UNVERIFIED`)**
   - Directly probes live `/pricing` endpoints alongside public market indexes in parallel (`ThreadPoolExecutor`).
   - Explicitly separates **`OBSERVED PRICE`** tiers from **`UNVERIFIED (INFERRED)`** positioning when rival pricing is gated behind enterprise sales calls.
   - Retains the exact attempted `https://.../pricing` source URL and UTC `check_date` across both the Studio UI and exported `.CSV` battlecards.

2. **4-Competitor Arbitrage & Displacement Matrix**
   - Maps rival pricing tiers, core product strengths, exploitable technical gaps, and actionable sales displacement wedges.

3. **DNS/MX-Verified B2B Buyer Hunter & Live Gmail Dispatch**
   - Identifies 4 high-intent B2B target accounts anchored to real buying triggers.
   - Verifies live domain DNS/MX records in parallel and drafts 3-paragraph founder-to-founder outbound emails (editable directly in the browser with 1-click **Gmail Web Draft** dispatch).

---

## 🛠️ Technical Stack
- **Backend:** Zero-dependency concurrent Python (`ThreadingHTTPServer` + `ThreadPoolExecutor` parallel recon + SQLite telemetry & caching)
- **Frontend:** Executive Studio Light UI (Vanilla ES6 + CSS Grid, zero-bundle latency)
- **Deployment:** Render Cloud (`render.yaml`)
