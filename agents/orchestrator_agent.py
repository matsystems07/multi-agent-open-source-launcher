from models import make_message


class OrchestratorAgent:
    def __init__(self, bus):
        self.name = "orchestrator"
        self.bus = bus

    def process(self, message):
        print(f"\n[{self.name}] Received message:")
        print(message)

        sender = message.get("fromagent", "")
        payload = message.get("payload", {})

        if sender == "system":
            idea = payload.get("idea", "")
            focus = payload.get("focus", "")

            print(f"[orchestrator] Project idea: {idea}")
            print(f"[orchestrator] Focus: {focus}")
            print("[orchestrator] Sending task to Project Spec Agent...")

            spec_task = make_message(
                from_agent="orchestrator",
                to_agent="project_spec",
                message_type="task",
                payload={
                    "idea": idea,
                    "focus": "Create a structured open-source project specification including users, problem, core features, repo goals, docs needs, and roadmap inputs.",
                },
                parent_message_id=message.get("messageid"),
            )
            self.bus.send(spec_task)
            print("[orchestrator] Sent task message to project_spec.")

        elif sender == "project_spec":
            print("[orchestrator] Received project specification from Project Spec Agent.")
            print("[orchestrator] Spec summary:")
            print(payload)

            idea = payload.get("idea", "")
            specification = payload.get("specification", {})

            print("[orchestrator] Sending task to Code Scaffold Agent...")

            scaffold_task = make_message(
                from_agent="orchestrator",
                to_agent="code_scaffold",
                message_type="task",
                payload={
                    "idea": idea,
                    "focus": "Generate a starter repository scaffold from the approved project specification.",
                    "specification": specification,
                },
                parent_message_id=message.get("messageid"),
            )
            self.bus.send(scaffold_task)
            print("[orchestrator] Sent task message to code_scaffold.")

        elif sender == "code_scaffold":
            print("[orchestrator] Received scaffold from Code Scaffold Agent.")
            print("[orchestrator] Scaffold summary:")
            print(payload)

            idea = payload.get("idea", "")
            specification = payload.get("specification", {})
            repo_path = payload.get("repo_path", "")
            scaffold = payload.get("scaffold", {})

            print("[orchestrator] Sending task to Documentation Agent...")

            docs_task = make_message(
                from_agent="orchestrator",
                to_agent="documentation",
                message_type="task",
                payload={
                    "idea": idea,
                    "focus": "Generate project documentation for the scaffolded repository.",
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "revision_round": 0,
                },
                parent_message_id=message.get("messageid"),
            )
            self.bus.send(docs_task)
            print("[orchestrator] Sent task message to documentation.")

        elif sender == "documentation":
            print("[orchestrator] Received documentation output from Documentation Agent.")
            print("[orchestrator] Documentation summary:")
            print(payload)

            idea = payload.get("idea", "")
            specification = payload.get("specification", {})
            repo_path = payload.get("repo_path", "")
            scaffold = payload.get("scaffold", {})
            generated_docs = payload.get("generated_docs", {})
            revision_round = payload.get("revision_round", 0)

            # If this documentation message is from a revision pass, stop here
            if revision_round > 0:
                print("[orchestrator] Revised documentation received.")
                print("[orchestrator] Revision loop complete.")
                print("[orchestrator] Pipeline complete after documentation refinement.")
                return

            print("[orchestrator] Sending task to GitHub Repo Agent...")

            github_task = make_message(
                from_agent="orchestrator",
                to_agent="github_repo",
                message_type="task",
                payload={
                    "idea": idea,
                    "focus": "Create or sync the generated repository to GitHub.",
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "generated_docs": generated_docs,
                },
                parent_message_id=message.get("messageid"),
            )
            self.bus.send(github_task)
            print("[orchestrator] Sent task message to github_repo.")

        elif sender == "github_repo":
            print("[orchestrator] Received GitHub output from GitHub Repo Agent.")
            print("[orchestrator] GitHub summary:")
            print(payload)

            idea = payload.get("idea", "")
            specification = payload.get("specification", {})
            repo_path = payload.get("repo_path", "")
            scaffold = payload.get("scaffold", {})
            generated_docs = payload.get("generated_docs", {})
            github_repo_url = payload.get("github_repo_url", "")

            print("[orchestrator] Sending task to Issue Feedback Agent...")

            feedback_task = make_message(
                from_agent="orchestrator",
                to_agent="issue_feedback",
                message_type="task",
                payload={
                    "idea": idea,
                    "focus": "Review generated outputs and propose follow-up issues.",
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "generated_docs": generated_docs,
                    "github_repo_url": github_repo_url,
                },
                parent_message_id=message.get("messageid"),
            )
            self.bus.send(feedback_task)
            print("[orchestrator] Sent task message to issue_feedback.")

        elif sender == "issue_feedback":
            print("[orchestrator] Received issue feedback from Issue Feedback Agent.")
            print("[orchestrator] Feedback summary:")
            print(payload)

            idea = payload.get("idea", "")
            specification = payload.get("specification", {})
            repo_path = payload.get("repo_path", "")
            scaffold = payload.get("scaffold", {})
            generated_docs = payload.get("generated_docs", {})
            revision_needed = payload.get("revision_needed", False)
            readiness_score = payload.get("readiness_score", 0)
            proposed_issues = payload.get("proposed_issues", [])

            print(f"[orchestrator] Readiness score: {readiness_score}")
            print(f"[orchestrator] Revision needed: {revision_needed}")

            if revision_needed:
                print("[orchestrator] Triggering one revision loop to Documentation Agent...")

                revision_notes = "\n".join(
                    [f"- {issue.get('title', '')}: {issue.get('body', '')}" for issue in proposed_issues]
                )

                revision_task = make_message(
                    from_agent="orchestrator",
                    to_agent="documentation",
                    message_type="task",
                    payload={
                        "idea": idea,
                        "focus": "Revise the project documentation based on issue feedback and improve clarity, completeness, and contributor readiness.",
                        "specification": specification,
                        "repo_path": repo_path,
                        "scaffold": scaffold,
                        "generated_docs": generated_docs,
                        "revision_round": 1,
                        "revision_notes": revision_notes,
                    },
                    parent_message_id=message.get("messageid"),
                )
                self.bus.send(revision_task)
                print("[orchestrator] Sent revision task to documentation.")
            else:
                print("[orchestrator] No revision needed.")
                print("[orchestrator] Pipeline complete up to issue feedback stage.")

        else:
            print(f"[orchestrator] No handling rule defined for sender: {sender}")