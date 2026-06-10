# Создаёт ярлык "Nixi.lnk" для запуска ассистента Никси из трея (двойной клик / закрепление
# на панели задач), генерирует иконку и подсказывает по автозапуску.
#   .\install-tray.ps1
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$pyw = Join-Path $root ".venv\Scripts\pythonw.exe"
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $pyw)) {
    Write-Host "Окружение не найдено. Сначала запусти .\setup.ps1, затем pip install -r requirements-ui.txt" -ForegroundColor Red
    exit 1
}

# Иконка из круга-индикатора (PIL уже в requirements-ui). Кладём в assets/tray.
$assets = Join-Path $root "assets\tray"
New-Item -ItemType Directory -Force -Path $assets | Out-Null
$icoPath = Join-Path $assets "assistant.ico"
$pyCode = @"
from PIL import Image, ImageDraw
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.ellipse([24, 24, 232, 232], fill=(60, 200, 90, 255), outline=(20, 20, 20, 255), width=10)
img.save(r'$icoPath', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
"@
& $py -c $pyCode
if (-not (Test-Path $icoPath)) {
    Write-Host "Не удалось создать иконку (нет Pillow?). Ярлык будет с иконкой pythonw." -ForegroundColor Yellow
    $icoPath = $pyw
}

$lnkPath = Join-Path $root "Nixi.lnk"
$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($lnkPath)
$lnk.TargetPath = $pyw
$lnk.Arguments = '"' + (Join-Path $root "src\tray.py") + '"'
$lnk.WorkingDirectory = $root
$lnk.IconLocation = $icoPath
$lnk.Description = "Nixi.EXE — домашний голосовой ассистент Никси (иконка в трее)"
$lnk.Save()

Write-Host "Готово. Ярлык: $lnkPath" -ForegroundColor Green
Write-Host "  - Двойной клик по ярлыку — запуск иконки в трее (двойной ЛКМ по ней открывает панель)." -ForegroundColor Gray
Write-Host "  - ПКМ по ярлыку -> Закрепить на панели задач, чтобы держать под рукой." -ForegroundColor Gray
Write-Host "  - Автозапуск с Windows включается/выключается в ПКМ-меню самой иконки." -ForegroundColor Gray
