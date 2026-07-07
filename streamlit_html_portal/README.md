# PFS Streamlit HTML Portal

这个 Streamlit 项目会把两份离线 HTML 看板整合到一个入口页里，不经过 GitHub Pages 中转。
首页用于选择看板，点击后由 Streamlit 组件直接渲染对应 HTML。

## 本地运行

```powershell
cd C:\Users\Lenovo\Documents\Codex\2026-05-20\files-mentioned-by-the-user-customer\streamlit_html_portal
py -3 -m streamlit run app.py
```

## 部署到 Streamlit Cloud

1. 将整个 `streamlit_html_portal` 文件夹上传到一个 GitHub 仓库。
2. 在 Streamlit Cloud 选择该仓库。
3. Main file path 填：`streamlit_html_portal/app.py`。
4. 部署完成后，打开生成的 `*.streamlit.app` 地址。

## 文件说明

- `app.py`：Streamlit 入口页面，提供两个看板入口，并在 Streamlit 内渲染 HTML。
- `static/2026-sales-dashboard.html`：2026年销售数据看板。
- `static/2026-vs-2025-yoy-dashboard.html`：2026 vs 2025 同比分析。
- `.streamlit/config.toml`：Streamlit 主题配置。
