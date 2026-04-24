import os
from datetime import datetime
from models import make_message
from tools import call_groq_llm


class DocumentationAgent:
    def __init__(self, bus):
        self.name = "documentation"
        self.bus = bus

    def _safe_slug(self, text: str) -> str:
        slug = text.lower().strip()
        slug = slug.replace(" ", "-")
        slug = "".join(ch for ch in slug if ch.isalnum() or ch in ["-", "_"])
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or "generated-project"

    def _write_file(self, repo_path, filename, content):
        file_path = os.path.join(repo_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def _generate_doc(self, system_prompt, user_prompt, fallback_text):
        try:
            return call_groq_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
        except Exception as e:
            print(f"[{self.name}] Groq failed while generating doc: {e}")
            return fallback_text

    def process(self, message):
        print(f"\n[{self.name}] Received message:")
        print(message)

        payload = message.get("payload", {})
        idea = payload.get("idea", "open source project")
        focus = payload.get("focus", "generate project documentation")
        specification = payload.get("specification", {})
        repo_path = payload.get("repo_path", "")
        scaffold = payload.get("scaffold", {})
        revision_round = payload.get("revision_round", 0)
        revision_notes = payload.get("revision_notes", "")
        previous_generated_docs = payload.get("generated_docs", {})

        if not repo_path or not os.path.exists(repo_path):
            print(f"[{self.name}] Invalid repo path: {repo_path}")

            response = make_message(
                from_agent="documentation",
                to_agent="orchestrator",
                message_type="documentation_completed",
                payload={
                    "status": "failed",
                    "idea": idea,
                    "focus": focus,
                    "specification": specification,
                    "repo_path": repo_path,
                    "scaffold": scaffold,
                    "generated_docs": {},
                    "created_files": [],
                    "revision_round": revision_round,
                    "error": "Invalid repo path"
                },
                parent_message_id=message.get("messageid")
            )
            self.bus.send(response)
            return

        project_title = specification.get("project_title", idea.title())
        project_slug = self._safe_slug(idea)
        problem_statement = specification.get("problem_statement", f"A project for {idea}")
        core_features = specification.get("core_features", [])
        target_users = specification.get("target_users", [])
        repo_goals = specification.get("repo_goals", [])
        roadmap_inputs = specification.get("roadmap_inputs", [])

        features_text = "\n".join([f"- {feature}" for feature in core_features]) or "- Starter feature set"
        users_text = "\n".join([f"- {user}" for user in target_users]) or "- Developers"
        goals_text = "\n".join([f"- {goal}" for goal in repo_goals]) or "- Clean onboarding"
        roadmap_text = "\n".join([f"- {item}" for item in roadmap_inputs]) or "- Initial project launch"

        revision_context = ""
        if revision_round > 0 and revision_notes:
            revision_context = f"""
Revision round: {revision_round}

Please revise the documentation based on the following feedback:
{revision_notes}

Also improve clarity, completeness, contributor-readiness, and realism of the generated docs.
"""

        generated_docs = dict(previous_generated_docs) if previous_generated_docs else {}
        created_files = []

        # README.md
        readme_system = """
You are a Documentation Agent for an open-source project launch system.
Write a professional README.md for a newly generated open-source software project.
Keep it practical, clean, and GitHub-ready.
"""
        readme_user = f"""
Project title: {project_title}
Idea: {idea}
Problem statement: {problem_statement}

Target users:
{users_text}

Core features:
{features_text}

Repository goals:
{goals_text}

{revision_context}

Write a complete README.md with:
- project title
- overview
- problem it solves
- key features
- intended users
- setup instructions
- usage section
- contribution invitation
"""
        readme_fallback = f"""# {project_title}

## 🎯 Overview

{problem_statement}

This project addresses key challenges in {', '.join(target_users) if target_users else 'modern software development'} by providing a comprehensive solution with enterprise-grade features and developer-friendly tooling.

## ✨ Key Features

{features_text}

### 🚀 Core Capabilities
- **Production Ready**: Built with scalability and reliability in mind
- **Developer Experience**: Comprehensive tooling and clear documentation
- **Extensible Architecture**: Modular design for easy customization
- **Quality Assurance**: Built-in testing and validation frameworks

## 👥 Intended Users

{users_text}

## 🏗️ Architecture

### System Components
- **Core Engine**: Handles primary business logic and data processing
- **API Layer**: RESTful/GraphQL interfaces for seamless integration
- **Data Management**: Robust data storage and retrieval systems
- **User Interface**: Intuitive dashboards and management consoles

### Technology Stack
- **Backend**: Python-based microservices architecture
- **Frontend**: Modern web technologies with responsive design
- **Database**: Scalable data storage solutions
- **DevOps**: Containerized deployment with CI/CD pipelines

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Git for version control

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_slug}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from {project_title.lower().replace(' ', '_').replace('-', '_')} import {project_title.replace(' ', '').replace('-', '')}App

# Initialize the application
app = {project_title.replace(' ', '').replace('-', '')}App()

# Run the application
app.run()
```

### Configuration

Create a `.env` file in the project root:

```env
# Application Settings
APP_NAME={project_title}
APP_VERSION=1.0.0
DEBUG=true

# Database Configuration
DATABASE_URL=sqlite:///app.db

# API Keys (if applicable)
API_KEY=your-api-key-here
```

## 📖 Usage Examples

### Basic Operations
```python
# Example: Core feature demonstration
app = {project_title.replace(' ', '').replace('-', '')}App()
app.initialize()
app.demonstrate_features()
```

### Advanced Configuration
```python
# Custom configuration
config = {{
    "features": {core_features},
    "target_users": {target_users},
    "repo_goals": {repo_goals}
}}

app.configure(config)
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_core.py
```

## 📊 Project Roadmap

{roadmap_text}

### Current Status
- ✅ Repository scaffolding complete
- ✅ Core architecture implemented
- 🔄 Feature development in progress
- 📋 Documentation framework established
- 🔄 Testing framework planned
- 📋 CI/CD pipeline planned

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the open-source community
- Special thanks to all contributors and early adopters
"""

        # Generate and write README.md
        readme_content = self._generate_doc(readme_system, readme_user, readme_fallback)
        readme_path = self._write_file(repo_path, "README.md", readme_content)
        generated_docs["README.md"] = readme_content
        created_files.append(readme_path)

        # CONTRIBUTING.md
        contributing_system = """
You are a Documentation Agent for an open-source project launch system.
Write a practical CONTRIBUTING.md file for a new open-source project.
"""
        contributing_user = f"""
Project title: {project_title}
Core features:
{features_text}

{revision_context}

Write CONTRIBUTING.md covering:
- how to fork and clone
- branch naming
- pull request expectations
- code style expectations
- issue reporting guidance
"""
        contributing_fallback = f"""# Contributing to {project_title}

Thank you for your interest in contributing to **{project_title}**! 🎉

We welcome contributions from developers of all skill levels and backgrounds. This document provides guidelines and information to help you get started with contributing to our project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other community members
- Help create a positive environment

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Fork and Clone

1. Fork this repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/your-username/{project_slug}.git
cd {project_slug}
```

3. Set up the development environment:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## 🔄 Development Workflow

### 1. Choose an Issue

- Check [GitHub Issues](https://github.com/username/{project_slug}/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### Branch Naming Convention

- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation updates
- `refactor/description`: Code refactoring
- `test/description`: Testing improvements

### 3. Make Changes

- Write clear, focused commits
- Test your changes thoroughly
- Follow the code standards below
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=src --cov-report=html

# Run specific tests
python -m pytest tests/test_specific_feature.py

# Run linting
flake8 src/
black --check src/
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: add user authentication feature

- Implement login/logout functionality
- Add password hashing
- Create user session management
- Add input validation

Closes #123"
```

### 6. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
# - Use a clear title
# - Provide detailed description
# - Link related issues
# - Request review from maintainers
```

## 📏 Code Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with some additional guidelines:

```python
# ✅ Good
def calculate_total(items: List[Dict[str, float]]) -> float:
    \"""Calculate total price of items.\"""
    return sum(item["price"] * item.get("quantity", 1) for item in items)

# ❌ Avoid
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item.get('quantity', 1)
    return total
```

### Key Guidelines

- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Write comprehensive docstrings using Google style
- **Naming**: Use descriptive names (variables, functions, classes)
- **Imports**: Group imports (standard library, third-party, local)
- **Line Length**: Keep lines under 88 characters (Black formatter default)
- **Error Handling**: Use specific exceptions, not bare `except:`

### Code Formatting

We use automated formatters to maintain consistency:

```bash
# Format code
black .

# Sort imports
isort .

# Check style
flake8 .
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
pip install pre-commit
pre-commit install
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests
├── integration/         # Integration tests
├── e2e/                 # End-to-end tests
├── fixtures/            # Test data
└── conftest.py         # Test configuration
```

### Writing Tests

```python
import pytest
from src.your_module import YourClass

class TestYourClass:
    def test_initialization(self):
        \"""Test class initialization.\"""
        obj = YourClass()
        assert obj.is_initialized

    def test_core_functionality(self):
        \"""Test main functionality.\"""
        obj = YourClass()
        result = obj.process_data(test_data)
        assert result is not None
        assert len(result) > 0

    @pytest.mark.parametrize("input_data,expected", [
        ({{{{"key": "value"}}}}, True),
        ({{}}, False),
    ])
    def test_edge_cases(self, input_data, expected):
        \"""Test edge cases with parametrized inputs.\"""
        obj = YourClass()
        assert obj.validate(input_data) == expected
```

### Test Coverage

Maintain test coverage above 80%:

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View report in browser
open htmlcov/index.html
```

## 📚 Documentation

### Code Documentation

- Use docstrings for all public functions, classes, and modules
- Include parameter descriptions and return value information
- Provide usage examples where helpful

### Project Documentation

- Keep README.md up to date
- Update docs/ for major features
- Include API documentation for web services
- Maintain changelog for releases

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, please include:

- **Clear Title**: Summarize the issue
- **Steps to Reproduce**: Numbered steps to reproduce the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Screenshots/Logs**: If applicable

### Feature Requests

For new features, please provide:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Additional Context**: Screenshots, examples, etc.

## 🔄 Pull Request Process

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] PR description explains changes
- [ ] Related issues linked

### Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: Maintainers review code quality and logic
3. **Testing**: Additional testing may be requested
4. **Approval**: PR approved and merged
5. **Deployment**: Changes deployed to production

### PR Template

Please use this template for pull requests:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran and how to reproduce.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guidelines
```

## 🌟 Community

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and community discussion
- **Pull Requests**: For code contributions

### Recognition

Contributors are recognized in our README.md and at project events. We believe in celebrating all contributions, big and small!

Thank you for contributing to {project_title}! 🚀
"""

        contributing_content = self._generate_doc(contributing_system, contributing_user, contributing_fallback)
        contributing_path = self._write_file(repo_path, "CONTRIBUTING.md", contributing_content)
        generated_docs["CONTRIBUTING.md"] = contributing_content
        created_files.append(contributing_path)

        # ROADMAP.md
        roadmap_system = """
You are a Documentation Agent for an open-source project launch system.
Write a practical ROADMAP.md for a newly launched project.
"""
        roadmap_user = f"""
Project title: {project_title}
Roadmap inputs:
{roadmap_text}

{revision_context}

Write ROADMAP.md with:
- short-term goals
- medium-term goals
- long-term goals
- contributor opportunities
"""
        roadmap_fallback = f"""# {project_title} Product Roadmap

## 🎯 Vision & Mission

**Vision**: {problem_statement}

**Mission**: Deliver a robust, scalable solution that meets the needs of {', '.join(target_users) if target_users else 'our target users'} while maintaining high standards of code quality and community engagement.

## 📊 Current Status

- ✅ **Repository Scaffolding**: Complete - Project structure established
- ✅ **Core Architecture**: Implemented - Basic framework in place
- 🔄 **Feature Development**: In Progress - Core features being built
- 📋 **Documentation**: In Progress - Setup and contribution guides created
- 🔄 **Testing Framework**: Planned - Unit and integration tests needed
- 📋 **CI/CD Pipeline**: Planned - Automated testing and deployment

## 🗺️ Roadmap Overview

### Phase 1: Foundation (Current - Next 2 Weeks)
**Goal**: Establish solid project foundation and basic functionality

#### ✅ Completed
- [x] Project repository setup
- [x] Basic code structure and architecture
- [x] Initial documentation framework
- [x] Development environment configuration

#### 🔄 In Progress
- [ ] Core feature implementation
- [ ] Basic testing framework
- [ ] API documentation
- [ ] User authentication system

#### 📋 Planned
- [ ] Database schema design
- [ ] User interface wireframes
- [ ] Performance optimization
- [ ] Security audit

### Phase 2: Core Features (Weeks 3-8)
**Goal**: Implement core functionality and establish product-market fit

#### 📋 Planned Features
- [ ] Advanced search and filtering
- [ ] User dashboard and analytics
- [ ] Integration with third-party services
- [ ] Mobile-responsive design
- [ ] Performance monitoring
- [ ] Automated backup systems

### Phase 3: Enhancement & Scale (Weeks 9-16)
**Goal**: Enhance user experience and prepare for scaling

#### 📋 Planned Features
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Advanced user permissions
- [ ] API rate limiting
- [ ] Real-time notifications
- [ ] Advanced caching strategies

### Phase 4: Enterprise & Ecosystem (Weeks 17-26)
**Goal**: Enterprise features and ecosystem development

#### 📋 Planned Features
- [ ] Enterprise SSO integration
- [ ] Advanced audit logging
- [ ] Custom workflow builder
- [ ] Plugin architecture
- [ ] Advanced API management
- [ ] White-label solutions

## 🎯 Key Milestones

### Q1 2024: Foundation
- Complete core feature set
- Reach 100 beta users
- Establish development workflow
- Implement basic CI/CD

### Q2 2024: Growth
- Launch public beta
- Implement advanced features
- Grow to 1000 active users
- Establish community governance

### Q3 2024: Scale
- Launch stable release
- Implement enterprise features
- Reach 10,000 users
- Establish partner ecosystem

### Q4 2024: Maturity
- Advanced enterprise features
- Global expansion
- 50,000+ users
- Sustainable business model

## 📈 Success Metrics

### User Metrics
- **Daily Active Users**: Track engagement
- **User Retention**: 30-day retention rate > 70%
- **Feature Adoption**: % of users using key features
- **Support Tickets**: < 5% of user base

### Technical Metrics
- **Uptime**: 99.9% service availability
- **Performance**: < 2s average response time
- **Error Rate**: < 0.1% error rate
- **Test Coverage**: > 85% code coverage

### Business Metrics
- **Revenue Growth**: Monthly recurring revenue
- **Customer Acquisition Cost**: < $50 per customer
- **Customer Lifetime Value**: > $500 per customer
- **Net Promoter Score**: > 50

## 🚧 Risks & Mitigations

### Technical Risks
- **Scalability Issues**: Implement performance monitoring and optimization
- **Security Vulnerabilities**: Regular security audits and penetration testing
- **Third-party Dependencies**: Diversify providers and implement fallbacks

### Market Risks
- **Competition**: Focus on unique value proposition and community building
- **Changing Requirements**: Agile development and regular user feedback
- **Regulatory Changes**: Stay informed and adapt compliance strategy

### Operational Risks
- **Team Scaling**: Implement documentation and onboarding processes
- **Burnout**: Maintain work-life balance and team morale
- **Funding**: Diversify revenue streams and maintain runway

## 🤝 How to Contribute

### For Developers
- **Core Features**: Help implement planned features
- **Testing**: Write comprehensive test suites
- **Documentation**: Improve developer documentation
- **Performance**: Optimize code and infrastructure

### For Designers
- **UI/UX**: Improve user interface and experience
- **Wireframes**: Create mockups for new features
- **Design System**: Maintain consistent design language
- **Accessibility**: Ensure WCAG compliance

### For DevOps
- **Infrastructure**: Improve deployment and scaling
- **Monitoring**: Implement comprehensive observability
- **Security**: Enhance security posture
- **Automation**: Streamline development workflow

### For Community Managers
- **Documentation**: Write user guides and tutorials
- **Support**: Help users with issues and questions
- **Marketing**: Promote the project and grow community
- **Events**: Organize meetups and conferences

## 📞 Contact & Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and community discussion
- **Email**: For security issues and sensitive matters
- **Slack/Discord**: For real-time community support

## 🙏 Acknowledgments

This roadmap represents our vision for {project_title}. We welcome feedback and contributions from the community to help us achieve these goals. Together, we can build something amazing!

Last updated: {datetime.now().strftime('%Y-%m-%d')}
"""

        roadmap_content = self._generate_doc(roadmap_system, roadmap_user, roadmap_fallback)
        roadmap_path = self._write_file(repo_path, "ROADMAP.md", roadmap_content)
        generated_docs["ROADMAP.md"] = roadmap_content
        created_files.append(roadmap_path)

        # ONBOARDING.md
        onboarding_system = """
You are a Documentation Agent for an open-source project launch system.
Write a practical ONBOARDING.md file for new contributors.
"""
        onboarding_user = f"""
Project title: {project_title}
Core features:
{features_text}

{revision_context}

Write ONBOARDING.md covering:
- quick start guide
- development setup
- first contribution steps
- getting help
"""
        onboarding_fallback = f"""# Welcome to {project_title}! 🎉

Welcome to the {project_title} project! This guide will help you get started as a contributor. Whether you're a seasoned developer or just getting started with open-source, we're excited to have you here.

## 🚀 Quick Start

### What is {project_title}?

{problem_statement}

{project_title} provides {', '.join(core_features) if core_features else 'powerful tools and features'} to help {', '.join(target_users) if target_users else 'developers and organizations'} build better software.

### Prerequisites

Before you begin, make sure you have:
- **Python 3.8+** installed
- **Git** for version control
- **A GitHub account**
- **A code editor** (we recommend VS Code)

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/{project_slug}.git
cd {project_slug}
```

### 2. Set Up Development Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if available)
pip install -r requirements-dev.txt
```

### 3. Verify Setup

```bash
# Run a quick test
python -c "import sys; print(f'Python version: {{sys.version}}')"

# Check that everything is working
python main.py --help
```

### 4. Set Up Pre-commit Hooks (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## 🎯 Your First Contribution

### Step 1: Find an Issue

1. Visit our [GitHub Issues](https://github.com/username/{project_slug}/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to let others know you're working on it

### Step 2: Create a Branch

```bash
# Create a new branch for your work
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### Step 3: Make Changes

1. **Write Code**: Implement your changes following our [Contributing Guide](CONTRIBUTING.md)
2. **Write Tests**: Add tests for your changes
3. **Update Documentation**: Update docs if needed
4. **Test Locally**: Make sure everything works

```bash
# Run tests
python -m pytest

# Run linting
flake8 src/
black --check src/
```

### Step 4: Commit and Push

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: add awesome new feature

- Add feature implementation
- Add comprehensive tests
- Update documentation

Closes #123"

# Push to your fork
git push origin feature/your-feature-name
```

### Step 5: Create a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Write a clear description of your changes
5. Link the issue you're fixing
6. Request review from maintainers

## 📚 Learning Resources

### Codebase Overview

```
{project_slug}/
├── src/                    # Main source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── scripts/               # Utility scripts
├── requirements.txt       # Python dependencies
└── README.md             # Project overview
```

### Key Files to Know

- **`main.py`**: Entry point of the application
- **`src/core/`**: Core business logic
- **`tests/`**: Test files and fixtures
- **`docs/`**: Project documentation

### Development Workflow

1. **Local Development**: Make changes and test locally
2. **Code Review**: Submit PR and get feedback
3. **Continuous Integration**: Automated tests run on every PR
4. **Merge**: Changes are merged after approval

## 🆘 Getting Help

### Where to Ask Questions

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For general questions and community discussion
- **Documentation**: Check our docs first

### How to Ask Good Questions

When asking for help, please include:
- What you're trying to do
- What you've tried so far
- Error messages or unexpected behavior
- Your environment (OS, Python version, etc.)

### Example: Good Question

```
I'm trying to add a new API endpoint for user management.

I've added the route in `src/api/routes.py` and the handler in `src/api/handlers.py`, but I'm getting a 404 error when I test it.

Here's my code:
```python
# routes.py
@app.route('/api/users', methods=['GET'])
def get_users():
    return UserHandler.get_all_users()
```

Environment: Python 3.9, Windows 11
```

## 🎉 Next Steps

### Level 1: Getting Comfortable
- [ ] Set up your development environment
- [ ] Run the test suite
- [ ] Make a small documentation change
- [ ] Submit your first pull request

### Level 2: Contributing Code
- [ ] Fix a small bug
- [ ] Add a test for existing functionality
- [ ] Implement a small feature
- [ ] Review someone else's pull request

### Level 3: Advanced Contributions
- [ ] Implement a major feature
- [ ] Refactor existing code
- [ ] Improve performance
- [ ] Mentor new contributors

## 🌟 Recognition & Impact

Your contributions matter! Here's how we recognize contributors:

- **GitHub Contributors**: Listed in our README
- **Pull Request Merges**: Your changes in the codebase
- **Issue Resolutions**: Problems solved for users
- **Community Building**: Helping others learn and grow

## 📞 Stay Connected

- **Follow** our GitHub repository for updates
- **Watch** issues you're interested in
- **Join** GitHub Discussions for community chat
- **Star** the repo if you find it useful!

## 🙏 Thank You

Thank you for your interest in contributing to {project_title}! Your contributions help make this project better for everyone. We appreciate your time and effort.

If you have any questions or need help, don't hesitate to ask. We're here to support you! 🚀

---

*This onboarding guide is living documentation. Help us improve it by submitting suggestions!*
"""

        onboarding_content = self._generate_doc(onboarding_system, onboarding_user, onboarding_fallback)
        onboarding_path = self._write_file(repo_path, "ONBOARDING.md", onboarding_content)
        generated_docs["ONBOARDING.md"] = onboarding_content
        created_files.append(onboarding_path)

        response = make_message(
            from_agent="documentation",
            to_agent="orchestrator",
            message_type="documentation_completed",
            payload={
                "status": "success",
                "idea": idea,
                "focus": focus,
                "specification": specification,
                "repo_path": repo_path,
                "scaffold": scaffold,
                "generated_docs": generated_docs,
                "created_files": created_files,
                "revision_round": revision_round
            },
            parent_message_id=message.get("messageid")
        )
        self.bus.send(response)
        print(f"[{self.name}] Sent documentation result back to orchestrator.")