import csv

with open('loom_strings.csv', 'r', encoding='utf-8') as f_in:
    reader = csv.reader(f_in)
    with open('loom_strings_translated.txt', 'w', encoding='utf-8') as f_out:
        for row in reader:
            if len(row) >= 4 and row[3].strip():
                f_out.write(f'{row[1]},"{row[3]}"\n')
