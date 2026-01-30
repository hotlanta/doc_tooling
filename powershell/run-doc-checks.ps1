<#
.SYNOPSIS
  Runs documentation quality checks locally:
  - Vale (manual mode, autofix enabled)
  - PDF Analyzer (layout + link checks)

.DESCRIPTION
  Intended for iterative local use before committing.
  Produces JSON results under .vale/results/.
  Does NOT block commits or modify Git state.

.EXAMPLE
  ./run-doc-checks.ps1
#>

param(
  [string]$PdfDir = "out/pdf",
  [string]$ResultsDir = ".vale/results",
  [switch]$SkipVale,
  [switch]$SkipPdf
)

$ErrorActionPreference = "Stop"

# --------------------------------------------------
# Helpers
# --------------------------------------------------

function Ensure-Dir($Path) {
  if (-not (Test-Path $Path)) {
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Section($Title) {
  Write-Host ""
  Write-Host "==== $Title ====" -ForegroundColor Cyan
}

# --------------------------------------------------
# Setup
# --------------------------------------------------

Ensure-Dir $ResultsDir

$valeJson = Join-Path $ResultsDir "vale-manual.json"
$pdfJson  = Join-Path $ResultsDir "pdf-analysis.json"

$valeWarnings = 0
$valeErrors   = 0
$pdfWarnings  = 0
$pdfErrors    = 0

# --------------------------------------------------
# Vale
# --------------------------------------------------

if (-not $SkipVale) {
  Section "Vale (manual mode)"

  if (-not (Get-Command vale -ErrorAction SilentlyContinue)) {
    Write-Warning "Vale not found in PATH — skipping Vale checks."
  }
  else {
    Write-Host "Running Vale with autofix where possible..."

    powershell `
      -ExecutionPolicy Bypass `
      -File ./run-vale.ps1 `
      -RunContext manual `
      -Mode console | Tee-Object -Variable valeConsole

    # Re-run Vale in JSON mode for structured output
    powershell `
      -ExecutionPolicy Bypass `
      -File ./run-vale.ps1 `
      -RunContext manual `
      -Mode json `
      -OutFile $valeJson

    if (Test-Path $valeJson) {
      $valeData = Get-Content $valeJson | ConvertFrom-Json
      $valeWarnings = $valeData.summary.warning
      $valeErrors   = $valeData.summary.error
    }
  }
}

# --------------------------------------------------
# PDF Analyzer
# --------------------------------------------------

if (-not $SkipPdf) {
  Section "PDF Analysis"

  if (-not (Test-Path $PdfDir)) {
    Write-Warning "PDF directory '$PdfDir' not found — skipping PDF analysis."
  }
  else {
    $pdfs = Get-ChildItem -Path $PdfDir -Filter *.pdf -Recurse

    if (-not $pdfs) {
      Write-Warning "No PDFs found under $PdfDir."
    }
    else {
      $allPdfIssues = @()

      foreach ($pdf in $pdfs) {
        Write-Host "Analyzing $($pdf.FullName)"

        python scripts/pdf_analyzer.py `
          $pdf.FullName `
          --check-links `
          --json $pdfJson

        if (Test-Path $pdfJson) {
          $data = Get-Content $pdfJson | ConvertFrom-Json
          $allPdfIssues += $data
        }
      }

      if ($allPdfIssues.Count -gt 0) {
        $pdfWarnings = (
          $allPdfIssues |
          ForEach-Object { $_.summary.warning } |
          Measure-Object -Sum
        ).Sum

        $pdfErrors = (
          $allPdfIssues |
          ForEach-Object { $_.summary.error } |
          Measure-Object -Sum
        ).Sum

        # Write merged result
        $merged = @{
          generated = (Get-Date).ToString("s")
          pdf_count = $allPdfIssues.Count
          summary = @{
            warning = $pdfWarnings
            error   = $pdfErrors
          }
          documents = $allPdfIssues
        }

        $merged | ConvertTo-Json -Depth 6 |
          Set-Content $pdfJson -Encoding UTF8
      }
    }
  }
}

# --------------------------------------------------
# Summary
# --------------------------------------------------

Section "Summary"

Write-Host ("Vale: {0} errors, {1} warnings" -f $valeErrors, $valeWarnings)
Write-Host ("PDFs: {0} errors, {1} warnings" -f $pdfErrors,  $pdfWarnings)

Write-Host ""
Write-Host "Results written to:" -ForegroundColor DarkGray
Write-Host "  $ResultsDir"

Write-Host ""
Write-Host "No commits were blocked. Fix issues and re-run as needed." -ForegroundColor Green
