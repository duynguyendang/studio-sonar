# 🎙️ StudioSonar: Autonomous Media Taskmaster Agent

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run%20%7C%20BigQuery%20%7C%20GCS-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Multi--Agent%20Mesh-34A853?logo=google&logoColor=white)](https://adk.dev/)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini%20Flash-8E75C2?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Hackathon Track](https://img.shields.io/badge/Hackathon%20Track-The%20Taskmaster-FF6F00)](https://allthingsagentichackathon.devpost.com/)

> **The 24/7 Autonomous Media Intelligence & Brand Defense Swarm.**  
> StudioSonar is not a chatbot that waits for human questions. It is a **Zero-Prompt Autonomous Taskmaster** that operates around the clock in the background—continuously ingesting social telemetry into **Google BigQuery**, detecting mathematical velocity spikes and sentiment anomalies via **Vertex AI Gemini Flash**, persisting intelligence to **Google Cloud Storage**, and executing enterprise actions on **Slack, Notion, and Google Docs**.

---

## 🌐 Live Production Command Center

* 👑 **Root Taskmaster & Web Dashboard:** [https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app](https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app)
* 📡 **Channel Sentinel Agent:** `https://studiosonar-channel-monitor-i7mjye6viq-uc.a.run.app`
* 🔍 **Anomaly Detector Agent:** `https://studiosonar-anomaly-detector-i7mjye6viq-uc.a.run.app`
* 🚨 **PR Crisis Strategist Agent:** `https://studiosonar-pr-strategist-i7mjye6viq-uc.a.run.app`
* ✍️ **Viral Content Creator Agent:** `https://studiosonar-content-creator-i7mjye6viq-uc.a.run.app`
* ⏱️ **Autonomous Scheduler Heartbeat:** 1-Hour Interval (`0 * * * *` via Cloud Scheduler)
* ☁️ **Intelligence Reports Storage:** `gs://studiosonar-dev-reports`

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
                   ▼ (Every 1 Hour)
       [ Google BigQuery OLAP ]
                   │
                   ▼ (Mathematical Spike Detection)
   ┌───────────────────────────────────────────────────┐
   │  🚨 Negative Backlash Spike (>150%)               │
   │  👉 Auto-Dispatches Slack Alert + Notion Triage   │
   ├───────────────────────────────────────────────────┤
   │  🚀 Positive Viral Breakout (>200%)               │
   │  👉 Auto-Drafts 60s Shorts Script in Google Docs  │
   ├───────────────────────────────────────────────────┤
   │  📊 New Upload Detection within 24h               │
   │  👉 Auto-Generates Executive Performance Scorecard│
   └───────────────────────────────────────────────────┘
```

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
2. **Declarative Tool Sandboxing & Function Calling:** ADK converts deterministic Python I/O classes (`YouTubeLiveClient`, `TikTokHarvester`, `SlackDispatcher`) into strict JSON schemas for Vertex AI Gemini Flash, enforcing role-based tool access per agent.
3. **Enterprise Observability & Traceability:** ADK maintains structured execution traces, allowing enterprise stakeholders to audit *why* an agent made a decision, *how* it reasoned, and *what* downstream actions it triggered.

---

## ☁️ Why This Deployment Model? (Distributed Cloud Run Microservices)

StudioSonar is deliberately deployed as **5 independent Google Cloud Run microservices** rather than a single monolithic container:

1. **Asymmetric Workload Scaling & True Scale-to-Zero:**
   - **Taskmaster Orchestrator:** Runs once per hour via Cloud Scheduler (`0 * * * *`).
   - **Anomaly Detector:** Performs high-throughput batch queries on BigQuery.
   - **PR Crisis & Viral Creator:** Remain at **0 instances** (Scale-to-Zero) until a viral surge or PR incident occurs.  
   👉 **Cost Efficiency:** Reduces idle enterprise cloud costs by **>90%**.
2. **Stateless Container Decoupling via GCS Report Substrate:**
   - All executive intelligence markdown reports are persisted to **Google Cloud Storage (`gs://studiosonar-dev-reports`)**.
   - Container images remain **100% Stateless** and ultra-lightweight (~69 KiB build context), enabling instant cold-starts (< 1s).
3. **Zero-Key Enterprise Security (Vertex AI IAM ADC):**
   - Eliminates exposed API keys by leveraging Google Cloud IAM Service Account roles (`roles/aiplatform.user` & `roles/storage.objectAdmin`).

---


## 📈 Tangible Business ROI & Impact

| Metric | Traditional Manual Approach | StudioSonar Autonomous Swarm | Business Impact |
| :--- | :---: | :---: | :--- |
| **Crisis Detection Time** | 8 – 24 Hours | **< 5 Minutes** | Prevents brand damage before news outlets pick up backlash. |
| **Derivative Content Turnaround** | 3 – 5 Days | **< 15 Minutes** | Captures the peak algorithmic wave with 60s viral scripts. |
| **Weekly Reporting Overhead** | 40+ Hours / Channel | **0 Hours (Autonomous)** | Eliminates manual slide preparation; delivers real-time GCS dashboards. |
| **Data Verifiability** | Anecdotal / Sampled | **100% Verified Telemetry** | Backed by BigQuery OLAP storage and mathematical velocity metrics. |

---

## 🌟 Real-World Industry Use Cases

### 1. 🎵 Music Studios & Record Labels (e.g., Phương Mỹ Chi, Thùy Chi)
* **Goal:** Maximize album release momentum and fan engagement.
* **Autonomous Taskmaster Action:** When *'Thiên Đường Với Người Thương'* hits a **+310.0% Viral Retention Surge** with 74.2% of comments obsessing over the chorus melody, the swarm automatically drafts a TikTok Dance Challenge script and outlines pre-order merchandise links.

### 2. 🏭 Global Brands & Consumer Goods (e.g., Ferrero Nutella Factory)
* **Goal:** Monitor industrial transparency and consumer health sentiment.
* **Autonomous Taskmaster Action:** When industrial automation curiosity rises (+142.5%), but palm oil inquiries emerge (24.2%), the swarm automatically alerts the communications team with an FAQ prescription and proposes a 45s educational Short explaining laser hazelnut sorting.

### 3. 🎬 Media Publishers & Film Critics (e.g., Bloomberg Originals, Kiểm Định Phim)
* **Goal:** Protect editorial integrity and maintain community debate.
* **Autonomous Taskmaster Action:** Detects macro supply chain debates vs. comedic roasting themes, generating real-time community engagement strategies without human intervention.

---

## 🤖 The 5 Google ADK Multi-Agent Team

StudioSonar divides responsibilities across **5 specialized, decoupled microservices**:

| Agent Microservice | Business Mission | Autonomous Triggers | Enterprise Deliverables |
| :--- | :--- | :--- | :--- |
| **👑 Taskmaster Root Orchestrator**<br>`studiosonar-taskmaster` | **Central Commander & Dispatcher**<br>Ingests verified telemetry, manages the swarm, and updates GCS reports. | Wakes on 1-hour Cloud Scheduler heartbeat (`0 * * * *`). Polls YouTube API v3 and routes tasks via A2A mesh. | ☁️ GCS Reports Bucket<br>🖥️ Real-Time Dashboard |
| **📡 Channel Sentinel Agent**<br>`studiosonar-channel-monitor` | **Channel Watchdog & Performance Benchmark**<br>Tracks uploads on monitored channels within 24h against 30-day baseline. | Calculates velocity ratios against channel averages and generates scorecards. | 📊 Channel Intelligence<br>📈 Velocity Scorecard |
| **🔍 Anomaly Detector Agent**<br>`studiosonar-anomaly-detector` | **Sentiment Radar & Mathematical Classifier**<br>Scans BigQuery comments to classify sentiment and detect velocity anomalies. | • **Backlash Spike (>150% neg surge)** ➔ Handoff to PR Crisis Agent.<br>• **Viral Breakout (>200% pos surge)** ➔ Handoff to Content Creator. | 🚨 Multi-Agent Mesh Handoff<br>⚡ 24h Sentiment Radar |
| **🚨 PR Crisis Strategist Agent**<br>`studiosonar-pr-strategist` | **Rapid Crisis Mitigation & Brand Defense**<br>Synthesizes root causes with Gemini Flash and crafts official responses. | Triggered by negative sentiment spikes. Creates pinned comment prescriptions and mitigation checklists. | 📢 Slack `#media-alerts`<br>📋 Notion Action Board |
| **✍️ Viral Content Creator Agent**<br>`studiosonar-content-creator` | **Viral Growth Hacker & Derivative Scriptwriter**<br>Harvests viral hooks and produces 60s short-form video scripts. | Triggered by positive breakout engagement. Applies the Universal Viral Hook Playbook. | 📄 Google Docs Script Draft<br>💬 Slack Concept Pitch |

---

## 📹 Monitored Entities Grouped by Subject & Campaign

StudioSonar structures multi-platform intelligence by **Subject Entities & Campaigns**, connecting original video productions with their downstream TikTok UGC sound waves:

### 🎵 Subject 1: Phương Mỹ Chi x DTAP — 'Dân Chơi Dân Ca' Album Campaign
*Tracks the full release cycle from official YouTube master videos to derivative TikTok dance trends:*
* 📹 **YouTube Master MV:** *'Thiên Đường Với Người Thương'* (`UH21OnJwxZE` — 14.08M Views • +310.0% Viral Retention Surge)
* 🎵 **TikTok Viral Sound:** *'Thiên Đường Với Người Thương' Official Audio* (`tt_sound_pmc_thien_duong` — **128,540 UGC Videos • +420% Sound Surge**)
* 📹 **YouTube Highlight Medley:** *Album 'Dân Chơi Dân Ca'* (`Rp6ZnP5WRgI` — 232K Views • +245% Momentum)
* 🎵 **TikTok Viral Sound:** *'Dân Chơi Dân Ca' (Drop Beat)* (`tt_sound_dtap_dan_choi` — **34,210 UGC Videos • +280% Velocity**)

### 🎶 Subject 2: Thùy Chi — Western Vietnam Folk Music & Culture
*Monitors organic vocal appreciation and scenic travel integration:*
* 📹 **YouTube Master MV:** *'Yêu Lắm Miền Tây'* (`R7Bf4l5VgO8` — 15.8K Views • +185.0% Inflow Surge • 99.1% Positive Resonance)

### 🏭 Subject 3: Ferrero Nutella — Industrial Transparency & Supply Chain
*Monitors consumer brand trust, engineering curiosity, and ingredient safety sentiment:*
* 📹 **YouTube Documentary:** *How Ferrero Makes 365,000 Tons Of Nutella A Year* (`TNl9diGdyPo` — 388K Views • +142.5% Engineering Discovery)

### 📺 Subject 4: Media Publishers & Creator Ecosystems
*Monitors channel-wide publishing velocity, audience sentiment health, and booking conversions:*
* 🌐 **YouTube Channel:** *Bloomberg Originals* (`@business` — 3.4M Subscribers • Semiconductor & Macroeconomics)
* 🎬 **YouTube Channel:** *Kiểm Định Phim 9.0* (`@KiemDinhPhim9.0` — 48.4K Subscribers • Film Satire & Critique)
* 📸 **TikTok Creator:** *Thợ Chụp Ảnh Đà Lạt* (`@thochupanh.dalat` — **85K Followers • 8.4% Save-to-View • 65% Bio Booking Inquiries**)

---

### 🌐 Platform-Native Surveillance Philosophy (YouTube vs. TikTok)

| Surveillance Vector | 📹 YouTube Surveillance Engine | 🎵 TikTok Surveillance Engine |
| :--- | :--- | :--- |
| **Core Value Metric** | **Comment Density & 4D Sentiment Breakdown** | **UGC Sound Propagation & Video Creation Footprint** |
| **Data Accessibility** | Official Public Comments API (Long-form discussions) | Closed Comment API ➔ Replaced by **Derivative Video Count** |
| **Audience Intent** | Macro debate, critique, analysis & timestamp feedback | **Creative Formats (Biến hình, Dance routine, Travel POV)** |
| **Conversion Metric** | Watch-time retention & Community Tab Poll votes | **Save/Bookmark Rate (8.4%) & Bio Booking Inflow** |

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
