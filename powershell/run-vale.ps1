<#
run-vale.ps1
Runs Vale with context-aware behavior for hook, manual, and CI usage.
#>

param(
    [ValidateSet("hook", "manual", "ci")]
    [string]$RunContext = "hook",

    [switch]$Json,
    [string]$BaseBranch = "origin/main"
)

# -----------------------------
# Configuration
# -----------------------------
$ValeExe = "vale"
$ResultsDir = ".vale/results"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$JsonOutput = Join-Path $ResultsDir "vale-$RunContext-$Timestamp.json"

New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

# -----------------------------
# Helper functions
# -----------------------------
function Get-StagedFiles {
    git diff --cached --name-only --diff-filter=ACM |
        Where-Object { $_ -match '\.(dita|md|adoc)$' }
}

function Get-WorkingTreeFiles {
    git diff --name-only --diff-filter=ACM |
        Where-Object { $_ -match '\.(dita|md|adoc)$' }
}

function Get-DiffFiles($Base) {
    git diff --name-only $Base |
        Where-Object { $_ -match '\.(dita|md|adoc)$' }
}

# -----------------------------
# Determine behavior by context
# -----------------------------
$Files = @()
$AllowFixes = $false
$FailOnWarnings = $false

switch ($RunContext) {
    "hook" {
        $Files = Get-StagedFiles
        $AllowFixes = $false
        $FailOnWarnings = $false
    }
    "manual" {
        $Files = Get-WorkingTreeFiles
        $AllowFixes = $true
        $FailOnWarnings = $false
    }
    "ci" {
        $Files = Get-DiffFiles $BaseBranch
        $AllowFixes = $false
        $FailOnWarnings = $true
    }
}

if (-not $Files -or $Files.Count -eq 0) {
    Write-Host "✓ Vale: no applicable files to check"
    exit 0
}

# -----------------------------
# Build Vale arguments
# -----------------------------
$ValeArgs = @()

if ($Json) {
    $ValeArgs += "--output=JSON"
}

if ($AllowFixes) {
    Write-Host "⚙ Vale manual mode: auto-fix ENABLED"
    $ValeArgs += "--fix"
}

# -----------------------------
# Run Vale
# -----------------------------
Write-Host "Running Vale ($RunContext) on $($Files.Count) file(s)..."

$Output = & $ValeExe @ValeArgs $Files 2>&1
$ExitCode = $LASTEXI
