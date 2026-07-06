import json

with open('charmap.json', 'r', encoding='utf-8') as f:
    charmap = json.load(f)

target = ['請', '擇', '遊', '選', '戲', '難', '度']
res = {k: charmap.get(k) for k in target}
print(res)
