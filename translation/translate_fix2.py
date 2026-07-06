import csv
import re

csv_path = r'd:\git\遊戲中文化\LOOM\translation\loom_strings.csv'

def get_byte_len(text):
    return sum(2 if ord(c) > 127 else 1 for c in text)

replacements = {
    "草案": "織法",
    "紡織任何草案": "編織任何織法", # Based on user asking for '紡織任何織法' meaning fixing '紡織任何草案' which now becomes '編織任何織法'
    "紡得不對": "編織得不對",
    "紡出來": "編織出來",
    "無法紡織任何": "無法編織任何"
}

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

modified_replace = 0
errors = 0

for i, row in enumerate(rows):
    if i == 0:
        continue
    eng = row[2]
    chi = row[3] if len(row) > 3 else ""

    if chi:
        new_chi = chi
        # Apply specific logic first
        new_chi = new_chi.replace("紡織任何草案", "編織任何織法")
        new_chi = new_chi.replace("紡織任何草稿", "編織任何織法")
        new_chi = new_chi.replace("無法紡織任何", "無法編織任何")
        new_chi = new_chi.replace("紡得不對", "編織得不對")
        new_chi = new_chi.replace("紡出來", "編織出來")
        new_chi = new_chi.replace("草案", "織法")
        new_chi = new_chi.replace("草稿", "織法")
        
        if new_chi != chi:
            eng_len = get_byte_len(eng)
            chi_len = get_byte_len(new_chi)
            if chi_len <= eng_len:
                row[3] = new_chi
                modified_replace += 1
            else:
                print(f"Error at line {i+1}: '{eng}' -> '{new_chi}' is too long (Len: {chi_len} > {eng_len})")
                errors += 1

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Applied term replacements to {modified_replace} lines. Errors: {errors}")
