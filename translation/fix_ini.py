import os
ini_path = os.path.expandvars('%APPDATA%\\ScummVM\\scummvm.ini')

try:
    with open(ini_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    encoding = 'utf-8'
except UnicodeDecodeError:
    with open(ini_path, 'r', encoding='mbcs') as f:
        lines = f.readlines()
    encoding = 'mbcs'

new_lines = []
for l in lines:
    if l.startswith('path=D:\\git\\'):
        new_lines.append('path=d:\\git\\遊戲中文化\\LOOM\\from steam\\LOOM\\\n')
    else:
        new_lines.append(l)

with open(ini_path, 'w', encoding=encoding) as f:
    f.writelines(new_lines)
print("INI path fixed successfully.")
