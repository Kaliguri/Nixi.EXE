# Запуск.  .\run.ps1 (текст)  |  .\run.ps1 -voice (голос)  |  .\run.ps1 -ui (веб-панель)
param([switch]$voice, [switch]$ui)

$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Окружение не найдено. Сначала запусти .\setup.ps1" -ForegroundColor Red
    exit 1
}
if ($ui) {
    Write-Host "Веб-панель: http://127.0.0.1:8000  (дев-фронт: cd apps/web; npm run dev)" -ForegroundColor Cyan
    & $py -m src.server.app
}
elseif ($voice) { & $py -m src.main --voice }
else { & $py -m src.main }
