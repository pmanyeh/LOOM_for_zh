@echo off
chcp 65001 >nul
echo ==========================================
echo    《LOOM》Steam 版繁體中文化安裝程式
echo ==========================================
echo.
echo 正在為您的遊戲檔案注入繁體中文文本...
echo.

if not exist "DISK01.LEC" (
    echo [錯誤] 找不到 DISK01.LEC！請確保您將這些檔案解壓縮到 Steam 的 LOOM 遊戲資料夾內。
    echo.
    pause
    exit /b
)

scummtr.exe -w -g loomcd -h -i -f loom_strings_translated.txt -p "."

echo.
echo ==========================================
echo 中文化安裝完成！
echo 請使用 ScummVM 開啟遊戲，並享受繁體中文版！
echo ==========================================
pause
