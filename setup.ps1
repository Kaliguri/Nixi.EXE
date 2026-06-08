# Создаёт виртуальное окружение и ставит зависимости.
# Запуск:  .\setup.ps1            (всё, включая голосовой стек)
#          .\setup.ps1 -CoreOnly  (только ядро, без голоса — быстро)
param([switch]$CoreOnly)

$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "Создаю виртуальное окружение .venv ..."
    python -m venv .venv
}

& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt
if (-not $CoreOnly) {
    Write-Host "Ставлю голосовой стек (может занять пару минут)..."
    & $py -m pip install -r requirements-voice.txt
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "`nСоздан .env — впиши в него ключи ANTHROPIC_API_KEY / OPENAI_API_KEY." -ForegroundColor Yellow
}
Write-Host "`nГотово. Запуск:  .\run.ps1   (текст)   или   .\run.ps1 -voice   (голос)" -ForegroundColor Green
