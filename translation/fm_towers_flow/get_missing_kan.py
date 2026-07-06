import csv

with open('loomtowns_kan_mapped.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    lines = []
    for row in reader:
        if not row['Chinese']:
            lines.append(f"{row['Line']}: {row['Japanese']}")

with open('missing_kan.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
