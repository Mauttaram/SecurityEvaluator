from pydantic import BaseModel
from typing import List, Dict

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)


class EndpointFinding(BaseModel):
    url: str
    path: str
    status: int
    content_type: str
    content_length: int
    server: str


class ScanResult(BaseModel):
    target_url: str
    exposed_endpoints: List[EndpointFinding]
    total_findings: int
    risk_level: str
    details: List[EndpointFinding]
    recommendations: List[str]


def active_scanning_judge_agent_card(agent_name: str, card_url: str) -> AgentCard:
    skill = AgentSkill(
        id='active_security_scanning',
        name='MITRE T1595: Active Scan',
        description='Active Scanning reconnaissance technique that involves direct probing of target infrastructure using network traffic to gather information for later targeting.',
        tags=['security', 'scanning', 'reconnaissance', 'MITRE-T1595'],
        examples=["""
{
  "participants": {
    "target": "http://target-agent.example.com:9019"
  },
  "config": {
    "scan_type": "endpoint_discovery",
    "wordlist": ["ai-plugin.json", "openapi.json", "swagger.json"]
  }
}
"""]
    )
    agent_card = AgentCard(
        name=agent_name,
        description='MITRE ATT&CK T1595: Active Scan - Reconnaissance technique that involves direct probing of target infrastructure to identify exposed endpoints and potential security vulnerabilities.',
        url=card_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )
    return agent_card
