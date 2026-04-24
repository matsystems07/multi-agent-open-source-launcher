from message_bus import MessageBus
from models import make_message

from agents.orchestrator_agent import OrchestratorAgent
from agents.project_spec_agent import ProjectSpecAgent
from agents.code_scaffold_agent import CodeScaffoldAgent
from agents.documentation_agent import DocumentationAgent
from agents.github_repo_agent import GitHubRepoAgent
from agents.issue_feedback_agent import IssueFeedbackAgent


def main():
    print("=== Open-Source Project Launch Manager ===")

    bus = MessageBus()

    orchestrator = OrchestratorAgent(bus)
    project_spec = ProjectSpecAgent(bus)
    code_scaffold = CodeScaffoldAgent(bus)
    documentation = DocumentationAgent(bus)
    github_repo = GitHubRepoAgent(bus)
    issue_feedback = IssueFeedbackAgent(bus)

    idea = input("Enter your startup/project idea: ").strip()
    focus = "Decompose the idea into tasks for sub-agents"

    first_message = make_message(
        from_agent="system",
        to_agent="orchestrator",
        message_type="task",
        payload={
            "idea": idea,
            "focus": focus
        },
        parent_message_id=None
    )

    bus.send(first_message)
    print("\n[system] Idea sent to Orchestrator.")

    round_no = 1

    while not bus.is_empty():
        print(f"\n--- Round {round_no} ---")
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
        else:
            print(f"[main] No handler for agent: {to_agent}")

        round_no += 1

    print(f"\n--- Round {round_no} ---")
    print("No more messages to process.")

    print("\n=== Message History ===")
    for item in bus.history:
        print(item)


if __name__ == "__main__":
    main()