#!/usr/bin/env python3
"""
Generate visual flow diagrams for the Security Evaluator framework.

Requirements:
    pip install pillow

Usage:
    python generate_flow_diagram.py
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_sequence_diagram():
    """Create a sequence diagram showing the evaluation flow."""

    # Image dimensions
    width = 2400
    height = 3000
    background_color = (255, 255, 255)

    # Create image
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)

    # Colors
    black = (0, 0, 0)
    blue = (33, 150, 243)
    green = (76, 175, 80)
    orange = (255, 152, 0)
    purple = (156, 39, 176)
    gray = (158, 158, 158)
    light_blue = (187, 222, 251)
    light_green = (200, 230, 201)
    light_orange = (255, 224, 178)

    # Try to load a font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Title
    draw.text((width//2 - 400, 30), "Security Evaluator - Sequence Diagram",
              fill=black, font=title_font)

    # Component positions (X coordinates)
    client_x = 150
    judge_x = 450
    ecosystem_x = 800
    agents_x = 1150
    purple_x = 1500
    sandbox_x = 1850

    y_start = 120
    y_spacing = 60

    # Draw component boxes
    components = [
        (client_x, "Client", blue),
        (judge_x, "Green Agent\n(Judge)", green),
        (ecosystem_x, "Ecosystem", orange),
        (agents_x, "Agents", purple),
        (purple_x, "Purple\nAgent", blue),
        (sandbox_x, "Sandbox", gray)
    ]

    for x, label, color in components:
        # Box
        draw.rectangle([x-60, y_start, x+60, y_start+60],
                      outline=color, fill=color, width=2)
        # Label
        lines = label.split('\n')
        for i, line in enumerate(lines):
            draw.text((x - 40, y_start + 15 + i*18), line,
                     fill=(255,255,255), font=small_font)
        # Lifeline
        draw.line([x, y_start+60, x, height-50], fill=gray, width=1)

    # Current Y position
    y = y_start + 100

    def draw_arrow(x1, y1, x2, y2, label, color=black, is_return=False):
        """Draw an arrow with label."""
        # Arrow line
        if is_return:
            draw.line([x1, y1, x2, y2], fill=gray, width=1)
        else:
            draw.line([x1, y1, x2, y2], fill=color, width=2)

        # Arrow head
        if x2 > x1:
            draw.polygon([(x2, y2), (x2-10, y2-5), (x2-10, y2+5)], fill=color)
        else:
            draw.polygon([(x2, y2), (x2+10, y2-5), (x2+10, y2+5)], fill=color)

        # Label
        label_x = (x1 + x2) // 2
        label_y = y2 - 20
        draw.text((label_x - 60, label_y), label, fill=black, font=small_font)

    def draw_box(x, y, text, color=light_blue):
        """Draw a text box."""
        # Split text into lines
        lines = text.split('\n')
        box_height = len(lines) * 20 + 10
        box_width = 200

        draw.rectangle([x - box_width//2, y, x + box_width//2, y + box_height],
                      outline=black, fill=color, width=1)

        for i, line in enumerate(lines):
            draw.text((x - box_width//2 + 10, y + 5 + i*20), line,
                     fill=black, font=small_font)

        return box_height

    # Sequence flow

    # 1. Client sends request
    draw_arrow(client_x, y, judge_x, y, "POST /tasks", blue)
    y += y_spacing

    # 2. Judge creates task
    draw_arrow(judge_x, y, ecosystem_x, y, "create_task()", green)
    y += y_spacing

    # 3. Initialize
    box_h = draw_box(ecosystem_x, y, "• Load Scenario\n• Create Agents\n• Setup Orchestrator", light_green)
    y += box_h + 20

    # 4. Return task ID
    draw_arrow(judge_x, y, client_x, y, "task_id", green, is_return=True)
    y += y_spacing

    # 5. Start evaluation
    draw_arrow(judge_x, y, ecosystem_x, y, "start_eval()", green)
    y += y_spacing

    # Header: Round 1
    draw.text((width//2 - 100, y), "=== ROUND 1 (Exploration) ===",
             fill=orange, font=header_font)
    y += 50

    # 6. Form coalition
    draw_arrow(ecosystem_x, y, agents_x, y, "form_coalition()", orange)
    y += y_spacing

    # 7. Agent execution
    box_h = draw_box(agents_x, y,
                    "• BoundaryProber\n• Exploiter\n• Mutator\n• Validator",
                    light_orange)
    y += box_h + 20

    # 8. Generate attacks
    draw_arrow(agents_x, y, ecosystem_x, y, "attacks[]", purple, is_return=True)
    y += y_spacing

    # 9. Wrap in sandbox
    draw_arrow(ecosystem_x, y, sandbox_x, y, "wrap_in_sandbox()", orange)
    y += y_spacing

    # 10. Execute attack
    draw_arrow(sandbox_x, y, purple_x, y, "execute_attack()", gray)
    y += y_spacing

    # 11. Detect
    draw_arrow(purple_x, y, purple_x + 100, y, "detect()", blue)
    y += y_spacing

    # 12. Return result
    draw_arrow(purple_x, y, sandbox_x, y, "result", blue, is_return=True)
    y += y_spacing

    # 13. Test result
    draw_arrow(sandbox_x, y, ecosystem_x, y, "test_result", gray, is_return=True)
    y += y_spacing

    # 14. Share knowledge
    draw_arrow(ecosystem_x, y, agents_x, y, "share_knowledge()", orange)
    y += y_spacing

    # Header: Round 2
    draw.text((width//2 - 100, y), "=== ROUND 2 (Exploitation) ===",
             fill=orange, font=header_font)
    y += 50

    # 15. Repeat
    draw.text((ecosystem_x - 100, y), "(Repeat coalition, generation, testing)",
             fill=gray, font=small_font)
    y += y_spacing * 2

    # Header: Finalization
    draw.text((width//2 - 100, y), "=== FINALIZATION ===",
             fill=green, font=header_font)
    y += 50

    # 16. Return results
    draw_arrow(ecosystem_x, y, judge_x, y, "eval_result", orange, is_return=True)
    y += y_spacing

    # 17. Client polls
    draw_arrow(client_x, y, judge_x, y, "GET /tasks/{id}", blue)
    y += y_spacing

    # 18. Return results
    draw_arrow(judge_x, y, client_x, y, "results", green, is_return=True)

    # Save image
    output_path = "docs/sequence_diagram.png"
    os.makedirs("docs", exist_ok=True)
    img.save(output_path)
    print(f"✅ Sequence diagram saved to: {output_path}")


def create_architecture_diagram():
    """Create an architecture diagram showing components."""

    # Image dimensions
    width = 2400
    height = 2000
    background_color = (255, 255, 255)

    # Create image
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)

    # Colors
    black = (0, 0, 0)
    blue = (33, 150, 243)
    green = (76, 175, 80)
    orange = (255, 152, 0)
    purple = (156, 39, 176)
    red = (244, 67, 54)
    light_blue = (187, 222, 251)
    light_green = (200, 230, 201)
    light_orange = (255, 224, 178)
    light_purple = (225, 190, 231)

    # Try to load a font
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Title
    draw.text((width//2 - 350, 30), "Security Evaluator - System Architecture",
              fill=black, font=title_font)

    def draw_component(x, y, w, h, label, sublabels, color, text_color=black):
        """Draw a component box with sublabels."""
        # Main box
        draw.rectangle([x, y, x+w, y+h], outline=color, fill=color, width=3)

        # Label
        draw.text((x + 10, y + 10), label, fill=text_color, font=label_font)

        # Sublabels
        y_offset = y + 45
        for sublabel in sublabels:
            draw.text((x + 15, y_offset), f"• {sublabel}", fill=text_color, font=small_font)
            y_offset += 25

    # Layer 1: API Layer
    y = 120
    draw.text((50, y), "API Layer", fill=black, font=header_font)
    y += 40

    draw_component(50, y, 500, 150, "Green Agent (Judge/API Server)",
                  ["A2A Protocol Endpoints",
                   "Task Management",
                   "Dataset Management"],
                  light_blue)

    draw_component(600, y, 500, 150, "Purple Agent (Detector)",
                  ["Detection Logic",
                   "HTTP Endpoints",
                   "Pattern Matching / ML Model"],
                  light_green)

    # Arrow between
    draw.line([550, y+75, 600, y+75], fill=black, width=3)
    draw.polygon([(600, y+75), (590, y+70), (590, y+80)], fill=black)
    draw.text((520, y+50), "HTTP", fill=black, font=small_font)

    # Layer 2: Framework Core
    y = 350
    draw.text((50, y), "Framework Core", fill=black, font=header_font)
    y += 40

    draw_component(50, y, 350, 200, "UnifiedEcosystem",
                  ["Main Orchestrator",
                   "Agent Management",
                   "Configuration",
                   "Result Aggregation"],
                  light_orange)

    draw_component(450, y, 350, 200, "MetaOrchestrator",
                  ["Coalition Formation",
                   "Round Management",
                   "Phase Progression",
                   "Budget Enforcement"],
                  light_purple)

    draw_component(850, y, 350, 200, "Knowledge Base",
                  ["Shared Memory",
                   "Agent Communication",
                   "Attack Registry",
                   "Boundary Info"],
                  light_green)

    # Layer 3: Agents
    y = 600
    draw.text((50, y), "Specialized Agents", fill=black, font=header_font)
    y += 40

    agent_width = 280
    agent_height = 150

    agents = [
        (50, y, "BoundaryProber", ["Thompson Sampling", "Weak Detection"]),
        (350, y, "Exploiter", ["Hybrid Generation", "40% Dataset, 40% Algo"]),
        (650, y, "Mutator", ["Novelty Search", "Diversity Evolution"]),
        (950, y, "Validator", ["Syntax Check", "Semantic Check"]),
        (50, y+180, "Perspective", ["Multi-Viewpoint", "LLM Assessment"]),
        (350, y+180, "LLMJudge", ["Dawid-Skene", "Consensus Building"]),
        (650, y+180, "Counterfactual", ["Beam Search", "Remediation"])
    ]

    for ax, ay, alabel, asublabels in agents:
        draw_component(ax, ay, agent_width, agent_height, alabel,
                      asublabels, light_purple, black)

    # Layer 4: Production Features
    y = 1000
    draw.text((50, y), "Production Features", fill=black, font=header_font)
    y += 40

    draw_component(50, y, 350, 180, "Formal Sandbox",
                  ["Docker Isolation",
                   "seccomp Profile",
                   "Resource Limits",
                   "Network Blocking"],
                  light_blue)

    draw_component(450, y, 350, 180, "Cost Optimization",
                  ["Model Router",
                   "Budget Enforcer",
                   "Cost Predictor",
                   "Phase Budgets"],
                  light_green)

    draw_component(850, y, 350, 180, "Coverage Tracker",
                  ["MITRE ATT&CK",
                   "Gap Analysis",
                   "Scenario Templates",
                   "Priority Queue"],
                  light_orange)

    # Layer 5: Data Layer
    y = 1230
    draw.text((50, y), "Data & Models", fill=black, font=header_font)
    y += 40

    draw_component(50, y, 550, 150, "Core Models",
                  ["Attack, TestResult, EvaluationResult",
                   "Coalition, KnowledgeEntry",
                   "AgentCard, eBOM"],
                  light_green)

    draw_component(650, y, 550, 150, "Datasets",
                  ["SQL Injection Samples (27)",
                   "Vulnerable & Secure Code",
                   "MITRE ATT&CK Mapping"],
                  light_blue)

    # Save image
    output_path = "docs/architecture_diagram.png"
    os.makedirs("docs", exist_ok=True)
    img.save(output_path)
    print(f"✅ Architecture diagram saved to: {output_path}")


def main():
    """Generate all diagrams."""
    print("🎨 Generating flow diagrams...")
    print()

    try:
        create_sequence_diagram()
        create_architecture_diagram()

        print()
        print("=" * 60)
        print("✅ All diagrams generated successfully!")
        print("=" * 60)
        print()
        print("📂 Output files:")
        print("   • docs/sequence_diagram.png")
        print("   • docs/architecture_diagram.png")
        print()
        print("💡 View the diagrams:")
        print("   open docs/sequence_diagram.png")
        print("   open docs/architecture_diagram.png")
        print()

    except Exception as e:
        print(f"❌ Error generating diagrams: {e}")
        print()
        print("💡 Install Pillow if needed:")
        print("   pip install pillow")


if __name__ == '__main__':
    main()
