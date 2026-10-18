# ✦ Star Intel | Autonomous B2B Competitive Intelligence Engine

**Repository:** https://github.com/jmakhanu/Star-intel  
**Live Web Portal:** https://jmakhanu.github.io/Star-intel/

### 📄 View Live Sample Deliverables (Generated Automatically in 35 Seconds)
* **[Aerospace & Defense Sample (Capella Space vs. ICEYE)](samples/Sample_Aerospace_Capella_vs_ICEYE.pdf)** — Full 5-section SAR satellite technical & commercial battlecard.
* **[AgriTech & IoT Hardware Sample (Rethink Organic vs. Flybox UK)](samples/Sample_AgriTech_Rethink_vs_Flybox.pdf)** — Full 5-section decentralized BSF & sensor battlecard.

---

Star Intel is an autonomous, multi-agent competitive intelligence pipeline built with **LangGraph** and **120B Cloud LLMs**. It infiltrates competitor documentation, pricing tiers, and technical specs, stress-tests findings through an adversarial Red Team loop, commits structured records to a local SQLite Data Moat, renders executive-ready PDF battlecards, and fires real-time Block Kit alerts into Slack.

## Core Architecture
1. **Dual-Context Ingestion:** Scrapes both the protected client's baseline capabilities and the target adversary's live pages.
2. **Primary Analyst Node:** Extracts structured JSON pricing/vulnerability arrays alongside a comprehensive technical and commercial breakdown.
3. **Adversarial Red Team Node:** Assumes the persona of the rival Chief Strategy Officer to critique weak assumptions and assign a 1–10 Threat Severity Score.
4. **Lead Strategist Refinement Node:** Hardens the final dossier with field-ready sales trap questions and direct rebuttals.
5. **Local SQLite Data Moat (vault/):** Tracks SHA-256 content hashes, vulnerability matrices, and historical Red Team critiques.
6. **Automated Delivery (reports/ & Slack):** Generates timestamped, branded PDF dossiers and pushes instant threat summaries via Slack Webhooks.
