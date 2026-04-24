# Contributing to Mobile Phone Website

Thank you for your interest in contributing to **Mobile Phone Website**! 🎉

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
git clone https://github.com/your-username/mobile-phone-website.git
cd mobile-phone-website
```

3. Set up the development environment:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## 🔄 Development Workflow

### 1. Choose an Issue

- Check [GitHub Issues](https://github.com/username/mobile-phone-website/issues) for open tasks
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
    """Calculate total price of items."""
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
        """Test class initialization."""
        obj = YourClass()
        assert obj.is_initialized

    def test_core_functionality(self):
        """Test main functionality."""
        obj = YourClass()
        result = obj.process_data(test_data)
        assert result is not None
        assert len(result) > 0

    @pytest.mark.parametrize("input_data,expected", [
        ({{"key": "value"}}, True),
        ({}, False),
    ])
    def test_edge_cases(self, input_data, expected):
        """Test edge cases with parametrized inputs."""
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

Thank you for contributing to Mobile Phone Website! 🚀
