import csv
import re
import time
import urllib.request
import urllib.parse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_byte_len(text):
    length = sum(2 if ord(c) > 127 else 1 for c in text)
    length -= len(re.findall(r'\\\d{3}', text)) * 3
    return length

def is_bad_control_code_placement(eng, chi):
    if not chi:
        return False
    eng_codes = re.findall(r'\\\d{3}', eng)
    if not eng_codes:
        return False
    eng_ends_with_code = eng.endswith(eng_codes[-1])
    chi_codes = re.findall(r'(\\\d{3})+$', chi)
    if chi_codes and not eng_ends_with_code:
        return True
    return False

def translate_chunk(text):
    if not text.strip():
        return text
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-TW&dt=t&q=' + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode('utf-8'))
                return ''.join([part[0] for part in res[0]])
        except Exception as e:
            time.sleep(1)
    print(f"Failed to translate chunk: {text}")
    return text

def translate_with_codes(eng):
    parts = re.split(r'(\\\d{3})', eng)
    translated_parts = []
    for part in parts:
        if re.match(r'\\\d{3}', part):
            translated_parts.append(part)
        elif part.strip():
            trans = translate_chunk(part)
            translated_parts.append(trans)
        else:
            translated_parts.append(part)
    return translated_parts

def enforce_length(eng, translated_parts):
    eng_len = get_byte_len(eng)
    while True:
        chi = "".join(translated_parts)
        chi_len = get_byte_len(chi)
        if chi_len <= eng_len:
            break
        longest_idx = -1
        longest_len = -1
        for i, part in enumerate(translated_parts):
            if not re.match(r'\\\d{3}', part) and len(part.strip()) > 0:
                l = len(part)
                if l > longest_len:
                    longest_len = l
                    longest_idx = i
        if longest_idx != -1:
            part = translated_parts[longest_idx]
            translated_parts[longest_idx] = part[:-1]
        else:
            break
    return "".join(translated_parts)

def process_row(args):
    idx, row = args
    eng = row.get('English', '')
    chi = row.get('Chinese', '')
    
    needs_translation = False
    is_fix = False
    
    if not chi and any(c.isalpha() for c in eng):
        needs_translation = True
    elif is_bad_control_code_placement(eng, chi):
        needs_translation = True
        is_fix = True
        
    if needs_translation:
        translated_parts = translate_with_codes(eng)
        final_trans = enforce_length(eng, translated_parts)
        row['Chinese'] = final_trans
        return idx, row, True, is_fix
    return idx, row, False, False

def main():
    target_csv = r'd:\git\遊戲中文化\LOOM\translation\loom_strings.csv'
    
    with open(target_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total rows: {len(rows)}")
    translated_count = 0
    fixed_count = 0
    
    tasks = [(i, row) for i, row in enumerate(rows)]
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_row, task): task for task in tasks}
        for i, future in enumerate(as_completed(futures)):
            idx, row, was_translated, is_fix = future.result()
            rows[idx] = row
            if was_translated:
                if is_fix:
                    fixed_count += 1
                else:
                    translated_count += 1
            if (i+1) % 50 == 0:
                print(f"Processed {i+1}/{len(rows)} lines...")

    print(f"Finished! Translated {translated_count} new strings. Fixed {fixed_count} existing strings.")
    
    with open(target_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Line', 'Context', 'English', 'Chinese'])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    main()
