---
name: 💡 Feature Request
about: Have an idea to make CherryScript better? We'd love to hear it!
title: "[FEATURE] "
labels: enhancement
assignees: ''
---

<!--
  🍒 Thanks for suggesting a new feature!
  The more detail you provide, the faster we can evaluate and implement it.
-->

## 💡 Feature Summary

> A brief, one-line description of the feature.

<!-- Example: "Add native async/await support for I/O-bound operations" -->

---

## 🎯 Problem / Motivation

> What problem does this feature solve? Why do you need it?

<!-- Example: "Currently, when running multiple HTTP requests in a loop, they execute sequentially 
     which makes large data collection pipelines extremely slow." -->

---

## 🌟 Proposed Solution

> How would you like this feature to work? Show example CherryScript code if possible.

```cherry
// Example of the proposed syntax / feature
async fn fetch_data(url) {
    var response = await http.get(url)
    return response.json()
}

var results = await parallel([
    fetch_data("https://api.example.com/data/1"),
    fetch_data("https://api.example.com/data/2"),
])
```

---

## 🔄 Alternatives Considered

> Have you considered any alternative approaches or workarounds?

---

## 📊 Use Case

> Describe a concrete real-world use case where this feature would be useful.

---

## 📌 Implementation Notes

> Do you have any thoughts on how this could be implemented? (Optional — technical detail welcome)

---

## 🏷️ Category

> Select the most relevant category:

- [ ] Language syntax / grammar
- [ ] Built-in functions
- [ ] Database adapters
- [ ] ML / AI integrations
- [ ] Model deployment
- [ ] CLI / tooling
- [ ] Performance
- [ ] Documentation
- [ ] Other: _____

---

## ✔️ Checklist

- [ ] I searched existing issues / discussions and this hasn't been requested before
- [ ] This feature aligns with CherryScript's goal of simplifying data science automation
- [ ] I'd be willing to help implement this
