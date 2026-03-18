# 🤝 Contributing to CherryScript

<div align="center">

[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-FF69B4?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Infinite-Networker/CherryScript/pulls)
[![Code of Conduct](https://img.shields.io/badge/Contributor%20Covenant-2.1-E91E8C?style=for-the-badge)](https://www.contributor-covenant.org/)
[![Good First Issues](https://img.shields.io/github/issues/Infinite-Networker/CherryScript/good%20first%20issue?style=for-the-badge&color=00C853&logo=github)](https://github.com/Infinite-Networker/CherryScript/labels/good-first-issue)

*Thank you for your interest in making CherryScript better!* 🍒

</div>

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Ways to Contribute](#-ways-to-contribute)
- [Development Setup](#-development-setup)
- [Project Structure](#-project-structure)
- [Coding Standards](#-coding-standards)
- [Testing](#-testing)
- [Submitting a Pull Request](#-submitting-a-pull-request)
- [Issue Labels](#-issue-labels)
- [Commit Message Format](#-commit-message-format)
- [Release Process](#-release-process)

---

## 🧭 Code of Conduct

By participating in this project you agree to abide by our [Code of Conduct](./CODE_OF_CONDUCT.md). We are committed to providing a welcoming and harassment-free experience for everyone.

**TL;DR** — Be kind, be constructive, be collaborative. 💜

---

## 🌟 Ways to Contribute

You don't have to write code to contribute! Here are many ways to help:

| Area | Examples |
|------|---------|
| 🐛 **Bug Reports** | Find and report bugs with detailed reproduction steps |
| 💡 **Feature Requests** | Propose new language features or integrations |
| 📖 **Documentation** | Fix typos, improve guides, add examples |
| 🧪 **Testing** | Write tests, improve coverage, performance tests |
| 🔤 **Language Design** | Suggest syntax improvements or new constructs |
| 🔌 **Adapters** | Add new database or ML framework adapters |
| 🌍 **Community** | Answer questions, write blog posts, give talks |

---

## 🛠️ Development Setup

### 1. Fork & Clone

```bash
# Fork on GitHub first, then:
git clone https://github.com/<your-username>/CherryScript.git
cd CherryScript
```

### 2. Create a Feature Branch

```bash
# Always branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
# or: fix/bug-description, docs/what-you-documented
```

### 3. Set Up Python Environment

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate.bat     # Windows

# Install with all development dependencies
pip install -e ".[dev,ml,db,deploy]"
```

### 4. Verify Setup

```bash
# Run all tests
pytest tests/ -v

# Check the CLI works
cherryscript --version
cherryscript -c 'print("🍒 Dev environment ready!")'
```

---

## 📁 Project Structure

```
CherryScript/
├── cherryscript/
│   ├── __init__.py         ← Version bump goes here
│   ├── parser.py           ← Tokenizer & statement splitter
│   ├── cli/
│   │   └── __init__.py     ← CLI & REPL logic
│   └── runtime/
│       ├── interpreter.py  ← Core expression & statement evaluator
│       └── adapters.py     ← Database, H2O, Deploy adapters
├── tests/
│   ├── test_parser.py      ← Parser unit tests
│   └── test_interpreter.py ← Interpreter unit tests
├── examples/               ← .cherry example scripts
├── docs/                   ← Markdown documentation
└── pyproject.toml          ← Package metadata & deps
```

**Key files to understand first:**
1. `cherryscript/parser.py` — how source text is split into statements
2. `cherryscript/runtime/interpreter.py` — how each statement is evaluated
3. `cherryscript/runtime/adapters.py` — how DB/ML/Deploy calls work

---

## 🎨 Coding Standards

We use **Black** for formatting and **Flake8** for linting.

```bash
# Format your code before committing
black cherryscript/ tests/

# Lint check
flake8 cherryscript/ tests/ --max-line-length=100

# Type check (optional but appreciated)
mypy cherryscript/ --ignore-missing-imports
```

### Style Rules

- **Line length:** 100 characters max
- **Docstrings:** All public functions and classes must have docstrings
- **Type hints:** Encouraged on new public APIs
- **Comments:** Explain *why*, not *what*
- **No magic numbers:** Use named constants

```python
# ✅ Good
MAX_LEADERBOARD_SIZE = 10

def segment_customers(customers: list, threshold: float = 2000.0) -> dict:
    """Split customers into VIP and standard segments.

    Args:
        customers: List of customer dicts with 'total_spent' key.
        threshold: Minimum spend to qualify as VIP. Defaults to 2000.0.

    Returns:
        Dict with 'vip' and 'standard' keys.
    """
    ...

# ❌ Bad
def f(l, t=2000):
    # loop through list
    ...
```

---

## 🧪 Testing

We use **pytest** with **pytest-cov** for coverage.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=cherryscript --cov-report=term-missing

# Run a specific test file
pytest tests/test_interpreter.py -v

# Run tests matching a keyword
pytest tests/ -k "test_variables" -v
```

### Writing Tests

Every new feature or bug fix **must** include a test:

```python
# tests/test_interpreter.py
import pytest
from cherryscript.runtime.interpreter import Runtime

def test_variable_assignment():
    rt = Runtime()
    rt.run('var x = 42')
    assert rt.env['x'] == 42

def test_function_definition_and_call():
    rt = Runtime()
    rt.run('fn double(n) { return n * 2 }')
    rt.run('var result = double(7)')
    assert rt.env['result'] == 14
```

**Coverage target:** ≥ 80% on new code.

---

## 🔀 Submitting a Pull Request

1. **Ensure tests pass locally:**
   ```bash
   pytest tests/ -v --cov=cherryscript
   ```

2. **Format & lint your code:**
   ```bash
   black cherryscript/ tests/
   flake8 cherryscript/ tests/ --max-line-length=100
   ```

3. **Update documentation** if your change affects user-facing behaviour.

4. **Add an entry to [`CHANGELOG.md`](./CHANGELOG.md)** under `Unreleased`.

5. **Push your branch and open a PR:**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then visit GitHub and click **"Compare & pull request"**.

6. **Fill out the PR template** completely — the more context you provide, the faster we can review!

---

## 🏷️ Issue Labels

| Label | Meaning |
|-------|---------|
| `bug` 🐛 | Something is broken |
| `enhancement` ✨ | New feature or improvement |
| `good-first-issue` 🌱 | Great for new contributors |
| `help-wanted` 🙋 | We need community help |
| `documentation` 📖 | Docs-only change |
| `question` ❓ | Needs clarification |
| `wontfix` 🚫 | Out of scope or by design |
| `duplicate` 🔁 | Already tracked |

---

## 📝 Commit Message Format

We follow the **Conventional Commits** spec:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types

| Type | When to Use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding/fixing tests |
| `refactor` | Code change with no feature/fix |
| `perf` | Performance improvement |
| `chore` | Build, CI, dependency updates |
| `style` | Formatting, whitespace |

### Examples

```bash
feat(interpreter): add async/await statement support
fix(parser): handle nested backtick string interpolation
docs(readme): add database integration examples
test(runtime): add coverage for model.predict() edge cases
chore(ci): update Python matrix to include 3.12
```

---

## 🚀 Release Process

_(For maintainers)_

1. Update `__version__` in `cherryscript/__init__.py`
2. Update `CHANGELOG.md` — move `Unreleased` → `vX.Y.Z - YYYY-MM-DD`
3. Commit: `git commit -m "chore(release): bump version to vX.Y.Z"`
4. Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Push: `git push origin main --tags`
6. GitHub Actions will publish to PyPI automatically

---

<div align="center">

**Questions?** Open a [Discussion](https://github.com/Infinite-Networker/CherryScript/discussions) or drop a comment on any issue.

*Happy coding with 🍒 CherryScript!*

</div>
