# Запуск ассистента.   .\run.ps1  (текст)   |   .\run.ps1 -voice  (голос)
param([switch]$voice)

$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Окружение не найдено. Сначала запусти .\setup.ps1" -ForegroundColor Red
    exit 1
}
if ($voice) { & $py -m src.main --voice } else { & $py -m src.main }
