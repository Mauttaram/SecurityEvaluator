# Active Scan Report - MITRE ATT&CK T1595

## Overview
This report documents the execution of an **Active Scanning** test using the MITRE ATT&CK framework technique T1595. The test demonstrates how adversaries perform reconnaissance by directly probing target infrastructure using network traffic to gather information for later targeting.

## MITRE ATT&CK Technique Details

**Technique ID:** T1595  
**Technique Name:** Active Scanning  
**Tactic:** Reconnaissance  

**Description:**  
Active Scanning is a reconnaissance method involving direct interaction with target infrastructure using network traffic. Adversaries may probe targets to identify exposed endpoints, services, and potential vulnerabilities. This technique emulates real-world adversary behavior where attackers systematically scan target networks to build a profile of the infrastructure before launching attacks.

## Test Configuration

### Green Agent (Scanner)
- **Role:** Active Scan Judge
- **Endpoint:** http://127.0.0.1:9021
- **Technique:** MITRE T1595 - Active Scanning
- **Method:** Direct HTTP probing with endpoint discovery wordlist

### Purple Agent (Target)
- **Role:** Target Agent (Debater)
- **Endpoint:** http://127.0.0.1:9019
- **Type:** A2A-enabled AI Agent

### Scan Parameters
- **Total Paths Scanned:** 13
- **Scan Method:** HTTP GET requests
- **Wordlist:** Standard endpoint discovery paths including:
  - ai-plugin.json
  - plugin.json
  - .well-known/agent-card.json
  - openapi.json, swagger.json
  - API documentation endpoints
  - Health/status endpoints
  - GraphQL endpoints

## Scan Results

### Summary
- **Target:** http://127.0.0.1:9019/
- **Total Paths Scanned:** 13
- **Exposed Endpoints (HTTP 200):** 1
- **Risk Level:** **HIGH**

### Exposed Endpoints

| Path | Status | Content Type | Finding |
|------|--------|--------------|---------|
| `.well-known/agent-card.json` | 200 | application/json | ✓ Publicly Accessible |

### Risk Assessment

**Risk Level: HIGH**

The target agent has exposed endpoints that can be discovered through active scanning. The `.well-known/agent-card.json` endpoint is publicly accessible without authentication, which could allow adversaries to:

1. **Enumerate agent capabilities** - Understand what the agent can do
2. **Identify attack surface** - Map available interfaces and skills
3. **Plan targeted attacks** - Use gathered intelligence for precision targeting
4. **Reconnaissance** - Build a profile of the agent's functionality

## Security Recommendations

### Immediate Actions
⚠️ **The target agent has exposed endpoints**

1. **Implement Authentication/Authorization**
   - Consider requiring authentication for metadata endpoints
   - Implement API key or OAuth-based access control
   - Restrict access to agent card information to authorized parties only

2. **Rate Limiting**
   - Implement rate limiting to prevent automated scanning
   - Set thresholds for suspicious scanning behavior
   - Add CAPTCHA or challenge-response for repeated requests

3. **Monitoring and Alerting**
   - Monitor for suspicious endpoint access patterns
   - Alert on automated scanning attempts
   - Log all agent card access requests for audit trails

4. **Network Security**
   - Consider placing agent behind reverse proxy with WAF
   - Implement IP allowlisting for known clients
   - Use network segmentation to limit exposure

### Long-term Security Posture
- **Defense in Depth:** Layer multiple security controls
- **Zero Trust Architecture:** Verify every access request
- **Continuous Monitoring:** Implement real-time threat detection
- **Security Awareness:** Educate about active scanning threats

## A2A Protocol Implementation

This test successfully demonstrates:

✅ **Proper A2A Communication**
- Green Agent (Scanner) initiates A2A task request
- Purple Agent (Target) responds to probing attempts
- AgentBeats platform orchestrates agent lifecycle
- Scenario runner manages both agents via `scenario.toml`

✅ **MITRE ATT&CK Framework Integration**
- Technique T1595 properly identified and documented
- Real-world adversary behavior emulated
- Security findings mapped to MITRE framework
- Defensive recommendations aligned with best practices

## Conclusion

The Active Scan test successfully demonstrated MITRE ATT&CK technique T1595 in an agent-to-agent context. The scan identified 1 exposed endpoint on the target agent, highlighting the importance of implementing proper security controls even for agent metadata endpoints.

### Key Takeaways
1. Even "metadata" endpoints can leak valuable intelligence to adversaries
2. Active scanning is a critical reconnaissance technique that must be defended against
3. A2A protocol enables realistic security testing between agents
4. MITRE ATT&CK framework provides valuable context for security assessments

---

**Test Completed:** November 9, 2025  
**Framework:** AgentBeats + A2A Protocol  
**Technique:** MITRE ATT&CK T1595 - Active Scanning  
**Status:** ✅ Completed Successfully
