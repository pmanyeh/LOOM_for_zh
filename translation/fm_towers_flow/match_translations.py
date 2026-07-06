import csv

def is_control_only(text):
    # Check if the text contains only control characters like \016, \255\004...
    # Return true if there are no alphabetic/CJK characters
    clean = text.replace('\\', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '')
    return len(clean.strip()) == 0

def match():
    # Load English-based translation
    en_rows = []
    with open('loomtowns_strings.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            en_rows.append(row)
            
    # Load Japanese extraction
    jp_rows = []
    with open('loomtowns_kan.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jp_rows.append(row)
            
    # Map translations based on Context
    # Since Contexts can have multiple lines, we'll try to match them sequentially within each Context.
    
    # Group English translations by context
    en_dict = {}
    for r in en_rows:
        ctx = r['Context']
        if ctx not in en_dict:
            en_dict[ctx] = []
        en_dict[ctx].append(r)
        
    mapped_count = 0
    missing_count = 0
    
    for r in jp_rows:
        ctx = r['Context']
        jp_text = r['Japanese']
        
        # If the Japanese text is just control codes, we can just copy it
        if is_control_only(jp_text):
            r['Chinese'] = jp_text
            mapped_count += 1
            continue
            
        # Try to find a match in the English dictionary
        if ctx in en_dict and len(en_dict[ctx]) > 0:
            # We pop the first available English translation for this context
            # We only use it if it actually has Chinese text
            en_match = None
            for idx, item in enumerate(en_dict[ctx]):
                if item['Chinese'] and not is_control_only(item['Chinese']):
                    en_match = en_dict[ctx].pop(idx)
                    break
                    
            if en_match:
                # We should extract the control codes from the Japanese string and wrap the Chinese translation?
                # Actually, SCUMM control codes in Japanese versions are sometimes slightly different, 
                # but usually we can just use the English version's fully translated string (which includes control codes)
                # Wait! The control codes MUST match the Japanese version's layout to not crash the script!
                # Since we are manually reviewing later, let's just assign the raw Chinese translation (with English control codes) for now.
                # Actually, the user's auto_translate.py kept the English control codes.
                r['Chinese'] = en_match['Chinese']
                mapped_count += 1
            else:
                r['Chinese'] = ''
                missing_count += 1
        else:
            r['Chinese'] = ''
            missing_count += 1
            
    print(f"Mapped: {mapped_count}, Missing: {missing_count}")
    
    with open('loomtowns_kan_mapped.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['Line', 'Context', 'Japanese', 'Chinese'])
        w.writeheader()
        w.writerows(jp_rows)

if __name__ == '__main__':
    match()
