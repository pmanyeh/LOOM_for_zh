@echo off
chcp 65001 >nul
echo ==========================================
echo    《LOOM》FM-TOWNS 繁體中文化安裝程式
echo ==========================================
echo.
echo 正在將繁體中文翻譯資料注入遊戲檔案中...
echo.

if not exist "00.LFL" (
    echo [錯誤] 找不到 00.LFL！請確認您將此中文化包的「所有檔案」解壓縮到 LOOM FM-TOWNS 的遊戲資料夾內（與 00.LFL 放在同一層）。
    echo.
    pause
    exit /b
)

:: 移除檔案的唯讀屬性 (從光碟複製下來的檔案通常帶有唯讀屬性，這會導致 scummtr 無法覆寫檔案)
attrib -R *.LFL >nul 2>&1

scummtr.exe -w -h -g loomtowns -i -f loomtowns_zh_injected.txt -p "."

:: 清理可能殘留的暫存檔
del /q *~~scummio-tmp >nul 2>&1

echo.
echo ==========================================
echo 中文化安裝完成！
echo ==========================================
echo.
echo 【非常重要的最後一步】
echo 請務必依照以下步驟設定您的 ScummVM：
echo 由於 ScummVM 介面可能隱藏了日文選項，我們必須手動修改設定檔：
echo 1. 按下 Win+R 開啟執行，輸入 %%APPDATA%%\ScummVM\scummvm.ini 並按下 Enter
echo 2. 找到您的 LOOM 遊戲區塊 (例如 [loom-fmtowns])
echo 3. 將該區塊內的 language 設定改為 language=ja (若沒有請自行新增一行)
echo 4. 儲存並關閉檔案
echo 5. 直接在 ScummVM 點擊「開始」遊玩 (請勿再點擊遊戲設定，以免設定被還原！)
echo ==========================================
pause
