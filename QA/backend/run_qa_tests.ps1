param(
    [int]$Port = 8001,
    [string]$DbName = "LibraryDB_QA",
    [switch]$KeepRunning
)

$ErrorActionPreference = "Stop"
$root = "D:\ung dung tri tue nhan ao\app"
$backend = Join-Path $root "Backend"
$qaBackend = Join-Path $root "QA\backend"
$pidFile = Join-Path $qaBackend "qa_server.pid"
$conn = "mssql+pyodbc://@localhost\QUANGHUNG/${DbName}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"

# 1. Dừng server QA cũ nếu có
if (Test-Path -LiteralPath $pidFile) {
    $oldPid = [int](Get-Content -LiteralPath $pidFile)
    Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Da dung server QA cu (PID $oldPid)."
}

# 2. Xóa/tạo lại database QA
sqlcmd -S "localhost\QUANGHUNG" -E -C -Q "IF DB_ID('$DbName') IS NOT NULL BEGIN ALTER DATABASE [$DbName] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; DROP DATABASE [$DbName]; END; CREATE DATABASE [$DbName];"
Write-Host "Da tao lai database $DbName."

# 3. Migration + seed
Push-Location $backend
try {
    $env:DATABASE_URL = $conn
    python -m alembic upgrade head
    python (Join-Path $root "QA\backend\seed_qa_db.py")
} finally {
    Pop-Location
}

# 4. Khởi động server QA
$server = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$Port" -WorkingDirectory $backend -WindowStyle Hidden -PassThru
$server.Id | Set-Content -LiteralPath $pidFile
Write-Host "Da khoi dong server QA (PID $($server.Id), port $Port)."

# 5. Chờ server sẵn sàng
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/auth/login" -Method Post -ContentType "application/json" -Body '{"username":"qa_admin","password":"Test@12345"}' -TimeoutSec 2 | Out-Null
        $ready = $true
        break
    } catch {
    }
}
if (-not $ready) {
    throw "Server QA khong san sang tren port $Port."
}

# 6. Chạy pytest
Push-Location $qaBackend
try {
    python -m pytest -q --tb=short
} finally {
    Pop-Location
}

# 7. Dừng server (trừ khi giữ lại)
if (-not $KeepRunning) {
    Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Da dung server QA."
}
