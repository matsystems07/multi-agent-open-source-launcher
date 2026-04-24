import os
import json
import csv
from datetime import datetime


class EvaluationTracker:
    def __init__(self, output_dir="evaluation/results"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []

    def add_result(self, result: dict):
        self.results.append(result)

    def save_json(self, filename="results.json"):
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=4)
        return path

    def save_csv(self, filename="results.csv"):
        path = os.path.join(self.output_dir, filename)

        if not self.results:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("")
            return path

        fieldnames = sorted({key for row in self.results for key in row.keys()})

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        return path

    def build_summary(self):
        total = len(self.results)
        if total == 0:
            return {
                "total_runs": 0,
                "spec_success_rate": 0,
                "scaffold_success_rate": 0,
                "docs_success_rate": 0,
                "github_success_rate": 0,
                "issue_feedback_success_rate": 0,
                "revision_trigger_rate": 0,
                "avg_readiness_score": 0,
                "avg_runtime_seconds": 0,
                "total_github_issues_created": 0,
            }

        def avg(values):
            return round(sum(values) / len(values), 2) if values else 0

        spec_successes = [1 for r in self.results if r.get("spec_success") is True]
        scaffold_successes = [1 for r in self.results if r.get("scaffold_success") is True]
        docs_successes = [1 for r in self.results if r.get("docs_success") is True]
        github_successes = [1 for r in self.results if r.get("github_success") is True]
        feedback_successes = [1 for r in self.results if r.get("issue_feedback_success") is True]
        revision_triggers = [1 for r in self.results if r.get("revision_triggered") is True]

        readiness_scores = [
            r.get("readiness_score", 0)
            for r in self.results
            if isinstance(r.get("readiness_score", None), (int, float))
        ]
        runtimes = [
            r.get("runtime_seconds", 0)
            for r in self.results
            if isinstance(r.get("runtime_seconds", None), (int, float))
        ]
        issues_created = [
            r.get("github_issues_created", 0)
            for r in self.results
            if isinstance(r.get("github_issues_created", None), int)
        ]

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_runs": total,
            "spec_success_rate": round(len(spec_successes) / total * 100, 2),
            "scaffold_success_rate": round(len(scaffold_successes) / total * 100, 2),
            "docs_success_rate": round(len(docs_successes) / total * 100, 2),
            "github_success_rate": round(len(github_successes) / total * 100, 2),
            "issue_feedback_success_rate": round(len(feedback_successes) / total * 100, 2),
            "revision_trigger_rate": round(len(revision_triggers) / total * 100, 2),
            "avg_readiness_score": avg(readiness_scores),
            "avg_runtime_seconds": avg(runtimes),
            "total_github_issues_created": sum(issues_created),
        }

    def save_summary(self, filename="summary.json"):
        summary = self.build_summary()
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
        return path