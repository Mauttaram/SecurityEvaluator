from pydantic import BaseModel
from typing import Literal

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)


class ApplicationScore(BaseModel):
    emotional_appeal: float
    argument_clarity: float
    argument_arrangement: float
    relevance_to_topic: float
    total_score: float

class ApplicationEval(BaseModel):
    application_score: ApplicationScore
    overall_risk_rating: Literal["low", "medium" , "high"]
    reason: str


def cyber_sentinel_agent_card(agent_name: str, card_url: str) -> AgentCard:
    skill = AgentSkill(
        id='Evaluate Security posture of an application',
        name='Examines Application threats postures',
        description='Kicks off the synthetic test for application to evalute how secure the application is?',
        tags=['sentinel', 'security'],
        examples=["""
{
  "application": {
    "endpoint": "https://pro-debater.example.com:443",
  },
  "config": {
    "topic": "Is my application secure",
  }
}
"""]
    )
    agent_card = AgentCard(
        name=agent_name,
        description='Run various synthetic tests and provide the rating on security posture of application and present detailed analysis report',
        url=card_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    return agent_card
