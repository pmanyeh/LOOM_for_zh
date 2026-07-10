﻿@echo off
chcp 65001 >nul
echo ==========================================
echo    《LOOM》 Steam 語音版 繁體中文化安裝程式
echo ==========================================
echo.
echo 正在將繁體中文翻譯資料注入遊戲檔案中...
echo.
set GAMEDIR=.
if exist "game\DISK01.LEC" set GAMEDIR=game
if not exist "%GAMEDIR%\DISK01.LEC" (
    echo [錯誤] 找不到 DISK01.LEC！請確認您將遊戲本體放置於「game」資料夾內，或者與本程式放在同一層。
    echo.
    pause
    exit /b
)
attrib -R "%GAMEDIR%\*.LFL" >nul 2>&1
attrib -R "%GAMEDIR%\*.LEC" >nul 2>&1
set TEXTFILE=loom_strings_translated.txt
if exist "%GAMEDIR%\loom_strings_translated.txt" set TEXTFILE=%GAMEDIR%\loom_strings_translated.txt
scummtr.exe -w -h -g loomcd -i -f "%TEXTFILE%" -p "%GAMEDIR%"
del /q "%GAMEDIR%\*~~scummio-tmp" >nul 2>&1
echo.
echo ==========================================
echo 中文化安裝完成！
echo ==========================================
echo.
echo 請開啟您的 ScummVM 啟動遊戲。
echo ==========================================
pause
