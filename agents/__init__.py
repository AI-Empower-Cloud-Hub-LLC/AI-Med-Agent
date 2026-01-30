"""
AI-Med-Agent: Enterprise-Level AI Agent Framework
A comprehensive framework for building intelligent medical AI agents with AWS integration.
"""

__version__ = "1.0.0"
__author__ = "AI-Empower-Cloud-Hub-LLC"

from agents.base.agent import BaseAgent, AgentConfig, AgentStatus
from agents.orchestration.orchestrator import AgentOrchestrator
from agents.medical.diagnosis_agent import DiagnosisAgent
from agents.medical.triage_agent import TriageAgent
from agents.medical.monitoring_agent import PatientMonitoringAgent

__all__ = [
    'BaseAgent',
    'AgentConfig',
    'AgentStatus',
    'AgentOrchestrator',
    'DiagnosisAgent',
    'TriageAgent',
    'PatientMonitoringAgent',
]
