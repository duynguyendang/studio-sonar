# 🎬 StudioSonar: Autonomous Media Intelligence & Production Orchestrator

> **Built for Google Cloud x ClickHouse Partner Track — "Lights. Camera. Code." Hackathon**  
> An autonomous 8-agent swarm running on Google Cloud Run that continuously monitors multi-platform media telemetry, queries high-velocity comment streams via ClickHouse OLAP, and autonomously orchestrates PR alerts, executive task boards, and production-ready video scripts.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/)
[![Gemini](https://img.shields.io/badge/Gemini-3.8%20Flash-orange?logo=google&logoColor=white)](https://ai.google.dev/)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-OLAP%20Database%20(%3C30ms)-FFCC01?logo=clickhouse&logoColor=black)](https://clickhouse.com/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Multi--Agent%20Mesh%20v2.7.1-34A853?logo=google&logoColor=white)](https://adk.dev/)

---

## 📌 Submission Quick Links

* **Live Hosted Application:** [https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app](https://studiosonar-taskmaster-i7mjye6viq-uc.a.run.app)
* **3-Minute Walkthrough Video:** `https://youtu.be/your-demo-id` *(Replace with your presentation video)*
* **Partner Track:** ClickHouse Partner Track & Google Cloud Serverless Track
* **Repository License:** [MIT License](LICENSE)

---

## 1. Problem & Executive Summary

In modern high-velocity media and entertainment workflows, cultural trends and brand PR crises erupt within hours:

* **The Telemetry Bottleneck:** Studios track tens of thousands of audience comments, sudden velocity surges, and creator duets across YouTube and TikTok daily.
* **Passive Chatbot Failure:** Traditional conversational agents wait for human prompts (*"How can I help you today?"*). By the time a PR Director wakes up to ask questions, reputational damage is already viral across algorithms.
* **OLAP Necessity:** Processing vector clusters, velocity acceleration slopes, and sentiment shifts across millions of raw comments creates severe latency bottlenecks inside conventional LLM context loops.

**StudioSonar replaces passive chat with a deterministic, autonomous 8-agent production crew.** Operating continuously in the background, StudioSonar streams social telemetry into **ClickHouse Cloud (<30ms Hot Path)** and **Google BigQuery (System of Record)**, runs sub-second analytical aggregations, grounds findings via **Gemini 3.8 Flash**, and automatically executes enterprise actions on **Slack, Notion, and Google Docs**.

---

## 2. System Architecture

```
       [ YouTube Data API v3 ]           [ TikTok Trend Stream ]
                  │                                 │
                  ▼                                 ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             High-Throughput Streaming Ingestion             │
       └──────────────────────────────┬──────────────────────────────┘
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                 ClickHouse Cloud OLAP Engine                │
       │  • Real-time Columnar Comment Log Aggregation (<30ms)       │
       │  • P95 Comment Velocity & Anomaly Indices                   │
       │  • Native Time-Series Analytics (decay, slope, entropy)     │
       └──────────────────────────────┬──────────────────────────────┘
                                      ▲ ClickHouse MCP Server / Client
                                      │ (Native High-Frequency SQL)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                Google Cloud Run: 8-Agent Swarm Orchestrator Engine                      │
│                (Google ADK 2.7 • Antigravity SDK • Gemini 3.8 Flash)                    │
│                                                                                         │
│  [1. Telemetry Ingest] ──► [2. ClickHouse Query Agent] ──► [3. Anomaly Detector]       │
│  [4. Sentiment Vector] ──► [5. Trend Trajectory]       ──► [6. Triage Director]        │
│  [7. Script Drafter]   ──► [8. Dispatch Master]                                         │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │ Autonomous Action Dispatch
                ┌──────────────────────────┼──────────────────────────┐
                ▼                          ▼                          ▼
       [ Slack Webhook ]            [ Notion API ]           [ Google Docs API ]
        (P1 Crisis Alert)       (Executive Kanban Task)   (Script Draft + Retention Hooks)
```

---

## 3. Mission Control Dashboard: Core Feature Walkthrough

StudioSonar provides a single pane of glass command center designed for media executives, PR directors, and technical operations teams:

### 3.1 🎛️ Mission Cockpit: Real-Time Executive Surveillance & Hot Ledger
The **Mission Cockpit** is the primary executive dashboard providing instant situational awareness over all monitored media streams:
* **Live Telemetry Banners:** Top-level dynamic counters displaying Total Processed Views, Comments Logged (24h), and Historical Snapshots in BigQuery with real-time count-up animations.
* **PR Crisis Stance Indicator:** Color-coded status badge (`ALL_CLEAR_GREEN` vs `ESCALATED_P1_ALERT`) reflecting real-time threat levels across all monitored assets.
* **Interactive Asset Grid:** Real-time surveillance ledger for all monitored YouTube uploads and TikTok sounds (e.g., *Brent Oil Hits $100*, *Ferrero Nutella Inside*, *Phương Mỹ Chi MV*, *Thùy Chi MV*). Each card displays:
  - Direct clickable cross-check URLs linking to the live external platforms.
  - Multi-platform metrics (Views, Likes, Comments, Snapshots in BigQuery).
  - **4D Sentiment Spectrum Bar:** Interactive visualization breaking down audience sentiment into *Positive Resonance*, *Cultural Aesthetic*, and *Community Friction*.
* **ClickHouse Native Statistical Cards:** Real-time display of **Pearson Cross-Platform Synergy** ($r$) and **Momentum Slope** ($\beta$) measuring viral acceleration vs. audience fatigue.
* **Instant Attribution Trigger:** A dedicated action button on each asset card allowing operators to jump directly to deep root-cause forensics.

### 3.2 📄 Intelligence Dossier: Deep Multi-Agent Audits & GCS Substrate
The **Intelligence Dossier** delivers executive-ready, long-form analytical audits compiled autonomously by the Google ADK swarm:
* **Live Decoupled GCS Substrate:** Dossiers are rendered dynamically from Markdown files stored directly in Google Cloud Storage (`gs://studiosonar-dev-reports/`), ensuring zero frontend hardcoding debt.
* **Dynamic Catalog Auto-Discovery (`GET /api/v1/reports/list`):** The Dossier selector dropdown automatically queries the GCS bucket in real-time, instantly listing new video or channel reports as soon as they are uploaded without requiring code changes or redeployments.
* **Comprehensive Multi-Dimensional Audits:**
  - **Master 24h Pulse Dossier:** Cross-channel holistic synthesis of macro trends, velocity leaders, and brand safety health.
  - **High-Priority Asset Deep-Dives:** 6-section and 7-section audits featuring KaTeX mathematical baselines, sentiment cohort verbatim quotes, and prescriptive autonomous growth or PR containment strategies synthesized by Gemini 3.8 Flash.
* **Interactive Visualization Support:** Renders rich, dark-mode Mermaid flowcharts, formatted markdown data tables, and mathematical formulas directly in the browser.
* **On-Demand GCS Refresh:** The **🔄 Refresh Dossier** button re-queries the GCS bucket to pull the latest analytical deliverables on demand.

### 3.3 ⚙️ Tech Ops: Swarm Topology, ClickHouse Forensics & Attribution Radar
The **Tech Ops** screen provides an engineering-grade control room for inspecting swarm internals, distributed database telemetry, and granular mathematical forensics:
* **Live Agent Swarm Topology Graph:** An interactive HTML5 canvas mapping the 8 Google ADK agent nodes and their active communication edges.
  - **Agent Reasoning Inspector:** Clicking any agent node opens an interactive modal revealing the agent's live cognitive thought process, tool execution inputs, and decision rationale.
* **ClickHouse Advanced Mathematical Forensics Matrix:**
  - **1. Z-Score Outlier Radar:** Real-time 24-period rolling baseline evaluating statistical anomalies against $2.5\sigma$ and $3.0\sigma$ thresholds.
  - **2. Momentum Acceleration Slope ($\beta$):** ClickHouse linear regression slope measuring whether traffic velocity is actively accelerating, plateauing, or cooling down.
  - **3. Audience Polarization Spread ($Q_{90} - Q_{10}$):** Interquartile spread detecting internal community conflict ("Civil War" index).
  - **4. Coordinated Bot Brigade vs. Organic Forensics:** Computes Shannon author entropy and author hash diversity ($A_{\text{diversity}}$) to distinguish coordinated astroturfing attacks from genuine community outcry.
* **External Attribution & Root-Cause Radar (Google Search Grounded):**
  - Connects ClickHouse statistical outliers with live Google Search Grounding (Vertex AI ADC).
  - Traces external catalysts (press syndication, TikTok audio trends, Reddit discussion threads) and audience friction vectors.
  - Generates interactive Mermaid causal flowcharts and prescriptive creator response protocols with verified web citations.
* **Live Swarm Terminal (`studiosonar tail -f`):** Live streaming event log showing sub-second agent decisions and real container resource telemetry (CPU/RAM).
* **Monitored Asset Streams Sidebar:** Real-time catalog of all active stream endpoints with live verification links.

### 3.4 💬 Settings Copilot: Conversational Natural Language Control
StudioSonar includes a natural language command bar allowing operators to steer the system without navigating complex menus:
* **Zero-Prompt Background Operation:** The swarm functions autonomously on schedule, but operators can intervene at any time via the Settings Copilot bar.
* **Natural Language Command Processing:** Supports commands in English and Vietnamese (e.g., `"quét 30 ngày"`, `"kích hoạt chu kỳ phân tích"`, `"kiểm tra an toàn thương hiệu"`), processed by Gemini 3.8 Flash via `/api/v1/chat/command`.

---

## 4. Partner Integration: Why ClickHouse?

StudioSonar relies on **ClickHouse Cloud as the core analytical backbone** for sub-second telemetry aggregation before passing synthesized context to Gemini 3.8 Flash.

### Key ClickHouse Capabilities Leveraged:

1. **High-Throughput Columnar Aggregations:** Aggregating millions of sentiment data points across sliding windows in **<30ms** using `MergeTree` and `AggregatingMergeTree` with `-State` / `-Merge` combinators.
2. **Deterministic Anomaly Triggers:** Computing comment velocity spikes (`velocity > 250%` over rolling baseline) directly inside ClickHouse SQL rather than loading raw payloads into memory.
3. **Native Time-Series & Statistical Functions:** StudioSonar maps business media questions directly into native ClickHouse algorithms:

| Business Intelligence Question | ClickHouse Native Function | Architectural Role |
|---|---|---|
| *"Is this backlash accelerating or peaking?"* | `simpleLinearRegression(timestamp, velocity)` | Velocity acceleration slope ($\beta$) |
| *"Is this discussion heating up with exponential recency?"* | `exponentialTimeDecayedCount(600)` | Real-time heat score |
| *"Are comments authentic or from a bot brigade?"* | `entropy(author_id_hash)` + $c/u$ ratio | Shannon entropy brigade detection |
| *"Are YouTube and TikTok audiences cross-amplifying?"* | `corr(yt_hourly, tt_hourly)` | Pearson cross-platform synergy radar |
| *"What are the exact friction keywords?"* | `topK(5)(comment_text)` | Friction & dispute term extraction |
| *"What is the rolling 48-hour velocity sparkline?"* | `sparkbar(48)(hourly_views)` | Instant UTF-8 ASCII trendlines |

4. **MCP Tool Integration:** Exposing ClickHouse functions to Google ADK via a custom Model Context Protocol (MCP) toolset (`src/mcp/clickhouse_tools.py`) and high-frequency client (`src/data/clickhouse_client.py`).

### Sample Runtime Query Executed by Agent:

```sql
SELECT 
    channel_id, 
    video_id, 
    count() AS total_comments, 
    avg(sentiment_score) AS mean_sentiment, 
    countIf(sentiment_score < -0.6) / count() AS toxicity_ratio, 
    (count() - lagInFrame(count(), 1) OVER (PARTITION BY video_id ORDER BY window_start)) AS velocity_spike
FROM default.media_telemetry_stream 
WHERE timestamp >= now() - INTERVAL 6 HOUR 
GROUP BY channel_id, video_id, toStartOfInterval(timestamp, INTERVAL 1 HOUR) AS window_start 
HAVING toxicity_ratio > 0.35 AND velocity_spike > 150 
ORDER BY velocity_spike DESC 
LIMIT 5;
```

---

## 5. The 8-Agent Swarm Specification

StudioSonar coordinates **8 specialized, decoupled agents** executing via Google ADK v2.7.1 and Antigravity SDK:

| Agent Name | Framework / Engine | Core Responsibility |
|---|---|---|
| **1. Stream Ingest Agent** | FastAPI / Cloud Run | Handles platform rate limits, ingests live social feeds, streams clean payloads into ClickHouse hot path and BigQuery SoR. |
| **2. ClickHouse Query Agent** | ClickHouse MCP / ADK 2.7 | Translates natural language media queries into deterministic high-performance ClickHouse SQL with sub-30ms execution. |
| **3. Anomaly Detector** | Gemini 3.8 Flash / Antigravity | Scans ClickHouse velocity metrics, identifying toxic sentiment backlash (>150%) and viral breakouts (>200%). |
| **4. Sentiment Vector Agent** | ClickHouse Vector Engine | Correlates cross-platform comment clusters, identifying nuanced behavioral cohorts (slang, sarcasm, feature friction). |
| **5. Trajectory Predictor** | Gemini 3.8 Flash | Forecasts viral meme half-life, retention peaks, and audience drop-off points using ClickHouse linear regression slopes. |
| **6. Triage Director** | ADK Multi-Agent Coordinator | Topological supervisor deciding between PR Crisis Containment, Viral Content Creation, or No-Op standby. |
| **7. Production Script Drafter** | Gemini 3.8 Flash | Generates production-ready 60-second video scripts engineered with the Universal Viral Hook Playbook (Pattern Interrupt, Contrarian Truth). |
| **8. Dispatch Master** | Webhooks & Google Workspace API | Executes external side-effects: fires Slack P1 alerts, creates Notion triage task boards, and formats Google Docs scripts. |

---

## 6. Technology Stack

* **Foundation LLM:** Google Gemini 3.8 Flash (Vertex AI IAM ADC & API Key)
* **Agent Framework:** Google Agent Development Kit (ADK) v2.7.1 & Antigravity Multi-Agent SDK
* **Cloud Infrastructure:** Google Cloud Run (Serverless Mesh), Cloud Scheduler, Cloud Secret Manager, Cloud Storage (GCS)
* **Partner Technology:** **ClickHouse Cloud** (Sub-second OLAP Hot Path, Time-Series & Statistical Engine)
* **System of Record:** **Google BigQuery** (Audit Ledger, Partitioned Archival Storage, Vector Embeddings)
* **External APIs & Integrations:** Slack Incoming Webhooks, Notion REST API v1, Google Docs API, YouTube Data API v3

---

## 7. Local Setup & Reproduction Guide

### Prerequisites

* Python 3.11+
* Docker & Google Cloud SDK (`gcloud`)
* Active ClickHouse Cloud cluster or local ClickHouse instance

### 1. Clone & Configure Environment

```bash
git clone https://github.com/duynguyendang/studio-sonar.git
cd studio-sonar
cp .env.example .env
```

Configure your `.env` credentials:

```ini
# Google & Gemini Credentials
GEMINI_API_KEY="your_gemini_api_key"
GEMINI_MODEL="gemini-3.8-flash"
GCP_PROJECT_ID="your_gcp_project_id"
BIGQUERY_DATASET="studiosonar_analytics"

# ClickHouse Cloud Credentials
CLICKHOUSE_HOST="your-cluster.clickhouse.cloud"
CLICKHOUSE_PORT="8443"
CLICKHOUSE_USER="default"
CLICKHOUSE_PASSWORD="your_clickhouse_password"
CLICKHOUSE_DATABASE="default"

# External Enterprise Dispatch
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
NOTION_API_KEY="secret_..."
NOTION_DATABASE_ID="..."
YOUTUBE_DATA_API_KEY="AIza..."
```

### 2. Run Database Migrations

Initialize the ClickHouse schema (tables, materialized views, and native aggregation states):

```bash
python scripts/init_clickhouse_schema.py
```

*(You can also inspect or run [`infra/clickhouse_schema.sql`](infra/clickhouse_schema.sql) directly in ClickHouse Console).*

### 3. Run Locally

Install dependencies and start the local command center:

```bash
pip install -r requirements.txt
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

Open `http://localhost:8080` to access the StudioSonar Mission Control Dashboard.

### 4. Deploy to Google Cloud Run

Deploy the serverless container to Google Cloud Run:

```bash
# Option A: One-click automated deployment script
bash infra/deploy_cloud_run.sh

# Option B: Direct gcloud deploy
gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/studiosonar-taskmaster
gcloud run deploy studiosonar-taskmaster \
  --image gcr.io/[YOUR_PROJECT_ID]/studiosonar-taskmaster \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=[YOUR_PROJECT_ID],CLICKHOUSE_HOST=[YOUR_HOST],CLICKHOUSE_PASSWORD=[YOUR_PWD]"
```

---

## 7. Open Source License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
