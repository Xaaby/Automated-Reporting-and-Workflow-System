# System Test Script
Write-Host "========================================"
Write-Host "Automated Reporting System - Test Suite"
Write-Host "========================================"
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..."
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
    Write-Host "   ✓ Health check: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($response.Content)"
} catch {
    Write-Host "   ✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Reports API
Write-Host "2. Testing Reports API..."
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/api/reports -UseBasicParsing
    Write-Host "   ✓ Reports API: $($response.StatusCode)" -ForegroundColor Green
    $reports = $response.Content | ConvertFrom-Json
    Write-Host "   Found $($reports.Count) existing reports"
} catch {
    Write-Host "   ✗ Reports API failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode -eq 500) {
        Write-Host "   ⚠ Database connection issue - PostgreSQL may not be running" -ForegroundColor Yellow
    }
}
Write-Host ""

# Test 3: Create Test Report
Write-Host "3. Testing Create Report..."
$testReport = @{
    name = "System Test Report"
    description = "Basic functionality test"
    sql_query = "SELECT 'Automated Reporting System' as system_name, CURRENT_DATE as report_date, CURRENT_TIME as report_time, 'Test successful' as status"
    schedule_cron = "0 9 * * *"
    output_format = "CSV"
    is_active = $true
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/api/reports -Method POST -Body $testReport -ContentType "application/json" -UseBasicParsing
    Write-Host "   ✓ Create Report: $($response.StatusCode)" -ForegroundColor Green
    $report = $response.Content | ConvertFrom-Json
    Write-Host "   Created Report ID: $($report.id)"
    Write-Host "   Report Name: $($report.name)"
    $script:testReportId = $report.id
} catch {
    Write-Host "   ✗ Create Report failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Trigger Report Run
if ($script:testReportId) {
    Write-Host "4. Testing Trigger Report Run..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/reports/$($script:testReportId)/run" -Method POST -UseBasicParsing
        Write-Host "   ✓ Trigger Run: $($response.StatusCode)" -ForegroundColor Green
        $run = $response.Content | ConvertFrom-Json
        Write-Host "   Run ID: $($run.id)"
        Write-Host "   Status: $($run.status)"
        if ($run.row_count) {
            Write-Host "   Row Count: $($run.row_count)"
        }
        if ($run.output_path) {
            Write-Host "   Output Path: $($run.output_path)"
        }
        $script:testRunId = $run.id
    } catch {
        Write-Host "   ✗ Trigger Run failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 5: Get Run History
if ($script:testReportId) {
    Write-Host "5. Testing Get Run History..."
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/reports/$($script:testReportId)/runs" -UseBasicParsing
        Write-Host "   ✓ Get Run History: $($response.StatusCode)" -ForegroundColor Green
        $runs = $response.Content | ConvertFrom-Json
        Write-Host "   Found $($runs.Count) run(s)"
        if ($runs.Count -gt 0) {
            $latest = $runs[0]
            Write-Host "   Latest Run Status: $($latest.status)"
            Write-Host "   Latest Run Started: $($latest.started_at)"
        }
    } catch {
        Write-Host "   ✗ Get Run History failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Test 6: Frontend Check
Write-Host "6. Testing Frontend..."
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing
    Write-Host "   ✓ Frontend accessible: $($response.StatusCode)" -ForegroundColor Green
    if ($response.Content -match "Automated Reporting System") {
        Write-Host "   Frontend content loaded correctly"
    }
} catch {
    Write-Host "   ✗ Frontend check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: API Docs
Write-Host "7. Testing API Documentation..."
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing
    Write-Host "   ✓ API Docs accessible: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ API Docs check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 8: Output Files
Write-Host "8. Checking Output Files..."
if (Test-Path "outputs") {
    $files = Get-ChildItem outputs -Filter "*.csv" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3
    Write-Host "   ✓ Outputs directory exists"
    if ($files.Count -gt 0) {
        Write-Host "   Found $($files.Count) CSV file(s):"
        foreach ($file in $files) {
            $sizeKB = [math]::Round($file.Length / 1KB, 2)
            Write-Host "     - $($file.Name) ($sizeKB KB, $($file.LastWriteTime))"
        }
    } else {
        Write-Host "   No CSV files yet (expected if no successful runs)"
    }
} else {
    Write-Host "   ⚠ Outputs directory not found"
}
Write-Host ""

Write-Host "========================================"
Write-Host "Test Suite Complete"
Write-Host "========================================"
