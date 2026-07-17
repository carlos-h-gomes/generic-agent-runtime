[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('validate', 'lint', 'test', 'security', 'cost', 'runtime', 'bridge', 'package')]
    [string] $Command = 'validate',

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RemainingArgs
)

$script:HarnessExitCode = 0
$script:PythonExe = $null
$script:PythonPrefix = @()
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Initialize-HarnessPython {
    $candidates = @(
        @{ Name = 'python'; Prefix = @() },
        @{ Name = 'py'; Prefix = @('-3') }
    )
    foreach ($candidate in $candidates) {
        $commandInfo = Get-Command $candidate.Name -ErrorAction SilentlyContinue
        if (-not $commandInfo) { continue }
        $candidatePrefix = @($candidate.Prefix)
        & $commandInfo.Source @candidatePrefix -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) {
            $script:PythonExe = $commandInfo.Source
            $script:PythonPrefix = $candidatePrefix
            return $true
        }
    }
    Write-Error 'Harness requires Python 3.10 or newer.'
    return $false
}

function Invoke-HarnessPython {
    param([string] $Script, [string[]] $Arguments)
    & $script:PythonExe @script:PythonPrefix $Script @Arguments
    $script:HarnessExitCode = $LASTEXITCODE
}

function Invoke-SafeCommand {
    param([string] $Label, [string[]] $CommandLine)
    $config = Get-Content (Join-Path $Root 'harness.json') -Raw | ConvertFrom-Json
    $safeArgs = @(
        '-B', 'scripts/safe_exec.py',
        '--label', $Label,
        '--timeout', [string]$config.execution_limits.runtime_command_timeout_seconds,
        '--grace', [string]$config.execution_limits.kill_grace_seconds,
        '--tail-lines', [string]$config.execution_limits.failure_tail_lines,
        '--'
    ) + $CommandLine
    & $script:PythonExe @script:PythonPrefix @safeArgs
    $script:HarnessExitCode = $LASTEXITCODE
}

function Invoke-NativeLint {
    $commandLine = @($script:PythonExe) + $script:PythonPrefix + @('-B', 'scripts/runtime_check.py', '--static')
    Invoke-SafeCommand 'Harness structural lint' $commandLine
    if ($script:HarnessExitCode -ne 0) { return }

    $parseErrors = @()
    foreach ($path in @('run.ps1', 'bridge.ps1')) {
        $tokens = $null
        $found = $null
        [void][System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot $path), [ref]$tokens, [ref]$found)
        $parseErrors += $found
    }
    if ($parseErrors.Count) {
        $parseErrors | ForEach-Object { [Console]::Error.WriteLine($_.Message) }
        $script:HarnessExitCode = 1
        return
    }

    $bash = Get-Command bash -ErrorAction SilentlyContinue
    if ($bash) {
        foreach ($shellScript in Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.sh') {
            $relativeShellPath = 'scripts/' + $shellScript.Name
            & $bash.Source -n $relativeShellPath
            if ($LASTEXITCODE -ne 0) {
                $script:HarnessExitCode = $LASTEXITCODE
                return
            }
        }
    }

    Invoke-HarnessPython 'scripts/project_checks.py' @('lint')
}

function Invoke-NativeTest {
    $commandLine = @($script:PythonExe) + $script:PythonPrefix + @('-B', 'scripts/test_runtime.py')
    Invoke-SafeCommand 'Harness functional tests' $commandLine
    if ($script:HarnessExitCode -ne 0) { return }
    Invoke-HarnessPython 'scripts/project_checks.py' @('test')
}

function Invoke-NativeValidate {
    $incomplete = $false

    Invoke-NativeLint
    if ($script:HarnessExitCode -eq 3) { $incomplete = $true }
    elseif ($script:HarnessExitCode -ne 0) { return }

    Invoke-NativeTest
    if ($script:HarnessExitCode -eq 3) { $incomplete = $true }
    elseif ($script:HarnessExitCode -ne 0) { return }

    if ($RemainingArgs -contains '--full') {
        foreach ($mode in @('build', 'security')) {
            Invoke-HarnessPython 'scripts/project_checks.py' @($mode)
            if ($script:HarnessExitCode -eq 3) { $incomplete = $true }
            elseif ($script:HarnessExitCode -ne 0) { return }
        }
    }

    if ($incomplete) {
        Write-Output 'INCOMPLETE validation: one or more applicable checks were unavailable.'
        $script:HarnessExitCode = 3
    } else {
        Write-Output 'PASS validation completed.'
        $script:HarnessExitCode = 0
    }
}

if (-not (Initialize-HarnessPython)) { exit 2 }

switch ($Command) {
    'bridge'   { Invoke-HarnessPython 'scripts/bridge.py' $RemainingArgs }
    'runtime'  { Invoke-HarnessPython 'scripts/runtime_check.py' $RemainingArgs }
    'package'  { Invoke-HarnessPython 'scripts/package_runtime.py' $RemainingArgs }
    'cost'     { Invoke-HarnessPython 'scripts/cost_check.py' $RemainingArgs }
    'security' { Invoke-HarnessPython 'scripts/project_checks.py' @('security') }
    'lint'     { Invoke-NativeLint }
    'test'     { Invoke-NativeTest }
    default    { Invoke-NativeValidate }
}
exit $script:HarnessExitCode
