#!/bin/bash
# LOOM FM-TOWNS 繁體中文化安裝腳本 (macOS)

echo '=========================================='
echo '  《LOOM》FM-TOWNS 繁體中文化安裝程式'
echo '=========================================='
echo

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 尋找遊戲目錄（優先找同層的 00.LFL，其次找 game/ 資料夾）
GAMEDIR="$SCRIPT_DIR"
if [ -f "$SCRIPT_DIR/game/00.LFL" ]; then
    GAMEDIR="$SCRIPT_DIR/game"
fi

if [ ! -f "$GAMEDIR/00.LFL" ]; then
    echo "[錯誤] 找不到 00.LFL！"
    echo "請將 LOOM FM-TOWNS 的遊戲資料放置於本資料夾內（與腳本同層，或放進 game/ 資料夾）。"
    exit 1
fi

echo '正在將繁體中文翻譯資料注入遊戲檔案中...'
echo

# 確認 scummtr 有執行權限
chmod +x "$SCRIPT_DIR/scummtr"

# 尋找文本檔案位置
TEXTFILE="$SCRIPT_DIR/loomtowns_zh_injected.txt"
if [ -f "$GAMEDIR/loomtowns_zh_injected.txt" ]; then
    TEXTFILE="$GAMEDIR/loomtowns_zh_injected.txt"
fi

# 執行文本注入
"$SCRIPT_DIR/scummtr" -w -h -g loomtowns -i -f "$TEXTFILE" -p "$GAMEDIR"

# 清理暫存檔
rm -f "$GAMEDIR/"*~~scummio-tmp 2>/dev/null

echo
echo '=========================================='
echo '中文化安裝完成！'
echo '=========================================='
echo
echo '請依照「使用說明.txt」中的 ScummVM 設定步驟完成設定後，即可開始遊玩。'
echo
