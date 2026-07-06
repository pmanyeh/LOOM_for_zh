import csv
import re
import string

def normalize_text(text):
    # Remove SCUMM escape sequences
    text = re.sub(r'\\\d{3}', '', text)
    # Remove punctuation and spaces, convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)).replace(" ", "").lower()
    return text

def main():
    source_csv = r'd:\git\遊戲中文化\LOOM\translation\loom_strings.csv'
    target_csv = r'd:\git\遊戲中文化\LOOM\translation\fm_towers_flow\loomtowns_strings.csv'
    
    translations = {}
    normalized_translations = {}
    
    with open(source_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eng = row.get('English', '').strip()
            chi = row.get('Chinese', '').strip()
            if chi:
                translations[eng] = chi
                normalized_translations[normalize_text(eng)] = (eng, chi)
                
    with open(target_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        target_rows = list(reader)
        
    mapped_count = 0
    missing = []
    
    for row in target_rows:
        eng = row.get('English', '').strip()
        # exact match first
        if eng in translations:
            row['Chinese'] = translations[eng]
            mapped_count += 1
        elif eng:
            norm_eng = normalize_text(eng)
            if norm_eng in normalized_translations and norm_eng != "":
                # Found a fuzzy match
                matched_eng, chi_trans = normalized_translations[norm_eng]
                
                # Now we need to re-insert the SCUMM escape sequences from the original `eng` into the `chi_trans`
                # A simple approach for now: if the translation doesn't need precise escape placement, just copy it.
                # Actually, in LOOM CD, we often kept the original escapes at the start/end or just used the chi_trans.
                # Let's just use the `chi_trans` but warn if escapes differ significantly.
                # Wait, it's safer to just take the chi_trans, since our `helper.py compile` handles length padding.
                # But wait, we need the exact `\255` codes that are in the TARGET `eng`, not the SOURCE `chi_trans`.
                
                # Let's try to extract prefixes/suffixes like \255\001
                prefix_escapes = "".join(re.findall(r'^(\\\d{3})+', eng))
                suffix_escapes = "".join(re.findall(r'(\\\d{3})+$', eng))
                
                # Clean the translation from its own escapes
                clean_chi = re.sub(r'\\\d{3}', '', chi_trans)
                
                # Re-apply the target's prefix and suffix
                new_chi = prefix_escapes + clean_chi + suffix_escapes
                
                row['Chinese'] = new_chi
                mapped_count += 1
            else:
                if any(c.isalpha() for c in eng):
                    missing.append(eng)
    
    print(f"Mapped: {mapped_count}, Missing: {len(missing)}")
    if missing:
        print("First 10 missing strings:")
        for m in missing[:10]:
            print(f" - {m}")
            
    with open(target_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Line', 'Context', 'English', 'Chinese'])
        writer.writeheader()
        writer.writerows(target_rows)

if __name__ == '__main__':
    main()
