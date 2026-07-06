import subprocess
import shutil
import os
import glob

with open('loomtowns_kan_zh_injected.txt', 'rb') as f:
    lines = f.readlines()

low = 0
high = len(lines) - 1
bad_line = -1

while low <= high:
    mid = (low + high) // 2
    print(f"Testing lines 0 to {mid}...")
    
    with open('test_line.txt', 'wb') as f:
        f.writelines(lines[:mid+1])
        
    for src_file in glob.glob(r'd:\git\遊戲中文化\LOOM\from FM Towers\LOOMKAN\*.LFL'):
        fname = os.path.basename(src_file)
        shutil.copyfile(src_file, os.path.join(r'tmp_test_scummtr', fname))
        tmp = os.path.join(r'tmp_test_scummtr', fname + '~~scummio-tmp')
        if os.path.exists(tmp):
            os.remove(tmp)
        
    res = subprocess.run([
        r'.\scummtr.exe', '-w', '-h', '-g', 'loomtowns', '-i', '-f', 'test_line.txt', '-p', 
        r'tmp_test_scummtr'
    ], capture_output=True)
    
    if b'Unknown function id' in res.stdout or b'Unknown function id' in res.stderr:
        print(f"Failed at mid {mid}. Error is in lower half.")
        bad_line = mid
        high = mid - 1
    else:
        print(f"Passed at mid {mid}. Error is in upper half.")
        low = mid + 1

if bad_line != -1:
    print(f"FIRST BAD LINE: {bad_line}")
    print(lines[bad_line])
else:
    print("NO BAD LINE FOUND??")
