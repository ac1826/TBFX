$ErrorActionPreference = "Stop"

if (-not $env:DASHBOARD_PASSWORD) {
    $secure = Read-Host "请输入看板访问密码" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $env:DASHBOARD_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

node (Join-Path $PSScriptRoot "tools\encrypt_pages.js")

git -C $PSScriptRoot diff --quiet -- index.html 2026-dashboard.html
if ($LASTEXITCODE -eq 0) {
    Write-Host "看板文件没有变化，不需要提交。"
    exit 0
}

git -C $PSScriptRoot add index.html 2026-dashboard.html
git -C $PSScriptRoot commit -m "Update dashboard"
git -C $PSScriptRoot push
