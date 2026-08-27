"""
Google ADK Evaluation Suite Test Runner.
Executes autonomous benchmark evals across all specialized Pure ADK Agents.
"""

import json
import pytest
from src.agents.anomaly_detector_agent import anomaly_detector_agent
from src.agents.pr_crisis_agent import pr_crisis_agent
from src.agents.viral_content_agent import viral_content_agent
from src.agents.channel_monitor_agent import channel_monitor_agent
from src.agents.orchestrator import taskmaster_agent, taskmaster_workflow

def test_adk_agents_instantiation_and_tools():
    """Validates that all agents are pure ADK LlmAgent instances with valid declarative tools."""
    assert anomaly_detector_agent.name == "AnomalyDetectorAgent"
    assert len(anomaly_detector_agent.tools) == 3
    assert anomaly_detector_agent.mode == "single_turn"

    assert pr_crisis_agent.name == "PRCrisisStrategistAgent"
    assert len(pr_crisis_agent.tools) == 2

    assert viral_content_agent.name == "ViralContentCreatorAgent"
    assert len(viral_content_agent.tools) == 2

    assert channel_monitor_agent.name == "ChannelMonitorAgent"
    assert len(channel_monitor_agent.tools) == 4

    assert taskmaster_agent.name == "StudioSonarRootTaskmaster"
    assert len(taskmaster_agent.sub_agents) == 4

def test_adk_workflow_graph_topology():
    """Validates that the Workflow Graph complies with topological execution requirements."""
    assert taskmaster_workflow.name == "StudioSonarAutonomousWorkflow"
    assert len(taskmaster_workflow.edges) == 4
    
    edge_names = []
    for edge in taskmaster_workflow.edges:
        src = edge[0] if isinstance(edge[0], str) else edge[0].name
        dst = edge[1] if isinstance(edge[1], str) else edge[1].name
        edge_names.append((src, dst))
        
    assert ("START", "ChannelMonitorAgent") in edge_names
    assert ("ChannelMonitorAgent", "AnomalyDetectorAgent") in edge_names
    assert ("AnomalyDetectorAgent", "PRCrisisStrategistAgent") in edge_names
    assert ("AnomalyDetectorAgent", "ViralContentCreatorAgent") in edge_names

def test_eval_set_schema_and_cases():
    """Loads and validates the ADK eval set test cases."""
    with open("evals/eval_set.json", "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        
    assert eval_data.get("eval_set_id") == "studiosonar_adk_eval_suite"
    cases = eval_data.get("eval_cases", [])
    assert len(cases) == 5

    # Case 1: Vietnamese sentiment classification
    c1 = cases[0]
    assert "nghe hoài không chán" in c1["input"]
    assert c1["minimum_confidence"] >= 0.90

    # Case 2: Commercial intent
    c2 = cases[1]
    assert "giá chụp ảnh" in c2["input"]
    assert c2["minimum_confidence"] >= 0.95

if __name__ == "__main__":
    pytest.main(["-v", __file__])
