# SecurityEvaluator: Comprehensive Framework & Workflow Guide

**Version:** 1.0.0  
**Date:** January 2026  
**Authors:** Subramanian S

---

## Executive Summary

SecurityEvaluator is a next-generation, agentic framework designed to automate the security assessment of AI agents and traditional software systems. Unlike static application security testing (SAST) tools that rely on pattern matching, SecurityEvaluator employs a dynamic **Meta-Orchestrator** to manage coalitions of specialized AI agents. These agents collaboratively probe, attack, and validate the defenses of a "Purple Agent" (System Under Test).

By leveraging **Bayesian optimization (Thompson Sampling)** for test allocation and a **Dual Evaluation Framework** that minimizes false positives, SecurityEvaluator provides a rigorous, adaptive, and standards-compliant (MITRE ATT&CK/ATLAS) security assessment.

---

## 1. Introduction

As AI agents become more autonomous and integrated into critical infrastructure, the attack surface expands beyond traditional vulnerabilities (like SQL Injection) to semantic threats (like Prompt Injection and Goal Hijacking). Traditional security tools often fail to detect these nuanced, context-dependent vulnerabilities.

SecurityEvaluator addresses this gap by simulating a sophisticated, adaptive adversary. It does not just run a checklist of exploits; it explores the target's boundaries, evolves attack payloads based on feedback, and validates findings using multi-perspective consensus.

### Core Objectives
1.  **Adaptive Adversarial Simulation**: Move beyond static signatures to behavior-based attacks.
2.  **Dual-Perspective Reporting**: Clearly distinguish between the *evaluator's performance* (Precision/Recall) and the *target's security posture* (CVSS/Risk).
3.  **Standardization**: Full alignment with MITRE ATT&CK and ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems) frameworks.

---

## 2. System Architecture & Core Components

SecurityEvaluator operates as a "Green Agent" (the evaluator) interacting with a "Purple Agent" (the defender/target). The architecture is organized into five distinct layers, orchestrated by a central unified ecosystem.

### Core Components
*   **UnifiedEcosystem**: The main entry point that initializes the environment, agents, and scenario.
*   **MetaOrchestrator**: The central brain that coordinates the evaluation lifecycle, manages phases, and forms coalitions.
*   **ThompsonSamplingAllocator**: A Bayesian optimization component used to intelligently allocate tests to the most promising attack vectors.
*   **Knowledge Base**: A shared repository where agents store and retrieve information about the target, attack attempts, and results.

### Layer 1: User Interface
Provides the entry points for the system via CLI tools, Python APIs, and a FastAPI-based REST server. It handles the initial configuration of the evaluation run (scenario selection, budget, max rounds).

### Layer 2: Orchestration
The heart of the system is the **Meta-Orchestrator**. It is responsible for:
*   **Task Routing**: Assigning objectives to the appropriate agent coalition.
*   **Phase Control**: Managing the transition between Exploration, Exploitation, and Validation phases.
*   **Resource Management**: Optimizing token usage and financial cost via the Cost Optimizer.
*   **Dynamic Coalition Formation**: Instantiating specialized agents based on required capabilities (e.g., `Capability.PROBE`, `Capability.MUTATE`).

### Layer 3: Agent Coalitions
Specialized agents are grouped into functional coalitions:
*   **🎯 Attack Coalition**: Generates and evolves threats.
    *   *BoundaryProberAgent*: Maps the target's input surface and identifies defense boundaries.
    *   *ExploiterAgent*: Deploys known attack patterns based on exploration data.
    *   *MutatorAgent*: Evolves failed or partially successful attacks using techniques like obfuscation, encoding, or semantic variation.
*   **✅ Validation Coalition**: Verifies the success of attacks to minimize false positives.
    *   *ValidatorAgent*: Checks system state changes and response codes.
    *   *PerspectiveAgent*: Analyzes attacks from different user roles (e.g., user vs. admin).
    *   *LLMJudgeAgent*: Uses independent LLMs to review interaction logs and vote on semantic violations.
*   **🔧 Remediation Coalition**:
    *   *CounterfactualAgent*: Analyzes successful attack traces and suggests specific patches or prompt hardening strategies.

### Layer 4: Security Scenarios
A modular library of attack scenarios, including:
*   **Technical Exploits**: SQL Injection, Command Injection (T1059).
*   **AI-Specific Threats**: Prompt Injection, Jailbreaking (AML.T0051).
*   **Reconnaissance**: Active Scanning (T1595).

### Layer 5: External Services & Infrastructure
*   **Sandboxing**: Docker-based isolation for safely executing the Purple Agent.
*   **Knowledge Base**: A shared updateable memory store.
*   **LLM Providers**: Integration with OpenAI, Anthropic, and Google models for agent intelligence.

---

## 3. Detailed Workflow Lifecycle

The evaluation process follows a structured lifecycle managed by the `MetaOrchestrator`. This typically runs for a configured number of rounds (default 10).

### 3.1 Initialization
The workflow begins when `create_ecosystem` is called.
1.  **Scenario Loading**: A specific `SecurityScenario` (e.g., SQL Injection configs) is loaded.
2.  **Agent Initialization**: All specialized agents are instantiated with access to the shared Knowledge Base.
3.  **Target Setup**: The Purple Agent (SUT) is wrapped (optionally sandboxed) via `PurpleAgentA2AProxy`.

### 3.2 The Evaluation Loop
Each round consists of distinct phases designed to mimic a human attacker's methodology:

#### Phase 1: Exploration
**Goal**: Identify the boundaries of the target's defenses.
*   **Coalition**: The Orchestrator forms a coalition with `BoundaryProberAgent`.
*   **Action**: Agents send probe inputs to the target to understand what formats, payloads, or schemas are accepted or rejected.
*   **Allocation**: `ThompsonSamplingAllocator` uses past results to prioritize which boundaries to probe next (e.g., focusing on boundaries that seem "soft" or inconsistent).

#### Phase 2: Exploitation
**Goal**: Generate and evolve successful attacks.
*   **Coalition**: `ExploiterAgent` (initial attacks) and `MutatorAgent` (evolving attacks).
*   **Action**:
    *   `ExploiterAgent` attempts known attack patterns based on exploration data.
    *   `MutatorAgent` modifies failed or partially successful attacks. Techniques include Base64 encoding, synonym replacement, emotional manipulation (for LLMs), or syntax obfuscation (for SQLi).
*   **Feedback**: Results are recorded in the Knowledge Base to inform future mutations.

#### Phase 3: Validation
**Goal**: Ensure attacks are valid and realistic.
*   **Coalition**: `ValidatorAgent` and `PerspectiveAgent`.
*   **Action**:
    *   `ValidatorAgent` checks if an attack actually succeeded. Did the system return a 200 OK? Did the database state change?
    *   `PerspectiveAgent` may analyze the attack from different viewpoints to determine impact.

#### Phase 4: Consensus (Optional/Configurable)
**Goal**: High-fidelity verification using LLMs.
*   **Coalition**: `LLMJudgeAgent`.
*   **Action**: Uses one or multiple LLMs (OpenAI, Anthropic, Gemini) to review interaction logs. They vote on whether a security violation occurred. This is critical for subtle biological or semantic attacks (like Prompt Injection) where code-based validation is insufficient.

### 3.3 Remediation (Post-Attack)
If vulnerabilities are found, the Remediation Coalition is activated.
*   `CounterfactualAgent` analyzes the successful attack trace to understand *why* it succeeded.
*   It generates specific suggestions for the Purple Agent's system prompt or filtering logic to block the specific vector.

---

## 4. Scoring & Reporting (Dual Evaluation)

We implement a **Dual Evaluation Framework** to separate detector quality from target security, ensuring clear and actionable metrics.

### 4.1 Green Agent Metrics (Detector Performance)
Focuses on the effectiveness of the specialized agents.
*   **Precision/Recall/F1**: How accurate was the evaluator? Did it raise false alarms?

### 4.2 Purple Agent Assessment (Target Security)
Focuses on the security posture of the System Under Test.
*   **CVSS Scoring**: Vulnerabilities are scored (0.0 - 10.0) based on severity.
*   **Risk Grading**: The target receives a letter grade (A-F) and a list of unpatched CVEs/weaknesses.

### 4.3 Output Artifacts
At the end of an evaluation, the system generates:
1.  **EvaluationResult**: A structured object containing all rounds, scores, and detected vulnerabilities.
2.  **eBOM (Evaluation Bill of Materials)**: A JSON/dict record ensuring reproducibility. It lists exact versions of agents/LLMs, configuration parameters, and the hash of the scenario definition.
3.  **Coverage Report**: Maps the tested attacks against the MITRE ATT&CK/ATLAS framework to show testing breadth.

---

## 5. MITRE ATT&CK & ATLAS Integration

SecurityEvaluator is built on standard taxonomies.
*   **Full Metadata Coverage**: Every generated attack is tagged with its corresponding MITRE Technique ID.
*   **Hybrid Coverage**: Combines **Enterprise ATT&CK** (for traditional software flaws) and **ATLAS** (for ML vulnerabilities).
*   **Coverage Reporting**: The system generates a report mapping the tested vectors against the full matrix of 975+ techniques, ensuring no blind spots.

---

## 6. Technical Implementation

*   **Language**: Python 3.11+
*   **Communication**: Implements the **A2A (Agent-to-Agent) Protocol** for standardized inter-agent messaging.
*   **Isolation**: Uses `PurpleAgentA2AProxy` to wrap the target application, allowing for network interception and sandboxed execution.
*   **Reproducibility**: Generates an **Evaluation Bill of Materials (eBOM)** for every run.

---

## 7. Conclusion

SecurityEvaluator represents a paradigm shift in automated security testing. By treating security evaluation as a multi-agent collaborative task, it achieves a depth of analysis previously reserved for human red teams. Its adherence to standards like CVSS and MITRE ATT&CK ensures that its outputs are actionable for engineering and compliance teams alike.
