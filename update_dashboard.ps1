$ErrorActionPreference = "Stop"

$source = "F:\llqdocument\大成文件\客户贡献分析\26年与25年_1-5月数据对比分析.html"
$target = Join-Path $PSScriptRoot "index.html"
$source2026 = "F:\llqdocument\大成文件\客户贡献分析\2026年1-5月数据分析仪表盘.html"
$target2026 = Join-Path $PSScriptRoot "2026-dashboard.html"

Copy-Item -LiteralPath $source -Destination $target -Force
Copy-Item -LiteralPath $source2026 -Destination $target2026 -Force

git -C $PSScriptRoot diff --quiet -- index.html 2026-dashboard.html
if ($LASTEXITCODE -eq 0) {
    Write-Host "看板文件没有变化，不需要提交。"
    exit 0
}

git -C $PSScriptRoot add index.html 2026-dashboard.html
git -C $PSScriptRoot commit -m "Update dashboard"
git -C $PSScriptRoot push
