from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


APP_TITLE = "PFS销售数据分析看板"
STATIC_DIR = Path(__file__).parent / "static"

DASHBOARDS = {
    "sales": {
        "title": "2026年销售数据看板",
        "description": "查看2026年1-6月客户、区域、渠道、品类和贡献表现。",
        "filename": "2026-sales-dashboard.html",
        "button_class": "primary",
    },
    "yoy": {
        "title": "2026 vs 2025 同比分析",
        "description": "查看销量、销额、净边贡的同比增减，以及渠道、产品、区域变化。",
        "filename": "2026-vs-2025-yoy-dashboard.html",
        "button_class": "secondary",
    },
}


st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {
        max-width: 100%;
        padding: 0;
    }
    .portal-shell {
        min-height: 100vh;
        padding: 78px 7vw;
        background:
            linear-gradient(rgba(177, 205, 236, .34) 1px, transparent 1px),
            linear-gradient(90deg, rgba(177, 205, 236, .34) 1px, transparent 1px),
            radial-gradient(circle at 12% 8%, rgba(255,255,255,.9), transparent 28%),
            linear-gradient(120deg, #dfeefa 0%, #f7fbff 48%, #d9f0f2 100%);
        background-size: 48px 48px, 48px 48px, auto, auto;
        color: #08213f;
        box-sizing: border-box;
    }
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 28px;
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 14px;
        font-size: 20px;
        font-weight: 800;
    }
    .brand-mark {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1565c0, #009688);
        box-shadow: 0 18px 34px rgba(0, 96, 120, .18);
    }
    .portal-note {
        color: #29445f;
        font-size: 15px;
    }
    .chooser {
        border: 1px solid rgba(143, 172, 205, .48);
        border-radius: 26px;
        background: rgba(255,255,255,.86);
        padding: 44px;
        box-shadow: 0 24px 68px rgba(8, 33, 63, .10);
    }
    .chooser h1 {
        margin: 0 0 20px 0;
        font-size: 34px;
        letter-spacing: 0;
    }
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 22px;
    }
    .dashboard-card {
        min-height: 268px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border: 1px solid #d6e4f2;
        border-radius: 24px;
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        padding: 34px;
    }
    .dashboard-card h2 {
        margin: 0 0 18px 0;
        font-size: 34px;
        line-height: 1.2;
        letter-spacing: 0;
        color: #08213f;
    }
    .dashboard-card p {
        margin: 0;
        color: #526a84;
        font-size: 18px;
        line-height: 1.65;
    }
    .open-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        min-height: 58px;
        margin-top: 38px;
        border-radius: 13px;
        text-decoration: none !important;
        color: white !important;
        font-size: 22px;
        font-weight: 800;
    }
    .open-link.primary { background: #0f766e; }
    .open-link.secondary { background: #0b2545; }
    .viewer-header {
        position: sticky;
        top: 0;
        z-index: 20;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 14px 18px;
        background: #f4f7fb;
        border-bottom: 1px solid #d8e4f2;
    }
    .viewer-title {
        font-size: 20px;
        font-weight: 800;
        color: #08213f;
    }
    .back-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 40px;
        padding: 0 16px;
        border: 1px solid #c8d8ea;
        border-radius: 10px;
        background: #fff;
        color: #0b2545 !important;
        text-decoration: none !important;
        font-weight: 700;
    }
    .error-box {
        margin: 40px;
        padding: 18px 20px;
        border: 1px solid #f1b8b8;
        border-radius: 12px;
        color: #8a1f1f;
        background: #fff7f7;
    }
    @media (max-width: 900px) {
        .portal-shell { padding: 36px 18px; }
        .topbar { display: block; }
        .portal-note { margin-top: 12px; }
        .chooser { padding: 24px; }
        .dashboard-grid { grid-template-columns: 1fr; }
        .dashboard-card h2 { font-size: 28px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_selected_dashboard() -> str | None:
    selected = st.query_params.get("dashboard")
    return selected if selected in DASHBOARDS else None


def dashboard_file(dashboard_key: str) -> Path:
    return STATIC_DIR / DASHBOARDS[dashboard_key]["filename"]


def render_portal() -> None:
    missing_files = [item["filename"] for item in DASHBOARDS.values() if not (STATIC_DIR / item["filename"]).exists()]
    if missing_files:
        st.markdown(
            f'<div class="error-box">缺少报表文件：{"、".join(missing_files)}</div>',
            unsafe_allow_html=True,
        )
        return

    cards = []
    for key, dashboard in DASHBOARDS.items():
        cards.append(
            f'<article class="dashboard-card">'
            f'<div><h2>{dashboard["title"]}</h2><p>{dashboard["description"]}</p></div>'
            f'<a class="open-link {dashboard["button_class"]}" href="?dashboard={key}" target="_self">打开看板</a>'
            f'</article>'
        )

    st.markdown(
        f'<main class="portal-shell">'
        f'<div class="topbar">'
        f'<div class="brand"><div class="brand-mark"></div><div>{APP_TITLE}</div></div>'
        f'<div class="portal-note">Streamlit 托管 · 两份 HTML 整合入口</div>'
        f'</div>'
        f'<section class="chooser"><h1>选择看板</h1><div class="dashboard-grid">{"".join(cards)}</div></section>'
        f'</main>',
        unsafe_allow_html=True,
    )


def render_dashboard(dashboard_key: str) -> None:
    dashboard = DASHBOARDS[dashboard_key]
    path = dashboard_file(dashboard_key)
    if not path.exists():
        st.markdown(
            f'<div class="error-box">找不到报表文件：{dashboard["filename"]}</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="viewer-header">
            <a class="back-link" href="?" target="_self">返回选择看板</a>
            <div class="viewer-title">{dashboard["title"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    html = path.read_text(encoding="utf-8", errors="replace")
    components.html(html, height=1200, scrolling=True)


selected_dashboard = get_selected_dashboard()
if selected_dashboard:
    render_dashboard(selected_dashboard)
else:
    render_portal()
