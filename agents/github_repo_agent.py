from models import make_message
from tools import (
    github_env_ready,
    ensure_github_repo,
    sync_local_repo_to_github,
)


class GitHubRepoAgent:
    def __init__(self, bus):
        self.name = "github_repo"
        self.bus = bus

    def process(self, message):
        print(f"\n[{self.name}] Received message:")
        print(message)

        payload = message.get("payload", {})
        idea = payload.get("idea", "")
        focus = payload.get("focus", "Push generated repository to GitHub")
        specification = payload.get("specification", {})
        repo_path = payload.get("repo_path", "")
        scaffold = payload.get("scaffold", {})
        generated_docs = payload.get("generated_docs", {})

        # If GitHub is not configured yet, return a clean skipped result
        if not github_env_ready():
            print(f"[{self.name}] GitHub environment not configured yet. Skipping remote sync.")

            response = make_message(
                from_agent="github_repo",
                to_agent="orchestrator",
                message_type="github_repo_completed",
                payload={
                    "status": "skipped",
                    "idea": idea,
                    "focus": focus,
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "generated_docs": generated_docs,
                    "repo_created": False,
                    "github_repo_url": "",
                    "uploaded_files": [],
                    "error": "GitHub environment variables are missing."
                },
                parent_message_id=message.get("messageid")
            )
            self.bus.send(response)
            print(f"[{self.name}] Sent skipped result back to orchestrator.")
            return

        try:
            print(f"[{self.name}] Ensuring GitHub repo exists...")
            repo, was_created = ensure_github_repo(private=False, auto_init=True)

            print(f"[{self.name}] Syncing local files to GitHub...")
            uploaded_files = sync_local_repo_to_github(
                repo=repo,
                repo_path=repo_path,
                commit_prefix="RepoPilot upload"
            )

            response = make_message(
                from_agent="github_repo",
                to_agent="orchestrator",
                message_type="github_repo_completed",
                payload={
                    "status": "success",
                    "idea": idea,
                    "focus": focus,
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "generated_docs": generated_docs,
                    "repo_created": was_created,
                    "github_repo_url": repo.html_url,
                    "uploaded_files": uploaded_files
                },
                parent_message_id=message.get("messageid")
            )
            self.bus.send(response)
            print(f"[{self.name}] Sent GitHub sync result back to orchestrator.")

        except Exception as e:
            print(f"[{self.name}] GitHub sync failed: {e}")

            response = make_message(
                from_agent="github_repo",
                to_agent="orchestrator",
                message_type="github_repo_completed",
                payload={
                    "status": "failed",
                    "idea": idea,
                    "focus": focus,
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "generated_docs": generated_docs,
                    "repo_created": False,
                    "github_repo_url": "",
                    "uploaded_files": [],
                    "error": str(e)
                },
                parent_message_id=message.get("messageid")
            )
            self.bus.send(response)
            print(f"[{self.name}] Sent failure result back to orchestrator.")