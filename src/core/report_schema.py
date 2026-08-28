"""
Standardized schemas for autonomous intelligence reports.

Every asset type owns ONE canonical schema. Reports authored for assets of the
same type must follow the exact same layout: identical section order, titles and
metadata block. The authoring engine enforces these schemas so all reports stay
consistent across runs.
"""

import re
from typing import Dict, List, Optional

SCHEMA_VIDEO = {
    "type": "video",
    "title_prefix": "# 📹 Deep Intelligence Report",
    "sections": [
        "## 1. 📊 Executive Performance Overview",
        "## 2. 📈 Live Telemetry & Performance Metrics",
        "## 3. 💬 4D Sentiment Breakdown & Community Cohorts",
        "## 4. 🚀 Prescriptive Autonomous Growth Strategy",
        "## 5. ⚡ Autonomous Next Steps",
    ],
}

SCHEMA_CHANNEL = {
    "type": "channel",
    "title_prefix": "# 📺 Channel Surveillance Report",
    "sections": [
        "## 1. 📡 Channel Strategy & Audience Demographics",
        "## 2. 📈 Upload Velocity & Statistical Benchmark",
        "## 3. 🛡️ Brand Safety & Community Health Scorecard",
        "## 4. 🎯 Prescriptive Optimization Directives",
        "## 5. ⚡ Autonomous Next Steps",
    ],
}

SCHEMA_TIKTOK = {
    "type": "tiktok_sound",
    "title_prefix": "# 🎵 TikTok Sound UGC Velocity Report",
    "sections": [
        "## 1. 🎧 Sound Adoption & UGC Velocity Surge",
        "## 2. 💃 Dominant Creation Archetypes & Challenges",
        "## 3. 🚀 Short-Form Creator Amplification Playbook",
        "## 4. 📈 Live Telemetry & Performance Metrics",
        "## 5. ⚡ Autonomous Next Steps",
    ],
}

SCHEMA_BY_TYPE: Dict[str, dict] = {
    "video": SCHEMA_VIDEO,
    "channel": SCHEMA_CHANNEL,
    "tiktok_sound": SCHEMA_TIKTOK,
}

MIN_CONTENT_CHARS = 600


def footer(model_label: str = "Gemini Agent Platform") -> str:
    return f"\n---\n*Authored autonomously by StudioSonar Swarm ({model_label} Engine)*\n"


def _norm_heading(h: str) -> str:
    """Normalize a heading for fuzzy matching: keep letters/digits/spaces, lowercase."""
    h = re.sub(r'#+\s*', '', h)          # strip leading '# '
    h = re.sub(r'^\d+[\.\)]\s*', '', h)  # strip '1. ' numbering
    h = re.sub(r'[^\w\s]', '', h)         # drop emoji / punctuation
    return ' '.join(h.split()).lower()


def enforce_schema(
    schema: dict,
    metadata_block: str,
    generated: Optional[str],
    fallback_bodies: Dict[str, str],
) -> str:
    """
    Guarantees the final report follows the schema layout exactly:
      metadata_block + one body per required section (schema order) + footer.

    - Uses the model's own text for a section when present.
    - Falls back to `fallback_bodies[section]` when the model omitted the
      section or produced nothing usable.
    """
    sections = schema["sections"]
    norm_to_heading = {_norm_heading(s): s for s in sections}

    # Map generated content to each required section.
    section_bodies: Dict[str, str] = {}
    if generated:
        # Split the generated markdown on any heading line.
        parts = re.split(r'(?m)^(#{1,6}\s.*)$', generated)
        current = None
        for chunk in parts:
            if re.match(r'^#{1,6}\s', chunk.strip()):
                heading_key = _norm_heading(chunk)
                matched = norm_to_heading.get(heading_key)
                current = matched
            else:
                if current is not None and chunk.strip():
                    # keep first body found for a section
                    if current not in section_bodies:
                        section_bodies[current] = chunk.strip()

    out: List[str] = [metadata_block.strip(), ""]
    for heading in sections:
        body = section_bodies.get(heading) or fallback_bodies.get(heading, "").strip()
        if not body:
            body = "_No data available for this section._"
        out.append(heading)
        out.append("")
        out.append(body)
        out.append("")
    out.append(footer().strip())
    return "\n".join(out)


def schema_for(asset_type: str) -> dict:
    return SCHEMA_BY_TYPE.get(asset_type, SCHEMA_VIDEO)


def sections_prompt(schema: dict) -> str:
    """Returns a numbered bullet list of required sections for the prompt."""
    return "\n".join(f"  {i+1}. {s.lstrip('#').strip()}" for i, s in enumerate(schema["sections"]))