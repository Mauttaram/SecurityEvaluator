

import argparse
import contextlib
import uvicorn
import asyncio
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal
import aiohttp

import time

load_dotenv()

from google import genai
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    TaskState,
    Part,
    TextPart,
)
from a2a.utils import (
    new_agent_text_message
)

from agentbeats.green_executor import GreenAgent, GreenExecutor
from agentbeats.models import EvalRequest, EvalResult
from agentbeats.tool_provider import ToolProvider

from cyber_sentinel_common import cyber_sentinel_agent_card, ApplicationEval 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cyber_sentinel")


class CyberSentinel(GreenAgent):
    def __init__(self):
        self._required_config_keys = ["topic"]
        self._client = genai.Client()
        self._tool_provider = ToolProvider()

  
    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self._required_roles) - set(request.application.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        missing_config_keys = set(self._required_config_keys) - set(request.config.keys())
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"
        return True, "ok"


    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> None:
        logger.info(f"Starting synthetic tests: {req}")

        try:

            ##  TODO check how does the application as particpant is set in the models of Eval request
            application = await self.simulate_ddos_attack(req.participants,
                                                req.config["topic"],
                                                updater)

            # sql_injection = await self.simulate_sql_injection(req.participants,
            #                                     req.config["topic"],
            #                                     updater)


            security_report = ""
            for i, (sec, insec) in enumerate(zip(application["secure_application"], application["insecure_application"]), start=1):
                security_report += f"Security Application Report {i}: {sec}\n"
                security_report += f"InSecure Application Report {i}: {insec}\n"

            await updater.update_status(TaskState.working, new_agent_text_message(f"Security Auditing finished. Starting evaluation."))
            logger.info("Security Auditing finished. Starting evaluation")
            application_eval: ApplicationEval = await self.cyber_sentinel_analyze(req.config["topic"], security_report)
            logger.info(f"Security Evaluation:\n{application_eval.model_dump_json()}")

            result = EvalResult(winner=application_eval.winner, detail=application_eval.model_dump())
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=application_eval.reason)),
                    Part(root=TextPart(text=result.model_dump_json())),
                ],
                name="Result",
            )
        finally:
            self._tool_provider.reset()

   




    async def simulate_ddos_attack(participants: dict[str, str], topic: str, updater: TaskUpdater,
                                concurrent_requests: int = 100, duration: int = 60):
        """
        Asynchronously simulate a DDoS attack on application URL derived from participants.

        :param participants: Dictionary of participant names to URLs
        :param topic: Topic string (for logging or status updates)
        :param updater: TaskUpdater instance for status updates
        :param concurrent_requests: Number of concurrent requests (default 100)
        :param duration: Duration of the attack in seconds (default 60)
        """
        application_name = None
        application_url = None

        # Derive application name and url from participants dict (assuming key 'application')
        if 'application' in participants:
            application_name = 'application'
            application_url = participants['application']
        else:
            # Fallback or pick first entry as application
            application_name, application_url = next(iter(participants.items()))

        stop_time = time.time() + duration

        async def attack(session: aiohttp.ClientSession):
            while time.time() < stop_time:
                try:
                    async with session.get(application_url, timeout=5) as response:
                        await response.text()
                except Exception:
                    # Ignore exceptions to keep attacking
                    pass

        async with aiohttp.ClientSession() as session:

            # Periodic status updater coroutine
            async def status_updater():
                while time.time() < stop_time:
                    elapsed = int(time.time() + duration - stop_time)
                    status_msg = (f"[{topic}] DDoS Attack in progress on {application_name} "
                                f"({application_url}), time left: {int(stop_time - time.time())} seconds")
                    await updater.update_status(status_msg)
                    await asyncio.sleep(5)  # Update every 5 seconds

            attack_tasks = [asyncio.create_task(attack(session)) for _ in range(concurrent_requests)]
            updater_task = asyncio.create_task(status_updater())

            # Wait for attack duration to complete
            await asyncio.gather(*attack_tasks)
            await updater.update_status(f"[{topic}] DDoS attack simulation finished on {application_name}.")

            # Cancel updater task on completion
            updater_task.cancel()
            try:
                await updater_task
            except asyncio.CancelledError:
                pass

    async def cyber_sentinel_analyze(self, topic: str, security_report: str) -> ApplicationEval:
        # prompt adapted from InspireScore: https://github.com/fywang12/InspireDebate/blob/main/inspirescore.py

        system_prompt = """
            You are an experienced Application Security Evaluator tasked with assessing the security posture of an Application Under Test (AUT) following synthetic testing. For each security dimension, you will provide a score from 0 to 1 (with 0 being the lowest and 1 being the highest), reflecting the AUT’s performance. Additionally, provide a brief analysis for each dimension.

            Scoring Criteria:

            1. **Vulnerability Severity and Impact**  
            - How many and how severe are the vulnerabilities identified in the AUT? Are there critical or exploitable issues?  
            - **0**: Numerous critical vulnerabilities with high exploitability.  
            - **1**: No critical vulnerabilities; the application is secure.

            2. **Authentication and Authorization Robustness**  
            - How well does the AUT enforce user authentication and authorization? Are there weaknesses in access control?  
            - **0**: Poor or missing authentication controls, easy to bypass.  
            - **1**: Strong, multi-layered authentication and strict authorization.

            3. **Resilience Under Synthetic Testing**  
            - How well does the AUT perform under simulated attacks and synthetic workflows? Are there failures or security breakdowns during testing?  
            - **0**: Numerous failures, crashes, or security bypasses during synthetic tests.  
            - **1**: Smooth, secure operation with no test anomalies.

            4. **Data Protection and Configuration Security**  
            - Does the AUT properly protect sensitive data and adhere to security best practices in configuration (e.g., encryption, secure settings)?  
            - **0**: Sensitive data is exposed, and configuration weaknesses exist.  
            - **1**: Data properly protected and secure configuration verified.

            Please output the result in the following format:

            1. **AUT Security Scores**:  
            - Vulnerability Severity and Impact: [score]  
            - Authentication and Authorization: [score]  
            - Resilience Under Synthetic Testing: [score]  
            - Data Protection and Configuration: [score]  
            - **Total Security Score**: [total score]

            2. **Analysis**:  
            - Provide a detailed explanation of the scoring for each dimension.  
            - Highlight critical findings and their implications.  
            - Recommend prioritized remediation actions based on score impact.

            3. **Security Posture Summary**:  
            - Summarize the overall security health of the AUT and risk level.  
            - Suggest next steps for ongoing security validation and improvement.

            This prompt guides a precise, structured security evaluation with quantitative scoring and qualitative analysis for comprehensive application security assessment.
        """

        user_prompt = f"""
        Evaluate the application on topic: '{topic}'
        Application Details are as follows
        {security_report}
        Provide a JSON formatted response with scores and analysis for each criterion for the application under test.
        """

        response = self._client.models.generate_content(
            model="gemini-2.5-flash",
            config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=ApplicationEval,
                ),
            contents=user_prompt,
        )
        return response.parsed



async def main():
    parser = argparse.ArgumentParser(description="Run the Security Evaluator (Green Agent)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9019, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    parser.add_argument("--cloudflare-quick-tunnel", action="store_true", help="Use a Cloudflare quick tunnel. Requires cloudflared. This will override --card-url")
    args = parser.parse_args()

    if args.cloudflare_quick_tunnel:
        from agentbeats.cloudflare import quick_tunnel
        agent_url_cm = quick_tunnel(f"http://{args.host}:{args.port}")
    else:
        agent_url_cm = contextlib.nullcontext(args.card_url or f"http://{args.host}:{args.port}/")

    async with agent_url_cm as agent_url:
        agent = CyberSentinel()
        executor = GreenExecutor(agent)
        agent_card = cyber_sentinel_agent_card("CyberSentinel", agent_url)

        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        uvicorn_config = uvicorn.Config(server.build(), host=args.host, port=args.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()

if __name__ == '__main__':
    asyncio.run(main())
