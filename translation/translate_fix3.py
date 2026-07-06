import csv
import re

translations = {
    "Yuck.": "好噁.",
    "Aieeeeaaah!": "啊啊啊啊啊",
    "OUCH!": "哎喲!",
    "Or trouble.": "或找麻煩。",
    "Fleece?": "Fleece?",
    "Me neither.": "我也是。",
    "She isn't.": "她不好。"
}

def get_byte_len(text):
    return sum(2 if ord(c) > 127 else 1 for c in text)

csv_path = r'd:\git\遊戲中文化\LOOM\translation\loom_strings.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

modified = 0

for i, row in enumerate(rows):
    if i == 0:
        continue
    eng = row[2]
    chi = row[3] if len(row) > 3 else ""

    if not chi and eng in translations:
        translated = translations[eng]
        eng_len = get_byte_len(eng)
        chi_len = get_byte_len(translated)

        if chi_len <= eng_len:
            if len(row) > 3:
                row[3] = translated
            else:
                row.append(translated)
            modified += 1
        else:
            print(f"Error at line {i+1}: '{eng}' -> '{translated}' is too long (Len: {chi_len} > {eng_len})")

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Fixed {modified} lines.")
