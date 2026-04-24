import os
import sys
import time

# Ensure project root is importable when running this file directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from message_bus import MessageBus
from models import make_message

from agents.orchestrator_agent import OrchestratorAgent
from agents.project_spec_agent import ProjectSpecAgent
from agents.code_scaffold_agent import CodeScaffoldAgent
from agents.documentation_agent import DocumentationAgent
from agents.github_repo_agent import GitHubRepoAgent
from agents.issue_feedback_agent import IssueFeedbackAgent

from evaluation.metrics import EvaluationTracker


TEST_PROMPTS = [
    "website showing honda cars",
    "car startup",
    "student expense tracker",
    "travel planner website",
    "restaurant menu and ordering platform",
]


def run_single_prompt(prompt: str):
    bus = MessageBus()

    orchestrator = OrchestratorAgent(bus)
    project_spec = ProjectSpecAgent(bus)
    code_scaffold = CodeScaffoldAgent(bus)
    documentation = DocumentationAgent(bus)
    github_repo = GitHubRepoAgent(bus)
    issue_feedback = IssueFeedbackAgent(bus)

    first_message = make_message(
        from_agent="system",
        to_agent="orchestrator",
        message_type="task",
        payload={
            "idea": prompt,
            "focus": "Decompose the idea into tasks for sub-agents"
        },
        parent_message_id=None
    )

    bus.send(first_message)

    start_time = time.time()

    spec_success = False
    scaffold_success = False
    docs_success = False
    github_success = False
    issue_feedback_success = False
    revision_triggered = False
    readiness_score = 0
    github_issues_created = 0
    github_repo_url = ""
    last_error = ""

    round_no = 1

    while not bus.is_empty():
        msg = bus.receive()
        if msg is None:
            break

        to_agent = msg.get("toagent", "")

        if to_agent == "orchestrator":
            orchestrator.process(msg)
        elif to_agent == "project_spec":
            project_spec.process(msg)
        elif to_agent == "code_scaffold":
            code_scaffold.process(msg)
        elif to_agent == "documentation":
            documentation.process(msg)
        elif to_agent == "github_repo":
            github_repo.process(msg)
        elif to_agent == "issue_feedback":
            issue_feedback.process(msg)

        round_no += 1

    end_time = time.time()

    # Parse message history for results
    for item in bus.history:
        sender = item.get("fromagent", "")
        message_type = item.get("messagetype", "")
        payload = item.get("payload", {})

        if sender == "project_spec" and message_type == "project_spec_completed":
            spec_success = True

        if sender == "code_scaffold" and payload.get("status") == "success":
            scaffold_success = True

        if sender == "documentation" and payload.get("status") == "success":
            docs_success = True
            if payload.get("revision_round", 0) > 0:
                revision_triggered = True

        if sender == "github_repo":
            github_success = payload.get("status") == "success"
            github_repo_url = payload.get("github_repo_url", "")
            if payload.get("status") != "success":
                last_error = payload.get("error", "")

        if sender == "issue_feedback":
            issue_feedback_success = payload.get("status") == "success"
            readiness_score = payload.get("readiness_score", 0)
            github_issues_created = len(payload.get("created_issues", []))
            if payload.get("status") != "success":
                last_error = payload.get("error", "")

    result = {
        "prompt": prompt,
        "spec_success": spec_success,
        "scaffold_success": scaffold_success,
        "docs_success": docs_success,
        "github_success": github_success,
        "issue_feedback_success": issue_feedback_success,
        "revision_triggered": revision_triggered,
        "readiness_score": readiness_score,
        "github_issues_created": github_issues_created,
        "github_repo_url": github_repo_url,
        "runtime_seconds": round(end_time - start_time, 2),
        "rounds_processed": round_no - 1,
        "error": last_error,
    }

    return result


def main():
    tracker = EvaluationTracker()

    print("=== Running RepoPilot Evaluation Experiments ===")
    for i, prompt in enumerate(TEST_PROMPTS, start=1):
        print(f"\n--- Experiment {i}/{len(TEST_PROMPTS)} ---")
        print(f"Prompt: {prompt}")

        try:
            result = run_single_prompt(prompt)
            tracker.add_result(result)

            print("Result:")
            for k, v in result.items():
                print(f"  {k}: {v}")

        except Exception as e:
            failed_result = {
                "prompt": prompt,
                "spec_success": False,
                "scaffold_success": False,
                "docs_success": False,
                "github_success": False,
                "issue_feedback_success": False,
                "revision_triggered": False,
                "readiness_score": 0,
                "github_issues_created": 0,
                "github_repo_url": "",
                "runtime_seconds": 0,
                "rounds_processed": 0,
                "error": str(e),
            }
            tracker.add_result(failed_result)
            print(f"Experiment failed: {e}")

    json_path = tracker.save_json()
    csv_path = tracker.save_csv()
    summary_path = tracker.save_summary()

    print("\n=== Evaluation Complete ===")
    print(f"Saved JSON results to: {json_path}")
    print(f"Saved CSV results to: {csv_path}")
    print(f"Saved summary to: {summary_path}")

    print("\nSummary:")
    summary = tracker.build_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()