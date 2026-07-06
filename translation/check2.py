import json

with open('charmap.json', 'r', encoding='utf-8') as f:
    charmap = json.load(f)

# Hardcode the hex representation of the target characters to bypass any console mangling
target = ['\u8acb', '\u64c7', '\u904a', '\u9078', '\u6232', '\u96e3', '\u5ea6']

res = {k: charmap.get(k) for k in target}
with open('res.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False)
