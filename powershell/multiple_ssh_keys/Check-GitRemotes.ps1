# Define repo groups with expected host aliases
$repoGroups = @{
    "HCLTech GitHub" = @(
        "d:\hcltech_git\cms-techdocs-deg",
        "d:\hcltech_git\cms-techdocs-eium",
        "d:\hcltech_git\cms-techdocs-snap"
    )
    "HPE GitHub" = @(
        "d:\hpe_git\5g-user-docs-common",
        "d:\hpe_git\AQC",
        "d:\hpe_git\charging_gateway",
        "d:\hpe_git\cmb",
        "d:\hpe_git\cms-techdocs-5gcs",
        "d:\hpe_git\cms-techdocs-audit-tool",
        "d:\hpe_git\cms-techdocs-deg",
        "d:\hpe_git\cms-techdocs-dsp",
        "d:\hpe_git\cms-techdocs-eir",
        "d:\hpe_git\cms-techdocs-ins",
        "d:\hpe_git\cms-techdocs-nwdaf",
        "d:\hpe_git\cms-techdocs-ocmp",
        "d:\hpe_git\cms-techdocs-rspm",
        "d:\hpe_git\cms-techdocs-snap",
        "d:\hpe_git\cms-techdocs-tas",
        "d:\hpe_git\cms-techdocs-ts43router",
        "d:\hpe_git\cms-techdocs-vtemip",
        "d:\hpe_git\cms-techdocs-wifi-auth-gateway",
        "d:\hpe_git\cms-techdocs-wso",
        "d:\hpe_git\deg",
        "d:\hpe_git\deg_be_if",
        "d:\hpe_git\doc_review_automation",
        "d:\hpe_git\eium",
        "d:\hpe_git\eIUM-Mediation-Roaming-Support",
        "d:\hpe_git\esim_primary",
        "d:\hpe_git\GBA",
        "d:\hpe_git\gtp_router",
        "d:\hpe_git\Home_Device",
        "d:\hpe_git\https_router",
        "d:\hpe_git\RadAuth",
        "d:\hpe_git\review_automation",
        "d:\hpe_git\rspm_consumer_release_notes",
        "d:\hpe_git\sib",
        "d:\hpe_git\sm_im",
        "d:\hpe_git\terminology",
        "d:\hpe_git\vale_linter",
        "d:\hpe_git\vdeg",
        "d:\hpe_git\vdra"
    )
}

# Patterns to check in remote URLs
$hostPatterns = @{
    "HCLTech GitHub" = "github.com:ctg-bss"
    "HPE GitHub" = "github.hpe.com"
}

Write-Host "Checking Git remotes for your repos..."

foreach ($group in $repoGroups.GetEnumerator()) {
    $groupName = $group.Key
    $paths = $group.Value

    Write-Host "`n--- $groupName ---"

    foreach ($repoPath in $paths) {
        if (-Not (Test-Path $repoPath)) {
            Write-Host "Folder not found: $repoPath" -ForegroundColor Yellow
            continue
        }

        # Move to repo folder
        Push-Location $repoPath

        # Check if this is a git repo
        if (-Not (Test-Path ".git")) {
            Write-Host "Not a git repo: $repoPath" -ForegroundColor Yellow
            Pop-Location
            continue
        }

        # Get origin remote URL
        $remoteUrl = git remote get-url origin 2>$null

        if ([string]::IsNullOrEmpty($remoteUrl)) {
            Write-Host "No origin remote set in $repoPath" -ForegroundColor Yellow
            Pop-Location
            continue
        }

        # Check if remote URL contains expected pattern
        $expectedPattern = $hostPatterns[$groupName]

        if ($remoteUrl -like "*$expectedPattern*") {
            $matchStatus = "matches expected host"
        }
        else {
            $matchStatus = "does NOT match expected host ($expectedPattern)"
        }

        Write-Host "$repoPath"
        Write-Host "   Remote URL: $remoteUrl"
        Write-Host "   Status: $matchStatus"

        Pop-Location
    }
}

Write-Host "`nCheck complete."
