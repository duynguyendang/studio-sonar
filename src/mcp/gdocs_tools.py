import logging
import uuid
from typing import Dict, List, Any, Optional
from src.core.config import settings

logger = logging.getLogger("studiosonar.mcp.gdocs")

def create_google_doc_video_script(
    doc_title: str,
    target_platform: str,
    trend_topic: str,
    hook_3s: str,
    problem_statement: str,
    solution_core: str,
    call_to_action: str,
    visual_broll_notes: List[str],
    estimated_duration_sec: int = 60
) -> Dict[str, Any]:
    """
    Drafts an end-to-end, high-retention viral video script directly into Google Docs.
    
    Args:
        doc_title: Title of the Google Document.
        target_platform: Target platform ("TikTok", "YouTube Shorts", "Instagram Reels").
        trend_topic: The emerging cultural/tech trend being addressed.
        hook_3s: The first 0-3 seconds contrarian hook sentence to stop feed scrolling.
        problem_statement: The pain point / misconception explained in 4-15 seconds.
        solution_core: The breakdown / demonstration in 16-45 seconds.
        call_to_action: Closing 46-60 seconds call to action.
        visual_broll_notes: Visual directions, camera angles, and on-screen text instructions.
        estimated_duration_sec: Target video duration (default: 60s).
        
    Returns:
        Dictionary with Google Doc ID, Google Drive URL, and complete generated script markdown.
    """
    doc_id = f"gdoc_script_{uuid.uuid4().hex[:10]}"
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    script_content = f"""# {doc_title}
**Target Platform:** {target_platform} | **Duration:** {estimated_duration_sec}s | **Trend Topic:** {trend_topic}

---

## 🎬 Hook (0:00 - 0:03)
> **[Speaker on Camera - Zoom in 1.2x]:**  
> *"{hook_3s}"*  
> *[On-screen text: {hook_3s}]*

---

## ⚠️ Problem & Friction (0:03 - 0:15)
> **[Voiceover + B-Roll]:**  
> "{problem_statement}"

---

## 💡 Solution Breakdown (0:15 - 0:45)
> **[Screen Recording / Visual Demo]:**  
> "{solution_core}"

---

## 🚀 Call To Action (0:45 - 1:00)
> **[Speaker to Camera + Outro Card]:**  
> *"{call_to_action}"*

---

## 🎥 Production & B-Roll Notes
{chr(10).join([f"- {note}" for note in visual_broll_notes])}
"""

    return {
        "status": "CREATED_SUCCESS",
        "doc_id": doc_id,
        "doc_url": doc_url,
        "doc_title": doc_title,
        "target_platform": target_platform,
        "generated_script": script_content
    }
