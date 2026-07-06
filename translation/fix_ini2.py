import os
import shutil

ini_path = os.path.expandvars('%APPDATA%\\ScummVM\\scummvm.ini')
bak_path = ini_path + '.bak'

# Backup the file just in case
shutil.copy2(ini_path, bak_path)

# Read the file. It currently has a mix of ascii and Big5 (mbcs)
try:
    with open(ini_path, 'r', encoding='mbcs') as f:
        lines = f.readlines()
except Exception as e:
    print(f"Error reading mbcs: {e}")
    # Fallback if something weird is there
    with open(ini_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

new_lines = []
for l in lines:
    if l.startswith('path=D:\\git\\'):
        # Force the correct path in proper string
        new_lines.append('path=D:\\git\\遊戲中文化\\LOOM\\from steam\\LOOM\\\n')
    else:
        new_lines.append(l)

# Write the file strictly as UTF-8
with open(ini_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("INI file rewritten as UTF-8 successfully.")
