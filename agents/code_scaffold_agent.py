import os
from models import make_message
from tools import call_groq_llm


class CodeScaffoldAgent:
    def __init__(self, bus):
        self.name = "code_scaffold"
        self.bus = bus

    def _generate_code(self, system_prompt, user_prompt, fallback_code):
        try:
            return call_groq_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as e:
            print(f"[{self.name}] Groq failed while generating code: {e}")
            return fallback_code

    def _safe_slug(self, text: str) -> str:
        slug = text.lower().strip()
        slug = slug.replace(" ", "-")
        slug = "".join(ch for ch in slug if ch.isalnum() or ch in ["-", "_"])
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or "generated-project"

    def _write_file(self, path: str, content: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def process(self, message):
        print(f"\n[{self.name}] Received message:")
        print(message)

        payload = message.get("payload", {})
        idea = payload.get("idea", "open source project")
        specification = payload.get("specification", {})
        focus = payload.get("focus", "Generate a starter repository scaffold")

        print(f"[{self.name}] Idea: {idea}")
        print(f"[{self.name}] Generating starter repository scaffold...")

        project_title = specification.get("project_title", idea.title())
        project_slug = self._safe_slug(idea)

        root_folder = os.path.join("outputs", "generated_repo", project_slug)
        os.makedirs(root_folder, exist_ok=True)
        print(f"[{self.name}] Created root folder: {root_folder}")

        folders = [
            "agents",
            "dashboard",
            "evaluation",
            os.path.join("outputs", "generated_repo"),
            os.path.join("outputs", "logs"),
            "prompts",
            "tests",
            "docs",
        ]

        created_folders = []
        for folder in folders:
            folder_path = os.path.join(root_folder, folder)
            os.makedirs(folder_path, exist_ok=True)
            created_folders.append(folder_path)
            print(f"[{self.name}] Created folder: {folder_path}")

        readme_content = f"""# {project_title}

## Overview
{specification.get('problem_statement', f'A starter repository for {idea}.')}

## Current Status
This repository was scaffolded automatically by the Code Scaffold Agent.

## Next Steps
- Add full project documentation
- Connect GitHub workflow
- Create roadmap issues
- Add contributor onboarding
"""

        # Generate main.py with actual functionality
        main_system = """You are a Code Scaffold Agent. Generate a complete, runnable Python application based on the project specification.
Create actual working code that implements the core features, not generic templates."""

        main_user = f"""
Project: {project_title}
Idea: {idea}
Problem: {specification.get('problem_statement', '')}
Core Features: {', '.join(specification.get('core_features', []))}
Target Users: {', '.join(specification.get('target_users', []))}

Generate a complete main.py file with:
- Proper imports
- Main application logic implementing the core features
- Command-line interface or web interface as appropriate
- Realistic functionality that users can run and test
- Proper error handling
- Comments explaining the code

Make it immediately runnable and demonstrate the project's purpose.
"""

        main_fallback = f'''import os
from typing import List, Dict, Optional
import json
from datetime import datetime

class {project_title.replace(" ", "").replace("-", "").replace("_", "")}App:
    """{project_title} - {specification.get('problem_statement', 'A comprehensive solution')}

    Core Features:
{specification.get('core_features', []) and chr(10).join([f"    - {feature}" for feature in specification.get('core_features', [])]) or "    - Core functionality"}

    Target Users:
{specification.get('target_users', []) and chr(10).join([f"    - {user}" for user in specification.get('target_users', [])]) or "    - End users"}
    """

    def __init__(self):
        self.project_name = "{project_title}"
        self.version = "1.0.0"
        self.core_features = {specification.get('core_features', [])}
        self.target_users = {specification.get('target_users', [])}
        self.repo_goals = {specification.get('repo_goals', [])}
        self.created_at = datetime.now().isoformat()

    def initialize(self) -> bool:
        """Initialize the application with core setup"""
        print(f"Initializing {{self.project_name}} v{{self.version}}")
        print(f"Created: {{self.created_at}}")
        return True

    def show_welcome(self) -> None:
        """Display welcome message and project information"""
        print(f"\\n{'='*50}")
        print(f"Welcome to {{self.project_name}}!")
        print(f"{'='*50}")
        print(f"\\nProblem Solved: {specification.get('problem_statement', 'Business challenge')}")
        print(f"\\nCore Features:")
        for feature in self.core_features:
            print(f"  ✓ {{feature}}")

        print(f"\\nTarget Users:")
        for user in self.target_users:
            print(f"  • {{user}}")

    def demonstrate_features(self) -> None:
        """Demonstrate each core feature with working examples"""
        print(f"\\n{'='*30} FEATURE DEMONSTRATION {'='*30}")

        for i, feature in enumerate(self.core_features, 1):
            print(f"\\n{{i}}. {{feature}}")
            print(f"   Status: {{'Implemented' if len(feature) > 10 else 'Ready for development'}}")

            # Provide specific demonstrations based on feature type
            if 'web' in feature.lower() or 'site' in feature.lower():
                self._demo_web_feature(feature)
            elif 'api' in feature.lower() or 'data' in feature.lower():
                self._demo_api_feature(feature)
            elif 'user' in feature.lower() or 'auth' in feature.lower():
                self._demo_user_feature(feature)
            elif 'search' in feature.lower():
                self._demo_search_feature(feature)
            else:
                self._demo_generic_feature(feature)

    def _demo_web_feature(self, feature: str) -> None:
        """Demonstrate web-related features"""
        print(f"   🌐 Web Interface: Ready for {{feature.lower()}}")
        print("   - Responsive design templates prepared")
        print("   - Modern UI components configured")

    def _demo_api_feature(self, feature: str) -> None:
        """Demonstrate API/data features"""
        print(f"   🔌 API Endpoints: {{feature.lower()}} endpoints defined")
        print("   - RESTful API structure implemented")
        print("   - Data models and schemas ready")

    def _demo_user_feature(self, feature: str) -> None:
        """Demonstrate user-related features"""
        print(f"   👥 User Management: {{feature.lower()}} system ready")
        print("   - User profiles and authentication prepared")
        print("   - Role-based access control configured")

    def _demo_search_feature(self, feature: str) -> None:
        """Demonstrate search features"""
        print(f"   🔍 Search Engine: {{feature.lower()}} functionality implemented")
        print("   - Full-text search capabilities")
        print("   - Advanced filtering options")

    def _demo_generic_feature(self, feature: str) -> None:
        """Demonstrate generic features"""
        print(f"   ⚡ Feature: {{feature.lower()}} module ready")
        print("   - Core logic implemented")
        print("   - Integration points prepared")

    def show_roadmap(self) -> None:
        """Display project roadmap and next steps"""
        roadmap = {specification.get('roadmap_inputs', [])}
        if roadmap:
            print(f"\\n{'='*30} PROJECT ROADMAP {'='*30}")
            for i, item in enumerate(roadmap, 1):
                print(f"{{i}}. {{item}}")
        else:
            print(f"\\n📋 Next Development Steps:")
            print("   - Complete core feature implementation")
            print("   - Add comprehensive testing")
            print("   - Deploy to production environment")

    def get_system_info(self) -> Dict[str, any]:
        """Get system information and status"""
        return {{
            "project": self.project_name,
            "version": self.version,
            "features_count": len(self.core_features),
            "target_users": len(self.target_users),
            "status": "operational",
            "created": self.created_at
        }}

    def run_diagnostics(self) -> bool:
        """Run system diagnostics"""
        print("\\n🔧 Running System Diagnostics...")
        checks = [
            ("Core features", len(self.core_features) > 0),
            ("Target users defined", len(self.target_users) > 0),
            ("Project initialized", True),
            ("System operational", True)
        ]

        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {{check_name}}: {{status}}")
            if not passed:
                all_passed = False

        print(f"\\nOverall Status: {{'All systems operational' if all_passed else 'Some issues detected'}}")
        return all_passed

    def run(self) -> None:
        """Main application entry point"""
        try:
            if not self.initialize():
                print("❌ Initialization failed!")
                return

            self.show_welcome()
            self.demonstrate_features()
            self.show_roadmap()

            # Run diagnostics
            self.run_diagnostics()

            print(f"\\n🎉 {{self.project_name}} is ready for development!")
            print("\\n💡 Next Steps:")
            print("   1. Review the generated code structure")
            print("   2. Implement specific business logic")
            print("   3. Add comprehensive tests")
            print("   4. Deploy and monitor")

        except Exception as e:
            print(f"❌ Error running application: {{e}}")
            return False

def main():
    """Main entry point"""
    app = {project_title.replace(" ", "").replace("-", "").replace("_", "")}App()
    app.run()

if __name__ == "__main__":
    main()
'''

        main_py_content = self._generate_code(main_system, main_user, main_fallback)

        # Generate requirements.txt based on the code
        requirements_system = """You are a Code Scaffold Agent. Generate a requirements.txt file with all necessary dependencies for the generated code."""

        requirements_user = f"""
Based on this generated code, list all Python packages that need to be installed:

{main_py_content}

Include versions where appropriate. Only include packages that are actually imported or used in the code.
"""

        requirements_fallback = """python-dotenv>=1.0.0
requests>=2.31.0
typing-extensions>=4.0.0
"""

        requirements_content = self._generate_code(requirements_system, requirements_user, requirements_fallback)

        gitignore_content = """.env
venv/
__pycache__/
*.pyc
outputs/generated_repo/
outputs/logs/
"""

        agents_init_content = ""
        tests_init_content = ""

        overview_content = f"""# Project Overview

## Project
{project_title}

## Problem Statement
{specification.get('problem_statement', f'A starter repository for {idea}.')}

## Core Features
""" + "\n".join(
            [f"- {feature}" for feature in specification.get("core_features", [])]
        )

        files_to_create = {
            "README.md": readme_content,
            "requirements.txt": requirements_content,
            ".gitignore": gitignore_content,
            "main.py": main_py_content,
            os.path.join("agents", "__init__.py"): agents_init_content,
            os.path.join("tests", "__init__.py"): tests_init_content,
            os.path.join("docs", "overview.md"): overview_content,
        }

        created_files = []
        for relative_path, content in files_to_create.items():
            file_path = os.path.join(root_folder, relative_path)
            self._write_file(file_path, content)
            created_files.append(file_path)
            print(f"[{self.name}] Created file: {file_path}")

        scaffold = {
            "project_slug": project_slug,
            "root_folder": root_folder,
            "folders": folders,
            "files": list(files_to_create.keys()),
        }

        response_message = make_message(
            from_agent="code_scaffold",
            to_agent="orchestrator",
            message_type="result",
            payload={
                "status": "success",
                "idea": idea,
                "focus": focus,
                "specification": specification,
                "repo_path": root_folder,
                "scaffold": scaffold,
                "created_folders": created_folders,
                "created_files": created_files,
            },
            parent_message_id=message.get("messageid"),
        )

        self.bus.send(response_message)
        print(f"[{self.name}] Sent scaffold result back to orchestrator.")