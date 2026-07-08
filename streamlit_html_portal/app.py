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
    },
    "yoy": {
        "title": "2026 vs 2025 同比分析",
        "description": "查看销量、销额、净边贡的同比增减，以及渠道、产品、区域变化。",
        "filename": "2026-vs-2025-yoy-dashboard.html",
    },
}


st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .stApp {
        background:
            linear-gradient(rgba(177, 205, 236, .34) 1px, transparent 1px),
            linear-gradient(90deg, rgba(177, 205, 236, .34) 1px, transparent 1px),
            radial-gradient(circle at 14% 8%, rgba(255,255,255,.92), transparent 28%),
            linear-gradient(120deg, #dfeefa 0%, #f8fbff 46%, #d9f0f2 100%);
        background-size: 48px 48px, 48px 48px, auto, auto;
    }
    .block-container {
        max-width: 1240px;
        padding: 34px 28px 44px 28px;
    }
    .portal-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
    }
    .portal-brand {
        display: flex;
        align-items: center;
        gap: 14px;
        color: #08213f;
        font-size: 22px;
        font-weight: 800;
    }
    .portal-mark {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1565c0, #009688);
        box-shadow: 0 18px 34px rgba(0, 96, 120, .18);
    }
    .portal-note {
        color: #29445f;
        font-size: 15px;
    }
    .portal-hero {
        border: 1px solid rgba(143, 172, 205, .48);
        border-radius: 22px;
        background:
            radial-gradient(circle at 92% 16%, rgba(15,118,110,.10), transparent 34%),
            rgba(255,255,255,.90);
        padding: 34px 36px;
        margin-bottom: 22px;
        box-shadow: 0 22px 58px rgba(8, 33, 63, .10);
    }
    .portal-hero h1 {
        margin: 0 0 10px 0;
        color: #08213f;
        font-size: 36px;
        line-height: 1.12;
        letter-spacing: 0;
    }
    .portal-hero p {
        max-width: 780px;
        margin: 0;
        color: #526a84;
        font-size: 17px;
        line-height: 1.7;
    }
    div[data-testid="column"] {
        border: 1px solid #d6e4f2;
        border-radius: 20px;
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        padding: 28px 30px 26px 30px;
        min-height: 245px;
        box-shadow: 0 16px 42px rgba(8, 33, 63, .08);
    }
    div[data-testid="column"] h3 {
        color: #08213f;
        font-size: 28px;
        line-height: 1.25;
        margin-bottom: 14px;
    }
    div[data-testid="column"] p {
        color: #526a84;
        font-size: 16px;
        line-height: 1.65;
    }
    .stButton > button {
        width: 100%;
        min-height: 54px;
        border-radius: 12px;
        border: 0;
        background: #0f766e;
        color: #fff;
        font-size: 18px;
        font-weight: 800;
        margin-top: 24px;
        box-shadow: 0 12px 28px rgba(15,118,110,.18);
    }
    .stButton > button:hover {
        background: #0b625c;
        color: #fff;
        border: 0;
    }
    .viewer-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 14px 18px;
        margin-bottom: 12px;
        border: 1px solid #d8e4f2;
        border-radius: 14px;
        background: rgba(255,255,255,.92);
        color: #08213f;
        font-size: 20px;
        font-weight: 800;
    }
    @media (max-width: 900px) {
        .block-container { padding: 28px 18px; }
        .portal-topbar { display: block; }
        .portal-note { margin-top: 12px; }
        .portal-hero { padding: 24px; }
        .portal-hero h1 { font-size: 30px; }
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


def choose_dashboard(dashboard_key: str) -> None:
    st.query_params["dashboard"] = dashboard_key


def go_home() -> None:
    st.query_params.clear()


def render_portal() -> None:
    missing_files = [item["filename"] for item in DASHBOARDS.values() if not (STATIC_DIR / item["filename"]).exists()]

    st.markdown(
        f"""
        <div class="portal-topbar">
            <div class="portal-brand"><div class="portal-mark"></div><div>{APP_TITLE}</div></div>
            <div class="portal-note">两份 HTML 看板 · Streamlit 在线入口</div>
        </div>
        <div class="portal-hero">
            <h1>选择看板</h1>
            <p>把年度销售贡献和同比变化集中到一个入口。选择下方看板后，会在当前页面直接打开对应分析。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if missing_files:
        st.error("缺少报表文件：" + "、".join(missing_files))
        return

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader(DASHBOARDS["sales"]["title"])
        st.write(DASHBOARDS["sales"]["description"])
        st.button("打开看板", key="open_sales", on_click=choose_dashboard, args=("sales",))
    with right:
        st.subheader(DASHBOARDS["yoy"]["title"])
        st.write(DASHBOARDS["yoy"]["description"])
        st.button("打开看板", key="open_yoy", on_click=choose_dashboard, args=("yoy",))


def render_dashboard(dashboard_key: str) -> None:
    dashboard = DASHBOARDS[dashboard_key]
    path = dashboard_file(dashboard_key)
    if not path.exists():
        st.error(f"找不到报表文件：{dashboard['filename']}")
        return

    st.markdown(f'<div class="viewer-title">{dashboard["title"]}</div>', unsafe_allow_html=True)
    st.button("返回选择看板", on_click=go_home)
    html = path.read_text(encoding="utf-8", errors="replace")
    components.html(html, height=1200, scrolling=True)


current = selected_dashboard()
if current:
    render_dashboard(current)
else:
    render_portal()
