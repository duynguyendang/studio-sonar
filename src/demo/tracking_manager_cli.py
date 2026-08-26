#!/usr/bin/env python3
"""
StudioSonar Tracking Manager - Interactive Dashboard & Management CLI
Usage:
  - View Dashboard: python3 -m src.demo.tracking_manager_cli
  - Track New Video: python3 -m src.demo.tracking_manager_cli --add-video <URL>
  - Track New Channel: python3 -m src.demo.tracking_manager_cli --add-channel <HANDLE>
"""

import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.services.tracking_service import tracking_service

console = Console()

def display_dashboard():
    console.print(Panel(
        "[bold cyan]🎙️ StudioSonar Real-Time Tracking Engine: Asset Dashboard[/bold cyan]\n"
        "24/7 Background Telemetry Monitoring powered by [bold green]Google ADK & BigQuery[/bold green]",
        border_style="bright_blue"
    ))

    channels = tracking_service.list_channels()
    videos = tracking_service.list_videos()

    # 1. Channels Table
    ch_table = Table(title="📺 Tracked Channels (Continuous Monitoring)", border_style="cyan")
    ch_table.add_column("Channel ID", style="bold yellow")
    ch_table.add_column("Handle / Name", style="bold white")
    ch_table.add_column("Category", style="cyan")
    ch_table.add_column("Frequency", style="green")
    ch_table.add_column("Status", style="bold green")
    ch_table.add_column("Alert Destination", style="magenta")

    for c in channels:
        ch_table.add_row(
            c.channel_id,
            f"{c.title} ({c.handle})",
            c.category,
            f"Every {c.check_frequency_minutes}m",
            f"● {c.tracking_status}",
            c.notification_channel
        )
    console.print(ch_table)

    # 2. Videos Table
    v_table = Table(title="\n📹 Tracked Videos (Real-Time Telemetry & Reports)", border_style="yellow")
    v_table.add_column("Video ID", style="bold yellow")
    v_table.add_column("Video Title", style="bold white")
    v_table.add_column("Published", style="dim")
    v_table.add_column("Views", style="bold green")
    v_table.add_column("Sentiment", style="cyan")
    v_table.add_column("Monitoring Tier", style="magenta")
    v_table.add_column("Report Path", style="dim")

    for v in videos:
        latest = v.snapshots[-1] if v.snapshots else None
        views_str = f"{latest.views:,}" if latest else "N/A"
        sentiment_str = f"{latest.sentiment_positive_pct}% Pos" if latest else "N/A"
        
        v_table.add_row(
            v.video_id,
            v.title[:45] + ("..." if len(v.title) > 45 else ""),
            v.published_at[:10],
            views_str,
            sentiment_str,
            v.monitoring_tier,
            v.generated_report_path or "Generating..."
        )
    console.print(v_table)

    # Summary
    console.print(f"\n[bold green]Total Channels Under Surveillance:[/bold green] {len(channels)}  |  [bold green]Total Videos Active:[/bold green] {len(videos)}")

def main():
    parser = argparse.ArgumentParser(description="StudioSonar Tracking CLI")
    parser.add_argument("--add-video", type=str, help="YouTube video URL or ID to track")
    parser.add_argument("--add-channel", type=str, help="Channel handle (e.g. @atekco) to track")
    parser.add_argument("--category", type=str, default="General", help="Category tag for channel")
    args = parser.parse_args()

    if args.add_video:
        console.print(f"[bold magenta]Adding Video to StudioSonar Tracking Engine:[/bold magenta] {args.add_video}")
        video = tracking_service.add_video(args.add_video)
        console.print(f"✅ [bold green]Successfully registered video:[/bold green] {video.title} (ID: {video.video_id})")
        console.print(f"📄 Report generated at: [bold cyan]{video.generated_report_path}[/bold cyan]\n")
        display_dashboard()
    elif args.add_channel:
        console.print(f"[bold magenta]Adding Channel to StudioSonar Tracking Engine:[/bold magenta] {args.add_channel}")
        channel = tracking_service.add_channel(args.add_channel, category=args.category)
        console.print(f"✅ [bold green]Successfully registered channel:[/bold green] {channel.handle} (ID: {channel.channel_id})\n")
        display_dashboard()
    else:
        display_dashboard()

if __name__ == "__main__":
    main()
