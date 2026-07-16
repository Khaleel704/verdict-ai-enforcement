# Verdict

### Human-in-the-Loop AI Enforcement Pipeline

Verdict is an interactive prototype that explores how AI-powered cyber abuse detection can be combined with human analyst judgment to make consistent, explainable enforcement decisions.

Rather than replacing analysts, Verdict demonstrates a workflow where automated detection triages activity, analysts evaluate intent and context, and structured feedback continuously improves future detection quality.

> **Disclaimer**
>
> Verdict uses synthetic cases and a transparent baseline detector for demonstration purposes only. It is not affiliated with or endorsed by Anthropic or any other AI company.

---

## Overview

Modern AI systems receive millions of requests every day. Many are harmless, while others may facilitate phishing, malware development, credential theft, or other forms of cyber abuse.

The difficult cases are rarely obvious—they require human judgment.

Verdict demonstrates a human-in-the-loop review workflow consisting of:

- Automated risk scoring
- Model recommendation generation
- Human analyst review
- Structured enforcement rationale
- Model agreement / override tracking
- Enforcement analytics

---

## Workflow

```
User Request
      │
      ▼
Baseline Detector
(Risk Score + Recommendation)
      │
      ▼
Human Analyst Review
(Intent • Context • Capability • Harm)
      │
      ▼
Enforcement Decision

Allow
Block
Escalate
      │
      ▼
Quality Feedback

Model Agreement
Model Override
Policy Clarification
```

---

## Features

### Automated Detection

Each case receives:

- Risk score (0–100)
- Confidence score
- Baseline recommendation
- Detection signals

---

### Human Review

Each reviewed case records:

- Enforcement decision
- Policy category
- Analyst confidence
- Detailed rationale
- Model agreement / override

---

### Enforcement Analytics

The dashboard summarizes:

- Cases reviewed
- Decision distribution
- Model agreement rate
- Analyst overrides
- Escalation rate
- Policy category trends

---

## Design Philosophy

Verdict is built around four principles.

### Automation First

Routine and obvious cases should not require manual review.

### Human Judgment

Ambiguous, novel, and high-impact cases deserve analyst attention.

### Structured Feedback

Analyst decisions should improve future model performance rather than disappear after review.

### Policy Evolution

Real-world enforcement cases reveal opportunities to clarify and strengthen policy.

---

## Example Cases

The included synthetic dataset covers scenarios such as:

- Credential theft
- Malware development
- Security education
- Authorized security testing
- Vulnerability research
- Defensive security
- Defense evasion
- Unauthorized access
- Ambiguous escalation cases

---

## Technology

- Python
- Streamlit
- Pandas

---

## Repository Structure

```
verdict/
│
├── app.py
├── cases.json
├── verdict_decisions.csv
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

---

## Running Locally

Clone the repository.

```bash
git clone https://github.com/YOUR_USERNAME/verdict-ai-enforcement.git

cd verdict-ai-enforcement
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Windows

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Run the application.

```bash
streamlit run app.py
```

---

## Future Improvements

Potential future enhancements include:

- LLM-powered policy reasoning
- Adaptive risk scoring
- Reviewer assignment queues
- Multi-analyst consensus workflows
- Detection precision / recall metrics
- Policy versioning
- Review audit history
- Analyst productivity metrics

---

## Author

**Khaleel Abdulkarim**

Cybersecurity Engineer • AI Security

LinkedIn:
https://www.linkedin.com/in/khaleel704/

GitHub:
https://github.com/khaleel704/