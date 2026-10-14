from pathlib import Path


def customer_yoy_runtime() -> str:
    helper_path = Path(__file__).parents[1] / "tools" / "customer_rank_yoy.js"
    helper = helper_path.read_text(encoding="utf-8").split("\nif (typeof module !== 'undefined')", 1)[0]
    helper = helper.replace("function customerRankYoyRuntime(", "function customerRankYoyRuntimeFixed(", 1)
    return (
        f"{helper}\n"
        "customerRankYoyRuntimeFixed(RAW.filter(row => String(row.mo || '').startsWith('2025.')));\n"
    )


def inject_customer_yoy(html: str) -> str:
    runtime = customer_yoy_runtime()
    marker = "    fetch('2026-vs-2025-yoy-dashboard.html').then(response => {"
    start = html.find(marker)
    if start >= 0:
        end = html.find("    window.addEventListener('resize'", start)
        if end >= 0:
            return html[:start] + runtime + html[end:]

    if "customerRankYoyRuntime(" in html:
        return html.replace("</body>", f"<script>\n{runtime}</script>\n</body>", 1)
    return html
