# 🎙️ StudioSonar: Autonomous Media Taskmaster Agent

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run%20%7C%20BigQuery%20%7C%20GCS-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Multi--Agent%20Mesh%20v2.7.1-34A853?logo=google&logoColor=white)](https://adk.dev/)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini%203.7%20Flash-8E75C2?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Hackathon Track](https://img.shields.io/badge/Hackathon%20Track-The%20Taskmaster-FF6F00)](https://allthingsagentichackathon.devpost.com/)

> **The 24/7 Autonomous Media Intelligence & Brand Defense Swarm.**  
> StudioSonar is not a chatbot that waits for human questions. It is a **Zero-Prompt Autonomous Taskmaster** that operates around the clock in the background—continuously ingesting social telemetry into **Google BigQuery**, detecting mathematical velocity spikes and sentiment anomalies via **Vertex AI Gemini 3.7 Flash**, persisting intelligence to **Google Cloud Storage (GCS)**, and executing enterprise actions on **Slack, Notion, and Google Docs**.

---

### ⚡ Executive Snapshot

* **🚨 Problem:** Media and brand teams spend tens of hours every week manually sifting through comment sections, missing critical 24-hour algorithmic windows and letting PR crises explode overnight while teams sleep.
* **💡 Solution:** StudioSonar is an autonomous multi-agent swarm that:
  * **Understands Semantics at Scale:** Continuously ingests and deeply parses high-velocity comment streams from YouTube & TikTok on demand into behavioral micro-clusters.
  * **Acts Autonomously in Real Time:** Detects mathematical velocity spikes and PR backlash in minutes with zero human prompting.
  * **Executes Enterprise Workflows:** Automatically drafts ready-to-produce 60s viral scripts and dispatches containment playbooks across Slack, Notion, and Google Docs.
* **🛠️ Tech Stack:**
  * **Google ADK v2.7.1:** Multi-agent topological graph & A2A handoff mesh.
  * **Vertex AI Gemini 3.7 Flash:** Cognitive reasoning, deep semantic comprehension, and creative synthesis.
  * **Google BigQuery OLAP:** Partitioned time-series telemetry storage & SQL anomaly queries.
  * **Google Cloud Run:** 5 decoupled microservices with serverless scale-to-zero.
  * **Google Cloud Storage (GCS):** Zero-cache markdown intelligence report substrate.
* **📈 Core Superpowers:**
  * **Deep Semantic Comprehension:** Goes far beyond keyword matching to parse cultural nuances, audience obsession hooks, and brand friction.
  * **100% Autonomous Taskmaster:** Self-initiating multi-agent swarm that reasons, decides, and executes without waiting for prompts.
  * **Enterprise Data Sovereignty:** 100% private data stored and queried in your own BigQuery OLAP and GCS buckets.

---

## 🌐 Live Production Command Center

* 👑 **Web Command Center & Dashboard:** [https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app](https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app)
* ⏱️ **Autonomous Scheduler Heartbeat:** 1-Hour Interval (`0 * * * *` via Google Cloud Scheduler)

---

## 🎯 The Problem: The "Blind 24 Hours" in Media & Brand Governance

Modern media studios, record labels, and global brands publish high-stakes content to millions of viewers daily. However, their operational workflow is critically broken:

1. **The 24-Hour Viral Window is Lost:** The first 24 hours determine whether a video captures algorithm momentum or dies. Teams manually review analytics days later when the trend has already peaked.
2. **PR Crises Explode While Teams Sleep:** A subtle wave of negative sentiment in the comment section can escalate into a full-blown PR disaster overnight before the communications team even opens Slack.
3. **Manual Analysis Fatigue:** Marketing teams spend 40+ hours per week manually categorizing comments, assembling slide decks, and guessing what derivative content to create.
4. **Passive AI is Useless in Crises:** Standard conversational chatbots wait for human prompts (*"How can I help you?"*). When a crisis hits at 2:00 AM, a passive assistant is worthless.

---

## 💡 The Solution: StudioSonar Autonomous Taskmaster Swarm

StudioSonar replaces manual monitoring with a **proactive, decentralized multi-agent team** that never sleeps.

```
       [ 24/7 Social Telemetry ]
                   │
                   ▼ (Every 1 Hour via Cloud Scheduler)
       [ Google BigQuery OLAP ]
                   │
                   ▼ (Mathematical Velocity & Sentiment Radar)
   ┌───────────────────────────────────────────────────┐
   │  🚨 Negative Backlash Spike (>150% Velocity)      │
   │  👉 Auto-Dispatches Slack Alert + Notion Triage   │
   ├───────────────────────────────────────────────────┤
   │  🚀 Positive Viral Breakout (>200% Velocity)      │
   │  👉 Auto-Drafts 60s Shorts Script in Google Docs  │
   ├───────────────────────────────────────────────────┤
   │  📊 New Upload Detection within 24h               │
   │  👉 Auto-Generates Executive Performance Scorecard│
   └───────────────────────────────────────────────────┘
```

---

## 🎛️ Single Pane of Glass Command Center

The StudioSonar Web Interface provides a streamlined, modern command center structured across **3 Core Views**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⚡ StudioSonar • AI MISSION CONTROL CENTER • GOOGLE ADK SWARM (Gemini 3.7)   │
├─────────────────────────────────────────────────────────────────────────────┤
│  [ 🎛️ Mission Cockpit ]    [ 📄 Intelligence Dossier ]    [ ⚙️ Tech Ops ]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **🎛️ Mission Cockpit (Default Executive View):**
   * **Cross-Platform Campaign Synergy Radar:** Real-time summary of views, BigQuery OLAP ingestion records, PR safety status, and polling velocity.
   * **Real-Time Surveillance Assets Grid:** Live cards displaying YouTube MVs & TikTok audio footprint, 4D behavioral sentiment spectrums, and one-click actions (*Reasoning Trace, View Report*).

2. **📄 Intelligence Dossier (Strategic Intelligence View):**
   * Real-time markdown intelligence documents rendered directly from **Google Cloud Storage (`gs://studiosonar-dev-reports`)**.
   * Interactive **Mermaid execution diagrams** and **KaTeX mathematical formulas**.
   * Fast report switcher for Master 24h Pulse, Company Campaign Scorecards, and Breakout Trends.

3. **⚙️ Tech Ops (Engineering & Swarm Observability View):**
   * **Live Agent Swarm Topology Graph:** Interactive visual canvas of the Google ADK execution mesh with node-level LLM reasoning inspection.
   * **4 Live Running Telemetry Counters:** Comments/24h, UGC Audio Videos, Views Tracked, and BigQuery OLAP Rows.
   * **3-Column Observability:** Swarm Agent Telemetry & Monitored Asset Streams (Left), 24h Autonomous Agent Reasoning & Decision Log (Center), Real-Time Alert Stream & Live Container Terminal (Right).

---

## 🧠 Why Google ADK? (The Multi-Agent Nervous System)

Why not simply write a monolithic Python cron script? **Traditional automation fails when scale, reasoning, and multi-disciplinary governance are required.** 

Google ADK serves as the **central nervous system** that transforms isolated tools into an intelligent, self-healing swarm:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🧠 GOOGLE ADK AGENT SWARM (Autonomous Reasoning & Context Transfer)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Native A2A Protocol: Decoupled Agent-to-Agent state & intent handoffs.   │
│ 2. Declarative Tool Binding: Least-privilege schema bindings for Gemini.   │
│ 3. Dual-Tier Fault Tolerance: Auto-fallback from HTTP mesh to in-process.   │
│ 4. Deterministic Observability: Full audit trail of AI decision-making.     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ▲
                                      │ (Orchestrated by Google ADK)
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🛠️ DETERMINISTIC TOOL CONNECTORS (I/O & Raw Data Muscle)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ • YouTube Live API  • TikTok Harvester  • BigQuery OLAP  • GCS Reports      │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Native Agent-to-Agent (A2A) Handoff Protocol:** Unlike brittle REST APIs or hardcoded `if/else` scripts, ADK standardizes contextual state transfer. When the `AnomalyDetectorAgent` flags an alert, it packages full BigQuery telemetry and autonomously handoffs execution to the `PRCrisisStrategistAgent`.
2. **Declarative Tool Sandboxing & Function Calling:** ADK converts deterministic Python I/O classes (`YouTubeLiveClient`, `TikTokHarvester`, `SlackDispatcher`) into strict JSON schemas for Vertex AI Gemini 3.7 Flash, enforcing role-based tool access per agent.
3. **Enterprise Observability & Traceability:** ADK maintains structured execution traces, allowing enterprise stakeholders to audit *why* an agent made a decision, *how* it reasoned, and *what* downstream actions it triggered.

---

## ☁️ Why This Deployment Model? (Distributed Cloud Run Microservices)

StudioSonar is deliberately deployed as **5 independent Google Cloud Run microservices** rather than a single monolithic container:

1. **Asymmetric Workload Scaling & True Scale-to-Zero:**
   * **Taskmaster Orchestrator:** Runs once per hour via Cloud Scheduler (`0 * * * *`).
   * **Anomaly Detector:** Performs high-throughput batch queries on BigQuery.
   * **PR Crisis & Viral Creator:** Remain at **0 instances** (Scale-to-Zero) until a viral surge or PR incident occurs.  
   👉 **Cost Efficiency:** Reduces idle enterprise cloud costs by **>90%**.
2. **Stateless Container Decoupling via GCS Report Substrate:**
   * All executive intelligence markdown reports are persisted to **Google Cloud Storage (`gs://studiosonar-dev-reports`)**.
   * Container images remain **100% Stateless** and ultra-lightweight (~69 KiB build context), enabling instant cold-starts (< 1s).
3. **Zero-Key Enterprise Security (Vertex AI IAM ADC):**
   * Eliminates exposed API keys by leveraging Google Cloud IAM Service Account roles (`roles/aiplatform.user` & `roles/storage.objectAdmin`).

---

## 🚀 Outstanding AI-Powered Capabilities & Business Impact

StudioSonar operates as a **Zero-Prompt Autonomous Taskmaster Swarm** powered by Google ADK and Vertex AI Gemini 3.7 Flash:

| Core Pillar | Autonomous Swarm Architecture | Enterprise Impact |
| :--- | :--- | :--- |
| **🧠 Deep Semantic Understanding at Scale** | Continuously streams & parses high-velocity comments into behavioral micro-clusters on demand. | Goes far beyond primitive polarity to uncover root causes and creative hooks. |
| **⚡ Autonomous Taskmaster Execution** | Self-initiating multi-agent graph triggers real-time actions with zero human prompting. | Eliminates human latency in capturing viral peaks or containing crises. |
| **✍️ Instant 60s Script Synthesis** | Detects algorithmic momentum and auto-drafts production-ready short-form scripts. | Captures the peak algorithmic FYP window across YouTube Shorts & TikTok. |
| **🚨 Predictive PR Crisis Containment** | Evaluates mathematical negative velocity spikes and formulates root-cause containment plans. | Prevents brand damage before external public relations escalation. |
| **☁️ Serverless Scale-to-Zero & Sovereignty** | Elastic microservices scale on demand and sleep when idle; 100% private BigQuery & GCS storage. | Maximum cloud efficiency with complete enterprise data privacy and zero vendor lock-in. |

---

### 💎 The 5 Superpowers of StudioSonar

1. **🧠 Continuous Deep Semantic Understanding at Massive Scale (Scale on Demand):**
   * Continuously ingests unstructured, high-velocity social comment streams from YouTube and TikTok without human bottleneck.
   * Leverages Gemini 3.7 Flash to decipher nuanced multilingual vernacular, sarcasm, slang, and cultural subtext into **actionable behavioral micro-clusters** (e.g., *Chorus Replay Obsession, Visual Aesthetic Appreciation, Technical Inquiries, Toxic Backlash*), providing rich creative and strategic direction far beyond primitive positive/negative scores.
2. **⚡ Autonomous 60s Short-Form Script Synthesis (Universal Viral Hook Engine):**
   * Automatically detects viral velocity breakouts on master videos and derivative audio waves.
   * Synthesizes ready-to-produce 60s video drafts (Shorts/TikTok/Reels) using the *Universal Viral Hook Playbook* (Pattern Interrupt, Contrarian Truth, Aesthetic Pacing) and exports directly into Google Docs and Slack with zero manual prompting.
3. **🚨 Predictive PR Crisis Containment & Root-Cause Diagnosis:**
   * Continuously benchmarks negative comment velocity against historical baselines on BigQuery OLAP.
   * Autonomously diagnoses the underlying root cause of audience friction in minutes, generating a comprehensive mitigation checklist, official pinned comment responses, and Notion emergency triage boards.
4. **☁️ Cloud-Native Elastic Scale-to-Zero Architecture:**
   * Built on 5 decoupled Google Cloud Run microservices that automatically scale on demand to handle viral traffic surges seamlessly, and scale back down to zero instances during idle periods for maximum cloud efficiency.
5. **🛡️ 100% Enterprise Data Sovereignty & Zero-Key Security:**
   * All raw comments, time-series metrics, and intelligence reports remain securely housed inside your enterprise's private **Google BigQuery** partitions and **GCS buckets** (`gs://studiosonar-dev-reports`), governed by Vertex AI IAM Workload Identity with zero exposed API keys.

---

## 🌟 Industry-Agnostic Applications

StudioSonar is architected as a **universal autonomous intelligence engine** adaptable across diverse media domains:

### 1. 🎵 Entertainment Studios & Music Labels
* **Goal:** Maximize release momentum, detect viral audio propagation, and protect artist brand safety.
* **Taskmaster Flow:** Detects algorithmic velocity surges on YouTube MVs and derivative TikTok audio trends, auto-synthesizing short-form challenge hooks and community engagement playbooks.

### 2. 🏭 Consumer Brands & Enterprise Product Teams
* **Goal:** Monitor industrial transparency, product launches, customer sentiment friction, and brand trust.
* **Taskmaster Flow:** Continuously benchmarks audience commentary against historical baselines, surfacing product perception shifts and drafting crisis response FAQs in real time.

### 3. 🎬 Digital Media Networks & Creator Collectives
* **Goal:** Benchmark multi-channel publishing velocity, editorial sentiment health, and audience conversion.
* **Taskmaster Flow:** Automates weekly channel scorecards, pinpoints high-CTR packaging opportunities, and routes action items directly into enterprise Notion and Slack workflows.

---

## 🤖 The 5 Google ADK Multi-Agent Team

StudioSonar divides responsibilities across **5 specialized, decoupled microservices**:

| Agent Microservice | Business Mission | Autonomous Triggers | Enterprise Deliverables |
| :--- | :--- | :--- | :--- |
| **👑 Taskmaster Root Orchestrator**<br>`studiosonar-taskmaster` | **Central Commander & Dispatcher**<br>Ingests verified telemetry, manages the swarm, and updates GCS reports. | Wakes on 1-hour Cloud Scheduler heartbeat (`0 * * * *`). Polls YouTube API v3 and routes tasks via A2A mesh. | ☁️ GCS Reports Bucket<br>🖥️ Real-Time Dashboard |
| **📡 Channel Sentinel Agent**<br>`studiosonar-channel-monitor` | **Channel Watchdog & Performance Benchmark**<br>Tracks uploads on monitored channels within 24h against 30-day baseline. | Calculates velocity ratios against channel averages and generates scorecards. | 📊 Channel Intelligence<br>📈 Velocity Scorecard |
| **🔍 Anomaly Detector Agent**<br>`studiosonar-anomaly-detector` | **Sentiment Radar & Mathematical Classifier**<br>Scans BigQuery comments to classify sentiment and detect velocity anomalies. | • **Backlash Spike (>150% neg surge)** ➔ Handoff to PR Crisis Agent.<br>• **Viral Breakout (>200% pos surge)** ➔ Handoff to Content Creator. | 🚨 Multi-Agent Mesh Handoff<br>⚡ 24h Sentiment Radar |
| **🚨 PR Crisis Strategist Agent**<br>`studiosonar-pr-strategist` | **Rapid Crisis Mitigation & Brand Defense**<br>Synthesizes root causes with Gemini 3.7 Flash and crafts official responses. | Triggered by negative sentiment spikes. Creates pinned comment prescriptions and mitigation checklists. | 📢 Slack `#media-alerts`<br>📋 Notion Action Board |
| **✍️ Viral Content Creator Agent**<br>`studiosonar-content-creator` | **Viral Growth Hacker & Derivative Scriptwriter**<br>Harvests viral hooks and produces 60s short-form video scripts. | Triggered by positive breakout engagement. Applies the Universal Viral Hook Playbook. | 📄 Google Docs Script Draft<br>💬 Slack Concept Pitch |

---

## 📡 Dynamic Entity Monitoring & Extensible Taxonomy

StudioSonar operates with **Zero Hardcoded Entities**. Channels, videos, and UGC audio streams are registered dynamically at runtime:

1. **Multi-Platform Support:** Ingests official YouTube Channels (`@handle` or Channel ID), individual YouTube Videos/Shorts, and TikTok UGC Sound Waves.
2. **Custom Sentiment & Intent Taxonomies:** Each tracked entity supports custom behavioral classification dimensions (e.g., *Brand Loyalty, Product Feedback, Technical Inquiries, Viral Adoption*).
3. **Flexible Lookback Windows & Cost Governance:** Configure 7-day, 14-day, or 30-day surveillance windows to optimize API quota and BigQuery compute.
4. **Multi-Interface Registration:**
   * **Web Cockpit UI:** One-click registration via the Command Center modal.
   * **Natural Language Copilot:** Chat commands like *"Track channel @TheVerge with 14-day lookback"*.
   * **Interactive CLI:** Run `python3 -m src.demo.tracking_manager_cli` for terminal-based management.
   * **REST API:** Programmatic CRUD endpoints at `/api/v1/registry/tracking`.

---

## 📊 Sample Reports vs. Real-Time Intelligence

* 📁 **Pre-Generated Sample Reports:** The [`reports/`](reports/) folder contains canonical reference intelligence dossiers demonstrating the standardized 7-section channel audit and 6-section video performance architectures produced by Gemini 3.7 Flash.
* 🌐 **Live Dynamic Dossiers:** For real-time, zero-cache intelligence dossiers generated dynamically from live BigQuery telemetry and stored in GCS (`gs://studiosonar-dev-reports`), visit the production command center:  
  👉 [**https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app**](https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app)

---

## ⚡ Quickstart & Local Run

```bash
git clone https://github.com/StudioSonar-AI/studiosonar-taskmaster.git
cd studio-sonar
pip install -r requirements.txt

# Run Local Dashboard
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

> 📖 **For the Deep Technical Blueprint & Mathematical Formulations, read [docs/architecture.md](docs/architecture.md).**
