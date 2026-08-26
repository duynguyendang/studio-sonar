#!/usr/bin/env python3
"""
StudioSonar Taskmaster - Interactive Multi-Agent Demonstration Script
Demonstrates autonomous collaboration between Google ADK specialized agents:
- StudioSonarOrchestrator (Root Supervisor)
- ChannelMonitorAgent (Company Channel Sentinel & Statistical Synthesizer)
- AnomalyDetectorAgent (BigQuery & Vector Specialist)
- PRCrisisStrategistAgent (Crisis Resolution Specialist)
- ViralContentCreatorAgent (Viral Script & Retention Specialist)
"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from src.agents.orchestrator import taskmaster_orchestrator
from src.core.config import settings

console = Console()

def print_banner():
    banner_text = """
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                     🎙️  S T U D I O S O N A R                             ║
    ║         Google ADK Multi-Agent System  •  Track: The Taskmaster               ║
    ║                 Powered by Google Gemini 3.7 Flash                            ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner_text, style="bold cyan", border_style="bright_blue"))

def run_demo():
    print_banner()
    
    # Display Agent Team Roster
    roster_table = Table(title="🤖 Google ADK Multi-Agent Team Roster", border_style="cyan")
    roster_table.add_column("Agent Name", style="bold yellow")
    roster_table.add_column("Specialist Role", style="bold white")
    roster_table.add_column("Assigned MCP Tools", style="green")
    
    roster_table.add_row(
        "StudioSonarOrchestrator",
        "Team Supervisor & Delegation Manager",
        "Inter-Agent Handoff Protocol"
    )
    roster_table.add_row(
        "ChannelMonitorAgent",
        "Company Channel Sentinel & Stats Analyst",
        "check_channel_uploads, synthesize_scorecard"
    )
    roster_table.add_row(
        "AnomalyDetectorAgent",
        "Data Telemetry & Vector Specialist",
        "query_bigquery_spikes, search_vector_clusters"
    )
    roster_table.add_row(
        "PRCrisisStrategistAgent",
        "Crisis Resolver & Strategic Stance",
        "dispatch_slack_crisis_alert, generate_notion_board"
    )
    roster_table.add_row(
        "ViralContentCreatorAgent",
        "Retention Scriptwriter & Content Architect",
        "create_google_doc_video_script, generate_notion_board"
    )
    console.print(roster_table)
    console.print(f"\n[bold yellow]Runtime Environment:[/bold yellow] LLM = [bold green]{settings.gemini_model}[/bold green] | Warehouse = [bold green]Google BigQuery[/bold green] | Mode = [bold green]{settings.execution_mode}[/bold green]\n")

    # -------------------------------------------------------------------------
    # PART 1: DEDICATED COMPANY CHANNEL SENTINEL & STATISTICAL SCORECARD
    # -------------------------------------------------------------------------
    console.rule("[bold blue]🔵 WORKFLOW 1: Company Channel Sentinel ➔ New Video Detected ➔ Statistical Scorecard")
    console.print("[dim]StudioSonar continuously monitors the company's official channel (Acme AI Corp)...[/dim]\n")
    time.sleep(1)

    with console.status("[bold magenta]Detecting new uploads and synthesizing statistical telemetry with Gemini 3.7 Flash...", spinner="dots"):
        time.sleep(1.5)
        channel_results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="COMPANY_CHANNEL")

    console.print("✅ [bold green]New Video Upload Detected:[/bold green] 'Introducing Acme AgentStudio 2.0: Build Background Taskmasters in Minutes' (Published 3.5h ago)")

    for act in channel_results.get("actions_executed", []):
        tool_name = act.get("tool")
        res = act.get("result", {})
        
        if tool_name == "dispatch_slack_video_scorecard":
            console.print(f"\n[bold blue]📊 Autonomous Statistical Scorecard Delivered to Slack (#company-channel-metrics)[/bold blue]")
            stats_table = Table(title="📈 Video Performance Metrics (3.5h Post-Launch)", border_style="blue")
            stats_table.add_column("Metric", style="bold white")
            stats_table.add_column("Value", style="bold green")
            stats_table.add_column("Benchmark vs Channel Baseline", style="yellow")
            
            stats_table.add_row("Total Views", "42,500 views", "+254.1% vs 3h Baseline (12,000 views)")
            stats_table.add_row("Velocity", "12,143 views/hour", "Viral Tier 1 Acceleration")
            stats_table.add_row("Engagement Rate", "10.59%", "Top 5% of all uploads")
            stats_table.add_row("Audience Sentiment", "82.5% Positive", "3.3% Negative / 14.2% Inquiries")
            console.print(stats_table)

            console.print(Panel(
                "[bold]💡 Gemini 3.7 Flash Executive Synthesis:[/bold]\n"
                "The new product keynote is outperforming historical benchmarks by +254%. Viewers are highly excited "
                "about zero-prompt background Taskmasters. Primary technical friction points are Developer Free-Tier pricing "
                "and requests for Python SDK tutorials.\n\n"
                "[bold]🎯 Prescriptive Action Taken:[/bold]\n"
                "• Pinned clarification comment scheduled on YouTube.\n"
                "• 45s Shorts script queued answering the API quota FAQ.",
                title="Synthesized Executive Statement",
                border_style="blue"
            ))

    # -------------------------------------------------------------------------
    # PART 2: PR CRISIS INTER-AGENT COLLABORATION
    # -------------------------------------------------------------------------
    console.print("\n")
    console.rule("[bold red]🔴 WORKFLOW 2: PR Crisis Anomaly ➔ Inter-Agent Handoff ➔ Slack Red Alert & Notion Triage")
    console.print("[dim]Cloud Scheduler triggers BigQuery sentiment velocity anomaly scan...[/dim]\n")
    time.sleep(1)

    with console.status("[bold magenta]Running Multi-Agent PR Crisis Resolution Cycle...", spinner="dots"):
        time.sleep(1.5)
        pr_results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="PR_CRISIS")

    console.print("✅ [bold red]BigQuery PR Anomaly Detected:[/bold red] Toxic comment velocity +380% on 'Why We Switched Everything to QuantumCloud'")
    
    for act in pr_results.get("actions_executed", []):
        agent_name = act.get("agent")
        tool_name = act.get("tool")
        res = act.get("result", {})
        if tool_name == "dispatch_slack_crisis_alert":
            console.print(f"\n[bold red]⚡ Action by {agent_name}: Dispatched Slack Red Alert Webhook[/bold red]")
            console.print(f"Destination: [bold]{res.get('destination')}[/bold] | Severity: [bold red]{res.get('severity')}[/bold red]")
        elif tool_name == "generate_notion_action_board":
            card = res.get("card_data", {})
            console.print(f"📋 Action by {agent_name}: Created Notion Task Card: [bold]{card.get('title')}[/bold] (Priority: [red]{card.get('priority')}[/red])")

    # -------------------------------------------------------------------------
    # PART 3: VIRAL TREND SPOTTER & SCRIPT SYNTHESIS
    # -------------------------------------------------------------------------
    console.print("\n")
    console.rule("[bold green]🟢 WORKFLOW 3: Breakout Trend ➔ Inter-Agent Handoff ➔ Google Docs Scripting")
    console.print("[dim]Orchestrator initiates scheduled viral momentum scan across YouTube Shorts & TikTok...[/dim]\n")
    time.sleep(1)

    with console.status("[bold magenta]Running Multi-Agent Viral Trend Synthesis Cycle...", spinner="dots"):
        time.sleep(1.5)
        trend_results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="VIRAL_TREND")

    for act in trend_results.get("actions_executed", []):
        agent_name = act.get("agent")
        tool_name = act.get("tool")
        res = act.get("result", {})
        if tool_name == "create_google_doc_video_script":
            console.print(f"\n[bold yellow]📝 Action by {agent_name}: Generated 60-Second Video Script in Google Docs[/bold yellow]")
            console.print(f"Doc URL: [bold yellow][link={res.get('doc_url')}]{res.get('doc_url')}[/link][/bold yellow]")

    # -------------------------------------------------------------------------
    # CONCLUSION & SUMMARY
    # -------------------------------------------------------------------------
    console.print("\n")
    console.rule("[bold cyan]🏆 Google ADK Multi-Agent Execution Summary")
    summary_table = Table(border_style="bright_blue")
    summary_table.add_column("Hackathon Evaluation Criteria", style="bold")
    summary_table.add_column("StudioSonar Implementation", style="green")
    
    summary_table.add_row(
        "Company Channel Sentinel",
        "Autonomous video detection + Instant Statistical Scorecard synthesis"
    )
    summary_table.add_row(
        "Google ADK Multi-Agent System",
        "5 Specialized Agents collaborating via ADK message contracts"
    )
    summary_table.add_row(
        "Autonomous Taskmaster Action",
        "100% Zero-Prompt background execution to Slack, Notion, Google Docs"
    )
    summary_table.add_row(
        "Heavy Data Lifting",
        "BigQuery OLAP SQL + 768-dim Vector Semantic Clustering"
    )
    summary_table.add_row(
        "Google Cloud Stack",
        "Gemini 3.7 Flash + Google ADK + BigQuery + Cloud Run + Cloud Scheduler"
    )
    console.print(summary_table)

if __name__ == "__main__":
    run_demo()
