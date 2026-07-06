import os
import shutil
from generate_fmt_fnt import generate_fmt_fnt
from fmt_helper import compile_translation
from generate_voice_map import main as generate_voice_map

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    flow_dir = os.path.join(base_dir, "translation", "fm_towers_flow")
    
    csv_path = os.path.join(flow_dir, "loomtowns_strings.csv")
    ttf_path = r"C:\Windows\Fonts\mingliu.ttc"
    out_rom_path = os.path.join(flow_dir, "FMT_FNT.ROM")
    out_json_path = os.path.join(flow_dir, "sjis_charmap.json")
    
    template_txt = os.path.join(flow_dir, "loomtowns_en.txt")
    out_injected_txt = os.path.join(flow_dir, "loomtowns_zh_injected.txt")
    
    # Target directories
    patch_dir = os.path.join(base_dir, "FM-TOWNS_Patch")
    portable_game_dir = os.path.join(base_dir, "LOOM_FM-TOWNS_ZH_Portable", "game")
    portable_root_dir = os.path.join(base_dir, "LOOM_FM-TOWNS_ZH_Portable")
    
    print("=== Step 1: Generating Chinese Font ROM (FMT_FNT.ROM) ===")
    generate_fmt_fnt(csv_path, ttf_path, out_rom_path, out_json_path)
    
    print("\n=== Step 2: Compiling Translation Strings ===")
    compile_translation(csv_path, template_txt, out_injected_txt, charmap_path=out_json_path)
    
    print("\n=== Step 3: Generating Voice Map (voice_map.json) ===")
    generate_voice_map()
    out_map_path = os.path.join(flow_dir, "voice_map.json")
    
    print("\n=== Step 4: Copying Patched Files & Voice Map to Target Directories ===")
    targets = [patch_dir, portable_game_dir]
    for target in targets:
        if os.path.exists(target):
            shutil.copy2(out_rom_path, os.path.join(target, "FMT_FNT.ROM"))
            shutil.copy2(out_injected_txt, os.path.join(target, "loomtowns_zh_injected.txt"))
            shutil.copy2(out_map_path, os.path.join(target, "voice_map.json"))
            print(f"Copied files to: {target}")
        else:
            print(f"Warning: Target directory {target} does not exist. Skipping.")
            
    print("\n=== Step 5: Normalizing Portable Batch Files (UTF-8 BOM + CRLF) ===")
    batch_files = [
        os.path.join(portable_root_dir, "play.bat"),
        os.path.join(portable_root_dir, "安裝中文化.bat")
    ]
    for bat_path in batch_files:
        if os.path.exists(bat_path):
            with open(bat_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Standardize line endings to Windows CRLF
            content = content.replace('\r\n', '\n').replace('\n', '\r\n')
            # Write back as UTF-8 with BOM
            with open(bat_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            print(f"Normalized: {os.path.basename(bat_path)} (UTF-8 BOM & CRLF)")
        else:
            print(f"Warning: Batch file {bat_path} does not exist. Skipping.")
            
    print("\n=== Pipeline Complete Successfully! ===")

if __name__ == "__main__":
    main()

