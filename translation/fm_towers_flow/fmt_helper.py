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

def compile_translation(csv_path, txt_template_path, txt_out_path, charmap_path="sjis_charmap.json"):
    print(f"Compiling {csv_path} -> {txt_out_path} using custom encoding...")
    if not os.path.exists(csv_path):
        print(f"Error: CSV file {csv_path} does not exist.")
        return
    if not os.path.exists(txt_template_path):
        print(f"Error: Template file {txt_template_path} does not exist.")
        return
    if not os.path.exists(charmap_path):
        print("Error: sjis_charmap.json not found! Please run generate_fnt.py first.")
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
                english = row.get('English', row.get('Japanese', ''))
                translations.append(chinese if chinese else english)
    except UnicodeDecodeError:
        print("Detected non-UTF8 CSV. Falling back to cp950 (Big5)...")
        with open(csv_path, 'r', encoding='cp950', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                chinese = row['Chinese'].strip()
                english = row.get('English', row.get('Japanese', ''))
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
                
                # Calculate injected lengths
                orig_injected_len = len(match.group(2)) - len(re.findall(r'\\\d{3}', match.group(2))) * 3
                
                trans_injected_len = 0
                for c in translated_text:
                    if ord(c) < 128:
                        trans_injected_len += 1
                    else:
                        trans_injected_len += 2
                trans_injected_len -= len(re.findall(r'\\\d{3}', translated_text)) * 3

                # Encode translated text using charmap
                encoded_bytes = bytearray()
                for c in translated_text:
                    if ord(c) < 128:
                        encoded_bytes.append(ord(c))
                    elif c in charmap:
                        code = charmap[c]
                        encoded_bytes.append(code[0])
                        encoded_bytes.append(code[1])
                    else:
                        encoded_bytes.append(0x20)

                # Pad or truncate to original length to prevent scummtr pointer bugs
                if trans_injected_len < orig_injected_len:
                    padding = orig_injected_len - trans_injected_len
                    lines = encoded_bytes.split(b'\\255\\001')
                    num_lines = len(lines)
                    base_pad = padding // num_lines
                    extra_pad = padding % num_lines
                    new_lines = []
                    for i, line_bytes in enumerate(lines):
                        line_pad = base_pad + (1 if i < extra_pad else 0)
                        left_pad = line_pad // 2
                        right_pad = line_pad - left_pad
                        new_lines.append((b' ' * left_pad) + line_bytes + (b' ' * right_pad))
                    encoded_bytes = b'\\255\\001'.join(new_lines)
                elif trans_injected_len > orig_injected_len:
                    print(f"Warning: [{match.group(1)}] Translated string is longer than original ({trans_injected_len} > {orig_injected_len}). Truncating to fit!")
                    # Keep the last characters as they might be control codes, truncate from the end of text (before control codes)
                    # For simplicity, since the difference is small, we truncate from the end. But wait, control codes are at the end!
                    # Actually, we can just truncate encoded_bytes.
                    encoded_bytes = encoded_bytes[:orig_injected_len]

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
