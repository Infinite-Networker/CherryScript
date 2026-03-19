<div align="center">

<!-- Banner -->
<img src="https://github.com/Infinite-Networker/CherryScript/blob/67b1d33104b4689e918433ccf99e49d76500fbf9/Resize%20image%20project.png" alt="CherryScript Banner" width="320"/>

<br/>

<!-- Title -->
# 🍒 CherryScript

### *The scripting language built for Data Science, Automation & AI — at the speed of thought.*

<br/>

<!-- Badges Row 1 -->
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-E91E8C?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](./LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-FF6B9D?style=for-the-badge&logo=semver&logoColor=white)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/Status-Active-00C853?style=for-the-badge&logo=statuspage&logoColor=white)](https://github.com/Infinite-Networker/CherryScript)

<!-- Badges Row 2 -->
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-FF69B4?style=for-the-badge&logo=github&logoColor=white)](./CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/Infinite-Networker/CherryScript?style=for-the-badge&logo=starship&logoColor=white&color=FFD700)](https://github.com/Infinite-Networker/CherryScript/stargazers)
[![Issues](https://img.shields.io/github/issues/Infinite-Networker/CherryScript?style=for-the-badge&logo=github&logoColor=white&color=FF6B6B)](https://github.com/Infinite-Networker/CherryScript/issues)

<br/>

<!-- Tagline divider -->
```
╔══════════════════════════════════════════════════════════════════╗
║   collect → process → predict → deploy  — in plain English.     ║
╚══════════════════════════════════════════════════════════════════╝
```

</div>

---

## 📖 Table of Contents

| | Section | Description |
|---|---|---|
| 🍒 | [What is CherryScript?](#-what-is-cherryscript) | Overview & philosophy |
| ✨ | [Feature Highlights](#-feature-highlights) | What you can do |
| ⚡ | [Quick Start](#-quick-start) | Up and running in 60 seconds |
| 🔤 | [Language Syntax](#-language-syntax) | Core language constructs |
| 🗄️ | [Database Integration](#️-database-integration) | MySQL / PostgreSQL |
| 🤖 | [AI & Machine Learning](#-ai--machine-learning) | H2O AutoML pipelines |
| 🚀 | [Model Deployment](#-model-deployment) | REST API in one line |
| 📦 | [Installation](#-installation) | Full setup guide |
| 🗺️ | [Roadmap](#️-roadmap) | What's coming next |
| 🤝 | [Contributing](#-contributing) | Join the community |
| 📄 | [License](#-license) | MIT |

---

## 🍒 What is CherryScript?

> **CherryScript** is an expressive, human-readable scripting language designed to unify **data collection**, **ML pipelines**, and **AI model deployment** behind a single, clean syntax.

Instead of stitching together Python scripts, YAML configs, SQL queries, and deployment manifests — you write plain **CherryScript** and let the runtime handle the rest.

```cherry
// Three lines from raw data to live API 🚀
collect images from "dataset/raw"
process using "h2o_automl"
deploy model "vision_classifier" to "http://api.myapp.com/predict"
```

**Built by [Cherry Computer Ltd.](https://github.com/Infinite-Networker)** — making data science accessible, one line at a time.

---

## ✨ Feature Highlights

<table>
<tr>
<td width="50%">

### 🗃️ Data Collection
- Collect **images, text, CSV, JSON** from local paths or URLs
- Social media scraping adapters
- MySQL / PostgreSQL ingestion
- Unified `collect` keyword — no boilerplate

</td>
<td width="50%">

### ⚙️ Data Processing
- H2O AutoML integration out of the box
- Built-in **DataFrame operations** (filter, sort, join)
- Statistical functions: `sum`, `mean`, `std`, `percentile`
- One-liner preprocessing: `process using "h2o_automl"`

</td>
</tr>
<tr>
<td width="50%">

### 🤖 AI / ML Generation
- Train classification, regression & clustering models
- Auto-generate Python, PHP, or Java model wrappers
- Model leaderboard & performance comparison
- `h2o.automl()` — zero-config model selection

</td>
<td width="50%">

### 🚀 Instant Deployment
- Deploy any model as a **FastAPI REST endpoint**
- Health-check route auto-generated
- `undeploy()` for clean teardown
- One-line: `deploy(model, "http://0.0.0.0:8080/predict")`

</td>
</tr>
<tr>
<td width="50%">

### 🔌 Multi-Language Export
- Export trained models to **Python, PHP, Java**
- Ready-to-use code scaffolding
- Works with scikit-learn & H2O MOJO formats

</td>
<td width="50%">

### 🖥️ Developer Experience
- Interactive **REPL** mode (`cherryscript -i`)
- Clean **CLI** interface
- Friendly error messages
- `.cherry` syntax highlighting (VS Code extension coming soon)

</td>
</tr>
</table>

---

## ⚡ Quick Start

### Install in 30 seconds

```bash
# Clone the repository
git clone https://github.com/Infinite-Networker/CherryScript.git
cd CherryScript

# Install core package
pip install -e .

# Or with ML support
pip install -e ".[ml]"

# Verify install
cherryscript --version
```

### Your First Script

Create a file `hello.cherry`:

```cherry
// hello.cherry — your first CherryScript program

var name = "World"
var version = 1.0

print(`Hello, ${name}! Welcome to CherryScript v${version}`)

// Variables & types
var fruits  = ["cherry", "mango", "kiwi"]
var profile = { "lang": "CherryScript", "purpose": "AI Automation" }

// Loop
for fruit in fruits {
    print("🍒", fruit)
}

// Functions
fn greet(person) {
    return `Hi ${person}, ready to automate some AI? 🚀`
}

print(greet("Developer"))
```

Run it:

```bash
cherryscript hello.cherry
```

### Interactive REPL

```bash
cherryscript --interactive
# >>> var x = 42
# >>> print("The answer is", x)
# The answer is 42
```

---

## 🔤 Language Syntax

### Variables

```cherry
var message  = "Hello CherryScript"   // mutable
let PI       = 3.14159                // constant-intent
var score    = 98.6
var active   = true
var tags     = ["ml", "automation", "ai"]
var config   = { "debug": false, "max_epochs": 100 }
```

### Control Flow

```cherry
// if / else if / else
if (score >= 90) {
    print("🏆 Grade: A")
} else if (score >= 75) {
    print("✅ Grade: B")
} else {
    print("📚 Keep studying!")
}

// for-in loop
for tag in tags {
    print("Tag:", tag)
}

// while loop
var counter = 0
while (counter < 5) {
    print("Iteration:", counter)
    counter = counter + 1
}
```

### Functions

```cherry
fn calculate_accuracy(correct, total) {
    return (correct / total) * 100
}

fn classify_model(auc) {
    if (auc >= 0.95) { return "Excellent 🏆" }
    else if (auc >= 0.85) { return "Good ✅" }
    else { return "Needs Improvement ⚠️" }
}

var accuracy = calculate_accuracy(94, 100)
print("Accuracy:", accuracy, "%")
print("Rating:", classify_model(0.96))
```

### String Interpolation

```cherry
var model_name = "ChurnPredictor"
var auc        = 0.978

print(`Model ${model_name} achieved AUC of ${auc}`)
// → Model ChurnPredictor achieved AUC of 0.978
```

---

## 🗄️ Database Integration

```cherry
// Connect to MySQL or PostgreSQL
var db = connect("mysql://user:password@localhost/sales_db")

// Query data
var customers = db.query("SELECT * FROM customers WHERE active = true")
print("Loaded", len(customers), "customers")

// Process results
var vip = []
for c in customers {
    if (c["lifetime_value"] > 5000) {
        vip.append(c["name"])
    }
}
print("VIP customers:", vip)
```

> 📌 **Supported databases:** MySQL, PostgreSQL  
> 🔜 **Coming soon:** MongoDB, Redis, BigQuery, Snowflake

---

## 🤖 AI & Machine Learning

### Full AutoML Pipeline

```cherry
// 1. Load your data
var db     = connect("mysql://user:pass@localhost/crm")
var data   = db.query("SELECT age, income, churn FROM customers")

// 2. Build an H2O frame
var frame  = h2o.frame(data)

// 3. Train AutoML — zero config needed
var model  = h2o.automl(frame, "churn")

// 4. Inspect the leaderboard
print("Best model:", model.name)
print("Model type:", model.model_type)
for entry in model.leaderboard {
    print(" -", entry["model_id"], "| AUC:", entry["auc"])
}

// 5. Predict on new data
var new_data    = [{ "age": 28, "income": 72000 }]
var predictions = model.predict(h2o.frame(new_data))
print("Churn probability:", predictions[0]["confidence"])
```

### Export Models

```cherry
// Generate ready-to-ship model wrappers
export to python    // → model_server.py
export to php       // → ModelPredictor.php
export to java      // → ModelPredictor.java
```

---

## 🚀 Model Deployment

```cherry
// Deploy model as a live REST API (FastAPI under the hood)
var endpoint = deploy(model, "http://0.0.0.0:8080/predict")

print("✅ API live at:", endpoint.url)
print("🔍 Health check:", endpoint.url.replace("/predict", "/health"))

// Call your API
// POST http://0.0.0.0:8080/predict
// Body: { "rows": [{ "age": 35, "income": 60000 }] }
// Returns: { "predictions": [{ "prediction": 1, "confidence": 0.85 }] }

// Graceful teardown
undeploy(endpoint, 5.0)
print("🛑 API offline")
```

---

## 📦 Installation

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | `≥ 3.8` | Required |
| pip | `≥ 21.0` | Required |
| MySQL / PostgreSQL | Any | Optional — needed for DB features |
| Java 8+ | `8 or 11` | Optional — needed for H2O AutoML |

### Installation Options

```bash
# Option 1: Core only (no ML dependencies)
pip install -e .

# Option 2: With database support
pip install -e ".[db]"

# Option 3: With ML support
pip install -e ".[ml]"

# Option 4: With deployment support
pip install -e ".[deploy]"

# Option 5: Everything
pip install -e ".[all]"

# Option 6: Development mode (includes testing tools)
pip install -e ".[dev]"
```

### Verify Your Install

```bash
cherryscript --version
# → CherryScript 1.0.0

cherryscript -c 'print("🍒 CherryScript is ready!")'
# → 🍒 CherryScript is ready!
```

---

## 📁 Project Structure

```
CherryScript/
├── 🍒 cherryscript/            # Core package
│   ├── __init__.py             # Version & exports
│   ├── parser.py               # Tokenizer & AST parser
│   ├── cli/
│   │   └── __init__.py         # CLI entry point & REPL
│   └── runtime/
│       ├── __init__.py         # Runtime exports
│       ├── interpreter.py      # Statement evaluator
│       └── adapters.py         # DB, H2O, Deploy adapters
│
├── 📚 docs/                    # Documentation
│   ├── ROADMAP.md              # Feature timeline
│   └── SYNTAX_GUIDE.md         # Full language reference
│
├── 🧪 examples/                # Sample .cherry scripts
│   ├── test.cherry             # Full feature showcase
│   ├── ml_pipeline.cherry      # ML pipeline example
│   ├── data_analysis.cherry    # Business intelligence example
│   └── deploy_api.cherry       # Deployment walkthrough
│
├── 🔬 tests/                   # Test suite
│   ├── test_parser.py
│   └── test_interpreter.py
│
├── ⚙️  .github/
│   ├── workflows/ci.yml        # GitHub Actions CI
│   ├── ISSUE_TEMPLATE/         # Bug & feature templates
│   └── pull_request_template.md
│
├── pyproject.toml              # Package configuration
├── requirements.txt            # Pinned dependencies
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guide
└── LICENSE                     # MIT License
```

---

## 🗺️ Roadmap

> See [`docs/ROADMAP.md`](./docs/ROADMAP.md) for the full detailed plan.

| Quarter | Milestone | Status |
|---|---|---|
| Q1 2024 | ✅ v1.0 — Core interpreter, CLI, H2O AutoML, MySQL, REST deploy | **Done** |
| Q2 2024 | 🔜 v2.0 — Plugin system, VS Code extension, NoSQL support | Planned |
| Q3 2024 | 🔜 v3.0 — JIT compilation, PyTorch/TF bridge, WASM | Planned |
| Q4 2024 | 🔜 v3.5 — Enterprise: RBAC, SSO, Kubernetes deploy | Planned |
| Q1 2025 | 🔜 v4.0 — AI-assisted coding, natural language → CherryScript | Planned |
| Q2 2025 | 🔜 v5.0 — CherryStudio web IDE, model marketplace | Planned |

---

## 🤝 Contributing

We ❤️ contributors! Check out [`CONTRIBUTING.md`](./CONTRIBUTING.md) for full guidelines.

```bash
# 1. Fork the repo on GitHub
# 2. Clone your fork
git clone https://github.com/<your-username>/CherryScript.git
cd CherryScript

# 3. Create a feature branch
git checkout -b feature/my-awesome-feature

# 4. Install dev dependencies
pip install -e ".[dev]"

# 5. Make your changes, run tests
pytest tests/ -v --cov=cherryscript

# 6. Commit & push
git commit -m "feat: add my awesome feature"
git push origin feature/my-awesome-feature

# 7. Open a Pull Request 🎉
```

### 🏷️ Good First Issues

Look for issues tagged [`good-first-issue`](https://github.com/Infinite-Networker/CherryScript/labels/good-first-issue) — these are specifically selected for new contributors.

---

## 🌟 Community & Support

<div align="center">

| Channel | Link |
|---|---|
| 🐛 Bug Reports | [GitHub Issues](https://github.com/Infinite-Networker/CherryScript/issues/new?template=bug_report.md) |
| 💡 Feature Requests | [GitHub Issues](https://github.com/Infinite-Networker/CherryScript/issues/new?template=feature_request.md) |
| 💬 Discussions | [GitHub Discussions](https://github.com/Infinite-Networker/CherryScript/discussions) |
| 📖 Documentation | [`/docs`](./docs/) |
| 📋 Changelog | [`CHANGELOG.md`](./CHANGELOG.md) |

</div>

---

## 📄 License

```
MIT License — © 2024 Cherry Computer Ltd.

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software.
```

See [`LICENSE`](./LICENSE) for full text.

---

<div align="center">

**Made with 🍒 by [Cherry Computer Ltd.](https://github.com/Infinite-Networker)**

*"Making Data Science Accessible, One Line at a Time."*

<br/>

[![Star this repo](https://img.shields.io/badge/⭐%20Star%20this%20repo-FFD700?style=for-the-badge&logo=github&logoColor=black)](https://github.com/Infinite-Networker/CherryScript)
[![Fork it](https://img.shields.io/badge/🍴%20Fork%20it-FF6B9D?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Infinite-Networker/CherryScript/fork)
[![Follow](https://img.shields.io/badge/👤%20Follow-292929?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Infinite-Networker)

</div>
