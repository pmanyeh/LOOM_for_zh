import os
import csv
import json
from PIL import Image, ImageFont, ImageDraw

def getCharFMTChunk(ch):
    f = ch & 0xFF
    s = ch >> 8
    
    KANA = 0
    KANJI = 1
    EKANJI = 2
    
    base = s - ((s + 1) % 32)
    c = 0
    p = 0
    kanjiType = KANA
    
    if 0x81 <= f <= 0x84: kanjiType = KANA
    if 0x88 <= f <= 0x9f: kanjiType = KANJI
    if 0xe0 <= f <= 0xea: kanjiType = EKANJI
    
    if (f > 0xe8 or (f == 0xe8 and base >= 0x9f)) or (f > 0x90 or (f == 0x90 and base >= 0x9f)):
        c = 48
        p = -8
        
    if kanjiType == KANA:
        chunk_f = (f - 0x81) * 2
    elif kanjiType == KANJI:
        p += f - 0x88
        chunk_f = c + 2 * p
    elif kanjiType == EKANJI:
        p += f - 0xe0
        chunk_f = c + 2 * p
        
    if base == 0x7f and s == 0x7f: base -= 0x20
    if base == 0x9f and s == 0xbe: base += 0x20
    if base == 0xbf and s == 0xde: base += 0x20
    
    cr = 0
    chunk = 0
    if base == 0x3f:
        cr = 0
        if kanjiType == KANA: chunk = 1
        elif kanjiType == KANJI: chunk = 31
        elif kanjiType == EKANJI: chunk = 111
    elif base == 0x5f:
        cr = 0
        if kanjiType == KANA: chunk = 17
        elif kanjiType == KANJI: chunk = 47
        elif kanjiType == EKANJI: chunk = 127
    elif base == 0x7f:
        cr = -1
        if kanjiType == KANA: chunk = 9
        elif kanjiType == KANJI: chunk = 63
        elif kanjiType == EKANJI: chunk = 143
    elif base == 0x9f:
        cr = 1
        if kanjiType == KANA: chunk = 2
        elif kanjiType == KANJI: chunk = 32
        elif kanjiType == EKANJI: chunk = 112
    elif base == 0xbf:
        cr = 1
        if kanjiType == KANA: chunk = 18
        elif kanjiType == KANJI: chunk = 48
        elif kanjiType == EKANJI: chunk = 128
    elif base == 0xdf:
        cr = 1
        if kanjiType == KANA: chunk = 10
        elif kanjiType == KANJI: chunk = 64
        elif kanjiType == EKANJI: chunk = 144
        
    return (((chunk_f + chunk) * 32 + (s - base)) + cr)

def is_valid_sjis(f, s):
    # Standard Kanji range
    if not (0x88 <= f <= 0x9F or 0xE0 <= f <= 0xEA):
        return False
    if not (0x80 <= s <= 0xFC):
        return False
    # Avoid problematic codes
    if s == 0x7F: return False
    return True

def generate_fmt_fnt(csv_path, ttf_path, out_rom_path, out_json_path):
    # 1. Parse unique characters
    unique_chars = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row['Chinese'].strip() if row.get('Chinese') else ''
                if not text and row.get('English'):
                    text = row['English']
                for c in text:
                    if ord(c) >= 128 and c not in unique_chars:
                        unique_chars.append(c)

    print(f"Found {len(unique_chars)} unique Chinese characters.")

    # 2. Generate valid SJIS codes and assign
    sjis_codes = []
    for f in range(0x88, 0x9F + 1):
        for s in range(0x40, 0xFC + 1):
            if is_valid_sjis(f, s):
                sjis_codes.append((f, s))
                
    if len(unique_chars) > len(sjis_codes):
        print("Error: Too many unique characters for the standard Kanji range!")
        return
        
    charmap = {}
    font = ImageFont.truetype(ttf_path, 14)
    
    # Create empty 288KB ROM (filled with 0)
    rom_data = bytearray(294912)
    
    # 3. Render and write to ROM
    for idx, char in enumerate(unique_chars):
        f, s = sjis_codes[idx]
        ch = f | (s << 8) # Little endian as expected by ScummVM
        charmap[char] = [f, s]
        
        chunkNum = getCharFMTChunk(ch)
        if chunkNum < 0 or chunkNum >= 7872:
            print(f"Error: Invalid chunk {chunkNum} for SJIS {hex(ch)}")
            continue
            
        # Render 16x16
        img = Image.new('1', (16, 16), 0)
        draw = ImageDraw.Draw(img)
        # Offset Y by +1 to center the 14px font in the 16x16 bounding box
        # This leaves ~1px on top and ~1px on bottom for readable spacing between lines
        draw.text((0, 1), char, font=font, fill=1)
        
        offset = chunkNum * 32
        
        for y in range(16):
            byte1 = 0
            byte2 = 0
            for x in range(8):
                if img.getpixel((x, y)):
                    byte1 |= (1 << (7 - x))
            for x in range(8, 16):
                if img.getpixel((x, y)):
                    byte2 |= (1 << (7 - (x - 8)))
            rom_data[offset + y*2] = byte1
            rom_data[offset + y*2 + 1] = byte2
            
    with open(out_rom_path, 'wb') as f:
        f.write(rom_data)
        
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(charmap, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated {out_rom_path} and {out_json_path}")

if __name__ == '__main__':
    generate_fmt_fnt(
        "loomtowns_strings.csv", 
        r"C:\Windows\Fonts\mingliu.ttc", 
        "FMT_FNT.ROM", 
        "sjis_charmap.json"
    )
