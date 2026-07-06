import os
import shutil

def main():
    flow_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(flow_dir))
    game_voice_dir = os.path.join(base_dir, "LOOM_FM-TOWNS_ZH_Portable", "game", "voice")
    rvc_workspace = os.path.join(base_dir, "rvc_workspace")
    
    if not os.path.exists(rvc_workspace):
        print(f"Error: {rvc_workspace} not found. Please run prepare_rvc.py and perform RVC conversion first.")
        return
        
    copied_count = 0
    # Scan for any folder ending with _output
    for folder_name in os.listdir(rvc_workspace):
        if folder_name.endswith("_output"):
            output_dir = os.path.join(rvc_workspace, folder_name)
            if not os.path.isdir(output_dir):
                continue
                
            for filename in os.listdir(output_dir):
                if filename.lower().endswith(".wav"):
                    src_file = os.path.join(output_dir, filename)
                    dst_file = os.path.join(game_voice_dir, filename)
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1
                    
    print(f"RVC Application Complete!")
    print(f"Merged {copied_count} converted files back into {game_voice_dir}")

if __name__ == "__main__":
    main()
