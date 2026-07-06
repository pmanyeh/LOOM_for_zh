import os

content = """@echo off
chcp 65001 >nul
echo ==========================================
echo  [LOOM] FM-TOWNS 日文版 繁體中文化安裝程式
echo ==========================================
echo.
echo 正在將繁體中文翻譯資料注入日文版遊戲檔案中...
echo.

if exist "00.LFL" goto do_patch

echo [錯誤] 找不到 00.LFL！請確認您將此中文化包的所有檔案解壓縮到 LOOM FM-TOWNS 日文版 LOOMKAN 的遊戲資料夾內。
echo.
pause
exit /b

:do_patch
scummtr.exe -w -h -g loomtowns -i -f loomtowns_kan_zh_injected.txt -p "."

echo.
echo ==========================================
echo 中文化安裝完成！
echo ==========================================
echo.
echo 這是專為日文版打造的補丁，ScummVM 會自動偵測為日文模式！
echo 您完全不需要修改 scummvm.ini，直接點擊開始遊玩即可享受高音質配樂與繁體中文！
echo ==========================================
pause
"""

with open('安裝日文專屬中文化.bat', 'wb') as f:
    f.write(content.replace('\n', '\r\n').encode('utf-8'))
