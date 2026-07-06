import re
import csv

def extract_japanese():
    CONTEXT_RE = re.compile(r'^\[(\d+:[^\]]+)\](.*)$')
    rows = []
    
    with open('loomtowns_kan_exported_hex.txt', 'r', encoding='latin-1') as f:
        lines = f.read().split('\n')
        
    for i, line in enumerate(lines, 1):
        if line.startswith(';;') or not line:
            continue
        m = CONTEXT_RE.match(line)
        if m:
            ctx = m.group(1)
            txt = m.group(2)
            
            # parse the \x escapes
            if '\\x' in txt:
                parts = txt.split('\\x')
                raw_bytes = bytearray()
                for p in parts[1:]:
                    if len(p) >= 2:
                        raw_bytes.append(int(p[:2], 16))
                        # if there are trailing characters, encode them as latin-1
                        if len(p) > 2:
                            raw_bytes.extend(p[2:].encode('latin-1'))
            else:
                raw_bytes = txt.encode('latin-1')
                
            try:
                dec = raw_bytes.decode('shift_jis', errors='replace')
            except Exception:
                dec = txt
                
            rows.append({'Line': i, 'Context': ctx, 'Japanese': dec})
            
    with open('loomtowns_kan.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['Line', 'Context', 'Japanese'])
        w.writeheader()
        w.writerows(rows)
        
if __name__ == '__main__':
    extract_japanese()
