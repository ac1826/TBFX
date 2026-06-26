$ErrorActionPreference = "Stop"

$source = "F:\llqdocument\大成文件\客户贡献分析\26年与25年_1-5月数据对比分析.html"
$target = Join-Path $PSScriptRoot "index.html"

Copy-Item -LiteralPath $source -Destination $target -Force

git -C $PSScriptRoot diff --quiet -- index.html
if ($LASTEXITCODE -eq 0) {
    Write-Host "index.html 没有变化，不需要提交。"
    exit 0
}

git -C $PSScriptRoot add index.html
git -C $PSScriptRoot commit -m "Update dashboard"
git -C $PSScriptRoot push
