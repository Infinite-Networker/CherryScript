# 📖 CherryScript Syntax Guide

<div align="center">

[![Version](https://img.shields.io/badge/Language%20Version-1.0.0-FF6B9D?style=flat-square)](../CHANGELOG.md)
[![Status](https://img.shields.io/badge/Reference-Complete-00C853?style=flat-square)](.)

*Complete language reference for CherryScript v1.0.0*

</div>

---

## 📋 Contents

1. [Comments](#1-comments)
2. [Variables](#2-variables)
3. [Data Types](#3-data-types)
4. [Operators](#4-operators)
5. [String Interpolation](#5-string-interpolation)
6. [Control Flow](#6-control-flow)
7. [Loops](#7-loops)
8. [Functions](#8-functions)
9. [Built-in Functions](#9-built-in-functions)
10. [Arrays](#10-arrays)
11. [Dictionaries](#11-dictionaries)
12. [Database Operations](#12-database-operations)
13. [H2O AutoML](#13-h2o-automl)
14. [Model Deployment](#14-model-deployment)
15. [Code Export](#15-code-export)
16. [Error Handling](#16-error-handling)
17. [Complete Examples](#17-complete-examples)

---

## 1. Comments

```cherry
// Single-line comment

// Multi-line: just use multiple // lines
// Line two
// Line three
```

> ⚠️ Block comments (`/* */`) are not supported in v1.0.0. Use `//` for every comment line.

---

## 2. Variables

CherryScript has two variable declaration keywords:

| Keyword | Mutability | Use When |
|---------|-----------|----------|
| `var` | Mutable | Value will change |
| `let` | Constant-intent | Value shouldn't change (not enforced at runtime in v1.0) |

```cherry
var counter  = 0
var username = "alice"
let MAX_SIZE = 1000
let PI       = 3.14159

// Re-assignment
counter = counter + 1
counter += 10
counter -= 5
counter *= 2
counter /= 4
counter %= 3
```

> Variable names must start with a letter or underscore, followed by letters, digits, or underscores.
> Valid: `my_var`, `_temp`, `value2` | Invalid: `2value`, `my-var`

---

## 3. Data Types

### Primitives

```cherry
// String
var name    = "CherryScript"
var path    = 'dataset/raw/images'

// Number (integer or float — unified)
var count   = 42
var rate    = 0.156
var large   = 1_000_000     // underscores for readability (future)

// Boolean
var enabled = true
var debug   = false

// Null / None
var empty   = null
```

### Collections

```cherry
// Array (ordered, mixed types allowed)
var fruits  = ["cherry", "mango", "kiwi"]
var scores  = [98, 87, 93, 72]
var mixed   = [1, "two", true, null]

// Dictionary (key-value pairs, string keys)
var config  = {
    "model":   "gradient_boost",
    "epochs":  100,
    "verbose": true
}

// Nested structures
var dataset = {
    "name": "customers",
    "schema": ["age", "income", "churned"],
    "rows": [
        { "age": 28, "income": 65000, "churned": 0 },
        { "age": 35, "income": 85000, "churned": 0 }
    ]
}
```

---

## 4. Operators

### Arithmetic

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `+` | Add | `5 + 3` | `8` |
| `-` | Subtract | `10 - 4` | `6` |
| `*` | Multiply | `3 * 7` | `21` |
| `/` | Divide | `15 / 4` | `3.75` |
| `%` | Modulo | `10 % 3` | `1` |

### Comparison

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `==` | Equal | `5 == 5` | `true` |
| `!=` | Not equal | `5 != 3` | `true` |
| `<` | Less than | `3 < 5` | `true` |
| `>` | Greater than | `5 > 3` | `true` |
| `<=` | Less or equal | `5 <= 5` | `true` |
| `>=` | Greater or equal | `6 >= 5` | `true` |

### Logical

```cherry
// AND
if (age > 18 && income > 50000) { ... }

// OR
if (is_admin || is_owner) { ... }

// NOT
if (!is_banned) { ... }
```

### Augmented Assignment

```cherry
var x = 10
x += 5    // x = 15
x -= 3    // x = 12
x *= 2    // x = 24
x /= 6    // x = 4
x %= 3    // x = 1
```

---

## 5. String Interpolation

Use **backtick strings** (`` ` ``) to embed expressions:

```cherry
var model   = "GBM_1"
var auc     = 0.953
var records = 12500

print(`Model ${model} trained on ${records} records with AUC = ${auc}`)
// → Model GBM_1 trained on 12500 records with AUC = 0.953

// Expressions inside ${}
var items = ["a", "b", "c"]
print(`Dataset has ${len(items)} columns`)
// → Dataset has 3 columns

// Arithmetic inside ${}
var base  = 1000
var rate  = 0.08
print(`Projected value: $${base * (1 + rate)}`)
// → Projected value: $1080.0
```

---

## 6. Control Flow

### if / else if / else

```cherry
var score = 87

if (score >= 95) {
    print("A+")
} else if (score >= 90) {
    print("A")
} else if (score >= 80) {
    print("B")
} else if (score >= 70) {
    print("C")
} else {
    print("Needs improvement")
}
```

> **Note:** Parentheses around the condition are required. Curly braces `{}` are required even for single-statement blocks.

### Inline conditional (ternary-style)

```cherry
// Supported as expression in var assignment (limited — use if/else for complex cases)
var label = "Pass" if score >= 60 else "Fail"
```

---

## 7. Loops

### for-in loop

Iterate over arrays:

```cherry
var cities = ["London", "Tokyo", "New York", "Sydney"]

for city in cities {
    print("Processing data for:", city)
}
```

Iterate with index using `range`:

```cherry
for i in range(5) {
    print("Iteration:", i)   // 0, 1, 2, 3, 4
}

for i in range(2, 8) {
    print(i)   // 2, 3, 4, 5, 6, 7
}
```

Iterate over dict keys:

```cherry
var config = { "lr": 0.01, "epochs": 50, "batch_size": 32 }

for key in keys(config) {
    print(key, "=", config[key])
}
```

### while loop

```cherry
var i = 0
while (i < 5) {
    print("Step:", i)
    i = i + 1
}

// With break condition using function
var attempts = 0
var success  = false
while (!success && attempts < 10) {
    attempts = attempts + 1
    // ... try something ...
    if (attempts == 3) {
        success = true
    }
}
print("Succeeded after", attempts, "attempts")
```

### C-style for loop

```cherry
for (var i = 0; i < 10; i += 1) {
    print(i)
}
```

---

## 8. Functions

### Definition

```cherry
fn function_name(param1, param2) {
    // body
    return result
}
```

### Examples

```cherry
// Simple function
fn square(n) {
    return n * n
}

// Multiple parameters
fn calculate_bmi(weight_kg, height_m) {
    return weight_kg / (height_m * height_m)
}

// Returning early
fn divide_safe(a, b) {
    if (b == 0) {
        print("Error: division by zero")
        return null
    }
    return a / b
}

// Recursive function
fn factorial(n) {
    if (n <= 1) { return 1 }
    return n * factorial(n - 1)
}

// Function returning a collection
fn top_n(scores, n) {
    var result = []
    for i in range(min(n, len(scores))) {
        result.append(scores[i])
    }
    return result
}
```

### Calling Functions

```cherry
var bmi    = calculate_bmi(70, 1.75)
var answer = divide_safe(100, 0)
var fact   = factorial(6)           // 720
var top3   = top_n([95, 88, 76, 65, 54], 3)

print("BMI:", bmi)
print("6! =", fact)
print("Top 3:", top3)
```

---

## 9. Built-in Functions

| Function | Description | Example |
|----------|-------------|---------|
| `print(...)` | Print to stdout | `print("Hello", name)` |
| `len(x)` | Length of string/array/dict | `len([1,2,3])` → `3` |
| `range(n)` | Integer range `[0, n)` | `range(5)` → `[0,1,2,3,4]` |
| `range(a, b)` | Range `[a, b)` | `range(2, 5)` → `[2,3,4]` |
| `sum(arr)` | Sum of numeric array | `sum([1,2,3])` → `6` |
| `min(arr)` / `min(a,b)` | Minimum | `min([3,1,2])` → `1` |
| `max(arr)` / `max(a,b)` | Maximum | `max([3,1,2])` → `3` |
| `format(val, spec)` | Python-style formatting | `format(3.14159, ".2f")` → `"3.14"` |
| `append(arr, item)` | Append to array (in place) | `append(list, "new")` |
| `keys(dict)` | Get dict keys | `keys({"a":1,"b":2})` → `["a","b"]` |
| `time()` | Current Unix timestamp | `time()` → `1710000000.0` |

---

## 10. Arrays

```cherry
var arr = [10, 20, 30, 40, 50]

// Access by index (0-based)
print(arr[0])    // 10
print(arr[4])    // 50

// Length
print(len(arr))  // 5

// Append
append(arr, 60)
print(arr)       // [10, 20, 30, 40, 50, 60]

// Iterate
for item in arr {
    print(item * 2)
}

// Nested arrays (matrix)
var matrix = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]
print(matrix[1][1])   // 1
```

---

## 11. Dictionaries

```cherry
var person = {
    "name":  "Alice",
    "age":   30,
    "roles": ["admin", "analyst"]
}

// Access
print(person["name"])    // "Alice"
print(person["roles"])   // ["admin", "analyst"]

// Nested access
print(person["roles"][0])  // "admin"

// Get keys
var k = keys(person)     // ["name", "age", "roles"]

// Safe access with .get()
var dept = person.get("department", "Unknown")  // "Unknown" (key missing)

// Update value
person["age"] = 31

// Iterate
for key in keys(person) {
    print(key, ":", person[key])
}
```

---

## 12. Database Operations

```cherry
// ── Connect ─────────────────────────────────────────
var db = connect("mysql://user:password@host:3306/database")
// Also works:
// var db = connect("postgresql://user:pass@host/dbname")

// ── Query ────────────────────────────────────────────
// Returns list of row dictionaries
var rows = db.query("SELECT id, name, score FROM users WHERE active = 1")

// Process results
for row in rows {
    print(row["name"], ":", row["score"])
}

// ── Parameterised-style queries ──────────────────────
// Pass values directly in the SQL string
var cutoff = "2023-01-01"
var recent = db.query(`SELECT * FROM events WHERE created_at > '${cutoff}'`)

// ── Aggregate queries ────────────────────────────────
var stats = db.query("SELECT COUNT(*) as total, AVG(score) as avg_score FROM users")
print("Total users:", stats[0]["total"])
print("Average score:", stats[0]["avg_score"])
```

---

## 13. H2O AutoML

```cherry
// ── Build a Frame ────────────────────────────────────
var data  = db.query("SELECT age, income, churn FROM customers")
var frame = h2o.frame(data)
// or from a list-of-dicts
var frame2 = h2o.frame([
    { "x1": 1.2, "x2": 3.4, "label": 0 },
    { "x1": 5.6, "x2": 7.8, "label": 1 }
])

// ── Describe the Frame ───────────────────────────────
print(frame.describe())

// ── Preprocess ──────────────────────────────────────
var clean_frame = h2o.preprocess(frame)

// ── Train AutoML ────────────────────────────────────
// h2o.automl(frame, target_column)
var model = h2o.automl(clean_frame, "churn")

// ── Inspect Model ───────────────────────────────────
print("Name :", model.name)
print("Type :", model.model_type)

// Leaderboard — ranked list of models
for entry in model.leaderboard {
    print(entry["model_id"], "AUC:", entry.get("auc", "N/A"))
}

// ── Predict ─────────────────────────────────────────
var new_data    = [{ "age": 29, "income": 72000 }]
var predictions = model.predict(h2o.frame(new_data))

for pred in predictions {
    print("Prediction:", pred["prediction"],
          "Confidence:", pred.get("confidence", "N/A"))
}
```

---

## 14. Model Deployment

```cherry
// ── Deploy ──────────────────────────────────────────
// deploy(model, url) → Endpoint object
var endpoint = deploy(model, "http://0.0.0.0:8080/predict")

// Endpoint properties
print(endpoint.url)    // http://0.0.0.0:8080/predict

// Auto-generated routes:
// POST /predict  → make predictions
// GET  /health   → health check
// GET  /docs     → FastAPI swagger docs

// ── Undeploy ────────────────────────────────────────
// undeploy(endpoint, timeout_seconds?)
undeploy(endpoint, 5.0)    // wait up to 5 s for clean shutdown
```

### Expected API Contract

**Request:**
```json
POST /predict
Content-Type: application/json

{
  "rows": [
    { "age": 35, "income": 60000 }
  ]
}
```

**Response:**
```json
{
  "predictions": [
    { "prediction": 1, "confidence": 0.87 }
  ]
}
```

---

## 15. Code Export

Export the current trained model as production-ready code:

```cherry
export to python    // Generates: model_server.py  (FastAPI + scikit-learn)
export to php       // Generates: ModelPredictor.php
export to java      // Generates: ModelPredictor.java
```

---

## 16. Error Handling

Runtime errors are caught and printed automatically:

```cherry
// Division by zero → prints [error] ...
var result = 10 / 0

// Accessing missing key → prints [error] ...
var d = { "a": 1 }
print(d["missing_key"])

// Safe access with .get()
var safe = d.get("missing_key", "default")   // returns "default"
```

For defensive coding patterns:

```cherry
fn safe_divide(a, b) {
    if (b == 0) {
        print("[warn] Division by zero — returning null")
        return null
    }
    return a / b
}

var result = safe_divide(10, 0)
if (result == null) {
    print("Skipping calculation due to error")
}
```

---

## 17. Complete Examples

### Hello Data Science

```cherry
var data = [
    { "name": "Alice",   "score": 92 },
    { "name": "Bob",     "score": 78 },
    { "name": "Charlie", "score": 85 }
]

fn grade(score) {
    if (score >= 90) { return "A" }
    else if (score >= 80) { return "B" }
    else { return "C" }
}

for student in data {
    let g = grade(student["score"])
    print(`${student["name"]}: ${student["score"]} → Grade ${g}`)
}
```

### End-to-End AutoML in 10 Lines

```cherry
var db   = connect("mysql://user:pass@localhost/db")
var data = db.query("SELECT * FROM training_data")

var model = h2o.automl(h2o.frame(data), "target")

print("Best model:", model.name, "| AUC:", model.leaderboard[0].get("auc"))

var preds = model.predict(h2o.frame([{ "feature1": 5.2, "feature2": 1.3 }]))
print("Prediction:", preds[0]["prediction"])

var ep = deploy(model, "http://0.0.0.0:8080/predict")
print("API live at:", ep.url)
```

---

<div align="center">

**📌 Tip:** Run any example interactively with `cherryscript --interactive`

*CherryScript v1.0.0 · [GitHub](https://github.com/Infinite-Networker/CherryScript) · [Roadmap](./ROADMAP.md)*

</div>
