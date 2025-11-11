"""
Green Agents for Security Evaluation.

This module contains Green Agents (evaluators) that test Purple Agents (detectors)
on their ability to detect various cybersecurity threats. All Green Agents expose
A2A (Agent-to-Agent) protocol endpoints for AgentBeats integration.
"""

from .cybersecurity_evaluator import CyberSecurityEvaluator
from .agent_card import cybersecurity_agent_card

__all__ = [
    'CyberSecurityEvaluator',
    'cybersecurity_agent_card',
]
