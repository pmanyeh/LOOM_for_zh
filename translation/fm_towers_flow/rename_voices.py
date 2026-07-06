import json
import os
import re

game_voice_dir = r"D:\git\遊戲中文化\LOOM\LOOM_FM-TOWNS_ZH_Portable\game\voice"
new_json_path = r"D:\git\遊戲中文化\LOOM\translation\fm_towers_flow\voice_map.json"
charmap_path = r"D:\git\遊戲中文化\LOOM\translation\fm_towers_flow\sjis_charmap.json"

FNV_OFF = 2166136261
FNV_PRIME = 16777619
MASK = 0xFFFFFFFF

with open(charmap_path, 'r', encoding='utf-8') as f:
    charmap = json.load(f)

def get_encoded_bytes(text):
    encoded_bytes = bytearray()
    for c in text:
        if ord(c) < 128:
            encoded_bytes.append(ord(c))
        elif c in charmap:
            code = charmap[c]
            encoded_bytes.append(code[0])
            encoded_bytes.append(code[1])
        else:
            encoded_bytes.append(0x20)
    return bytes(encoded_bytes)

def parse_octal_escapes(text_bytes):
    pattern = re.compile(rb'\\([0-7]{3})')
    def replace_octal(match):
        octal_val = int(match.group(1), 8)
        return bytes([octal_val])
    return pattern.sub(replace_octal, text_bytes)

def parse_decimal_escapes(text_bytes):
    pattern = re.compile(rb'\\([0-9]{3})')
    def replace_dec(match):
        dec_val = int(match.group(1), 10)
        return bytes([dec_val])
    return pattern.sub(replace_dec, text_bytes)

def normalize_and_hash(binary_bytes):
    clean_bytes = bytearray()
    i = 0
    n = len(binary_bytes)
    while i < n:
        if binary_bytes[i] == 0xFF:
            if i + 1 < n:
                code = binary_bytes[i + 1]
                if code in (1, 2, 3, 8):
                    i += 2
                elif code in (9, 10, 12, 13, 14):
                    i += 4
                else:
                    i += 2
            else:
                i += 1
        elif binary_bytes[i] <= 0x20:
            i += 1
        else:
            clean_bytes.append(binary_bytes[i])
            i += 1
    if not clean_bytes:
        return None
    h = FNV_OFF
    for b in clean_bytes:
        h = (h ^ b) & MASK
        h = (h * FNV_PRIME) & MASK
    return f"{h:08x}"

with open(new_json_path, 'r', encoding='utf-8') as f:
    new_map = json.load(f)

renamed = 0
for new_h, data in new_map.items():
    text = data['text']
    encoded = get_encoded_bytes(text)
    
    # Calculate old buggy hash (using octal parsing)
    buggy_bytes = parse_octal_escapes(encoded)
    old_h = normalize_and_hash(buggy_bytes)
    
    # Check if a file with the old hash exists
    if old_h and old_h != new_h:
        old_wav = os.path.join(game_voice_dir, f"{old_h}.wav")
        new_wav = os.path.join(game_voice_dir, f"{new_h}.wav")
        if os.path.exists(old_wav):
            print(f"Renaming {old_h}.wav -> {new_h}.wav (for text: {text[:15]}...)")
            os.rename(old_wav, new_wav)
            renamed += 1

print(f"Total files renamed: {renamed}")
