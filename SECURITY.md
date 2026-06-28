# Security Policy

## Supported Versions

The following versions of this project are currently supported with security updates:

| Version | Supported          |
|---------|--------------------|
| 1.x     | :white_check_mark: |

---

## Reporting a Vulnerability

If you discover a security vulnerability in any of the projects in this repository, please follow responsible disclosure practices.

### How to Report

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report privately via one of the following:

- **GitHub Private Advisory**: Go to [Security → Report a vulnerability](../../security/advisories/new) on this repository.
- **Email**: Reach out directly to the repository maintainer via GitHub profile contact.

### What to Include

Please provide as much of the following information as possible to help us understand and resolve the issue quickly:

- Project affected (P1 / P2 / P3)
- Type of vulnerability (e.g. code injection, data exposure, insecure dependency)
- Steps to reproduce the issue
- Potential impact and severity
- Any suggested fix (optional)

---

## Response Timeline

| Step | Timeline |
|------|----------|
| Acknowledgement of report | Within **48 hours** |
| Initial assessment | Within **5 business days** |
| Fix or mitigation | Within **14 days** (critical issues prioritised) |
| Public disclosure | After fix is released |

---

## Scope

This repository contains three AI/ML internship projects:

| Project | Scope |
|---------|-------|
| `rule-based-chatbot/` | Terminal chatbot — local execution only |
| `data-classification/` | ML pipeline — local execution only, no network access |
| `recommendation-engine/` | Desktop app — performs web scraping via DuckDuckGo and Wikipedia |

> **Note:** The Recommendation Engine (P3) makes outbound HTTP requests to third-party websites. Any vulnerability related to those external sources is outside our control.

---

## Security Best Practices for Contributors

- Do not hardcode API keys, passwords, or secrets in source code.
- Do not commit `.env` files or credential files.
- Keep dependencies up to date (`pip install --upgrade`).
- Run only from trusted environments — do not expose these apps on public servers without additional hardening.

---

*This security policy applies to all projects under the DecodeLabs AI Internship repository.*
