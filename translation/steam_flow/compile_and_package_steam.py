import os
import shutil
import csv
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

# --- Settings ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRANS_DIR = os.path.dirname(__file__)
PIXEL_FONT = os.path.join(TRANS_DIR, "Fusion_Pixel_10px.ttf")
FONT_SIZE = 10
Y_OFFSET = -1

def step1_generate_font():
    print("=== Step 1: Generating chinese_gb16x12.fnt ===")
    csv_path = os.path.join(TRANS_DIR, "loom_strings.csv")
    out_fnt = os.path.join(TRANS_DIR, "chinese_gb16x12.fnt")
    out_json = os.path.join(TRANS_DIR, "charmap.json")
    
    unique_chars = []
    # Add punctuation
    for p in "，。、！？；：「」『』【】（）《》〈〉…—～·“”‘’":
        if p not in unique_chars: unique_chars.append(p)
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get('Chinese', '').strip()
            if not text: text = row.get('English', '')
            for c in text:
                if ord(c) >= 128 and c not in unique_chars:
                    unique_chars.append(c)
                    
    # Fill remaining from Big5
    for high in range(0xA4, 0xC7):
        for low in range(0x40, 0xFF):
            if 0x7F <= low <= 0xA0: continue
            try:
                c = bytes([high, low]).decode('big5')
                if len(unique_chars) >= 8178: break
                if c not in unique_chars:
                    unique_chars.append(c)
            except: pass
            
    while len(unique_chars) < 8178:
        unique_chars.append(' ')
    unique_chars = unique_chars[:8178]
    
    charmap = {}
    font = ImageFont.truetype(PIXEL_FONT, FONT_SIZE)
    out_bytes = bytearray()
    char_idx = 0
    
    for row in range(0xA1, 0xF8):
        for col in range(0xA1, 0xFF):
            if col == 0xFE:
                char_str = ' '
            else:
                char_str = unique_chars[char_idx] if char_idx < len(unique_chars) else ' '
                charmap[char_str] = [row, col]
                char_idx += 1
            
            img = Image.new('1', (12, 12), color=0)
            draw = ImageDraw.Draw(img)
            draw.text((0, Y_OFFSET), char_str, font=font, fill=1)
            
            for y in range(12):
                byte1, byte2 = 0, 0
                for x in range(8):
                    if img.getpixel((x, y)): byte1 |= (1 << (7 - x))
                for x in range(8, 12):
                    if img.getpixel((x, y)): byte2 |= (1 << (7 - (x - 8)))
                out_bytes.append(byte1)
                out_bytes.append(byte2)
                
    with open(out_fnt, 'wb') as f:
        f.write(out_bytes)
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(charmap, f, ensure_ascii=False, indent=2)
    print(f"Generated {out_fnt} with {len(unique_chars)} characters.")

import helper

def step2_compile_text():
    print("\n=== Step 2: Compiling Translation Strings ===")
    csv_path = os.path.join(TRANS_DIR, "loom_strings.csv")
    txt_template = os.path.join(TRANS_DIR, "loom_strings_h.txt")
    txt_path = os.path.join(TRANS_DIR, "loom_strings_translated.txt")
    charmap_path = os.path.join(TRANS_DIR, "charmap.json")
    
    helper.compile_translation(csv_path, txt_template, txt_path, charmap_path)

def make_crlf_bom(text):
    return "\ufeff" + text.replace('\r\n', '\n').replace('\n', '\r\n')

def make_lf(text):
    return text.replace('\r\n', '\n')

def step3_package():
    print("\n=== Step 3: Packaging Steam Versions ===")
    
    # 1. Steam_Patch
    win_patch = os.path.join(ROOT_DIR, "Steam_Patch")
    os.makedirs(win_patch, exist_ok=True)
    shutil.copy2(os.path.join(ROOT_DIR, "FM-TOWNS_Patch", "scummtr.exe"), os.path.join(win_patch, "scummtr.exe"))
    shutil.copy2(os.path.join(TRANS_DIR, "chinese_gb16x12.fnt"), os.path.join(win_patch, "chinese_gb16x12.fnt"))
    shutil.copy2(os.path.join(TRANS_DIR, "loom_strings_translated.txt"), os.path.join(win_patch, "loom_strings_translated.txt"))
    
    if os.path.exists(os.path.join(TRANS_DIR, "000.LFL")):
        shutil.copy2(os.path.join(TRANS_DIR, "000.LFL"), os.path.join(win_patch, "000.LFL"))
    else:
        print("[警告] 找不到 translation/000.LFL，無法封裝至 Steam_Patch")

    with open(os.path.join(win_patch, "安裝中文化.bat"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(make_crlf_bom(
            "@echo off\n"
            "chcp 65001 >nul\n"
            "echo ==========================================\n"
            "echo    《LOOM》 Steam 語音版 繁體中文化安裝程式\n"
            "echo ==========================================\n"
            "echo.\n"
            "echo 正在將繁體中文翻譯資料注入遊戲檔案中...\n"
            "echo.\n"
            "set GAMEDIR=.\n"
            "if exist \"game\\DISK01.LEC\" set GAMEDIR=game\n"
            "if not exist \"%GAMEDIR%\\DISK01.LEC\" (\n"
            "    echo [錯誤] 找不到 DISK01.LEC！請確認您將遊戲本體放置於「game」資料夾內，或者與本程式放在同一層。\n"
            "    echo.\n"
            "    pause\n"
            "    exit /b\n"
            ")\n"
            "attrib -R \"%GAMEDIR%\\*.LFL\" >nul 2>&1\n"
            "attrib -R \"%GAMEDIR%\\*.LEC\" >nul 2>&1\n"
            "set TEXTFILE=loom_strings_translated.txt\n"
            "if exist \"%GAMEDIR%\\loom_strings_translated.txt\" set TEXTFILE=%GAMEDIR%\\loom_strings_translated.txt\n"
            "scummtr.exe -w -h -g loomcd -i -f \"%TEXTFILE%\" -p \"%GAMEDIR%\"\n"
            "del /q \"%GAMEDIR%\\*~~scummio-tmp\" >nul 2>&1\n"
            "echo.\n"
            "echo ==========================================\n"
            "echo 中文化安裝完成！\n"
            "echo ==========================================\n"
            "echo.\n"
            "echo 請開啟您的 ScummVM 啟動遊戲。\n"
            "echo ==========================================\n"
            "pause\n"
        ))

    with open(os.path.join(win_patch, "使用說明.txt"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(make_crlf_bom(
            "==========================================\n"
            "  《LOOM》Steam 語音版 繁體中文化補丁\n"
            "==========================================\n\n"
            "本中文化補丁專為 Steam 發行的 LOOM 語音版 (Talkie/CD) 製作，並相容於 ScummVM。\n\n"
            "【安裝步驟】\n"
            "1. 將本資料夾內的「所有檔案」複製並貼上到您的 LOOM 遊戲目錄下（與 DISK01.LEC 放在一起）。\n"
            "2. 執行「安裝中文化.bat」，程式會自動將中文文本注入到遊戲檔案中。\n"
            "3. 看到「中文化安裝完成」字樣後即可關閉視窗。\n\n"
            "【ScummVM 語言設定說明 (非常重要！)】\n"
            "由於引擎的限制，本遊戲必須手動將語言指定為簡體中文，才能啟動對應的中文字型渲染機制。\n"
            "請務必按照以下步驟設定，否則遊戲將會顯示亂碼或英文：\n\n"
            "1. 開啟 ScummVM 模擬器。\n"
            "2. 點選清單中的 LOOM 遊戲，然後點擊右側的「編輯遊戲 (Edit Game)」。\n"
            "3. 切換到上方選單的「引擎 (Engine)」分頁。\n"
            "4. 勾選「覆寫全域引擎設定 (Override global engine settings)」。\n"
            "5. 在「語言 (Language)」下拉選單中，選擇「簡體中文 (Chinese (Simplified))」(若用設定檔則為 cn)。\n"
            "6. 點擊「確定 (OK)」儲存設定，即可開始遊玩。\n\n"
            "【注意事項】\n"
            "- chinese_gb16x12.fnt 為必備字型檔，請務必與遊戲檔案放在一起。\n\n"
            "==========================================\n"
        ))

    # 2. Steam_Mac_Patch
    mac_patch = os.path.join(ROOT_DIR, "Steam_Mac_Patch")
    os.makedirs(mac_patch, exist_ok=True)
    shutil.copy2(os.path.join(ROOT_DIR, "scummtr_mac_tmp", "scummtr-0.5.1-macos", "scummtr"), os.path.join(mac_patch, "scummtr"))
    shutil.copy2(os.path.join(TRANS_DIR, "chinese_gb16x12.fnt"), os.path.join(mac_patch, "chinese_gb16x12.fnt"))
    shutil.copy2(os.path.join(TRANS_DIR, "loom_strings_translated.txt"), os.path.join(mac_patch, "loom_strings_translated.txt"))
    
    if os.path.exists(os.path.join(TRANS_DIR, "000.LFL")):
        shutil.copy2(os.path.join(TRANS_DIR, "000.LFL"), os.path.join(mac_patch, "000.LFL"))

    with open(os.path.join(mac_patch, "安裝中文化.sh"), "w", encoding="utf-8", newline="") as f:
        f.write(make_lf(
            "#!/bin/bash\n"
            "# LOOM Steam 語音版 繁體中文化安裝腳本 (macOS)\n"
            "echo '=========================================='\n"
            "echo '  《LOOM》Steam 語音版 繁體中文化安裝程式'\n"
            "echo '=========================================='\n"
            "echo\n"
            "SCRIPT_DIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"\n"
            "GAMEDIR=\"$SCRIPT_DIR\"\n"
            "if [ -f \"$SCRIPT_DIR/game/DISK01.LEC\" ]; then GAMEDIR=\"$SCRIPT_DIR/game\"; fi\n"
            "if [ ! -f \"$GAMEDIR/DISK01.LEC\" ]; then\n"
            "    echo '[錯誤] 找不到 DISK01.LEC！請將遊戲資料放置於本資料夾內。'\n"
            "    exit 1\n"
            "fi\n"
            "echo '正在將繁體中文翻譯資料注入遊戲檔案中...'\n"
            "echo\n"
            "chmod +x \"$SCRIPT_DIR/scummtr\"\n"
            "TEXTFILE=\"$SCRIPT_DIR/loom_strings_translated.txt\"\n"
            "if [ -f \"$GAMEDIR/loom_strings_translated.txt\" ]; then TEXTFILE=\"$GAMEDIR/loom_strings_translated.txt\"; fi\n"
            "\"$SCRIPT_DIR/scummtr\" -w -h -g loomcd -i -f \"$TEXTFILE\" -p \"$GAMEDIR\"\n"
            "rm -f \"$GAMEDIR/\"*~~scummio-tmp 2>/dev/null\n"
            "echo\n"
            "echo '=========================================='\n"
            "echo '中文化安裝完成！'\n"
            "echo '=========================================='\n"
            "echo\n"
        ))

    with open(os.path.join(mac_patch, "使用說明.txt"), "w", encoding="utf-8", newline="") as f:
        f.write(make_lf(
            "==========================================\n"
            "  《LOOM》Steam 語音版 繁體中文化補丁 (macOS)\n"
            "==========================================\n\n"
            "【安裝步驟】\n"
            "1. 將本資料夾內的「所有檔案」複製到您的 LOOM 遊戲目錄下。\n"
            "2. 開啟終端機 (Terminal)，切換到遊戲目錄： cd /path/to/your/LOOM\n"
            "3. 賦予權限並執行：\n"
            "   chmod +x 安裝中文化.sh\n"
            "   ./安裝中文化.sh\n"
            "4. 看到完成即可關閉。\n\n"
            "【ScummVM 語言設定說明 (非常重要！)】\n"
            "由於引擎的限制，本遊戲必須手動將語言指定為簡體中文，才能啟動對應的中文字型渲染機制。\n"
            "請務必按照以下步驟設定，否則遊戲將會顯示亂碼或英文：\n\n"
            "1. 開啟 ScummVM 模擬器。\n"
            "2. 點選清單中的 LOOM 遊戲，然後點擊右側的「編輯遊戲 (Edit Game)」。\n"
            "3. 切換到上方選單的「引擎 (Engine)」分頁。\n"
            "4. 勾選「覆寫全域引擎設定 (Override global engine settings)」。\n"
            "5. 在「語言 (Language)」下拉選單中，選擇「簡體中文 (Chinese (Simplified))」(若用設定檔則為 cn)。\n"
            "6. 點擊「確定 (OK)」儲存設定，即可開始遊玩。\n\n"
            "【注意事項】\n"
            "- chinese_gb16x12.fnt 為必備字型檔。\n\n"
            "==========================================\n"
        ))

    # 3. LOOM_Steam_ZH_Portable
    portable = os.path.join(ROOT_DIR, "LOOM_Steam_ZH_Portable")
    os.makedirs(portable, exist_ok=True)
    os.makedirs(os.path.join(portable, "game"), exist_ok=True)
    os.makedirs(os.path.join(portable, "saves"), exist_ok=True)
    
    # Copy ScummVM
    scummvm_dir = os.path.join(portable, "scummvm")
    os.makedirs(scummvm_dir, exist_ok=True)
    shutil.copy2(os.path.join(ROOT_DIR, "tools", "ScummVM_windows", "scummvm.exe"), os.path.join(scummvm_dir, "scummvm.exe"))
    shutil.copy2(os.path.join(ROOT_DIR, "tools", "ScummVM_windows", "WinSparkle.dll"), os.path.join(scummvm_dir, "WinSparkle.dll"))
    
    # Copy Tools & Patch data
    shutil.copy2(os.path.join(ROOT_DIR, "FM-TOWNS_Patch", "scummtr.exe"), os.path.join(portable, "scummtr.exe"))
    shutil.copy2(os.path.join(TRANS_DIR, "chinese_gb16x12.fnt"), os.path.join(portable, "chinese_gb16x12.fnt"))
    shutil.copy2(os.path.join(TRANS_DIR, "loom_strings_translated.txt"), os.path.join(portable, "loom_strings_translated.txt"))
    if os.path.exists(os.path.join(TRANS_DIR, "000.LFL")):
        shutil.copy2(os.path.join(TRANS_DIR, "000.LFL"), os.path.join(portable, "game", "000.LFL"))
    
    # Copy 安裝中文化.bat (same as patch, but adjusted paths if needed - wait, the patch one handles game\000.LFL already!)
    shutil.copy2(os.path.join(win_patch, "安裝中文化.bat"), os.path.join(portable, "安裝中文化.bat"))
    
    # create play.bat
    with open(os.path.join(portable, "play.bat"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(make_crlf_bom(
            "@echo off\n"
            "chcp 65001 >nul\n"
            "setlocal\n\n"
            "echo ==========================================\n"
            "echo    《LOOM》 Steam 語音版 繁體中文 啟動器\n"
            "echo ==========================================\n"
            "echo.\n\n"
            "set \"BASE=%~dp0\"\n"
            "if \"%BASE:~-1%\"==\"\\\" set \"BASE=%BASE:~0,-1%\"\n\n"
            "if not exist \"%BASE%\\game\\DISK01.LEC\" (\n"
            "    echo [錯誤] 找不到 game\\DISK01.LEC！\n"
            "    echo.\n"
            "    echo 請依照以下步驟完成設定：\n"
            "    echo   1. 將 LOOM Steam 版的遊戲資料（DISK01.LEC 等）複製到 game\\ 資料夾內\n"
            "    echo   2. 執行「安裝中文化.bat」 注入繁體中文文本\n"
            "    echo   3. 再執行本程式（play.bat）開始遊戲\n"
            "    echo.\n"
            "    pause\n"
            "    exit /b 1\n"
            ")\n\n"
            "if not exist \"%BASE%\\saves\" mkdir \"%BASE%\\saves\"\n\n"
            "(\n"
            "    echo [scummvm]\n"
            "    echo updates_check=0\n"
            ") > \"%BASE%\\scummvm\\scummvm.ini\"\n\n"
            "echo 正在啟動《LOOM》 Steam 語音 繁體中文版...\n"
            "echo (若畫面未出現，請稍等片刻)\n"
            "echo.\n"
            "start \"\" \"%BASE%\\scummvm\\scummvm.exe\" --config=\"%BASE%\\scummvm\\scummvm.ini\" --savepath=\"%BASE%\\saves\" --path=\"%BASE%\\game\" --language=cn loomcd\n\n"
            "endlocal\n"
        ))

    # create 使用說明.txt
    with open(os.path.join(portable, "使用說明.txt"), "w", encoding="utf-8-sig", newline="") as f:
        f.write(make_crlf_bom(
            "==========================================\n"
            "  《LOOM》Steam 語音版 繁體中文化免安裝包\n"
            "==========================================\n\n"
            "【本包內容】\n"
            "- scummvm\\     ScummVM 模擬器（免安裝，攜帶版）\n"
            "- game\\        遊戲資料夾（請自行放入遊戲本體）\n"
            "- saves\\       存檔資料夾（自動建立）\n"
            "- scummtr.exe  文本注入工具\n"
            "- 安裝中文化.bat 中文化安裝程式\n"
            "- play.bat     一鍵啟動遊戲\n\n"
            "==========================================\n"
            "【使用步驟】\n\n"
            "第一步：放入遊戲本體\n"
            "  將 LOOM Steam 版的遊戲資料（DISK01.LEC等）\n"
            "  複製到本資料夾內的「game」子資料夾中。\n\n"
            "第二步：安裝繁體中文化\n"
            "  對著「安裝中文化.bat」點兩下執行。\n\n"
            "第三步：開始遊玩\n"
            "  對著「play.bat」點兩下執行，即可直接開始遊玩！\n\n"
            "==========================================\n"
            "【注意事項】\n"
            "- 本包不含遊戲本體，請自行於 Steam 取得 LOOM。\n"
            "- 啟動腳本已經自動將語言設為簡體中文以正確載入字型。\n"
            "- 存檔位於 saves 資料夾。\n"
            "==========================================\n"
        ))
        
    print("Created Steam_Patch, Steam_Mac_Patch, and LOOM_Steam_ZH_Portable")

if __name__ == "__main__":
    step1_generate_font()
    step2_compile_text()
    step3_package()
