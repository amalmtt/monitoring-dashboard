import streamlit as st


def render_global_styles():
    st.markdown(
        """
        <style>
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
            }

            [data-testid="stHeader"] {
                background: transparent;
            }

            .block-container {
                padding-top: 0.8rem;
                padding-bottom: 1.2rem;
                max-width: 1900px;
            }

            h1 {
                letter-spacing: -0.5px;
                color: #0f172a !important;
            }

            .mini-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid #dbe4ee;
                border-radius: 14px;
                padding: 10px 10px;
                min-height: 78px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
            }

            .mini-label {
                font-size: 0.66rem;
                color: #64748b;
                line-height: 1.05;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }

            .mini-value {
                font-size: 0.96rem;
                font-weight: 700;
                margin-top: 0.18rem;
                line-height: 1.2;
                color: #0f172a;
                min-height: 2.2em;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                word-break: break-word;
                overflow-wrap: anywhere;
            }

            .badge {
                display: inline-block;
                padding: 0.18rem 0.58rem;
                border-radius: 999px;
                font-size: 0.70rem;
                font-weight: 700;
                margin-right: 0.24rem;
                letter-spacing: 0.02em;
            }

            .badge-ok {
                background: #dcfce7;
                color: #15803d;
                border: 1px solid #4ade80;
            }

            .badge-warning {
                background: #fff7ed;
                color: #b45309;
                border: 1px solid #f59e0b;
            }

            .badge-critical {
                background: #fee2e2;
                color: #b91c1c;
                border: 1px solid #ef4444;
            }

            .badge-neutral {
                background: #f1f5f9;
                color: #334155;
                border: 1px solid #cbd5e1;
            }

            .pill {
                display: inline-block;
                padding: 0.12rem 0.42rem;
                border-radius: 999px;
                font-size: 0.60rem;
                font-weight: 800;
                letter-spacing: 0.02em;
                line-height: 1.1;
            }

            .pill-overdue {
                background: #7f1d1d;
                color: #ffffff;
                border: 1px solid #991b1b;
            }

            .counter-row {
                display: flex;
                gap: 0.34rem;
                flex-wrap: wrap;
                margin-top: 0.30rem;
                margin-bottom: 0.30rem;
            }

            .counter-pill {
                display: inline-block;
                padding: 0.14rem 0.46rem;
                border-radius: 999px;
                font-size: 0.64rem;
                font-weight: 800;
                background: #eff6ff;
                color: #334155;
                border: 1px solid #dbeafe;
            }

            .category-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid #dbe4ee;
                border-radius: 16px;
                padding: 14px 16px;
                min-height: 108px;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
            }

            .category-title {
                font-size: 0.96rem;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 0.45rem;
            }

            .category-line {
                font-size: 0.84rem;
                color: #334155;
                line-height: 1.35;
            }

            .item-box {
                border: 1px solid #dbe4ee;
                border-radius: 14px;
                padding: 12px;
                margin-bottom: 10px;
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
            }

            .item-name {
                font-size: 0.96rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
                color: #0f172a;
            }

            .group-title {
                font-size: 0.98rem;
                font-weight: 700;
                margin-top: 0.5rem;
                margin-bottom: 0.45rem;
                color: #0f172a;
            }

            .card-details {
                display: flex;
                flex-direction: column;
                gap: 0.22rem;
                width: 100%;
                margin-top: 0.28rem;
            }

            .card-line {
                font-size: 0.80rem;
                line-height: 1.18;
                margin: 0;
                color: #1e293b;
            }

            .editor-title {
                font-size: 1.12rem;
                font-weight: 800;
                margin-bottom: 0.15rem;
                color: #0f172a;
            }

            .editor-subtitle {
                font-size: 0.86rem;
                color: #64748b;
                margin-bottom: 0.8rem;
            }

            .section-title {
                font-size: 0.98rem;
                font-weight: 800;
                margin-top: 0.7rem;
                margin-bottom: 0.35rem;
                color: #0f172a;
            }

            .helper-text {
                font-size: 0.80rem;
                color: #475569;
            }

            .stTextInput label,
            .stSelectbox label,
            .stNumberInput label,
            .stTextArea label,
            .stRadio label {
                color: #334155 !important;
                font-weight: 600 !important;
            }

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea {
                border-radius: 12px !important;
                background: #ffffff !important;
                color: #0f172a !important;
                border: 1px solid #cbd5e1 !important;
            }

            .stSelectbox div[data-baseweb="select"] > div {
                border-radius: 12px !important;
                background: #ffffff !important;
                color: #0f172a !important;
                border: 1px solid #cbd5e1 !important;
            }

            .stButton button,
            .stDownloadButton button {
                border-radius: 12px !important;
                background: linear-gradient(180deg, #4f46e5 0%, #4338ca 100%) !important;
                color: white !important;
                border: 1px solid rgba(255,255,255,0.08) !important;
            }

            .stButton button:hover,
            .stDownloadButton button:hover {
                background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
                color: white !important;
            }

            .stAlert {
                background-color: #ffffff !important;
                color: #1e293b !important;
                border: 1px solid #dbe4ee !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )