import os
import json
import csv
from PIL import Image, ImageDraw, ImageFont

def get_base_chars():
    chars = []
    for p in "，。、！？；：「」『』【】（）《》〈〉…—～·“”‘’":
        if p not in chars: chars.append(p)
    return chars

def get_next_gb2312_code(current_code):
    if current_code is None:
        return [0xA1, 0xA1]
    
    high, low = current_code
    low += 1
    # 0xFE and 0xFF are SCUMM escape codes, so we MUST stop at 0xFD!
    if low > 0xFD:
        low = 0xA1
        high += 1
        
    # We also shouldn't use 0xFE or 0xFF for the high byte
    if high > 0xFD:
        return None
        
    return [high, low]

def get_big5_chars():
    chars = []
    for high in range(0xA4, 0xC7):
        for low in range(0x40, 0xFF):
            if 0x7F <= low <= 0xA0: continue
            try:
                c = bytes([high, low]).decode('big5')
                chars.append(c)
            except: pass
    return chars


def generate_preview_multi(font_paths, presets, out_path="font_preview.png"):
    """Generate a side-by-side preview image comparing multiple font presets.
    font_paths : list of ttf paths, one per preset column.
    presets    : list of (label, font_size, y_offset).
    """
    from PIL import Image, ImageDraw, ImageFont as PILFont

    sample = "天地人"
    lines = [sample, sample, sample]  # 3 行展示行距

    scale = 6  # 放大倍率，讓像素清晰可見
    cell_w = 12 * scale
    cell_h = 12 * scale
    line_height = 13 * scale  # 對應 ScummVM getFontHeight() = _2byteHeight + 1 = 13
    pad = 10
    label_h = 22
    col_w = len(sample) * cell_w + pad * 2

    img_w = col_w * len(presets) + pad
    img_h = len(lines) * line_height + label_h + pad * 3
    preview = Image.new('RGB', (img_w, img_h), color=(30, 30, 30))
    draw = ImageDraw.Draw(preview)

    try:
        label_fnt = PILFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
    except:
        label_fnt = PILFont.load_default()

    for i, ((label, font_size, y_offset), fnt_path) in enumerate(zip(presets, font_paths)):
        try:
            fnt = PILFont.truetype(fnt_path, font_size)
        except Exception as e:
            print(f"  Warning: cannot load {fnt_path}: {e}")
            fnt = PILFont.load_default()

        x_base = i * col_w + pad

        # 欄標籤
        draw.text((x_base, pad // 2), label, font=label_fnt, fill=(200, 200, 100))

        for row_i, line_text in enumerate(lines):
            y_base = label_h + pad + row_i * line_height
            # 行邊界線（灰色）
            draw.line([(x_base, y_base), (x_base + col_w - pad, y_base)], fill=(70, 70, 70))

            for col_i, ch in enumerate(line_text):
                glyph_img = Image.new('1', (12, 12), color=0)
                glyph_draw = ImageDraw.Draw(glyph_img)
                glyph_draw.text((0, y_offset), ch, font=fnt, fill=1)

                # 放大並轉成 RGB
                scaled = glyph_img.resize((cell_w, cell_h), Image.NEAREST)
                rgb = Image.new('RGB', (cell_w, cell_h), (30, 30, 30))
                for py in range(cell_h):
                    for px in range(cell_w):
                        if scaled.getpixel((px, py)):
                            rgb.putpixel((px, py), (240, 220, 160))

                preview.paste(rgb, (x_base + col_i * cell_w, y_base))

        # 最後一行的底線
        y_last = label_h + pad + len(lines) * line_height
        draw.line([(x_base, y_last), (x_base + col_w - pad, y_last)], fill=(70, 70, 70))

    preview.save(out_path)
    print(f"Preview saved to {out_path}")


def generate_custom_font(csv_path, ttf_path, out_fnt_path, out_json_path,
                         font_size=11, y_offset=0):
    """
    font_size : TTF render size (smaller = shorter glyphs, more room for spacing)
    y_offset  : vertical offset within the 12px cell (positive = shift down = top padding)
    """
    width = 12
    height = 12
    num_char = 8178 # 87 * 94

    unique_chars = []
    
    for c in get_base_chars():
        if c not in unique_chars: unique_chars.append(c)
        
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text = row['Chinese'].strip() if row.get('Chinese') else ''
                    if not text and row.get('English'):
                        text = row['English']
                    for c in text:
                        if ord(c) >= 128 and c not in unique_chars:
                            unique_chars.append(c)
        except UnicodeDecodeError:
            with open(csv_path, 'r', encoding='cp950', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    text = row['Chinese'].strip() if row.get('Chinese') else ''
                    if not text and row.get('English'):
                        text = row['English']
                    for c in text:
                        if ord(c) >= 128 and c not in unique_chars:
                            unique_chars.append(c)
                        
    for c in get_big5_chars():
        if len(unique_chars) >= num_char: break
        if c not in unique_chars:
            unique_chars.append(c)
            
    while len(unique_chars) < num_char:
        unique_chars.append(' ')

    unique_chars = unique_chars[:num_char]

    charmap = {}
    
    try:
        font = ImageFont.truetype(ttf_path, font_size)
    except IOError:
        print(f"Error loading font {ttf_path}")
        return

    out_bytes = bytearray()
    char_idx = 0

    for row in range(0xA1, 0xF8):
        for col in range(0xA1, 0xFF):
            if col == 0xFE:
                # 0xFE is an escape code in SCUMM, never map a character to it!
                # We still write a blank glyph to the .fnt file to keep the 94-column structure.
                char_str = ' '
            else:
                char_str = unique_chars[char_idx] if char_idx < len(unique_chars) else ' '
                charmap[char_str] = [row, col]
                char_idx += 1
            
            img = Image.new('1', (width, height), color=0)
            draw = ImageDraw.Draw(img)
            
            draw.text((0, y_offset), char_str, font=font, fill=1)
            
            for y in range(height):
                byte1 = 0
                byte2 = 0
                for x in range(8):
                    if img.getpixel((x, y)):
                        byte1 |= (1 << (7 - x))
                for x in range(8, 12):
                    if img.getpixel((x, y)):
                        byte2 |= (1 << (7 - (x - 8)))
                out_bytes.append(byte1)
                out_bytes.append(byte2)
                
    with open(out_fnt_path, 'wb') as f:
        f.write(out_bytes)
        
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(charmap, f, ensure_ascii=False, indent=2)
        
    print(f"Generated {out_fnt_path} and {out_json_path} successfully.")
    
    # Auto-copy to the game directory so the user doesn't have to do it manually
    for game_dir in ["../from steam/LOOM", "../FM-TOWNS_KAN_Patch"]:
        if os.path.exists(game_dir):
            import shutil
            target_fnt = os.path.join(game_dir, os.path.basename(out_fnt_path))
            shutil.copy2(out_fnt_path, target_fnt)
            print(f"Automatically copied {out_fnt_path} to {game_dir}")


if __name__ == '__main__':
    # ── 字型路徑 ───────────────────────────────────────────────────────
    # Fusion Pixel 10px：像素字型，字形恰好 10px 高，放進 12px 格有 2px 自然行距
    PIXEL_FONT = "Fusion_Pixel_10px.ttf"

    # 備用：系統明體（傳統方案，需縮小才有行距）
    FALLBACK_FONT = "C:/Windows/Fonts/mingliu.ttc"
    if not os.path.exists(FALLBACK_FONT):
        FALLBACK_FONT = "C:/Windows/Fonts/simsun.ttc"

    use_pixel = os.path.exists(PIXEL_FONT)
    if use_pixel:
        print(f"Found {PIXEL_FONT}, using pixel font presets.")
    else:
        print(f"Pixel font not found, falling back to {FALLBACK_FONT}.")

    # ── 預覽方案對照 ───────────────────────────────────────────────────
    # Fusion Pixel 10px 字形天生是 10px，放進 12px 格：
    #   off=0 → 字貼頂，底部留 2px
    #   off=1 → 字置中，上下各 1px（最均衡）
    #   off=2 → 字貼底，頂部留 2px
    # 同時附上 mingliu 原版對照
    if use_pixel:
        presets = [
            ("mingliu(原版) sz=11 off=0", 11, 0),   # 用 mingliu 當基準對照
            ("Fusion off=0 (底留2px)",    10, 0),
            ("Fusion off=1 (上下各1px)",  10, 1),
            ("Fusion off=2 (頂留2px)",    10, 2),
        ]
        # 注意：Fusion Pixel 10px 在 PIL 裡 size=10 恰好對應 10px 像素高度
        preview_fonts = [FALLBACK_FONT, PIXEL_FONT, PIXEL_FONT, PIXEL_FONT]
    else:
        presets = [
            ("原版 size=11 off=0",  11, 0),
            ("方案A size=10 off=1", 10, 1),
            ("方案B size=9  off=1",  9, 1),
            ("方案C size=9  off=2",  9, 2),
        ]
        preview_fonts = [FALLBACK_FONT] * 4

    # 先生成預覽圖，讓你挑選喜歡的方案
    print("Generating preview...")
    # 為了支援每欄獨立字型，這裡傳入 font paths list
    generate_preview_multi(preview_fonts, presets, out_path="font_preview.png")
    print()

    # ── 選擇要套用的方案 ────────────────────────────────────────────────
    # 確認預覽後，修改下面兩個變數：
    CHOSEN_FONT   = FALLBACK_FONT
    CHOSEN_SIZE   = 12   # Fusion Pixel 10px → size=10
    CHOSEN_OFFSET = -1    # 上下各 1px 最均衡

    print(f"Generating font: {CHOSEN_FONT}, size={CHOSEN_SIZE}, y_offset={CHOSEN_OFFSET}...")
    generate_custom_font(
        "loom_strings.csv", CHOSEN_FONT,
        "chinese_gb16x12.fnt", "charmap.json",
        font_size=CHOSEN_SIZE,
        y_offset=CHOSEN_OFFSET,
    )
