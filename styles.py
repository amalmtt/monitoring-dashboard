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
                padding-top: 0.6rem;
                padding-bottom: 1.4rem;
                max-width: 1900px;
            }

            .page-title {
                font-size: 3rem;
                font-weight: 900;
                letter-spacing: -0.04em;
                color: #0f172a;
                margin-top: 2.4rem;
                margin-bottom: 1.2rem;
                line-height: 1.05;
            }

            h1 {
                letter-spacing: -0.5px;
                color: #0f172a !important;
            }

            .kpi-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid #dbe4ee;
                border-radius: 16px;
                padding: 12px 14px;
                min-height: 90px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
            }

            .kpi-label {
                font-size: 0.68rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }

            .kpi-value {
                margin-top: 0.35rem;
                font-size: 1.15rem;
                font-weight: 800;
                color: #0f172a;
            }

            .mini-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid #dbe4ee;
                border-radius: 14px;
                padding: 10px 10px;
                min-height: 84px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
            }

            .mini-label {
                font-size: 0.64rem;
                color: #64748b;
                line-height: 1.05;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }

            .mini-value {
                font-size: 0.90rem;
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
                margin-right: 0.00rem;
                letter-spacing: 0.02em;
                white-space: nowrap;
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

            .badge-critical,
            .badge-oos {
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
                display: none !important;
            }

            .counter-row {
                display: flex;
                gap: 0.34rem;
                flex-wrap: wrap;
                margin-top: 0.32rem;
                margin-bottom: 0.36rem;
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

            .card-details {
                display: flex;
                flex-direction: column;
                gap: 0.24rem;
                width: 100%;
                margin-top: 0.30rem;
                padding-bottom: 0.55rem;
            }

            .card-line {
                font-size: 0.80rem;
                line-height: 1.18;
                margin: 0;
                color: #1e293b;
            }

            .card-subtitle {
                font-size: 0.78rem;
                color: #64748b;
                margin-top: -0.06rem;
                margin-bottom: 0.28rem;
            }

            .editor-title {
                font-size: 1.06rem;
                font-weight: 800;
                margin-bottom: 0.10rem;
                color: #0f172a;
            }

            .editor-subtitle {
                font-size: 0.84rem;
                color: #64748b;
                margin-bottom: 0.8rem;
            }

            .section-title {
                font-size: 0.94rem;
                font-weight: 800;
                margin-top: 0.8rem;
                margin-bottom: 0.40rem;
                color: #0f172a;
            }

            .helper-text {
                font-size: 0.78rem;
                color: #475569;
                line-height: 1.5;
            }

            .readonly-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid #dbe4ee;
                border-radius: 14px;
                padding: 10px 12px;
                min-height: 52px;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
            }

            .readonly-label {
                font-size: 0.64rem;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.03em;
                margin-bottom: 0.22rem;
            }

            .readonly-value {
                font-size: 0.92rem;
                font-weight: 700;
                color: #0f172a;
                line-height: 1.25;
                word-break: break-word;
                overflow-wrap: anywhere;
            }

            .remarks-box {
                background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
                border: 1px solid #dbe4ee;
                border-radius: 14px;
                padding: 12px 14px;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
                color: #334155;
                font-size: 0.84rem;
                line-height: 1.45;
                white-space: normal;
                word-break: break-word;
                overflow-wrap: anywhere;
            }

            .stTextInput label,
            .stTextArea label,
            .stNumberInput label,
            .stSelectbox label {
                color: #334155 !important;
                font-weight: 600 !important;
            }

            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input {
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