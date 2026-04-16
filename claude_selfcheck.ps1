param(
    [string]$BaseUrl = "https://key.simpleai.com.cn/v1",
    [string]$ApiKey = "",
    [string]$Model = "claude-opus-4-6",
    [int]$TimeoutSec = 20
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Section([string]$title) {
    Write-Host ""
    Write-Host "=== $title ===" -ForegroundColor Cyan
}

function Write-Ok([string]$msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

function Write-WarnLine([string]$msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

function Write-Fail([string]$msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
}

function Get-HostFromUrl([string]$url) {
    try {
        return ([System.Uri]$url).Host
    } catch {
        throw "Invalid BaseUrl: $url"
    }
}

function Invoke-GetSafe([string]$url) {
    try {
        $resp = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec $TimeoutSec
        return @{ ok = $true; status = [int]$resp.StatusCode; body = $resp.Content; err = "" }
    } catch {
        $status = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $status = [int]$_.Exception.Response.StatusCode
        }
        return @{ ok = $false; status = $status; body = ""; err = $_.Exception.Message }
    }
}

function Invoke-PostSafe([string]$url, [hashtable]$headers, [string]$body) {
    try {
        $resp = Invoke-WebRequest -Uri $url -Method Post -Headers $headers -Body $body -TimeoutSec $TimeoutSec
        return @{ ok = $true; status = [int]$resp.StatusCode; body = $resp.Content; err = "" }
    } catch {
        $status = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $status = [int]$_.Exception.Response.StatusCode
        }
        return @{ ok = $false; status = $status; body = ""; err = $_.Exception.Message }
    }
}

Write-Host "Claude gateway self-check start..." -ForegroundColor Magenta
Write-Host "BaseUrl: $BaseUrl"
Write-Host "Model:   $Model"

$hostName = Get-HostFromUrl $BaseUrl

Write-Section "1) DNS resolve"
try {
    $dns = Resolve-DnsName -Name $hostName -Type A -ErrorAction Stop
    $ips = ($dns | Select-Object -ExpandProperty IPAddress -ErrorAction SilentlyContinue) -join ", "
    if ([string]::IsNullOrWhiteSpace($ips)) {
        Write-Ok "DNS resolved (no A record details)"
    } else {
        Write-Ok "DNS resolved: $ips"
    }
} catch {
    Write-Fail "DNS resolve failed: $($_.Exception.Message)"
    exit 1
}

Write-Section "2) TCP 443 connectivity"
try {
    $tcp = Test-NetConnection $hostName -Port 443 -WarningAction SilentlyContinue
    if ($tcp.TcpTestSucceeded) {
        Write-Ok "Port 443 reachable"
    } else {
        Write-Fail "Port 443 unreachable"
        exit 1
    }
} catch {
    Write-Fail "TCP check failed: $($_.Exception.Message)"
    exit 1
}

Write-Section "3) Endpoint probe"
$baseProbe = Invoke-GetSafe -url $BaseUrl
if ($baseProbe.ok) {
    Write-Ok "BaseUrl reachable, HTTP $($baseProbe.status)"
} else {
    if ($baseProbe.status) {
        Write-WarnLine "BaseUrl HTTP $($baseProbe.status) (may be normal)"
    } else {
        Write-Fail "BaseUrl request failed: $($baseProbe.err)"
        exit 1
    }
}

$modelsUrl = "$BaseUrl/models"
$modelsProbe = Invoke-GetSafe -url $modelsUrl
if ($modelsProbe.ok) {
    Write-Ok "/models reachable, HTTP $($modelsProbe.status)"
} else {
    if ($modelsProbe.status -eq 401 -or $modelsProbe.status -eq 403) {
        Write-Ok "/models auth error means service is online, HTTP $($modelsProbe.status)"
    } elseif ($modelsProbe.status) {
        Write-WarnLine "/models HTTP $($modelsProbe.status): $($modelsProbe.err)"
    } else {
        Write-Fail "/models network error: $($modelsProbe.err)"
    }
}

Write-Section "4) Proxy env check"
$proxyVars = "HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","NO_PROXY","http_proxy","https_proxy","all_proxy","no_proxy"
$foundProxy = $false
foreach ($k in $proxyVars) {
    $v = [Environment]::GetEnvironmentVariable($k, "Process")
    if (-not [string]::IsNullOrWhiteSpace($v)) {
        $foundProxy = $true
        Write-WarnLine "$k=$v"
    }
}
if (-not $foundProxy) {
    Write-Ok "No process-level proxy variables"
}

Write-Section "5) Anthropic minimal request (/messages)"
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-WarnLine "No -ApiKey provided, skip /messages test"
    Write-Host ""
    Write-Host "Run this command:" -ForegroundColor Yellow
    Write-Host '.\claude_selfcheck.ps1 -ApiKey "sk-xxxx"'
    exit 0
}

$headers = @{
    "x-api-key" = $ApiKey
    "anthropic-version" = "2023-06-01"
    "content-type" = "application/json"
}

$payload = @{
    model = $Model
    max_tokens = 16
    messages = @(
        @{
            role = "user"
            content = "ping"
        }
    )
} | ConvertTo-Json -Depth 6

$msgUrl = "$BaseUrl/messages"
$msgProbe = Invoke-PostSafe -url $msgUrl -headers $headers -body $payload

if ($msgProbe.ok) {
    Write-Ok "/messages success, HTTP $($msgProbe.status)"
    Write-Host ""
    Write-Host "Conclusion: network and gateway are mostly fine. If Claude Code still fails, check client config/env vars." -ForegroundColor Green
    exit 0
}

if ($msgProbe.status -eq 401 -or $msgProbe.status -eq 403) {
    Write-Fail "/messages auth failed, check ApiKey correctness/expiry"
    exit 2
}
if ($msgProbe.status -eq 404) {
    Write-Fail "/messages 404, gateway may not support Anthropic API or BaseUrl is wrong"
    exit 3
}
if ($msgProbe.status -eq 400) {
    Write-WarnLine "/messages 400, model name may be invalid: $Model"
    Write-WarnLine "Query /models for exact model id, then retry"
    exit 4
}
if ($msgProbe.status) {
    Write-Fail "/messages HTTP $($msgProbe.status): $($msgProbe.err)"
    exit 5
}

Write-Fail "/messages network error: $($msgProbe.err)"
exit 6
