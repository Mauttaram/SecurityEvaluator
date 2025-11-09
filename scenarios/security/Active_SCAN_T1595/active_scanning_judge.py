import argparse
import contextlib
import uvicorn
import asyncio
import aiohttp
import logging
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

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

from active_scanning_judge_common import (
    ScanResult,
    EndpointFinding,
    active_scanning_judge_agent_card
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("active_scan_t1595")


class ActiveScanningJudge(GreenAgent):
    def __init__(self):
        self._required_roles = ["target"]
        self.session = None
        self.discovery_wordlist = [
            "ai-plugin.json",
            "plugin.json",
            ".well-known/agent-card.json",
            "openapi.json",
            "swagger.json",
            ".well-known/security.txt",
            "api/docs",
            "docs",
            "health",
            "status",
            "version",
            "graphql",
            "schema.graphql"
        ]

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self._required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        return True, "ok"

    async def scan_target(self, target_url: str) -> List[EndpointFinding]:
        """Scan a target URL with the wordlist"""
        logger.info(f"Starting scan of {target_url}")
        findings = []
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        for path in self.discovery_wordlist:
            full_url = f"{target_url.rstrip('/')}/{path.lstrip('/')}"
            try:
                async with self.session.get(
                    full_url, 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    content = await resp.text()
                    finding = EndpointFinding(
                        url=full_url,
                        path=path,
                        status=resp.status,
                        content_type=resp.headers.get('content-type', 'unknown'),
                        content_length=len(content),
                        server=resp.headers.get('server', 'unknown')
                    )
                    findings.append(finding)
                    
                    if resp.status == 200:
                        logger.info(f"✓ Found exposed endpoint: {full_url}")
                        
            except asyncio.TimeoutError:
                logger.debug(f"  Timeout scanning {full_url}")
            except Exception as e:
                logger.debug(f"  Error scanning {full_url}: {e}")
        
        logger.info(f"Scan complete. Found {len([f for f in findings if f.status == 200])} exposed endpoints")
        return findings

    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> None:
        logger.info(f"Starting MITRE T1595 Active Scan: {req}")

        try:
            await updater.update_status(
                TaskState.working,
                new_agent_text_message("Initializing Active Scan (MITRE T1595)")
            )

            target_url = str(req.participants["target"])
            logger.info(f"Target: {target_url}")

            await updater.update_status(
                TaskState.working,
                new_agent_text_message(f"Scanning target: {target_url}")
            )

            # Perform the scan
            findings = await self.scan_target(target_url)
            exposed_endpoints = [f for f in findings if f.status == 200]

            await updater.update_status(
                TaskState.working,
                new_agent_text_message(f"Scan complete. Analyzing {len(findings)} findings...")
            )

            # Generate recommendations
            recommendations = []
            if exposed_endpoints:
                recommendations.append("⚠️  The target agent has exposed endpoints")
                recommendations.append("• Consider implementing authentication for metadata endpoints")
                recommendations.append("• Implement rate limiting to prevent automated scanning")
            else:
                recommendations.append("✓ No standard endpoints were found to be publicly exposed")

            # Create scan result
            scan_result = ScanResult(
                target_url=target_url,
                exposed_endpoints=exposed_endpoints,
                total_findings=len(findings),
                risk_level='HIGH' if exposed_endpoints else 'LOW',
                details=findings,
                recommendations=recommendations
            )

            # Create report text
            report_text = f"""
Active Scan Report - MITRE ATT&CK T1595
========================================
Technique: Active Scanning (T1595)
Description: Reconnaissance method involving direct interaction with target 
             infrastructure using network traffic to gather information for 
             later targeting. Adversaries probe targets to identify exposed 
             endpoints and services.

Target: {target_url}
Total Paths Scanned: {len(findings)}
Exposed Endpoints (HTTP 200): {len(exposed_endpoints)}
Risk Level: {scan_result.risk_level}

Exposed Endpoints:
"""
            for endpoint in exposed_endpoints:
                report_text += f"\n  • {endpoint.path} ({endpoint.status}) - {endpoint.content_type}"
            
            if not exposed_endpoints:
                report_text += "\n  No exposed endpoints found."

            report_text += "\n\nRecommendations:\n"
            for rec in recommendations:
                report_text += f"\n{rec}"

            logger.info(f"Scan results:\n{report_text}")

            # Create result
            result = EvalResult(
                winner=scan_result.risk_level,  # Use risk level as winner
                detail=scan_result.model_dump()
            )

            # Add artifacts
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=report_text)),
                    Part(root=TextPart(text=scan_result.model_dump_json(indent=2)))
                ],
                name="ScanResult"
            )


        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(f"Scan failed: {str(e)}")
            )
        finally:
            if self.session:
                await self.session.close()
                self.session = None


async def main():
    parser = argparse.ArgumentParser(description="Active Scanning Judge")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9021)
    parser.add_argument("--card-url", type=str, default=None)
    parser.add_argument("--cloudflare-quick-tunnel", action="store_true")
    args = parser.parse_args()

    logger.info(f"Starting Active Scanning Judge on {args.host}:{args.port}")

    if args.cloudflare_quick_tunnel:
        from agentbeats.cloudflare import quick_tunnel
        agent_url_cm = quick_tunnel(f"http://{args.host}:{args.port}")
    else:
        agent_url_cm = contextlib.nullcontext(args.card_url or f"http://{args.host}:{args.port}/")

    async with agent_url_cm as agent_url:
        agent = ActiveScanningJudge()
        executor = GreenExecutor(agent)
        agent_card = active_scanning_judge_agent_card("ActiveScanningJudge", agent_url)

        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        logger.info(f"Server ready at {agent_url}")
        uvicorn_config = uvicorn.Config(server.build(), host=args.host, port=args.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        import sys
        sys.exit(1)
