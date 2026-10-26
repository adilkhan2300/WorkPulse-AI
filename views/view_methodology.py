"""
Methodology and Scientific Documentation View for WorkPulse AI
Presents the management theory, statistical formulas, queueing theory principles,
and ethical governance boundaries underpinning the platform.
"""

import streamlit as st

def render_methodology_view():
    st.markdown("## 📚 Scientific Methodology & Theoretical Framework")
    st.caption("Documenting operational research principles, mathematical formulas, and ethical governance standards.")

    # Section 1: Management Theories
    st.markdown("### 🏛️ Organizational & Management Science Foundations")
    
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        st.markdown("""
        #### 1. Diminishing Marginal Productivity & Fatigue
        - **Principle:** As working hours extend past normal limits, cognitive exhaustion reduces vigilance and error-detection capacity.
        - **Mechanism:** Initial output gains are rapidly neutralized by elevated bug rates, rework cycles, and slower task cycle times.
        - **Modeling:** Quadratic polynomial regression $\\text{Output} = \\beta_0 + \\beta_1 H + \\beta_2 H^2$, where $\\beta_2 < 0$ proves diminishing returns with an inflection threshold at $H^* = -\\beta_1 / (2\\beta_2)$.
        """)

        st.markdown("""
        #### 2. Little's Law & Operational Queueing Latency
        - **Principle:** $L = \\lambda \\cdot W$, where $L$ is average tasks in progress (WIP), $\\lambda$ is throughput, and $W$ is waiting time.
        - **Mechanism:** In high-utilization environments (>90%), any minor variance or approval gate delay causes queue length and wait times to explode non-linearly.
        - **Application:** Explains why staging gates (e.g. QA gates, Architecture Sign-offs) create catastrophic project schedule delays.
        """)

    with t_c2:
        st.markdown("""
        #### 3. Context Switching Friction (Weinberg's Rule)
        - **Principle:** Each additional concurrent project reduces available cognitive focus time by ~20% due to context re-orientation.
        - **Observation:** Staff assigned to 3+ simultaneous projects lose up to 40% of their workday simply switching mental models.
        - **Application:** WorkPulse monitors weekly task switches and unplanned ad-hoc work to measure cognitive fragmentation.
        """)

        st.markdown("""
        #### 4. Brooks' Law & Workload Imbalance
        - **Principle:** "Adding manpower to a late software project makes it later" due to communication overhead and onboarding latency.
        - **Workload Imbalance:** Relying excessively on senior engineers creates severe single-point bottlenecks, leaving junior staff idling in queue wait states.
        """)

    st.markdown("---")

    # Section 2: Mathematical Formulations
    st.markdown("### 🧮 Mathematical & Algorithmic Formulations")

    st.markdown("""
    | Operational Metric | Precise Mathematical Definition | Operational Purpose |
    | :--- | :--- | :--- |
    | **Net Available Capacity** | $\\text{Cap}_{\\text{net}} = (\\text{Contracted Hours} - \\text{Absence Hours}) \\times (1 - \\theta_{\\text{buffer}})$ | Accounts for meetings, breaks, and administrative overhead (default $\\theta = 0.15$). |
    | **Capacity Utilization** | $U = \\frac{\\text{Total Working Hours}}{\\text{Cap}_{\\text{net}}}$ | Classifies employees into Underutilized ($<70\\%$), Balanced ($70-95\\%$), High ($95-115\\%$), and Overallocated ($>115\\%$). |
    | **Quality-Adjusted Output** | $Q_{\\text{adj}} = \\sum_{i \\in \\text{Comp}} \\left(\\frac{\\text{Quality}_i}{5.0}\\right) - \\frac{\\text{Rework Hours}}{8.0}$ | Penalizes superficial task volume that generates defects or requires rework. |
    | **Productivity Score (Index)** | $P = 0.40 \\cdot \\text{OnTime}\\% + 0.40 \\cdot \\text{Comp}\\% + 0.20 \\cdot \\max(0, 100 - 3 \\cdot \\text{Rework}\\%)$ | Balanced composite score reflecting delivery speed, throughput, and error avoidance. |
    | **Rework Rate %** | $\\text{Rework}\\% = \\frac{\\sum \\text{Rework Hours}}{\\sum \\text{Actual Hours}} \\times 100$ | Measures proportion of logged effort expended fixing previously delivered deliverables. |
    | **Estimated Overtime Burden** | $\\text{Cost}_{\\text{OT}} = \\sum (\\text{OT Hours} \\times \\text{Hourly Rate} \\times 1.5)$ | Actual or derived direct payroll premium paid for overtime hours. |
    """)

    st.markdown("---")

    # Section 3: Ethical AI and Governance
    st.markdown("### 🛡️ Ethical AI, Privacy & Causal Governance")

    st.markdown("""
    1. **Correlation vs. Causation Guardrails:**
       WorkPulse AI explicitly refuses to claim that overtime *causes* productivity decline without controlled experimental or quasi-experimental instrumental variable designs.
    2. **Zero PII Exposure to External LLMs:**
       When interacting with Large Language Models, only aggregated departmental statistics and anonymized constraint summaries are transmitted. No individual employee names, IDs, or survey responses are ever transmitted outside the system.
    3. **Anti-Punitive Design Mandate:**
       Machine learning predictions identify system-level scheduling risks and resource deficits to trigger supportive capacity rebalancing. The platform is architected to prohibit individual performance ranking for punitive measures.
    """)
