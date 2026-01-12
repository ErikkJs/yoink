<#
.SYNOPSIS
    YOINK CLI Test Script - Tests crawler functionality from command line.

.DESCRIPTION
    Runs various yoink CLI commands to test functionality locally.
    Similar to .http request files for API testing.

.PARAMETER Cleanup
    Remove all test output files after running.

.PARAMETER Quick
    Run only fast tests (skips slow rate-limiting tests).

.EXAMPLE
    .\test_crawl.ps1
    Run all tests.

.EXAMPLE
    .\test_crawl.ps1 -Quick
    Run only fast tests.

.EXAMPLE
    .\test_crawl.ps1 -Cleanup
    Run tests and clean up output files.
#>

param(
    [switch]$Cleanup,
    [switch]$Quick
)

$ErrorActionPreference = "Continue"
$OutputDir = "test_output"
$TestCount = 0
$PassCount = 0
$FailCount = 0

# ============================================================================
# Helper Functions
# ============================================================================

function Write-TestHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor DarkGray
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor DarkGray
}

function Test-Crawl {
    param(
        [string]$Name,
        [string]$Command,
        [switch]$Slow
    )

    if ($Slow -and $Quick) {
        Write-Host "  [SKIP] $Name (use -Quick to skip slow tests)" -ForegroundColor Yellow
        return
    }

    $script:TestCount++
    Write-Host ""
    Write-Host "  [$script:TestCount] $Name" -ForegroundColor White
    Write-Host "      > $Command" -ForegroundColor DarkGray

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        $output = Invoke-Expression "poetry run $Command 2>&1"
        $exitCode = $LASTEXITCODE
        $stopwatch.Stop()

        if ($exitCode -eq 0) {
            $script:PassCount++
            Write-Host "      PASS ($([math]::Round($stopwatch.Elapsed.TotalSeconds, 2))s)" -ForegroundColor Green
        } else {
            $script:FailCount++
            Write-Host "      FAIL (exit code: $exitCode)" -ForegroundColor Red
            Write-Host "      Output: $output" -ForegroundColor DarkRed
        }
    }
    catch {
        $script:FailCount++
        Write-Host "      ERROR: $_" -ForegroundColor Red
    }
}

function Show-FileContents {
    param([string]$FilePath, [int]$Lines = 5)

    if (Test-Path $FilePath) {
        Write-Host "      Preview of $FilePath`:" -ForegroundColor DarkGray
        Get-Content $FilePath -Head $Lines | ForEach-Object {
            Write-Host "        $_" -ForegroundColor DarkGray
        }
    }
}

function Test-RobotsBlocking {
    param(
        [string]$Name,
        [string]$Command,
        [string]$OutputFile,
        [string]$BlockedUrl,
        [bool]$ShouldBeBlocked
    )

    $script:TestCount++
    Write-Host ""
    Write-Host "  [$script:TestCount] $Name" -ForegroundColor White
    Write-Host "      > $Command" -ForegroundColor DarkGray
    Write-Host "      Expected: $BlockedUrl should $(if ($ShouldBeBlocked) { 'BE BLOCKED' } else { 'be crawled' })" -ForegroundColor DarkGray

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        $output = Invoke-Expression "poetry run $Command 2>&1"
        $exitCode = $LASTEXITCODE
        $stopwatch.Stop()

        if ($exitCode -ne 0) {
            $script:FailCount++
            Write-Host "      FAIL (exit code: $exitCode)" -ForegroundColor Red
            return
        }

        # Check if the blocked URL appears in output
        $fileExists = Test-Path $OutputFile
        $fileContent = if ($fileExists) { Get-Content $OutputFile -Raw -ErrorAction SilentlyContinue } else { "" }
        $fileEmpty = [string]::IsNullOrWhiteSpace($fileContent)
        $urlFound = $fileContent -match [regex]::Escape($BlockedUrl)

        if ($ShouldBeBlocked) {
            # URL should be blocked - file should be empty OR URL not in file
            if ($fileEmpty -or -not $urlFound) {
                $script:PassCount++
                $reason = if ($fileEmpty) { "no pages crawled (blocked)" } else { "URL not in output" }
                Write-Host "      PASS - $reason ($([math]::Round($stopwatch.Elapsed.TotalSeconds, 2))s)" -ForegroundColor Green
            } else {
                $script:FailCount++
                Write-Host "      FAIL - URL should have been blocked but was crawled" -ForegroundColor Red
            }
        } else {
            # URL should be crawled
            if ($urlFound) {
                $script:PassCount++
                Write-Host "      PASS - URL was crawled ($([math]::Round($stopwatch.Elapsed.TotalSeconds, 2))s)" -ForegroundColor Green
            } else {
                $script:FailCount++
                Write-Host "      FAIL - URL should have been crawled but wasn't found" -ForegroundColor Red
            }
        }
    }
    catch {
        $script:FailCount++
        Write-Host "      ERROR: $_" -ForegroundColor Red
    }
}

# ============================================================================
# Setup
# ============================================================================

Write-Host ""
Write-Host "YOINK CLI Test Runner" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta
Write-Host "Output directory: $OutputDir"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "Created output directory" -ForegroundColor Green
}

# ============================================================================
# Test 1: Basic Crawl Tests
# ============================================================================

Write-TestHeader "1. Basic Crawl Tests"

Test-Crawl -Name "Single page crawl" `
    -Command "yoink crawl https://example.com -n 1 -o $OutputDir/basic_single.jsonl"

Test-Crawl -Name "Crawl with depth" `
    -Command "yoink crawl https://httpbin.org -d 1 -n 3 -o $OutputDir/basic_depth.jsonl"

# ============================================================================
# Test 2: Output Format Tests
# ============================================================================

Write-TestHeader "2. Output Format Tests"

Test-Crawl -Name "JSON output format" `
    -Command "yoink crawl https://example.com -n 1 -f json -o $OutputDir/format_test.json"

Test-Crawl -Name "JSONL output format" `
    -Command "yoink crawl https://example.com -n 1 -f jsonl -o $OutputDir/format_test.jsonl"

Test-Crawl -Name "Text output format" `
    -Command "yoink crawl https://example.com -n 1 -f text -o $OutputDir/format_test.txt"

# Show file previews
if (Test-Path "$OutputDir/format_test.json") {
    Show-FileContents "$OutputDir/format_test.json"
}

# ============================================================================
# Test 3: Rate Limiting Tests
# ============================================================================

Write-TestHeader "3. Rate Limiting Tests"

Test-Crawl -Name "Rate limit 0.5 req/s (slow)" `
    -Command "yoink crawl https://httpbin.org -n 3 --rate-limit 0.5 -o $OutputDir/rate_limit.jsonl" `
    -Slow

Test-Crawl -Name "Request delay 0.5s" `
    -Command "yoink crawl https://example.com -n 2 --request-delay 0.5 -o $OutputDir/request_delay.jsonl" `
    -Slow

# ============================================================================
# Test 4: robots.txt Tests
# ============================================================================

Write-TestHeader "4. robots.txt Tests"

# Google blocks /search in robots.txt for all user-agents
# Test that we respect this by trying to crawl google.com with depth
# The /search links should NOT appear in output when respecting robots.txt

Test-Crawl -Name "Respect robots.txt (example.com - no restrictions)" `
    -Command "yoink crawl https://example.com -n 1 -o $OutputDir/robots_respect.jsonl"

Test-Crawl -Name "Ignore robots.txt flag works" `
    -Command "yoink crawl https://example.com -n 1 --no-robots -o $OutputDir/robots_ignore.jsonl"

# Test with a site that has actual robots.txt restrictions
# Reddit blocks everything with Disallow: /
Write-Host ""
Write-Host "  Testing robots.txt blocking with Reddit (Disallow: /)..." -ForegroundColor Yellow

Test-RobotsBlocking `
    -Name "Reddit: should be completely blocked (Disallow: /)" `
    -Command "yoink crawl https://www.reddit.com/r/python -d 0 -n 1 -o $OutputDir/robots_reddit_respect.jsonl" `
    -OutputFile "$OutputDir/robots_reddit_respect.jsonl" `
    -BlockedUrl "reddit.com" `
    -ShouldBeBlocked $true

Test-RobotsBlocking `
    -Name "Reddit: crawled with --no-robots" `
    -Command "yoink crawl https://www.reddit.com/r/python -d 0 -n 1 --no-robots -o $OutputDir/robots_reddit_ignore.jsonl" `
    -OutputFile "$OutputDir/robots_reddit_ignore.jsonl" `
    -BlockedUrl "reddit.com" `
    -ShouldBeBlocked $false

# ============================================================================
# Test 5: URL Filtering Tests
# ============================================================================

Write-TestHeader "5. URL Filtering Tests"

Test-Crawl -Name "Skip file extensions" `
    -Command "yoink crawl https://example.com -n 3 --skip-extensions pdf,zip,exe -o $OutputDir/filter_ext.jsonl"

# ============================================================================
# Test 6: Checkpoint Tests
# ============================================================================

Write-TestHeader "6. Checkpoint Tests"

Test-Crawl -Name "Crawl with checkpoint" `
    -Command "yoink crawl https://example.com -n 2 --checkpoint $OutputDir/checkpoint.jsonl"

Test-Crawl -Name "Resume from checkpoint" `
    -Command "yoink crawl https://example.com -n 3 --checkpoint $OutputDir/checkpoint.jsonl --resume"

# ============================================================================
# Test 7: Stats Command
# ============================================================================

Write-TestHeader "7. Stats Command Tests"

if (Test-Path "$OutputDir/basic_single.jsonl") {
    Test-Crawl -Name "Show stats" `
        -Command "yoink stats $OutputDir/basic_single.jsonl"

    Test-Crawl -Name "Stats as JSON" `
        -Command "yoink stats $OutputDir/basic_single.jsonl --json"
} else {
    Write-Host "  [SKIP] No data file available for stats" -ForegroundColor Yellow
}

# ============================================================================
# Test 8: Save HTML Test
# ============================================================================

Write-TestHeader "8. HTML Content Tests"

Test-Crawl -Name "Save raw HTML" `
    -Command "yoink crawl https://example.com -n 1 --save-html -o $OutputDir/with_html.jsonl"

# ============================================================================
# Test 9: Concurrency Test
# ============================================================================

Write-TestHeader "9. Concurrency Tests"

Test-Crawl -Name "High concurrency (5 workers)" `
    -Command "yoink crawl https://httpbin.org -n 5 -c 5 -o $OutputDir/concurrent.jsonl"

# ============================================================================
# Summary
# ============================================================================

Write-Host ""
Write-Host "=" * 60 -ForegroundColor DarkGray
Write-Host " TEST SUMMARY" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Total:  $TestCount" -ForegroundColor White
Write-Host "  Passed: $PassCount" -ForegroundColor Green
Write-Host "  Failed: $FailCount" -ForegroundColor $(if ($FailCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

# List output files
Write-Host "  Output files:" -ForegroundColor DarkGray
Get-ChildItem $OutputDir -File | ForEach-Object {
    $size = "{0:N2} KB" -f ($_.Length / 1KB)
    Write-Host "    - $($_.Name) ($size)" -ForegroundColor DarkGray
}

# ============================================================================
# Cleanup
# ============================================================================

if ($Cleanup) {
    Write-Host ""
    Write-Host "Cleaning up test files..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $OutputDir
    Write-Host "Removed $OutputDir" -ForegroundColor Green
}

Write-Host ""

# Exit with error code if any tests failed
if ($FailCount -gt 0) {
    exit 1
}
exit 0
