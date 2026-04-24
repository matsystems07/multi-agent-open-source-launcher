import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq
from github import Github
from github.GithubException import UnknownObjectException, GithubException
import openai


load_dotenv()


def get_env_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


# =========================
# LLM HELPERS
# =========================

def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in environment.")
    return Groq(api_key=api_key)


def call_openai_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini"
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in environment.")

    client = openai.OpenAI(api_key=api_key)
    combined_prompt = f"""System instruction:
{system_prompt}

User request:
{user_prompt}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": combined_prompt}],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def call_groq_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = "llama-3.3-70b-versatile"
) -> str:
    try:
        client = get_groq_client()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_completion_tokens=1024,
        )
        return completion.choices[0].message.content.strip()

    except Exception as groq_error:
        print(f"[tools] Groq failed, trying OpenAI fallback: {groq_error}")

        try:
            return call_openai_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as openai_error:
            print(f"[tools] OpenAI fallback also failed: {openai_error}")
            raise RuntimeError(
                f"Both Groq and OpenAI failed. Groq error: {groq_error} | OpenAI error: {openai_error}"
            )


# =========================
# GITHUB HELPERS
# =========================

def github_env_ready() -> bool:
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo_name = os.getenv("GITHUB_REPO_NAME")
    return bool(token and owner and repo_name)


def get_github_client() -> Github:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is missing in environment.")
    return Github(token)


def get_github_repo():
    owner = os.getenv("GITHUB_OWNER")
    repo_name = os.getenv("GITHUB_REPO_NAME")
    if not owner or not repo_name:
        raise ValueError("GITHUB_OWNER or GITHUB_REPO_NAME is missing in environment.")
    github_client = get_github_client()
    return github_client.get_repo(f"{owner}/{repo_name}")


def ensure_github_repo(private: bool = False, auto_init: bool = False):
    owner = os.getenv("GITHUB_OWNER")
    repo_name = os.getenv("GITHUB_REPO_NAME")

    if not owner or not repo_name:
        raise ValueError("GITHUB_OWNER or GITHUB_REPO_NAME is missing in environment.")

    github_client = get_github_client()

    try:
        repo = github_client.get_repo(f"{owner}/{repo_name}")
        return repo, False
    except Exception:
        user = github_client.get_user()
        repo = user.create_repo(
            name=repo_name,
            private=private,
            auto_init=auto_init
        )
        return repo, True


def upsert_file_to_github(repo, path_in_repo: str, content: str, commit_message: str):
    try:
        existing = repo.get_contents(path_in_repo)
        result = repo.update_file(
            path=path_in_repo,
            message=commit_message,
            content=content,
            sha=existing.sha
        )
        return {
            "path": path_in_repo,
            "action": "updated",
            "commit_sha": result["commit"].sha
        }

    except UnknownObjectException:
        result = repo.create_file(
            path=path_in_repo,
            message=commit_message,
            content=content
        )
        return {
            "path": path_in_repo,
            "action": "created",
            "commit_sha": result["commit"].sha
        }

    except GithubException as e:
        error_text = str(e)

        if "This repository is empty" in error_text:
            result = repo.create_file(
                path=path_in_repo,
                message=commit_message,
                content=content
            )
            return {
                "path": path_in_repo,
                "action": "created",
                "commit_sha": result["commit"].sha
            }

        raise


def sync_local_folder_to_github(repo, local_folder: str, commit_prefix: str = "Sync"):
    uploaded_files = []

    for root, _, files in os.walk(local_folder):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(full_path, local_folder).replace("\\", "/")

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            result = upsert_file_to_github(
                repo=repo,
                path_in_repo=relative_path,
                content=content,
                commit_message=f"{commit_prefix} {relative_path}"
            )
            uploaded_files.append(result)

    return uploaded_files


def sync_local_repo_to_github(repo, repo_path=None, local_folder=None, commit_prefix: str = "Sync"):
    folder = repo_path or local_folder
    if not folder:
        raise ValueError("repo_path or local_folder must be provided.")
    return sync_local_folder_to_github(repo, folder, commit_prefix=commit_prefix)


def create_github_issue(repo, title: str, body: str):
    issue = repo.create_issue(title=title, body=body)
    return {
        "title": issue.title,
        "number": issue.number,
        "url": issue.html_url
    }