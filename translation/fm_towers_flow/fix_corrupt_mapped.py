import csv

# Load English strings
en_dict = {}
with open('loomtowns_strings.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ctx = row['Context']
        if ctx not in en_dict:
            en_dict[ctx] = []
        en_dict[ctx].append(row)

# Load mapped strings
jp_rows = []
with open('loomtowns_kan_mapped.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        jp_rows.append(row)

# Fix corrupted Japanese control codes by using English equivalents
for row in jp_rows:
    if '\\x' in repr(row['Chinese']) or '\\x' in repr(row['Japanese']) or '嚙' in repr(row['Chinese']):
        ctx = row['Context']
        if ctx in en_dict and len(en_dict[ctx]) > 0:
            en_row = en_dict[ctx][0]
            if en_row['Chinese']:
                row['Chinese'] = en_row['Chinese']
            else:
                row['Chinese'] = en_row['English']
                
            print(f"Fixed {ctx} using English: {repr(row['Chinese'])}")

with open('loomtowns_kan_mapped.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['Line', 'Context', 'Japanese', 'Chinese'])
    w.writeheader()
    w.writerows(jp_rows)
