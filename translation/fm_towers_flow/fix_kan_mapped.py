import csv

with open('loomtowns_kan_mapped.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

for r in rows:
    if not r['Chinese']:
        r['Chinese'] = r['Japanese']

with open('loomtowns_kan_mapped.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['Line', 'Context', 'Japanese', 'Chinese'])
    w.writeheader()
    w.writerows(rows)
