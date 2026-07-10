#!/bin/bash
# LOOM Steam 語音版 繁體中文化安裝腳本 (macOS)
echo '=========================================='
echo '  《LOOM》Steam 語音版 繁體中文化安裝程式'
echo '=========================================='
echo
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GAMEDIR="$SCRIPT_DIR"
if [ -f "$SCRIPT_DIR/game/DISK01.LEC" ]; then GAMEDIR="$SCRIPT_DIR/game"; fi
if [ ! -f "$GAMEDIR/DISK01.LEC" ]; then
    echo '[錯誤] 找不到 DISK01.LEC！請將遊戲資料放置於本資料夾內。'
    exit 1
fi
echo '正在將繁體中文翻譯資料注入遊戲檔案中...'
echo
chmod +x "$SCRIPT_DIR/scummtr"
TEXTFILE="$SCRIPT_DIR/loom_strings_translated.txt"
if [ -f "$GAMEDIR/loom_strings_translated.txt" ]; then TEXTFILE="$GAMEDIR/loom_strings_translated.txt"; fi
"$SCRIPT_DIR/scummtr" -w -h -g loomcd -i -f "$TEXTFILE" -p "$GAMEDIR"
rm -f "$GAMEDIR/"*~~scummio-tmp 2>/dev/null
echo
echo '=========================================='
echo '中文化安裝完成！'
echo '=========================================='
echo
