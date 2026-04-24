import json
from models import make_message
from tools import call_groq_llm, github_env_ready, get_github_repo, create_github_issue


class IssueFeedbackAgent:
    def __init__(self, bus):
        self.name = "issue_feedback"
        self.bus = bus

    def _fallback_feedback(self, idea, specification, generated_docs):
        issues = [
            {
                "title": f"Add architecture documentation for {specification.get('project_title', idea.title())}",
                "body": (
                    "Create docs/architecture.md with a high-level system overview, agent responsibilities, "
                    "message flow, and external integrations."
                )
            },
            {
                "title": "Add CI workflow for linting and tests",
                "body": (
                    "Create a GitHub Actions workflow to run basic checks such as linting, import validation, "
                    "and future test execution on push/pull request."
                )
            },
            {
                "title": "Improve README setup and usage clarity",
                "body": (
                    "Refine README.md so environment setup, required API keys, installation steps, "
                    "and execution flow are clearly explained."
                )
            },
            {
                "title": "Add starter implementation tasks for generated project idea",
                "body": (
                    "Create starter implementation tasks for the actual product/application based on the generated "
                    "project specification, instead of only scaffold/docs generation."
                )
            },
            {
                "title": "Add evaluation and experiment scripts",
                "body": (
                    "Implement evaluation/metrics.py and a small experiment runner to test 3–5 prompts and "
                    "track pipeline success, runtime, and output completeness."
                )
            },
        ]

        return {
            "summary": (
                "The generated repository is a strong scaffold and documentation starter, but still needs "
                "architecture docs, CI/testing, clearer setup guidance, implementation tasks, and evaluation scripts."
            ),
            "readiness_score": 72,
            "revision_needed": True,
            "issues": issues
        }

    def _generate_feedback_with_llm(self, idea, specification, generated_docs, github_repo_url):
        system_prompt = """
You are an Issue and Feedback Agent for a multi-agent open-source project launcher.
Your job is to review the generated project outputs and propose practical next-step GitHub issues.

Return ONLY valid JSON with this structure:
{
  "summary": "short review summary",
  "readiness_score": 0,
  "revision_needed": true,
  "issues": [
    {
      "title": "Issue title",
      "body": "Detailed issue body"
    }
  ]
}

Rules:
- readiness_score must be an integer from 0 to 100
- revision_needed must be true or false
- provide 3 to 5 issues
- issue titles must be concrete and actionable
- issue bodies should explain scope and expected output
- focus on missing implementation, docs gaps, testing, CI, architecture, and usability
"""

        user_prompt = f"""
Project idea:
{idea}

Specification:
{json.dumps(specification, indent=2)}

Generated docs keys:
{list(generated_docs.keys())}

GitHub repo URL:
{github_repo_url}
"""

        raw = call_groq_llm(system_prompt=system_prompt, user_prompt=user_prompt)

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        parsed = json.loads(cleaned)

        if "issues" not in parsed or not isinstance(parsed["issues"], list):
            raise ValueError("LLM output missing valid 'issues' list.")

        return parsed

    def process(self, message):
        print(f"\n[{self.name}] Received message:")
        print(message)

        payload = message.get("payload", {})
        idea = payload.get("idea", "")
        focus = payload.get("focus", "Review outputs and generate follow-up issues")
        specification = payload.get("specification", {})
        repo_path = payload.get("repo_path", "")
        scaffold = payload.get("scaffold", {})
        generated_docs = payload.get("generated_docs", {})
        github_repo_url = payload.get("github_repo_url", "")

        print(f"[{self.name}] Reviewing outputs and generating issue feedback...")

        try:
            feedback = self._generate_feedback_with_llm(
                idea=idea,
                specification=specification,
                generated_docs=generated_docs,
                github_repo_url=github_repo_url
            )
            print(f"[{self.name}] LLM feedback generated successfully.")
        except Exception as e:
            print(f"[{self.name}] LLM feedback failed, using fallback: {e}")
            feedback = self._fallback_feedback(
                idea=idea,
                specification=specification,
                generated_docs=generated_docs
            )

        created_issues = []

        if github_repo_url and github_env_ready():
            try:
                repo = get_github_repo()
                for issue in feedback.get("issues", []):
                    created = create_github_issue(
                        repo=repo,
                        title=issue["title"],
                        body=issue["body"]
                    )
                    created_issues.append(created)
                print(f"[{self.name}] Created {len(created_issues)} GitHub issues.")
            except Exception as e:
                print(f"[{self.name}] GitHub issue creation failed: {e}")

        response = make_message(
            from_agent="issue_feedback",
            to_agent="orchestrator",
            message_type="issue_feedback_completed",
            payload={
                "status": "success",
                "idea": idea,
                "focus": focus,
                "specification": specification,
                "repo_path": repo_path,
                "scaffold": scaffold,
                "generated_docs": generated_docs,
                "github_repo_url": github_repo_url,
                "summary": feedback.get("summary", ""),
                "readiness_score": feedback.get("readiness_score", 0),
                "revision_needed": feedback.get("revision_needed", True),
                "proposed_issues": feedback.get("issues", []),
                "created_issues": created_issues,
            },
            parent_message_id=message.get("messageid"),
        )

        self.bus.send(response)
        print(f"[{self.name}] Sent issue feedback result back to orchestrator.")