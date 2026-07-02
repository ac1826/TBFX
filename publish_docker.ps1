param(
    [string]$ImageName = "tbfx-dashboard:latest",
    [int]$Port = 8080,
    [switch]$SkipEncrypt
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

if (-not $SkipEncrypt) {
    if (-not $env:DASHBOARD_PASSWORD) {
        $secure = Read-Host "Enter dashboard password" -AsSecureString
        $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
        try {
            $env:DASHBOARD_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
        }
        finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
        }
    }
    node (Join-Path $Root "tools\encrypt_pages.js")
    if ($LASTEXITCODE -ne 0) { throw "Dashboard encryption failed." }
}

docker build -t $ImageName $Root
if ($LASTEXITCODE -ne 0) { throw "Docker image build failed." }

$existing = docker ps -aq --filter "name=^tbfx-dashboard$"
if ($existing) {
    docker rm -f tbfx-dashboard | Out-Null
}

docker run -d `
    --name tbfx-dashboard `
    --restart unless-stopped `
    -p "${Port}:80" `
    $ImageName | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Docker container start failed." }

Write-Host "Docker dashboard started: http://localhost:$Port/"
Write-Host "For LAN access, replace localhost with this server's IP address."
