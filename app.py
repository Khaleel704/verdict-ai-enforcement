from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

DECISIONS_PATH = Path(__file__).parent / "verdict_decisions.csv"

def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        /* Main page width and spacing */
        .block-container {
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* Hide default Streamlit footer and menu */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Main headings */
        h1 {
            font-size: 2.6rem !important;
            letter-spacing: -0.04em;
            margin-bottom: 0.25rem !important;
        }

        h2, h3 {
            letter-spacing: -0.02em;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.055),
                rgba(255, 255, 255, 0.02)
            );
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 14px;
            padding: 18px 20px;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.82rem;
            color: #A8A8A8;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.9rem;
            font-weight: 650;
        }

        /* Containers and review cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
        }

        /* Buttons */
        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 9px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            font-weight: 600;
            transition: 0.15s ease;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
            border-color: #D97757;
        }

        /* Inputs */
        .stSelectbox,
        .stTextArea,
        .stRadio {
            margin-bottom: 0.5rem;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Info boxes */
        [data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            overflow: hidden;
        }

        /* Divider */
        hr {
            border-color: rgba(255, 255, 255, 0.08);
        }

        /* Small muted text */
        .muted {
            color: #999999;
            font-size: 0.92rem;
        }

        /* Status badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 650;
            letter-spacing: 0.02em;
        }

        .badge-allow {
            background: rgba(34, 197, 94, 0.13);
            color: #86EFAC;
            border: 1px solid rgba(34, 197, 94, 0.25);
        }

        .badge-block {
            background: rgba(239, 68, 68, 0.13);
            color: #FCA5A5;
            border: 1px solid rgba(239, 68, 68, 0.25);
        }

        .badge-review {
            background: rgba(245, 158, 11, 0.13);
            color: #FCD34D;
            border: 1px solid rgba(245, 158, 11, 0.25);
        }

        .badge-pending {
            background: rgba(148, 163, 184, 0.13);
            color: #CBD5E1;
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


APP_TITLE = "Verdict"
APP_SUBTITLE = "Human-in-the-loop AI cyber enforcement prototype"
CASES_PATH = Path(__file__).parent / "cases.json"


def load_cases() -> list[dict[str, Any]]:
    """Load synthetic review cases from disk."""
    try:
        with CASES_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("cases.json must contain a JSON list.")

        return data
    except FileNotFoundError:
        st.error("cases.json was not found.")
        st.stop()
    except (json.JSONDecodeError, ValueError) as exc:
        st.error(f"Unable to load cases: {exc}")
        st.stop()


def baseline_detector(prompt: str, context: str) -> dict[str, Any]:
    """
    Transparent demonstration detector.

    This is intentionally a simple heuristic baseline rather than a
    production moderation model. Its limitations create useful opportunities
    for analyst review, overrides, and policy feedback.
    """
    combined = f"{prompt} {context}".lower()
    score = 25
    signals: list[str] = []

    high_risk_signals = {
        "ransomware": 55,
        "stolen": 35,
        "revealing their corporate passwords": 45,
        "less likely to detect": 40,
        "credential-stuffing": 45,
        "conceal malicious": 45,
        "without the password": 30,
        "do not know the password": 30,
        "encrypts files and demands payment": 55,
        "offensive payload": 30,
    }

    medium_risk_signals = {
        "phishing": 20,
        "initial access": 10,
        "port-scanning": 10,
        "vulnerability": 8,
        "exploit": 15,
        "malware": 15,
        "gain access": 15,
    }

    defensive_signals = {
        "defensive": -25,
        "mitigation": -15,
        "incident-response": -20,
        "security analyst": -20,
        "personally owned": -20,
        "awareness program": -15,
        "yara rule": -20,
        "least-privilege": -15,
        "security review": -15,
        "high level": -10,
        "educational": -10,
    }

    for phrase, weight in high_risk_signals.items():
        if phrase in combined:
            score += weight
            signals.append(f"High-risk signal: {phrase}")

    for phrase, weight in medium_risk_signals.items():
        if phrase in combined:
            score += weight
            signals.append(f"Risk signal: {phrase}")

    for phrase, weight in defensive_signals.items():
        if phrase in combined:
            score += weight
            signals.append(f"Protective context: {phrase}")

    score = max(0, min(score, 100))

    if score >= 75:
        recommendation = "Block"
    elif score >= 40:
        recommendation = "Human Review"
    else:
        recommendation = "Allow"

    confidence = min(98, 55 + abs(score - 50))

    return {
        "risk_score": score,
        "recommendation": recommendation,
        "confidence": confidence,
        "signals": signals or ["No strong policy indicators detected"],
    }


def initialize_state() -> None:
    if "decisions" not in st.session_state:
        if DECISIONS_PATH.exists():
            try:
                saved_decisions = pd.read_csv(DECISIONS_PATH)

                boolean_columns = ["policy_gap", "model_agreement"]

                for column in boolean_columns:
                    if column in saved_decisions.columns:
                        saved_decisions[column] = (
                            saved_decisions[column]
                            .astype(str)
                            .str.lower()
                            .map({"true": True, "false": False})
                            .fillna(False)
                        )

                st.session_state.decisions = saved_decisions.to_dict(
                    orient="records"
                )
            except Exception as exc:
                st.warning(f"Unable to load saved decisions: {exc}")
                st.session_state.decisions = []
        else:
            st.session_state.decisions = []

    if "selected_case_id" not in st.session_state:
        st.session_state.selected_case_id = None


def decisions_dataframe() -> pd.DataFrame:
    if not st.session_state.decisions:
        return pd.DataFrame()

    return pd.DataFrame(st.session_state.decisions)


def render_sidebar() -> str:
    st.sidebar.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="
                font-size: 1.6rem;
                font-weight: 750;
                letter-spacing: -0.04em;
            ">
                ◈ Verdict
            </div>
            <div style="
                color: #999999;
                font-size: 0.85rem;
                margin-top: 0.2rem;
            ">
                AI Enforcement Pipeline
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "Workspace",
        ["Dashboard", "Review Queue", "Analytics", "About"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    reviewed_count = len(st.session_state.decisions)

    st.sidebar.markdown(
        f"""
        <div class="muted">
            <strong style="color:#F5F5F5;">Reviewer</strong><br>
            Khaleel Abdulkarim
        </div>

        <div style="height: 14px;"></div>

        <div class="muted">
            <strong style="color:#F5F5F5;">Session progress</strong><br>
            {reviewed_count} cases reviewed
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    st.sidebar.caption(
        "Synthetic cases and a transparent baseline detector. "
        "Portfolio prototype—not a production enforcement system."
    )

    return page


def render_dashboard(cases: list[dict[str, Any]]) -> None:
    st.markdown(
    """
<div style="padding-top:12px;padding-bottom:20px;">

<div style="
font-size:2.6rem;
font-weight:800;
color:#D97757;
line-height:1.2;
margin-bottom:6px;
">
Verdict
</div>

<div style="
font-size:1.7rem;
font-weight:650;
line-height:1.3;
margin-bottom:14px;
">
Human-in-the-Loop AI Enforcement System
</div>

<div style="
max-width:780px;
font-size:1.05rem;
color:#A0A0A0;
line-height:1.6;
">
An interactive prototype demonstrating how automated cyber abuse detection,
human analyst judgment, and structured policy feedback work together to produce
consistent, explainable enforcement decisions.
</div>

</div>
""",
    unsafe_allow_html=True,
)

    decisions = decisions_dataframe()
    total_reviewed = len(decisions)

    if decisions.empty:
        agreement_rate = 0
        override_count = 0
        escalation_count = 0
    else:
        agreement_rate = round(decisions["model_agreement"].mean() * 100)
        override_count = int((~decisions["model_agreement"]).sum())
        escalation_count = int(
            (decisions["analyst_decision"] == "Escalate").sum()
        )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Cases available", len(cases))
    col2.metric("Cases reviewed", total_reviewed)
    col3.metric(
        "Model agreement",
        f"{agreement_rate}%" if total_reviewed else "—",
    )
    col4.metric("Analyst overrides", override_count)

    st.markdown("### Enforcement workflow")

    workflow_cols = st.columns(5)

    workflow_steps = [
        ("01", "Detection", "Activity receives a baseline risk score."),
        ("02", "Routing", "Clear and ambiguous cases are separated."),
        ("03", "Review", "An analyst evaluates intent and context."),
        ("04", "Decision", "Allow, block, escalate, or flag policy."),
        ("05", "Feedback", "Outcomes become detection-quality signals."),
    ]

    for column, (number, title, description) in zip(
        workflow_cols,
        workflow_steps,
    ):
        with column:
            st.html(
                f"""
                <div style="
                    min-height: 175px;
                    padding: 18px;
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 14px;
                    background: rgba(255,255,255,0.025);
                ">
                    <div style="
                        color: #D97757;
                        font-size: 0.75rem;
                        font-weight: 700;
                    ">
                        {number}
                    </div>

                    <div style="
                        font-size: 1rem;
                        font-weight: 700;
                        margin-top: 10px;
                    ">
                        {title}
                    </div>

                    <div style="
                        color: #999999;
                        font-size: 0.85rem;
                        line-height: 1.5;
                        margin-top: 8px;
                    ">
                        {description}
                    </div>
                </div>
                """
            )

    st.markdown("### Why human review still matters")

    st.info(
        "Automated safeguards can handle obvious cases at scale. "
        "Ambiguous, novel, or high-impact activity still requires human "
        "judgment, and analyst overrides should improve future detection "
        "rather than disappear into a queue."
    )

    if total_reviewed:
        st.caption(f"Escalated cases in this session: {escalation_count}")

def render_completed_review(
    case: dict[str, Any],
    decision: dict[str, Any],
) -> None:
    st.divider()
    st.subheader(f"Case #{case['id']} — Completed Review")

    detector = baseline_detector(case["prompt"], case["context"])

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### Flagged activity")
        st.info(case["prompt"])

        st.markdown("#### Context")
        st.write(case["context"])

    with right:
        st.markdown("#### Baseline detector")
        st.metric("Risk score", f"{detector['risk_score']}/100")
        st.progress(detector["risk_score"] / 100)
        st.write(f"**Recommendation:** {detector['recommendation']}")
        st.write(f"**Confidence:** {detector['confidence']}%")

    st.markdown("### Analyst decision")

    col1, col2, col3 = st.columns(3)

    col1.metric("Decision", decision["analyst_decision"])
    col2.metric("Confidence", f"{decision['analyst_confidence']}%")
    col3.metric("Model agreement", "Yes" if decision["model_agreement"] else "No")

    st.markdown("#### Policy category")
    st.write(decision["policy_category"])

    st.markdown("#### Analyst rationale")
    st.success(decision["rationale"])

    if decision.get("policy_gap", False):
        st.warning(
            "This review identified a potential policy gap or need for clarification."
        )

    if decision["model_agreement"]:
        st.caption(
            "The analyst agreed with the detector's recommended enforcement action."
        )
    else:
        st.caption(
            "The analyst overrode the detector, creating a quality signal for future tuning."
        )
def render_review_queue(cases: list[dict[str, Any]]) -> None:
    st.title("Completed Review Queue")
    st.caption(
        "Explore 16 synthetic cyber-safety cases and the analyst decisions "
        "recorded for each one."
    )

    decisions_by_case = {
        int(decision["case_id"]): decision
        for decision in st.session_state.decisions
    }

    reviewed_count = len(decisions_by_case)

    col1, col2, col3 = st.columns(3)
    col1.metric("Cases", len(cases))
    col2.metric("Reviewed", reviewed_count)
    col3.metric("Coverage", f"{reviewed_count / len(cases):.0%}")
    
    st.divider()

    for case in cases:
        case_id = int(case["id"])
        decision = decisions_by_case.get(case_id)
        detector = baseline_detector(case["prompt"], case["context"])

        if decision:
            analyst_action = decision["analyst_decision"]
            policy_category = decision["policy_category"]

            label = (
                f"Case #{case_id} · {analyst_action} · "
                f"{policy_category}"
            )
        else:
            label = f"Case #{case_id} · Review unavailable"

        with st.expander(label):
            st.markdown("#### Flagged activity")
            st.info(case["prompt"])

            st.markdown("#### Context")
            st.write(case["context"])

            st.divider()

            model_col, analyst_col = st.columns(2)

            with model_col:
                st.markdown("### Model assessment")
                st.metric(
                    "Risk score",
                    f"{detector['risk_score']}/100",
                )
                st.progress(detector["risk_score"] / 100)
                st.write(
                    f"**Recommendation:** "
                    f"{detector['recommendation']}"
                )
                st.write(
                    f"**Confidence:** "
                    f"{detector['confidence']}%"
                )

                with st.expander("Detection signals"):
                    for signal in detector["signals"]:
                        st.write(f"- {signal}")

            with analyst_col:
                st.markdown("### Analyst review")

                if not decision:
                    st.warning(
                        "No completed analyst review is available "
                        "for this case."
                    )
                    continue

                metric1, metric2 = st.columns(2)
                metric1.metric(
                    "Decision",
                    decision["analyst_decision"],
                )
                metric2.metric(
                    "Confidence",
                    f"{decision['analyst_confidence']}%",
                )

                st.write(
                    f"**Policy category:** "
                    f"{decision['policy_category']}"
                )

                agreement_text = (
                    "Agreement"
                    if decision["model_agreement"]
                    else "Override"
                )

                st.write(
                    f"**Model outcome:** {agreement_text}"
                )

            if decision:
                st.markdown("#### Analyst rationale")
                st.success(decision["rationale"])

                if decision.get("policy_gap", False):
                    st.warning(
                        "This review identified a potential policy gap "
                        "or need for clarification."
                    )

                if decision["model_agreement"]:
                    st.caption(
                        "Quality signal: The analyst reinforced the "
                        "detector's recommendation."
                    )
                else:
                    st.caption(
                        "Quality signal: The analyst overrode the "
                        "detector, creating feedback for future tuning."
                    )


def render_case_review(case: dict[str, Any]) -> None:
    st.divider()
    st.subheader(f"Reviewing Case #{case['id']}")

    detector = baseline_detector(case["prompt"], case["context"])

    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### Flagged activity")
        st.info(case["prompt"])

        st.markdown("#### Context")
        st.write(case["context"])

    with right:
        st.markdown("#### Baseline detector")
        st.metric("Risk score", f"{detector['risk_score']}/100")
        st.progress(detector["risk_score"] / 100)        
        st.markdown(
        recommendation_badge(detector["recommendation"]),
        unsafe_allow_html=True,
        )       
        st.write(f"**Confidence:** {detector['confidence']}%")

        with st.expander("Detection signals"):
            for signal in detector["signals"]:
                st.write(f"- {signal}")

        st.markdown("### Analyst assessment")
        st.caption(
         "Evaluate apparent intent, context, capability uplift, and potential harm."
        )
    with st.form(f"review_form_{case['id']}"):
        analyst_decision = st.radio(
            "Decision",
            ["Allow", "Block", "Escalate"],
            horizontal=True,
        )

        policy_category = st.selectbox(
            "Policy category",
            [
                "Defensive Security",
                "Malware Development",
                "Credential Theft",
                "Unauthorized Access",
                "Defense Evasion",
                "Vulnerability Research",
                "Authorized Testing",
                "Security Education",
                "Ambiguous or Novel Risk",
            ],
        )

        confidence = st.slider(
            "Analyst confidence",
            min_value=0,
            max_value=100,
            value=80,
        )

        policy_gap = st.checkbox(
            "This case exposes a policy gap or requires policy clarification."
        )

        rationale = st.text_area(
         "Analyst rationale",
        placeholder=(
        "Document the apparent intent, relevant context, potential "
        "capability increase, and the basis for your decision."
        ),
        height=140,
        )

        submitted = st.form_submit_button("Submit Decision")

    if submitted:
        if len(rationale.strip()) < 20:
            st.warning(
                "Please provide a slightly more detailed rationale "
                "(at least 20 characters)."
            )
            return

        model_decision_mapping = {
            "Allow": "Allow",
            "Block": "Block",
            "Human Review": "Escalate",
        }

        normalized_model_decision = model_decision_mapping[
            detector["recommendation"]
        ]

        record = {
            "case_id": case["id"],
            "prompt": case["prompt"],
            "model_recommendation": detector["recommendation"],
            "model_risk_score": detector["risk_score"],
            "analyst_decision": analyst_decision,
            "policy_category": policy_category,
            "analyst_confidence": confidence,
            "policy_gap": policy_gap,
            "rationale": rationale.strip(),
            "model_agreement": analyst_decision == normalized_model_decision,
        }

        st.session_state.decisions.append(record)
        st.session_state.selected_case_id = None

        st.success(
            "Decision recorded. This review is now available as a quality "
            "signal for detection and policy teams."
        )
        st.rerun()


def render_analytics() -> None:

    st.markdown(
    """
<div style="padding-top:12px;padding-bottom:18px;">

<div style="
color:#D97757;
font-size:0.82rem;
font-weight:700;
text-transform:uppercase;
letter-spacing:.12em;
margin-bottom:8px;
">
QUALITY & ENFORCEMENT SIGNALS
</div>

<div style="
font-size:2.5rem;
font-weight:750;
letter-spacing:-.05em;
margin-bottom:8px;
">
Enforcement Analytics
</div>

<div style="
color:#999999;
font-size:1rem;
line-height:1.6;
max-width:800px;
">
Review outcomes, model agreement, analyst overrides,
escalation trends, and policy insights.
</div>

</div>
""",
    unsafe_allow_html=True,
)
    decisions = decisions_dataframe()

    if decisions.empty:
        st.info("Review at least one case to populate the analytics dashboard.")
        return

    total = len(decisions)
    agreement_rate = round(
        decisions["model_agreement"].mean() * 100,
        1,
    )
    escalation_rate = round(
        (decisions["analyst_decision"] == "Escalate").mean() * 100,
        1,
    )
    policy_gap_rate = round(
        decisions["policy_gap"].mean() * 100,
        1,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Reviewed", total)
    col2.metric("Model Agreement", f"{agreement_rate}%")
    col3.metric("Escalation Rate", f"{escalation_rate}%")
    col4.metric("Policy Gap Rate", f"{policy_gap_rate}%")

    st.subheader("Analyst decisions")
    decision_counts = decisions["analyst_decision"].value_counts()
    st.bar_chart(decision_counts)

    st.subheader("Policy categories")
    category_counts = decisions["policy_category"].value_counts()
    st.bar_chart(category_counts)

    st.subheader("Model disagreements")
    disagreements = decisions[~decisions["model_agreement"]]

    if disagreements.empty:
        st.success("No model disagreements have been recorded.")
    else:
        st.dataframe(
            disagreements[
                [
                    "case_id",
                    "model_recommendation",
                    "analyst_decision",
                    "policy_category",
                    "rationale",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Policy feedback")
    policy_cases = decisions[decisions["policy_gap"]]

    if policy_cases.empty:
        st.write("No policy gaps have been identified.")
    else:
        st.dataframe(
            policy_cases[
                [
                    "case_id",
                    "policy_category",
                    "analyst_decision",
                    "rationale",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    csv_data = decisions.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Export analyst decisions",
        data=csv_data,
        file_name="verdict_decisions.csv",
        mime="text/csv",
    )

def recommendation_badge(recommendation: str) -> str:
    mapping = {
        "Allow": ("badge-allow", "ALLOW"),
        "Block": ("badge-block", "BLOCK"),
        "Human Review": ("badge-review", "HUMAN REVIEW"),
    }

    css_class, label = mapping.get(
        recommendation,
        ("badge-pending", recommendation.upper()),
    )

    return (
        f'<span class="badge {css_class}">'
        f'{label}'
        f'</span>'
    )

def render_about() -> None:
    st.markdown(
    """
    <h1>
        About
        <span style="color:#D97757;">Verdict</span>
    </h1>
    """,
    unsafe_allow_html=True,
    )
    st.markdown(
        """
        Verdict is a small prototype exploring a central challenge in AI safeguards: combining automated detection with consistent human judgment.

It is designed around four principles:

- **Automation first:** Obvious cases should not require manual review.
- **Human judgment for ambiguity:** Uncertain, novel, and high-impact cases deserve analyst attention.
- **Structured feedback:** Analyst overrides should improve future detection quality.
- **Policy evolution:** Enforcement cases should reveal where policy needs clarification.

This demonstration uses synthetic prompts and a transparent heuristic detector. It is not affiliated with or endorsed by any AI company.

---

Built by **Khaleel Abdulkarim**

<div style="display:flex;gap:18px;align-items:center;margin-top:10px;">

<a href="https://www.linkedin.com/in/khaleel704/" target="_blank" title="LinkedIn">
<svg xmlns="http://www.w3.org/2000/svg"
width="30"
height="30"
fill="#D97757"
viewBox="0 0 24 24">
<path d="M20.447 20.452H16.89v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853
0-2.136 1.445-2.136 2.939v5.667H9.346V9h3.414v1.561h.049c.476-.9
1.637-1.85 3.37-1.85 3.604 0 4.268 2.372
4.268 5.456v6.285zM5.337 7.433a2.063
2.063 0 110-4.126 2.063 2.063 0 010
4.126zM7.119 20.452H3.556V9h3.563v11.452zM22.225
0H1.771C.792 0 0 .774 0
1.729v20.542C0 23.227.792 24 1.771
24h20.451C23.2 24 24 23.227
24 22.271V1.729C24 .774 23.2
0 22.222 0h.003z"/>
</svg>
</a>

<a href="https://github.com/khaleel704/" target="_blank" title="GitHub">
<svg xmlns="http://www.w3.org/2000/svg"
width="30"
height="30"
fill="#D97757"
viewBox="0 0 24 24">
<path d="M12 .297c-6.63 0-12 5.373-12
12 0 5.303 3.438 9.8 8.205
11.385.6.113.82-.258.82-.577
0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61-.546-1.385-1.333-1.754-1.333-1.754-1.09-.744.083-.729.083-.729
1.205.084 1.84 1.236 1.84
1.236 1.07 1.835 2.807
1.305 3.492.998.108-.776.418-1.305.762-1.605-2.665-.303-5.466-1.332-5.466-5.93
0-1.31.465-2.38
1.235-3.22-.124-.303-.535-1.523.117-3.176
0 0 1.008-.322
3.3 1.23a11.52 11.52 0 013.003-.404c1.018.005
2.043.138 3.003.404
2.29-1.552
3.297-1.23
3.297-1.23.653
1.653.242
2.873.119
3.176.77.84
1.233
1.91
1.233
3.22
0
4.61-2.804
5.624-5.475
5.921.43.372.823
1.103.823
2.222
0
1.606-.015
2.898-.015
3.293
0
.32.216
.694.825
.576C20.565
22.092
24
17.592
24
12.297c0-6.627-5.373-12-12-12"/>
</svg>
</a>

</div>
""",
    unsafe_allow_html=True,
        
    )


def main() -> None:
    st.set_page_config(
        page_title="Verdict | AI Enforcement Lab",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_css()
    initialize_state()

    cases = load_cases()
    page = render_sidebar()

    if page == "Dashboard":
        render_dashboard(cases)
    elif page == "Review Queue":
        render_review_queue(cases)
    elif page == "Analytics":
        render_analytics()
    else:
        render_about()


if __name__ == "__main__":
    main()