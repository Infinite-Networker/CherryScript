# 📋 Changelog

All notable changes to **CherryScript** will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/) and the [Keep a Changelog](https://keepachangelog.com/) format.

> Format: `Added` | `Changed` | `Deprecated` | `Removed` | `Fixed` | `Security`

---

## [Unreleased]

### Added
- Stylish `README.md` redesign with badges, feature tables, and full syntax reference
- `CONTRIBUTING.md` with detailed development guidelines and commit conventions
- `CHANGELOG.md` for tracking version history
- `.github/ISSUE_TEMPLATE/` — bug report & feature request templates
- `.github/pull_request_template.md` — standardised PR checklist
- `.github/workflows/ci.yml` — GitHub Actions CI pipeline (Python 3.8–3.12 matrix)
- `docs/SYNTAX_GUIDE.md` — comprehensive language reference
- `examples/ml_pipeline.cherry` — end-to-end AutoML pipeline example
- `examples/data_analysis.cherry` — business intelligence & analytics example
- `examples/deploy_api.cherry` — model deployment walkthrough

---

## [1.0.0] — 2024-03-01

> 🎉 **Initial public release** — the foundation of CherryScript.

### Added
- **Core Language**
  - Variable declarations: `var` (mutable) and `let` (constant-intent)
  - All primitive types: string, number, boolean, array, dict
  - String interpolation with backtick syntax: `` `Hello ${name}` ``
  - Arithmetic operators: `+`, `-`, `*`, `/`, `%`
  - Augmented assignment: `+=`, `-=`, `*=`, `/=`, `%=`
  - Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
  - Logical operators: `&&`, `||`, `!`

- **Control Flow**
  - `if` / `else if` / `else` blocks
  - `for item in collection` loop
  - C-style `for (init; condition; step)` loop
  - `while (condition)` loop

- **Functions**
  - `fn name(params) { body }` definitions
  - `return` statement
  - Closures and recursive functions

- **Built-in Functions**
  - `print(...)` — stdout output
  - `len(x)` — length of string/array/dict
  - `range(n)` / `range(start, end)` — integer ranges
  - `sum(arr)`, `min(arr)`, `max(arr)` — numeric aggregates
  - `format(value, spec)` — Python-style format strings
  - `append(arr, item)` — mutate array in place
  - `keys(dict)` — dict key list
  - `time()` — epoch timestamp

- **Database Adapter**
  - `connect(dsn)` → `Database` object
  - `db.query(sql)` → list of row dicts
  - MySQL and PostgreSQL DSN support

- **H2O AutoML Integration**
  - `h2o.frame(data)` → `Frame` object
  - `h2o.preprocess(frame)` → preprocessed Frame
  - `h2o.automl(frame, target)` → trained `Model` object
  - `model.predict(frame)` → predictions list
  - `model.leaderboard` — ranked model list
  - `model.name`, `model.model_type` properties

- **Model Deployment**
  - `deploy(model, url)` → `Endpoint` object (FastAPI)
  - `undeploy(endpoint, timeout)` — graceful shutdown
  - Auto-generated `/health` endpoint

- **Multi-Language Export**
  - `export to python` — generate Python model wrapper
  - `export to php` — generate PHP predictor class
  - `export to java` — generate Java predictor class

- **CLI**
  - `cherryscript <file.cherry>` — run a script file
  - `cherryscript -c "..."` — run inline code
  - `cherryscript --interactive` / `-i` — REPL mode
  - `cherryscript --version` — show version

- **Package**
  - `pyproject.toml` with optional dependency groups: `db`, `ml`, `deploy`, `dev`, `all`
  - `cherryscript` console script entry point
  - `requirements.txt` with pinned dependencies

- **Project Scaffolding**
  - `examples/test.cherry` — comprehensive test & demo script
  - `docs/ROADMAP.md` — 2024–2025 development timeline
  - `tests/test_parser.py` and `tests/test_interpreter.py`
  - MIT License

---

## Version Numbering Policy

| Version | Meaning |
|---------|---------|
| **MAJOR** (X.0.0) | Breaking changes to language syntax or runtime API |
| **MINOR** (1.X.0) | New features, backwards-compatible |
| **PATCH** (1.0.X) | Bug fixes, security patches, docs |

---

## Links

- [Full Roadmap](./docs/ROADMAP.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [GitHub Releases](https://github.com/Infinite-Networker/CherryScript/releases)
- [Compare versions](https://github.com/Infinite-Networker/CherryScript/compare)

[Unreleased]: https://github.com/Infinite-Networker/CherryScript/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Infinite-Networker/CherryScript/releases/tag/v1.0.0
