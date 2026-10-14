# PFS Streamlit 看板

本仓库只部署 Streamlit 应用。首页提供销售看板和同比看板入口，HTML 在浏览器端展示。

## 本地运行

在仓库根目录运行：

```powershell
py -3 -m pip install -r streamlit_html_portal/requirements.txt
py -3 -m streamlit run streamlit_html_portal/app.py
```

## Streamlit Community Cloud

选择此 GitHub 仓库，主文件路径填写 `streamlit_html_portal/app.py`。应用配置位于仓库根目录的 `.streamlit/config.toml`，其中启用了 WebSocket 压缩。

## 文件

- `streamlit_html_portal/app.py`：Streamlit 入口和看板选择页。
- `streamlit_html_portal/static/*.html.gz`：两份原始 HTML 看板的 gzip 无损副本；运行时解压后原样展示。
- `streamlit_html_portal/static/ka-customer-merge.json` 和 `customer-master-september.json`：客户合并和客户主数据，供看板数据刷新脚本使用。
- `tools/update_dashboard_data.py`：更新看板数据并重新生成 gzip 文件。
- `tools/customer_rank_yoy.js`：客户排名同比提示逻辑。
- `tests/`：数据更新和同比逻辑测试。

大区同比规则及数据口径由 `tools/update_dashboard_data.py` 维护。HTML gzip 只改变存储和传输形式，不改变解压后的看板内容。
