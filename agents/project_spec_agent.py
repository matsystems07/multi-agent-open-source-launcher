from models import make_message
from tools import call_groq_llm


class ProjectSpecAgent:
    def __init__(self, bus):
        self.name = "project_spec"
        self.bus = bus

    def process(self, message):
        print(f"\n[{self.name}] Received message:")
        print(message)

        payload = message.get("payload", {})
        idea = payload.get("idea", "open source project")
        focus = payload.get("focus", "define project specification")

        try:
            print(f"[{self.name}] Calling Groq for project specification...")

            system_prompt = """
You are a Project Specification Agent for an open-source project launch system.
Your job is to convert a raw software idea into a structured project specification
that can be used by downstream agents for repository scaffolding, documentation,
GitHub setup, and issue planning.

Return concise, practical, implementation-focused output.
"""

            user_prompt = f"""
Project idea: {idea}
Task focus: {focus}

Return a structured JSON-like specification with the following fields:
- project_title
- target_users
- problem_statement
- core_features
- repo_goals
- docs_needs
- roadmap_inputs

Be concrete and concise.
"""

            spec_text = call_groq_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

            print(f"[{self.name}] Groq response received.")

            specification = {
                "project_title": idea.title(),
                "target_users": ["developers", "maintainers", "contributors"],
                "problem_statement": f"A system to help launch and manage the open-source project '{idea}'.",
                "core_features": [
                    "Project specification generation",
                    "Repository scaffolding",
                    "Documentation drafting",
                    "GitHub workflow setup"
                ],
                "repo_goals": [
                    "Clear onboarding",
                    "Reusable starter structure",
                    "Contributor-friendly workflow"
                ],
                "docs_needs": [
                    "README.md",
                    "CONTRIBUTING.md",
                    "ROADMAP.md",
                    "ONBOARDING.md"
                ],
                "roadmap_inputs": [
                    "Scaffold repository",
                    "Generate docs",
                    "Create GitHub issues",
                    "Review and revise outputs"
                ],
                "llm_raw_output": spec_text
            }

        except Exception as e:
            print(f"[{self.name}] LLM failed, falling back to dummy spec: {e}")

            specification = {
                "project_title": idea.title(),
                "target_users": ["developers", "maintainers", "contributors"],
                "problem_statement": f"A system to help launch and manage the open-source project '{idea}'.",
                "core_features": [
                    "Project specification generation",
                    "Repository scaffolding",
                    "Documentation drafting",
                    "GitHub workflow setup"
                ],
                "repo_goals": [
                    "Clear onboarding",
                    "Reusable starter structure",
                    "Contributor-friendly workflow"
                ],
                "docs_needs": [
                    "README.md",
                    "CONTRIBUTING.md",
                    "ROADMAP.md",
                    "ONBOARDING.md"
                ],
                "roadmap_inputs": [
                    "Scaffold repository",
                    "Generate docs",
                    "Create GitHub issues",
                    "Review and revise outputs"
                ],
                "llm_raw_output": ""
            }

        print(f"[{self.name}] Generated specification for idea: {idea}")

        response_message = make_message(
            from_agent="project_spec",
            to_agent="orchestrator",
            message_type="project_spec_completed",
            payload={
                "idea": idea,
                "focus": focus,
                "specification": specification
            },
            parent_message_id=message.get("messageid")
        )

        self.bus.send(response_message)
        print(f"[{self.name}] Sent specification back to orchestrator.")