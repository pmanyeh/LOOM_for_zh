import csv
import os
import re

eng_csv_path = r'd:\git\遊戲中文化\LOOM\translation\loom_strings.csv'
towns_csv_path = r'd:\git\遊戲中文化\LOOM\translation\fm_towers_flow\loomtowns_strings.csv'

def get_injected_length(text):
    # Calculate byte length: ASCII = 1, Non-ASCII = 2, Control codes \xxx = 0 (handled by SCUMM engine as internal bytes)
    length = 0
    for c in text:
        if ord(c) < 128:
            length += 1
        else:
            length += 2
    # Subtract the length of the string representation of control codes
    length -= len(re.findall(r'\\\d{3}', text)) * 3
    return length

if not os.path.exists(eng_csv_path) or not os.path.exists(towns_csv_path):
    print("Error: CSV files not found.")
    exit()

# Load FM-Towns translations
towns_dict = {}
with open(towns_csv_path, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        if row['Chinese'].strip():
            towns_dict[row['English']] = row['Chinese'].strip()

# Process English CSV
rows = []
migrated_count = 0
with open(eng_csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row['Chinese'].strip() and row['English'] in towns_dict:
            english_text = row['English']
            chinese_text = towns_dict[english_text]
            
            orig_len = get_injected_length(english_text)
            new_len = get_injected_length(chinese_text)
            
            if new_len <= orig_len:
                row['Chinese'] = chinese_text
                migrated_count += 1
            else:
                print(f"Skipped migration for line {row['Line']} due to length constraint ({new_len} > {orig_len}).")
        
        rows.append(row)

# Save back to English CSV
with open(eng_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Line', 'Context', 'English', 'Chinese'])
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully migrated {migrated_count} translations from FM-TOWNS to English version.")
