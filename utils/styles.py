"""
Styling and Plotly Theme Configuration for WorkPulse AI
Injects modern typography, polished KPI cards, glassmorphic styling,
and cohesive color palettes for executive presentation.
"""

import streamlit as st
import plotly.io as pio
import plotly.graph_objects as go

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main container padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 96% !important;
    }

    /* Executive KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 12px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }
    .kpi-delta-positive {
        font-size: 0.75rem;
        font-weight: 600;
        color: #10b981;
        margin-top: 4px;
    }
    .kpi-delta-negative {
        font-size: 0.75rem;
        font-weight: 600;
        color: #ef4444;
        margin-top: 4px;
    }
    .kpi-delta-neutral {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        margin-top: 4px;
    }

    /* Diagnostic Callout Boxes */
    .alert-box-warning {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 6px;
        color: #92400e;
        margin-bottom: 14px;
        font-size: 0.9rem;
    }
    .alert-box-info {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 6px;
        color: #1e40af;
        margin-bottom: 14px;
        font-size: 0.9rem;
    }
    .alert-box-critical {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 12px 16px;
        border-radius: 6px;
        color: #991b1b;
        margin-bottom: 14px;
        font-size: 0.9rem;
    }
    .alert-box-success {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 12px 16px;
        border-radius: 6px;
        color: #166534;
        margin-bottom: 14px;
        font-size: 0.9rem;
    }

    /* Badge Pills */
    .badge-pill {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .badge-critical { background-color: #fee2e2; color: #b91c1c; }
    .badge-high { background-color: #ffedd5; color: #c2410c; }
    .badge-medium { background-color: #fef9c3; color: #854d0e; }
    .badge-low { background-color: #dcfce7; color: #15803d; }
    .badge-blue { background-color: #dbeafe; color: #1e40af; }

    /* Clean Tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* Subheader accents */
    .section-accent {
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
        margin-bottom: 16px;
        margin-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_plotly_theme():
    """Sets a clean, modern aesthetic dictionary for Plotly charts."""
    return {
        "layout": dict(
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=30, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
            colorway=["#2563eb", "#06b6d4", "#f59e0b", "#ec4899", "#8b5cf6", "#10b981", "#64748b"]
        )
    }
