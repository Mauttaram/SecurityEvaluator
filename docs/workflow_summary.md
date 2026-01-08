# SecurityEvaluator Workflow Summary

This document provides a comprehensive summary of the SecurityEvaluator workflow, detailing how the system orchestrates agent coalitions to evaluate the security of a "Purple Agent" (System Under Test).

## 1. Overview

SecurityEvaluator is an agentic framework designed to simulate sophisticated attacks, validate defenses, and suggest remediations. It uses a **Meta-Orchestrator** to manage dynamic coalitions of specialized agents through a multi-phase evaluation process.

High-level architecture involves 5 layers:
1.  **User Interface** (API, CLI)
2.  **Orchestration** (Meta-Orchestrator, Task Router)
3.  **Agent Coalitions** (Attack, Validation, Remediation)
4.  **Security Scenarios** (e.g., SQL Injection, Prompt Injection)
5.  **External Services** (LLMs, Target System)

## 2. Core Components

*   **UnifiedEcosystem**: The main entry point that initializes the environment, agents, and scenario.
*   **MetaOrchestrator**: The central brain that coordinates the evaluation lifecycle, manages phases, and forms coalitions.
*   **ThompsonSamplingAllocator**: A Bayesian optimization component used to intelligently allocate tests to the most promising attack vectors.
*   **Knowledge Base**: A shared repository where agents store and retrieve information about the target, attack attempts, and results.
*   **Agents**: Specialized AI agents divided into three coalitions:
    *   *Attack Coalition*: `BoundaryProberAgent`, `ExploiterAgent`, `MutatorAgent`.
    *   *Validation Coalition*: `ValidatorAgent`, `PerspectiveAgent`, `LLMJudgeAgent`.
    *   *Remediation Coalition*: `CounterfactualAgent`.

## 3. Detailed Workflow

The evaluation process follows a structured lifecycle managed by the `MetaOrchestrator`.

### 3.1 Initialization
The workflow begins when `create_ecosystem` is called.
1.  **Scenario Loading**: A specific `SecurityScenario` (e.g., SQL Injection configs) is loaded.
2.  **Agent Initialization**: All specialized agents are instantiated with access to the shared Knowledge Base.
3.  **Target Setup**: The Purple Agent (SUT) is wrapped (optionally sandboxed).

### 3.2 The Evaluation Loop
The core evaluation happens in a loop defined by `orchestrate_evaluation` (default 10 rounds). Each round consists of distinct phases:

#### Phase 1: Exploration
**Goal**: Identify the boundaries of the target's defenses.
*   **Coalition**: The Orchestrator forms a coalition with `BoundaryProberAgent`.
*   **Action**: Agents send probe inputs to the target to understand what formats or payloads are accepted or rejected.
*   **Allocation**: `ThompsonSamplingAllocator` uses past results to prioritize which boundaries to probe next (e.g. focusing on boundaries that seem "soft" or inconsistent).

#### Phase 2: Exploitation
**Goal**: Generate and evolve successful attacks.
*   **Coalition**: `ExploiterAgent` (initial attacks) and `MutatorAgent` (evolving attacks).
*   **Action**:
    *   `ExploiterAgent` attempts known attack patterns based on exploration data.
    *   `MutatorAgent` modifies failed or partially successful attacks using techniques like obfuscation or encoding.
*   **Feedback**: Results are recorded in the Knowledge Base to inform future mutations.

#### Phase 3: Validation
**Goal**: Ensure attacks are valid and realistic.
*   **Coalition**: `ValidatorAgent` and `PerspectiveAgent`.
*   **Action**:
    *   `ValidatorAgent` checks if an attack actually succeeded (did it bypass the filter?).
    *   `PerspectiveAgent` may analyze the attack from different viewpoints (e.g., user vs. admin execution context).

#### Phase 4: Consensus (Optional/Configurable)
**Goal**: High-fidelity verification using LLMs.
*   **Coalition**: `LLMJudgeAgent`.
*   **Action**: Uses one or multiple LLMs (OpenAI, Anthropic, Gemini) to review the interaction logs and vote on whether a security violation occurred. This is critical for subtle biological or semantic attacks (like Prompt Injection) where code-based validation is insufficient.

### 3.3 Dynamic Coalition Formation
Throughout the phases, the `MetaOrchestrator` dynamically forms coalitions using `_form_coalition`. It selects agents based on **Capabilities** required for the current task (e.g., `Capability.PROBE`, `Capability.MUTATE`).

## 4. Remediation (Post-Attack)
If vulnerabilities are found, the Remediation Coalition is activated (if configured).
*   `CounterfactualAgent` analyzes the successful attack trace.
*   It suggests modifications to the Purple Agent's system prompt or filtering logic to block the specific vector.

## 5. Reporting and Outputs
At the end of the evaluation:
1.  **EvaluationResult**: A structured object containing all rounds, scores, and detected vulnerabilities.
2.  **eBOM (Evaluation Bill of Materials)**: A JSON/dict record ensuring reproducibility, listing:
    *   Exact versions of agents and LLMs used.
    *   Configuration parameters.
    *   Hash of the scenario definition.
3.  **Coverage Report**: Maps the tested attacks against MITRE ATT&CK framework or other standards to show testing breadth.
