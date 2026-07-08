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
    .portal-inner {
        border: 1px solid rgba(143, 172, 205, .48);
        border-radius: 26px;
        background: rgba(255,255,255,.88);
        padding: 44px;
        box-shadow: 0 24px 68px rgba(8, 33, 63, .10);
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
    .stButton > button {
        width: 100%;
        min-height: 58px;
        border-radius: 13px;
        border: 0;
        background: #0f766e;
        color: #fff;
        font-size: 20px;
        font-weight: 800;
    }
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
    @media (max-width: 900px) {
        .portal-shell { padding: 36px 18px; }
        .portal-inner { padding: 24px; }
        .topbar { display: block; }
        .portal-note { margin-top: 12px; }
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
    st.rerun()


def go_home() -> None:
    st.query_params.clear()
    st.rerun()


def render_portal() -> None:
    missing_files = [item["filename"] for item in DASHBOARDS.values() if not (STATIC_DIR / item["filename"]).exists()]

    st.markdown('<main class="portal-shell">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand"><div class="brand-mark"></div><div>{APP_TITLE}</div></div>
            <div class="portal-note">Streamlit 托管 · 两份 HTML 整合入口</div>
        </div>
        <section class="portal-inner">
        """,
        unsafe_allow_html=True,
    )
    st.title("选择看板")

    if missing_files:
        st.error("缺少报表文件：" + "、".join(missing_files))
    else:
        left, right = st.columns(2, gap="large")
        with left:
            st.subheader(DASHBOARDS["sales"]["title"])
            st.write(DASHBOARDS["sales"]["description"])
            st.button("打开看板", key="open_sales", on_click=choose_dashboard, args=("sales",))
        with right:
            st.subheader(DASHBOARDS["yoy"]["title"])
            st.write(DASHBOARDS["yoy"]["description"])
            st.button("打开看板", key="open_yoy", on_click=choose_dashboard, args=("yoy",))

    st.markdown("</section></main>", unsafe_allow_html=True)


def render_dashboard(dashboard_key: str) -> None:
    dashboard = DASHBOARDS[dashboard_key]
    path = dashboard_file(dashboard_key)
    if not path.exists():
        st.error(f"找不到报表文件：{dashboard['filename']}")
        return

    st.markdown(
        f"""
        <div class="viewer-header">
            <div class="viewer-title">{dashboard["title"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.button("返回选择看板", on_click=go_home)
    html = path.read_text(encoding="utf-8", errors="replace")
    components.html(html, height=1200, scrolling=True)


current = selected_dashboard()
if current:
    render_dashboard(current)
else:
    render_portal()
