#!/usr/bin/env python3
"""
A2A Active Scanning Test - Uses agentbeats platform for proper A2A communication
This follows the debate_judge pattern for green-to-purple agent communication
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for agentbeats imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentbeats.client import send_message
from agentbeats.models import EvalRequest

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_a2a_active_scanning_test():
    """
    Run active scanning test using proper A2A protocol
    
    This test:
    1. Assumes both agents are running (started by scenario runner or manually)
    2. Sends an A2A task request to the judge
    3. Judge scans the target (purple agent)
    4. Receives and displays the results
    """
    
    logger.info("="*80)
    logger.info("A2A ACTIVE SCANNING TEST")
    logger.info("="*80)
    
    # Configure the test
    judge_url = "http://127.0.0.1:9021"  # Green agent (scanner/judge)
    target_url = "http://127.0.0.1:9019"  # Purple agent (target to scan)
    
    logger.info(f"\nGreen Agent (Scanner): {judge_url}")
    logger.info(f"Purple Agent (Target):  {target_url}")
    
    # Create the evaluation request following the A2A protocol
    # This matches the structure expected by ActiveScanningJudge.run_eval()
    eval_request = {
        "participants": {
            "target": target_url
        },
        "config": {
            "scan_type": "endpoint_discovery",
            "task": "active_security_scan"
        }
    }
    
    logger.info(f"\nSending A2A task request to judge...")
    logger.debug(f"Request: {json.dumps(eval_request, indent=2)}")
    
    try:
        # Send the message to the judge using A2A protocol
        # The judge will:
        # 1. Validate the request
        # 2. Scan the target URL
        # 3. Return results via A2A task artifacts
        
        logger.info("Initiating A2A communication...")
        
        # Create the message content
        message_content = json.dumps(eval_request)
        
        # Send via A2A protocol
        result = await send_message(
            message=message_content,
            base_url=judge_url,
            streaming=False
        )
        
        logger.info("\n" + "="*80)
        logger.info("A2A SCAN RESULTS RECEIVED")
        logger.info("="*80)
        
        # Display the context
        if result.get("context_id"):
            logger.info(f"\nContext ID: {result['context_id']}")
        
        if result.get("status"):
            logger.info(f"Task Status: {result['status']}")
        
        # Display the response
        logger.info("\n" + "-"*80)
        logger.info("RESPONSE:")
        logger.info("-"*80)
        print(result.get("response", "No response received"))
        
        # Try to parse and display structured data if available
        try:
            response_text = result.get("response", "")
            if "{" in response_text:
                # Extract JSON if present
                json_start = response_text.find("{")
                json_part = response_text[json_start:]
                # Try to find the complete JSON
                for i in range(len(json_part), 0, -1):
                    try:
                        data = json.loads(json_part[:i])
                        logger.info("\n" + "="*80)
                        logger.info("STRUCTURED SCAN DATA:")
                        logger.info("="*80)
                        print(json.dumps(data, indent=2))
                        break
                    except:
                        continue
        except Exception as e:
            logger.debug(f"Could not extract structured data: {e}")
        
        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETE")
        logger.info("="*80)
        
        # Save results
        report_file = f"/tmp/a2a_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write("A2A Active Scanning Test Results\n")
            f.write("="*80 + "\n\n")
            f.write(f"Judge URL: {judge_url}\n")
            f.write(f"Target URL: {target_url}\n")
            f.write(f"Context ID: {result.get('context_id', 'N/A')}\n")
            f.write(f"Status: {result.get('status', 'N/A')}\n\n")
            f.write("Response:\n")
            f.write("-"*80 + "\n")
            f.write(result.get("response", "No response"))
            f.write("\n" + "="*80 + "\n")
        
        logger.info(f"\n📄 Report saved to: {report_file}")
        
        return result
        
    except ConnectionError as e:
        logger.error(f"\n❌ Connection Error: Could not connect to judge at {judge_url}")
        logger.error(f"   Make sure both the judge and target agents are running.")
        logger.error(f"   Error: {e}")
        return None
        
    except Exception as e:
        logger.error(f"\n❌ Error during A2A communication: {e}", exc_info=True)
        return None


async def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    A2A ACTIVE SCANNING TEST                                  ║
║                                                                              ║
║  This test uses the AgentBeats platform with proper A2A protocol            ║
║  to perform security scanning from a Green Agent to a Purple Agent.         ║
║                                                                              ║
║  Prerequisites:                                                              ║
║  1. Start the target agent (Purple):                                         ║
║     python3 scenarios/debate/debater.py --host 127.0.0.1 --port 9019        ║
║                                                                              ║
║  2. Start the scanning judge (Green):                                        ║
║     python3 scenarios/security/active_scanning_judge.py \\                   ║
║         --host 127.0.0.1 --port 9021                                         ║
║                                                                              ║
║  OR use the scenario runner:                                                 ║
║     python3 -m agentbeats.run_scenario scenarios/security/scenario.toml     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        result = await run_a2a_active_scanning_test()
        
        if result:
            logger.info("\n✅ A2A test completed successfully")
            sys.exit(0)
        else:
            logger.error("\n❌ A2A test failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
