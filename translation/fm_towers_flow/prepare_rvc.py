import os
import json
import shutil

def main():
    flow_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(flow_dir))
    game_voice_dir = os.path.join(base_dir, "LOOM_FM-TOWNS_ZH_Portable", "game", "voice")
    voice_map_path = os.path.join(flow_dir, "voice_map.json")
    rvc_workspace = os.path.join(base_dir, "rvc_workspace")
    
    if not os.path.exists(voice_map_path):
        print(f"Error: {voice_map_path} not found.")
        return
        
    with open(voice_map_path, 'r', encoding='utf-8') as f:
        voice_map = json.load(f)
        
    copied_count = 0
    for h, data in voice_map.items():
        actor = data.get("actor", "").strip()
        if not actor:
            continue
            
        actor_input_dir = os.path.join(rvc_workspace, f"{actor}_input")
        os.makedirs(actor_input_dir, exist_ok=True)
        
        src_file = os.path.join(game_voice_dir, f"{h}.wav")
        dst_file = os.path.join(actor_input_dir, f"{h}.wav")
        
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            copied_count += 1
            
    print(f"RVC Preparation Complete!")
    print(f"Copied {copied_count} files into actor-specific folders inside {rvc_workspace}")

if __name__ == "__main__":
    main()
