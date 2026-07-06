import os
import csv
import json
import re

# FNV-1a 32-bit constants
FNV_OFF = 2166136261
FNV_PRIME = 16777619
MASK = 0xFFFFFFFF

def parse_decimal_escapes(text_bytes):
    # Replaces pattern like b'\\255' or b'\\001' with the actual byte value
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
                    i += 2  # fallback
            else:
                i += 1
        elif binary_bytes[i] <= 0x20:
            # skip whitespace and control bytes
            i += 1
        else:
            clean_bytes.append(binary_bytes[i])
            i += 1
            
    if not clean_bytes:
        return None
        
    # FNV-1a 32-bit hash
    h = FNV_OFF
    for b in clean_bytes:
        h = (h ^ b) & MASK
        h = (h * FNV_PRIME) & MASK
        
    return f"{h:08x}"

def main():
    flow_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(flow_dir, "loomtowns_strings.csv")
    charmap_path = os.path.join(flow_dir, "sjis_charmap.json")
    out_map_path = os.path.join(flow_dir, "voice_map.json")
    
    if not os.path.exists(charmap_path):
        print(f"Error: {charmap_path} not found. Run compile_and_package.py first.")
        return
        
    with open(charmap_path, 'r', encoding='utf-8') as f:
        charmap = json.load(f)
        
    voice_map = {}
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            context = row['Context']
            # Only keep SC (Script) and LS (Local Script) contexts for dialogue voice-overs
            # Skip OC (Object Comment), ON (Object Name), EN (Exit Name), EX (Exit)
            prefix = ""
            if ":" in context:
                parts = context.split(":")
                if len(parts) > 1 and "#" in parts[1]:
                    prefix = parts[1].split("#")[0]
            
            if prefix not in ("SC", "LS", "OC", "EN"):
                continue
                
            chinese = row['Chinese'].strip()
            english = row.get('English', '').strip()
            actor = row.get('Actor', '').strip()
            text = chinese if chinese else english
            if not text:
                continue
                
            # Encode using the custom SJIS map
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
                    
            binary_bytes = parse_decimal_escapes(bytes(encoded_bytes))
            h = normalize_and_hash(binary_bytes)
            if not h:
                continue
                
            voice_map[h] = {
                "context": context,
                "actor": actor,
                "text": text,
                "english_text": english,
                "suggested_file": f"{h}.wav"
            }
            
    with open(out_map_path, 'w', encoding='utf-8') as f:
        json.dump(voice_map, f, ensure_ascii=False, indent=2)
        
    print(f"Generated voice map with {len(voice_map)} entries at {out_map_path}")

if __name__ == "__main__":
    main()
