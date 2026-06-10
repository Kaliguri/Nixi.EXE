# Сборка standalone CPU-exe ассистента (PyInstaller).
# Делает отдельное чистое CPU-окружение (.venv-build) — БЕЗ GPU-пакетов, чтобы в exe
# не утянулся ~1 ГБ CUDA-библиотек. Затем собирает по assistant.spec.
#
#   .\build-exe.ps1            # обычная сборка
#   .\build-exe.ps1 -Clean     # пересоздать .venv-build с нуля
param([switch]$Clean)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$buildVenv = Join-Path $root ".venv-build"
$py = Join-Path $buildVenv "Scripts\python.exe"

# 1. Чистое CPU-окружение для сборки.
if ($Clean -and (Test-Path $buildVenv)) {
    Write-Host "Удаляю старое .venv-build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $buildVenv
}
if (-not (Test-Path $py)) {
    Write-Host "Создаю CPU-окружение для сборки (.venv-build)..." -ForegroundColor Cyan
    python -m venv $buildVenv
    & $py -m pip install --upgrade pip -q
    # Ядро + голос + UI, но БЕЗ requirements-gpu (никаких nvidia-* / CUDA в exe).
    & $py -m pip install -r (Join-Path $root "requirements.txt") `
                         -r (Join-Path $root "requirements-voice.txt") `
                         -r (Join-Path $root "requirements-ui.txt") pyinstaller
}

# 2. Фронт панели должен быть собран (он зашивается в exe).
$dist = Join-Path $root "apps\web\dist"
if (-not (Test-Path $dist)) {
    Write-Host "Фронт не собран — собираю (npm i + npm run build)..." -ForegroundColor Cyan
    Push-Location (Join-Path $root "apps\web")
    npm install
    npm run build
    Pop-Location
}
if (-not (Test-Path $dist)) {
    Write-Host "Нет apps\web\dist. Собери фронт вручную (cd apps\web; npm run build) и повтори." -ForegroundColor Red
    exit 1
}

# 3. Иконка для exe.
$ico = Join-Path $root "assets\tray\assistant.ico"
if (-not (Test-Path $ico)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $ico) | Out-Null
    $code = @"
from PIL import Image, ImageDraw
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.ellipse([24, 24, 232, 232], fill=(60, 200, 90, 255), outline=(20, 20, 20, 255), width=10)
img.save(r'$ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
"@
    & $py -c $code
}

# 4. Сборка.
Write-Host "Запускаю PyInstaller (это несколько минут)..." -ForegroundColor Cyan
& $py -m PyInstaller (Join-Path $root "assistant.spec") --noconfirm --distpath (Join-Path $root "dist") --workpath (Join-Path $root "build")

$exe = Join-Path $root "dist\Gaida.exe"
if (-not (Test-Path $exe)) {
    Write-Host "Сборка не дала dist\Gaida.exe — смотри вывод PyInstaller выше." -ForegroundColor Red
    exit 1
}

# 5. Раскладка для раздачи: рядом с exe нужны config.yaml, .env, wake_phrases и модели.
Copy-Item (Join-Path $root "config.yaml") (Join-Path $root "dist\config.yaml") -Force
if (Test-Path (Join-Path $root ".env.example")) {
    Copy-Item (Join-Path $root ".env.example") (Join-Path $root "dist\.env.example") -Force
}
if (Test-Path (Join-Path $root "wake_phrases.txt")) {
    Copy-Item (Join-Path $root "wake_phrases.txt") (Join-Path $root "dist\wake_phrases.txt") -Force
}

Write-Host ""
Write-Host "Готово: $exe" -ForegroundColor Green
Write-Host "Чтобы раздавать — рядом с Gaida.exe положи:" -ForegroundColor Gray
Write-Host "  config.yaml (уже скопирован), .env (с ключами ANTHROPIC/OPENAI_API_KEY)," -ForegroundColor Gray
Write-Host "  и папку models\ (faster-whisper + vosk). Подробности — DISTRIBUTION.md." -ForegroundColor Gray
