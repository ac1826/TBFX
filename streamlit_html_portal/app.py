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
        "button_class": "sales",
    },
    "yoy": {
        "title": "2026 vs 2025 同比分析",
        "description": "查看销量、销额、净边贡的同比增减，以及渠道、产品、区域变化。",
        "filename": "2026-vs-2025-yoy-dashboard.html",
        "button_class": "yoy",
    },
}


st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    #MainMenu, header, footer { visibility: hidden; }
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] { display: none; }
    .stApp {
        background:
            linear-gradient(rgba(166, 199, 232, .36) 1px, transparent 1px),
            linear-gradient(90deg, rgba(166, 199, 232, .36) 1px, transparent 1px),
            radial-gradient(circle at 9% 13%, rgba(255,255,255,.96), transparent 30%),
            linear-gradient(112deg, #dcecf8 0%, #f8fbff 45%, #d9f1f2 100%);
        background-size: 48px 48px, 48px 48px, auto, auto;
        color: #08213f;
    }
    .block-container {
        max-width: 100%;
        padding: 0;
    }
    .portal-wrap {
        min-height: 100vh;
        box-sizing: border-box;
        padding: 92px 7.4vw 80px;
    }
    .portal-topbar {
        max-width: 1500px;
        margin: 0 auto 34px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }
    .portal-brand {
        display: flex;
        align-items: center;
        gap: 18px;
        color: #08213f;
        font-size: 22px;
        font-weight: 900;
        letter-spacing: 0;
    }
    .portal-mark {
        width: 52px;
        height: 52px;
        border-radius: 13px;
        background: linear-gradient(135deg, #1477bd 0%, #008879 100%);
        box-shadow: 0 20px 38px rgba(0, 91, 126, .18);
        flex: 0 0 auto;
    }
    .portal-note {
        color: #29445f;
        font-size: 17px;
        font-weight: 500;
        white-space: nowrap;
    }
    .portal-panel {
        max-width: 1500px;
        margin: 0 auto;
        border: 1px solid rgba(158, 186, 215, .62);
        border-radius: 28px;
        background: rgba(255, 255, 255, .92);
        box-shadow: 0 28px 76px rgba(8, 33, 63, .11);
        padding: 62px 56px 54px;
    }
    .portal-panel h1 {
        margin: 0 0 44px;
        color: #08213f;
        font-size: 40px;
        line-height: 1.15;
        font-weight: 900;
        letter-spacing: 0;
    }
    .portal-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 22px;
    }
    .dashboard-card {
        min-height: 292px;
        border: 1px solid #d5e5f3;
        border-radius: 22px;
        background:
            radial-gradient(circle at 96% 4%, rgba(15,118,110,.08), transparent 30%),
            linear-gradient(180deg, #fff 0%, #f9fcff 100%);
        box-sizing: border-box;
        padding: 58px 42px 36px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .dashboard-card h2 {
        margin: 0 0 24px;
        color: #08213f;
        font-size: 34px;
        line-height: 1.25;
        font-weight: 900;
        letter-spacing: 0;
    }
    .dashboard-card p {
        margin: 0;
        color: #536b86;
        font-size: 19px;
        line-height: 1.7;
        font-weight: 500;
    }
    .dashboard-link {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        min-height: 60px;
        margin-top: 42px;
        border-radius: 13px;
        color: #fff !important;
        text-decoration: none !important;
        font-size: 23px;
        font-weight: 900;
        letter-spacing: 0;
        transition: transform .15s ease, filter .15s ease, box-shadow .15s ease;
    }
    .dashboard-link:hover {
        transform: translateY(-1px);
        filter: brightness(.98);
    }
    .dashboard-link.sales {
        background: #0f7f73;
        box-shadow: 0 16px 32px rgba(15,127,115,.18);
    }
    .dashboard-link.yoy {
        background: #0a294b;
        box-shadow: 0 16px 32px rgba(10,41,75,.18);
    }
    .viewer-shell {
        padding: 14px 18px 22px;
    }
    .viewer-topbar {
        position: sticky;
        top: 0;
        z-index: 50;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 12px 14px;
        margin: 0 0 12px;
        border: 1px solid #d8e4f2;
        border-radius: 14px;
        background: rgba(255,255,255,.94);
        box-shadow: 0 10px 28px rgba(8, 33, 63, .08);
    }
    .viewer-title {
        color: #08213f;
        font-size: 19px;
        font-weight: 900;
    }
    .stButton > button {
        min-height: 42px;
        border-radius: 10px;
        border: 1px solid #c9d8e8;
        background: #fff;
        color: #08213f;
        font-weight: 800;
    }
    @media (max-width: 1000px) {
        .portal-wrap { padding: 54px 20px; }
        .portal-topbar { align-items: flex-start; }
        .portal-note { white-space: normal; text-align: right; }
        .portal-panel { padding: 36px 26px; }
        .portal-grid { grid-template-columns: 1fr; }
        .dashboard-card { min-height: 250px; padding: 38px 30px 30px; }
        .dashboard-card h2 { font-size: 28px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def selected_dashboard() -> str | None:
    value = st.query_params.get("dashboard")
    return value if value in DASHBOARDS else None


def dashboard_file(dashboard_key: str) -> Path:
    return STATIC_DIR / DASHBOARDS[dashboard_key]["filename"]


def go_home() -> None:
    st.query_params.clear()


def render_portal() -> None:
    missing_files = [
        item["filename"]
        for item in DASHBOARDS.values()
        if not (STATIC_DIR / item["filename"]).exists()
    ]
    if missing_files:
        st.error("缺少报表文件：" + "、".join(missing_files))
        return

    cards = "".join(
        f'<article class="dashboard-card"><div><h2>{item["title"]}</h2><p>{item["description"]}</p></div><a class="dashboard-link {item["button_class"]}" href="?dashboard={key}" target="_self">打开看板</a></article>'
        for key, item in DASHBOARDS.items()
    )
    portal_html = (
        '<main class="portal-wrap">'
        '<div class="portal-topbar">'
        f'<div class="portal-brand"><div class="portal-mark"></div><div>{APP_TITLE}</div></div>'
        '<div class="portal-note">Streamlit 托管 · 两份 HTML 整合入口</div>'
        '</div>'
        '<section class="portal-panel">'
        '<h1>选择看板</h1>'
        f'<div class="portal-grid">{cards}</div>'
        '</section>'
        '</main>'
    )
    st.markdown(portal_html, unsafe_allow_html=True)


def render_dashboard(dashboard_key: str) -> None:
    dashboard = DASHBOARDS[dashboard_key]
    path = dashboard_file(dashboard_key)
    if not path.exists():
        st.error(f"找不到报表文件：{dashboard['filename']}")
        return

    st.markdown(
        f'<div class="viewer-shell"><div class="viewer-topbar"><div class="viewer-title">{dashboard["title"]}</div></div></div>',
        unsafe_allow_html=True,
    )
    if st.button("返回选择看板"):
        go_home()
    html = path.read_text(encoding="utf-8", errors="replace")
    components.html(html, height=1200, scrolling=True)


current = selected_dashboard()
if current:
    render_dashboard(current)
else:
    render_portal()
