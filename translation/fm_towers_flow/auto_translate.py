import csv
import re
import time
from googletrans import Translator

def get_byte_len(text):
    return sum(2 if ord(c) > 127 else 1 for c in text)

def main():
    target_csv = r'd:\git\遊戲中文化\LOOM\translation\fm_towers_flow\loomtowns_strings.csv'
    translator = Translator()
    
    with open(target_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    print(f"Total rows: {len(rows)}")
    translated_count = 0
    
    try:
        for i, row in enumerate(rows):
            eng = row.get('English', '')
            chi = row.get('Chinese', '')
            
            if not chi and any(c.isalpha() for c in eng):
                # preserve SCUMM escape codes by pulling them out
                escapes = re.findall(r'\\\d{3}', eng)
                clean_text = re.sub(r'\\\d{3}', '', eng).strip()
                
                if clean_text:
                    try:
                        trans_result = translator.translate(clean_text, dest='zh-tw').text
                        # put back escapes at the beginning or end depending on where they were
                        # simple approach: just put them all at the end
                        trans = trans_result + "".join(escapes)
                        
                        # Check length limit
                        eng_len = get_byte_len(eng)
                        chi_len = get_byte_len(trans)
                        
                        # Truncate if too long
                        while chi_len > eng_len and len(trans) > len("".join(escapes)):
                            # remove last character before escapes
                            trans = trans[:-(len("".join(escapes)) + 1)] + "".join(escapes)
                            chi_len = get_byte_len(trans)
                            
                        row['Chinese'] = trans
                        translated_count += 1
                        
                        if translated_count % 50 == 0:
                            print(f"Translated {translated_count} strings...")
                            
                        # Save periodically
                        if translated_count % 100 == 0:
                            with open(target_csv, 'w', encoding='utf-8-sig', newline='') as f_out:
                                writer = csv.DictWriter(f_out, fieldnames=['Line', 'Context', 'English', 'Chinese'])
                                writer.writeheader()
                                writer.writerows(rows)
                                
                    except Exception as e:
                        print(f"Error translating: {eng} - {e}")
                        time.sleep(1) # wait if error
                        
    except KeyboardInterrupt:
        print("Interrupted by user.")
        
    print(f"Translated {translated_count} new missing strings.")
    
    with open(target_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Line', 'Context', 'English', 'Chinese'])
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    main()
