import re
import csv
import sys
import os
import json

CONTEXT_RE = re.compile(r'^\[(\d+:[^\]]+)\](.*)$')

def extract(txt_path, csv_path):
    print(f"Extracting {txt_path} -> {csv_path}...")
    if not os.path.exists(txt_path):
        print(f"Error: Source file {txt_path} does not exist.")
        return

    rows = []
    with open(txt_path, 'r', encoding='latin-1') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\r\n')
            if line.startswith(';;') or not line:
                continue
            
            match = CONTEXT_RE.match(line)
            if match:
                context = match.group(1)
                text = match.group(2)
                rows.append({
                    'Line': line_num,
                    'Context': context,
                    'English': text,
                    'Chinese': ''
                })
            else:
                print(f"Warning: Line {line_num} does not match context format: {repr(line)}")

    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Line', 'Context', 'English', 'Chinese'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Extracted {len(rows)} translatable strings.")

def compile_translation(csv_path, txt_template_path, txt_out_path, charmap_path="charmap.json"):
    print(f"Compiling {csv_path} -> {txt_out_path} using custom encoding...")
    if not os.path.exists(csv_path):
        print(f"Error: CSV file {csv_path} does not exist.")
        return
    if not os.path.exists(txt_template_path):
        print(f"Error: Template file {txt_template_path} does not exist.")
        return
    if not os.path.exists(charmap_path):
        print("Error: charmap.json not found! Please run generate_fnt.py first.")
        return

    with open(charmap_path, 'r', encoding='utf-8') as f:
        charmap = json.load(f)

    # Load translations into a list sequentially
    translations = []
    # Read as utf-8-sig but fallback to cp950 if the user saved it as ANSI
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chinese = row['Chinese'].strip()
                english = row['English']
                translations.append(chinese if chinese else english)
    except UnicodeDecodeError:
        print("Detected non-UTF8 CSV. Falling back to cp950 (Big5)...")
        with open(csv_path, 'r', encoding='cp950', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chinese = row['Chinese'].strip()
                english = row['English']
                translations.append(chinese if chinese else english)

    out_bytes = bytearray()
    trans_idx = 0

    with open(txt_template_path, 'r', encoding='latin-1') as f:
        for line in f:
            line_str = line.rstrip('\r\n')
            if line_str.startswith(';;') or not line_str:
                out_bytes.extend(line_str.encode('latin-1'))
                out_bytes.extend(b'\r\n')
                continue
            
            match = CONTEXT_RE.match(line_str)
            if match:
                context = match.group(1)
                prefix = f"[{context}]"
                out_bytes.extend(prefix.encode('latin-1'))
                
                if trans_idx < len(translations):
                    translated_text = translations[trans_idx]
                    trans_idx += 1
                else:
                    translated_text = match.group(2)
                
                orig_parts = match.group(2).split('\\255\\001')
                trans_parts = translated_text.split('\\255\\001')
                
                orig_injected_len = len(match.group(2)) - len(re.findall(r'\\\d{3}', match.group(2))) * 3
                
                encoded_bytes = bytearray()
                if len(orig_parts) == len(trans_parts) and len(orig_parts) > 1:
                    # Calculate total translated length
                    part_tp_bytes = []
                    total_tp_len = (len(orig_parts) - 1) * 2
                    
                    for tp in trans_parts:
                        tp_len = 0
                        for c in tp:
                            tp_len += 1 if ord(c) < 128 else 2
                        tp_len -= len(re.findall(r'\\\d{3}', tp)) * 3
                        total_tp_len += tp_len
                        
                        tp_bytes = bytearray()
                        for c in tp:
                            if ord(c) < 128:
                                tp_bytes.append(ord(c))
                            elif c in charmap:
                                code = charmap[c]
                                tp_bytes.append(code[0])
                                tp_bytes.append(code[1])
                            else:
                                tp_bytes.append(0x20)
                        part_tp_bytes.append((tp_len, tp_bytes))
                        
                    if total_tp_len > orig_injected_len:
                        print(f"Warning: Line {trans_idx}: Translated string is longer than original ({total_tp_len} > {orig_injected_len}). This might corrupt DISK01.LEC!")
                    
                    remaining = max(0, orig_injected_len - total_tp_len)
                    N = len(orig_parts)
                    
                    pads = [0] * N
                    for i in range(remaining // 2):
                        pads[i % N] += 2
                    if remaining % 2 != 0:
                        pads[-1] += 1
                    
                    for idx, (tp_len, tp_bytes) in enumerate(part_tp_bytes):
                        pad = pads[idx]
                        left_pad = pad // 2
                        right_pad = pad - left_pad
                        
                        padded_bytes = (b' ' * left_pad) + tp_bytes + (b' ' * right_pad)
                        encoded_bytes.extend(padded_bytes)
                        if idx < len(orig_parts) - 1:
                            encoded_bytes.extend(b'\\255\\001')
                else:
                    # Global padding (fallback or single line)
                    trans_injected_len = 0
                    for c in translated_text:
                        if ord(c) < 128:
                            trans_injected_len += 1
                        else:
                            trans_injected_len += 2
                    trans_injected_len -= len(re.findall(r'\\\d{3}', translated_text)) * 3
    
                    for c in translated_text:
                        if ord(c) < 128:
                            encoded_bytes.append(ord(c))
                        elif c in charmap:
                            code = charmap[c]
                            encoded_bytes.append(code[0])
                            encoded_bytes.append(code[1])
                        else:
                            encoded_bytes.append(0x20)
    
                    if trans_injected_len < orig_injected_len:
                        padding = orig_injected_len - trans_injected_len
                        left_pad = padding // 2
                        right_pad = padding - left_pad
                        encoded_bytes = (b' ' * left_pad) + encoded_bytes + (b' ' * right_pad)
                    elif trans_injected_len > orig_injected_len:
                        print(f"Warning: Line {trans_idx}: Translated string is longer than original ({trans_injected_len} > {orig_injected_len}). This might corrupt DISK01.LEC!")

                out_bytes.extend(encoded_bytes)
                out_bytes.extend(b'\r\n')
            else:
                out_bytes.extend(line_str.encode('latin-1'))
                out_bytes.extend(b'\r\n')

    with open(txt_out_path, 'wb') as f:
        f.write(out_bytes)
    print(f"Successfully compiled custom encoded text to {txt_out_path}!")

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python helper.py extract <input_txt> <output_csv>")
        print("  python helper.py compile <input_csv> <template_txt> <output_txt>")
        return

    mode = sys.argv[1].lower()
    if mode == 'extract':
        extract(sys.argv[2], sys.argv[3])
    elif mode == 'compile':
        if len(sys.argv) < 5:
            print("Error: Missing arguments for compile mode.")
            return
        compile_translation(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()
