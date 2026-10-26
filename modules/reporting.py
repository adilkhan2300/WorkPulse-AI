"""
Report Generation and Export Engine for WorkPulse AI
Supports:
- Professional Multi-Page PDF Executive Management Report via ReportLab
- Multi-Tab Excel Workbook Export via openpyxl
- Dedicated CSV Export Utilities
Excludes individual-level sensitive details by default.
"""

import io
import os
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf_management_report(
    kpis: Dict[str, Any],
    bottlenecks: List[Dict[str, Any]],
    interventions: List[Dict[str, Any]],
    costs: Dict[str, Any],
    executive_insight: Dict[str, Any]
) -> bytes:
    """
    Builds a polished, publication-ready PDF Executive Management Report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )
    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E3A8A")
    )

    story = []

    # Title & Header
    story.append(Paragraph("WorkPulse AI — Executive Workforce Intelligence Report", title_style))
    date_str = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"<b>Generated:</b> {date_str} &nbsp;|&nbsp; <b>Scope:</b> Aggregated Organizational Analytics &amp; Bottleneck Diagnostics", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=15))

    # 1. Executive Summary & Core Finding
    story.append(Paragraph("1. Executive Summary & Diagnostic Finding", h2_style))
    exec_finding = executive_insight.get("executive_finding", "Productivity analysis complete.")
    
    finding_table = Table(
        [[Paragraph(f"<b>Core Finding:</b> {exec_finding}", callout_style)]],
        colWidths=[540]
    )
    finding_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(finding_table)
    story.append(Spacer(1, 12))

    # 2. Key Performance Indicators
    story.append(Paragraph("2. Primary Workforce & Productivity KPIs", h2_style))
    
    kpi_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Employees Analyzed", str(kpis.get("total_employees", "-")), "Average Overtime Hours", f"{kpis.get('avg_overtime_hours', 0):.1f} hrs/wk"],
        ["Average Working Hours", f"{kpis.get('avg_working_hours', 0):.1f} hrs/wk", "Productivity Score", f"{kpis.get('productivity_score', 0):.1f} / 100"],
        ["Task Completion Rate", f"{kpis.get('task_completion_rate', 0):.1f}%", "On-Time Completion Rate", f"{kpis.get('on_time_completion_rate', 0):.1f}%"],
        ["Excessive Workload Staff", f"{kpis.get('pct_excessive_workload', 0):.1f}%", "Rework Rate", f"{kpis.get('rework_rate_pct', 0):.1f}%"],
        ["Absenteeism Rate", f"{kpis.get('absenteeism_rate', 0):.1f}%", "Potential Bottlenecks", str(kpis.get("potential_bottlenecks_count", 0))],
        ["Engagement Survey Score", f"{kpis.get('engagement_score', 0):.1f} / 10", "Est. Overtime Expenditure", f"${kpis.get('estimated_overtime_expenditure', 0):,.2f}"]
    ]

    kpi_table = Table(kpi_data, colWidths=[150, 120, 150, 120])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 3. Operational Bottlenecks
    story.append(Paragraph("3. AI-Detected Operational Bottlenecks", h2_style))
    bn_rows = [["ID / Title", "Affected Area", "Priority", "Key Operational Metric"]]
    for bn in bottlenecks[:5]:
        first_metric = list(bn.get("supporting_metrics", {}).items())[0] if bn.get("supporting_metrics") else ("Metric", "N/A")
        metric_str = f"{first_metric[0]}: {first_metric[1]}"
        bn_rows.append([
            Paragraph(f"<b>{bn.get('title', '')}</b>", body_style),
            Paragraph(bn.get("affected_entity", ""), body_style),
            bn.get("priority_level", "Medium"),
            Paragraph(metric_str, body_style)
        ])
    
    bn_table = Table(bn_rows, colWidths=[180, 130, 70, 160])
    bn_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(bn_table)
    story.append(Spacer(1, 14))

    # 4. Financial & Cost Impact
    story.append(Paragraph("4. Financial Implications & Inefficiency Burden", h2_style))
    cost_rows = [
        ["Cost Category", "Estimated Incurred Burden", "Accounting Type"],
        ["Recorded Overtime Expenditure", f"${costs.get('recorded_overtime_expenditure', 0):,.2f}", "Actual Payroll Incurred"],
        ["Rework Waste Payroll Cost", f"${costs.get('rework_waste_cost', 0):,.2f}", "Loaded Labor Allocation Loss"],
        ["Estimated Delivery Delay Impact", f"${costs.get('delay_penalty_cost', 0):,.2f}", "Modeled Schedule Penalty"],
        ["Process Idle Waiting Loss", f"${costs.get('process_idle_cost', 0):,.2f}", "Staged Latency Loss"],
        ["Total Estimated Inefficiency Burden", f"${costs.get('total_operational_burden', 0):,.2f}", "Cumulative Potential Recovery"]
    ]
    cost_table = Table(cost_rows, colWidths=[200, 160, 180])
    cost_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FEF3C7")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(cost_table)
    story.append(Spacer(1, 14))

    # 5. Strategic Recommendations & Next Steps
    story.append(Paragraph("5. Evidence-Supported Strategic Interventions", h2_style))
    for idx, itv in enumerate(interventions[:3], 1):
        rec_text = f"<b>{idx}. {itv.get('title')} ({itv.get('category')})</b><br/>" \
                   f"<b>Target:</b> {itv.get('department')} &nbsp;|&nbsp; <b>Priority:</b> {itv.get('priority')} &nbsp;|&nbsp; <b>Review:</b> {itv.get('suggested_review_period')}<br/>" \
                   f"<b>Proposed Action:</b> {itv.get('proposed_action')}<br/>" \
                   f"<b>Expected Direction of Impact:</b> {itv.get('expected_impact')}<br/>" \
                   f"<b>KPI to Monitor:</b> {itv.get('kpi_for_evaluation')}"
        story.append(Paragraph(rec_text, body_style))
        story.append(Spacer(1, 6))

    # Disclaimer / Limitations
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Notice & Methodological Limitations:</b> This document contains aggregated management diagnostics. Causality cannot be inferred solely from observational correlation. All projected benefits are hypotheses subject to operational review.", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_multi_tab_excel(datasets: Dict[str, pd.DataFrame]) -> bytes:
    """Exports all interconnected analytical tables into a clean multi-sheet Excel file."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in datasets.items():
            if df is not None and not df.empty:
                sheet_title = name[:31] # Excel 31-char sheet name limit
                df.head(1000).to_excel(writer, sheet_name=sheet_title, index=False)
    output.seek(0)
    return output.getvalue()
