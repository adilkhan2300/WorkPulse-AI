# WorkPulse AI — Employee Productivity, Workload & Operational Bottleneck Intelligence

WorkPulse AI is an enterprise-grade workforce analytics, workload rebalancing, and operational bottleneck intelligence platform. Engineered for senior management, HR leadership, and MBA General Management & Data Science capstone projects, it addresses a critical modern organizational dilemma:

> **The Core Problem:** Management observes that employee working hours and overtime are steadily increasing while deliverable throughput and on-time completion rates are declining.

WorkPulse AI integrates seven core operational and workforce datasets to empirically diagnose **why expanded working hours fail to produce higher productivity**, pinpoints system chokepoints and workload imbalances, and prescribes evidence-based operational interventions.

---

## 🚀 Key Highlights & Capabilities

- **13 Specialized Executive Views:** Full-lifecycle management cockpit from high-level KPI scorecards to machine-learning delivery forecasts and interactive what-if policy simulations.
- **14 Primary Executive KPI Cards:** Covering actual measured throughput, quality-adjusted output, on-time completion, overtime expenditure, and absenteeism.
- **Empirical Diminishing Returns Modeling:** Polynomial regression ($\text{Productivity} = \beta_0 + \beta_1 H + \beta_2 H^2$) testing for negative marginal returns on overtime and identifying the optimal hours inflection threshold.
- **AI-Powered Bottleneck Detector:** Formulates 10-attribute structured diagnostic cards with customizable operational sensitivity thresholds.
- **Leakage-Free Predictive Machine Learning:** Logistic Regression, Random Forest, and Gradient Boosting models forecasting task delivery delays using strictly pre-execution variables, validated via chronological splitting and SHAP explainability.
- **LLM Executive Advisor with Rule-Based Fallback:** Delivers management-ready strategic memos with zero external API dependencies required.
- **5-Pillar Intervention Planner:** Actionable proposals across Workload Redistribution, Process Optimization, Capacity & Staffing, Sustainable Work Practices, and Employee Development.
- **Interactive What-If Scenario Simulator:** Adjust overtime caps, staffing changes, rework reduction, and waiting times with real-time baseline-vs-scenario delta modeling.
- **Automated Multi-Format Reporting:** Publication-ready PDF executive briefs via ReportLab, consolidated multi-tab Excel workbooks, and modular CSVs.

---

## 🏛️ Theoretical & Mathematical Framework

### 1. Management Science Foundations
- **Diminishing Marginal Returns:** Beyond a weekly threshold (~44-48 hours), cognitive fatigue increases defect injection rates, neutralizing incremental labor hours through compounding rework.
- **Weinberg's Context-Switching Law:** Assigning knowledge workers to multiple concurrent projects causes exponential loss of focus time (~20% lost per concurrent project).
- **Little's Queueing Law ($L = \lambda W$):** Upstream approval chokepoints and serialized QA gates cause work-in-progress (WIP) to explode non-linearly under high utilization.
- **Workload Imbalance & Brooks' Law:** Relying disproportionately on senior staff creates key-person dependencies, leaving junior staff under-leveraged and waiting.

### 2. Primary Mathematical Formulations
- **Net Available Capacity:**
  $$\text{Cap}_{\text{net}} = (\text{Contracted Hours} - \text{Absence Hours}) \times (1 - \theta_{\text{buffer}})$$
  *(where $\theta_{\text{buffer}} = 0.15$ accounts for syncs, admin, and cognitive breaks)*
- **Capacity Utilization:**
  $$U = \frac{\text{Total Working Hours}}{\text{Cap}_{\text{net}}}$$
  *(Classified into Underutilized $<70\%$, Balanced $70-95\%$, High $95-115\%$, and Overallocated $>115\%$)*
- **Quality-Adjusted Output:**
  $$Q_{\text{adj}} = \sum_{i \in \text{Completed}} \left(\frac{\text{Quality}_i}{5.0}\right) - \frac{\text{Rework Hours}}{8.0}$$
- **Productivity Index (0-100):**
  $$\text{Productivity} = 0.40 \cdot \text{OnTime}\% + 0.40 \cdot \text{Completion}\% + 0.20 \cdot \max(0, 100 - 3 \cdot \text{Rework}\%)$$
- **Diminishing Returns Inflection Point:**
  $$H^* = -\frac{\beta_1}{2\beta_2}$$

---

## 🛠️ Technology Stack

| Component | Library / Framework | Functionality |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Responsive, stateful executive web dashboard |
| **Data Processing** | Pandas, NumPy | Multi-table joins, chronological indexing, aggregations |
| **Visualizations** | Plotly Express & Graph Objects | Modern interactive charts, heatmaps, and regressions |
| **Machine Learning** | Scikit-Learn | Delay classification, ROC/PR curves, confusion matrices |
| **Explainable AI** | SHAP & Permutation Importance | Pre-execution driver attribution |
| **Statistical Analysis** | SciPy, Statsmodels | Pearson/Spearman correlations, OLS quadratic regression |
| **LLM Insights** | OpenAI API (gpt-4o-mini) | Structured executive memos with deterministic fallback |
| **Database** | SQLite (`data/workpulse.db`) | Relational persistence and audit trail |
| **Reporting** | ReportLab, OpenPyXL | Executive PDF briefs and multi-sheet Excel workbooks |
| **Testing** | Pytest | Automated verification of formulas and pipelines |

---

## 📁 Repository Structure

```
workpulse_ai/
│
├── app.py                         # Main Streamlit application launcher
├── requirements.txt               # Complete Python dependencies
├── README.md                      # Comprehensive project documentation
├── .env.example                   # Environment configuration template
│
├── modules/                       # Core analytical & computational engines
│   ├── synthetic_data_generator.py # Realistic 120+ employee cohort generator
│   ├── data_loader.py             # SQLite persistence, CSV/Excel parser, global filters
│   ├── data_validation.py         # Schema validation, negative-hour checks, audits
│   ├── productivity_metrics.py    # Executive KPIs, department breakdowns, quality adjustment
│   ├── statistical_analysis.py    # Correlations, quadratic regression, longitudinal trends
│   ├── capacity_planning.py       # Capacity utilization, team diagnostics, resource contention
│   ├── bottleneck_detection.py    # 10-attribute structured diagnostic constraint engine
│   ├── prediction_models.py       # Leakage-free ML classifiers (RF, GB, Logistic Regression)
│   ├── explainability.py          # SHAP & Permutation feature importance
│   ├── llm_insights.py            # OpenAI API integration + rule-based fallback
│   ├── intervention_engine.py     # 5-Pillar actionable management recommendations
│   ├── scenario_simulator.py      # What-If policy simulation engine
│   ├── cost_analysis.py           # Financial burden breakdown & intervention ROI
│   └── reporting.py               # PDF generation (ReportLab) & Excel export
│
├── views/                         # 13 Dedicated Navigation Page Renderers
│   ├── view_overview.py           # 1. Executive Overview & 14 KPI Cards
│   ├── view_upload.py             # 2. Data Upload & Validation Center
│   ├── view_productivity.py       # 3. Productivity Analytics
│   ├── view_working_hours.py      # 4. Working Hours vs. Productivity
│   ├── view_workload.py           # 5. Workload and Capacity
│   ├── view_bottlenecks.py        # 6. Bottleneck Intelligence
│   ├── view_ml.py                 # 7. Machine Learning Insights
│   ├── view_llm.py                # 8. LLM Recommendations
│   ├── view_interventions.py      # 9. Intervention Planner
│   ├── view_costs.py              # 10. Cost Analysis
│   ├── view_simulator.py          # 11. Scenario Simulator
│   ├── view_reports.py            # 12. Reports and Exports
│   └── view_methodology.py        # 13. Methodology & Governance
│
├── utils/
│   └── styles.py                  # Polished CSS styles, KPI badges, Plotly themes
│
├── data/
│   ├── synthetic/                 # Pre-generated realistic demo CSV datasets
│   ├── templates/                 # 7 Standard schema template CSV files
│   └── workpulse.db               # SQLite local relational database
│
└── tests/
    └── test_workpulse.py          # Automated test suite (Pytest)
```

---

## 🚦 Installation & Quick Start

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.11, 3.12, 3.13)
- Windows, macOS, or Linux

### 2. Setup Virtual Environment & Install Dependencies
```bash
# Clone or navigate to repository root
cd "path/to/workpulse_ai"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate

# Install all required packages
pip install -r requirements.txt
```

### 3. Configure Optional Environment Variables
If you wish to use live OpenAI API calls for executive insight generation:
```bash
copy .env.example .env
# Edit .env and enter your key: OPENAI_API_KEY=sk-...
```
*(Note: If no API key is configured, the application functions seamlessly using its deterministic rule-based executive intelligence engine.)*

### 4. Run Automated Test Suite
```bash
python -m pytest tests/test_workpulse.py
```

### 5. Launch the Streamlit Platform
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 📋 The 13 Navigation Pages

1. **Executive Overview:** 14 high-impact KPI cards, management diagnosis alert, longitudinal hours surge trajectory, and departmental ranking.
2. **Data Upload and Validation:** Independent upload tabs for all 7 datasets, schema validation, negative value auditing, and downloadable CSV templates.
3. **Productivity Analytics:** Actual vs estimated hours scatter plot, rework hours sinks, task status inventory, and cycle time distribution.
4. **Working Hours vs. Productivity:** Diminishing returns quadratic regression ($\beta_2 < 0$), inflection threshold calculation, correlation heatmap, and causal boundary notices.
5. **Workload and Capacity:** Available net capacity vs actual demand, status classification (Underutilized, Balanced, High, Overallocated), job-level heatmaps, and project resource contention.
6. **Bottleneck Intelligence:** 10-attribute constraint cards with real-time threshold customization and process queue telemetry.
7. **Machine Learning Insights:** Leakage-free delivery delay prediction (Random Forest, Gradient Boosting, Logistic Regression), ROC & PR curves, confusion matrices, and SHAP feature importance.
8. **LLM Recommendations:** Natural language executive synthesis, empirical evidence extraction, contributing factors, and interactive prompt advisory.
9. **Intervention Planner:** 5-pillar strategic roadmap (Workload Redistribution, Process Optimization, Capacity, Sustainable Practices, Employee Development) with progress tracking.
10. **Cost Analysis:** Accounting of overtime premiums, rework waste, delay penalties, queue latency losses, and intervention ROI payback schedules.
11. **Scenario Simulator:** Interactive what-if laboratory manipulating overtime targets, rework reduction, staffing levels, and process wait times.
12. **Reports and Exports:** Download multi-page ReportLab PDF management briefs, consolidated Excel workbooks, and modular analytical CSV files.
13. **Methodology:** Complete theoretical compendium detailing organizational research principles, Little's Law, Weinberg's Law, and ethical governance standards.

---

## 🛡️ Data Governance & Ethical Mandate

- **Strict Anonymization:** No personally identifiable employee information (PII) is transmitted to external LLM services. All external prompts use aggregated departmental and operational statistics.
- **Anti-Punitive Guardrails:** Predictive models are designed exclusively to identify operational friction and trigger early capacity support. The platform strictly prohibits individual punitive stack-ranking.
- **Causal Integrity:** Distinguishes correlation from causality, actively warning leadership against premature causal conclusions without controlled intervention trials.
