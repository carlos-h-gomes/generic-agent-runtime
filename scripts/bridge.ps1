[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $BridgeArgs
)

$python = Get-Command python -ErrorAction SilentlyContinue
$prefix = @()
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    $prefix = @('-3')
}
if (-not $python) {
    Write-Error 'Harness requires Python 3.10 or newer.'
    exit 2
}
& $python.Source @prefix -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Harness requires Python 3.10 or newer.'
    exit 2
}
& $python.Source @prefix (Join-Path $PSScriptRoot 'bridge.py') @BridgeArgs
exit $LASTEXITCODE
