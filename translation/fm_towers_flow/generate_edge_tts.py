import os
import sys
# Force utf-8 for stdout to prevent UnicodeEncodeError on Windows CP950
sys.stdout.reconfigure(encoding='utf-8')
import json
import asyncio
import zipfile
import urllib.request
import subprocess
import edge_tts

# Constants
VOICE = "en-US-ChristopherNeural" # Male English voice
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLOW_DIR = os.path.join(BASE_DIR, "translation", "fm_towers_flow")
VOICE_MAP_PATH = os.path.join(FLOW_DIR, "voice_map.json")
PORTABLE_GAME_DIR = os.path.join(BASE_DIR, "LOOM_FM-TOWNS_ZH_Portable", "game", "voice")
FFMPEG_EXE = os.path.join(FLOW_DIR, "ffmpeg.exe")

def ensure_ffmpeg():
    if os.path.exists(FFMPEG_EXE):
        return True
        
    print("ffmpeg.exe not found. Downloading static build from GitHub...")
    zip_path = os.path.join(FLOW_DIR, "ffmpeg.zip")
    
    try:
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
        print("Download complete. Extracting ffmpeg.exe...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # The structure in the zip is ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith('bin/ffmpeg.exe'):
                    file_info.filename = 'ffmpeg.exe' # flatten
                    zip_ref.extract(file_info, FLOW_DIR)
                    break
        os.remove(zip_path)
        print("ffmpeg.exe successfully set up.")
        return True
    except Exception as e:
        print(f"Error downloading ffmpeg: {e}")
        return False

import re

async def generate_voice(text, output_wav):
    temp_mp3 = output_wav.replace('.wav', '.mp3')
    
    # Generate MP3
    communicate = edge_tts.Communicate(text, VOICE)
    # Add a timeout to prevent hanging on bad inputs
    try:
        await asyncio.wait_for(communicate.save(temp_mp3), timeout=15.0)
    except asyncio.TimeoutError:
        print(f"Timeout while generating TTS for: {text[:20]}")
        return
    except Exception as e:
        print(f"Error during edge_tts generate: {e}")
        return
    
    if not os.path.exists(temp_mp3):
        return

    # Convert to WAV (22050 Hz, mono, 16-bit) to be safe for ScummVM
    cmd = [
        FFMPEG_EXE, 
        "-y", # overwrite
        "-i", temp_mp3, 
        "-ar", "22050", 
        "-ac", "1", 
        "-sample_fmt", "s16",
        output_wav
    ]
    
    # Run ffmpeg silently
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Clean up mp3
    try:
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
    except Exception as e:
        print(f"Warning: Could not remove {temp_mp3}: {e}")

async def main():
    if not ensure_ffmpeg():
        sys.exit(1)
        
    if not os.path.exists(VOICE_MAP_PATH):
        print(f"Voice map not found: {VOICE_MAP_PATH}")
        sys.exit(1)
        
    os.makedirs(PORTABLE_GAME_DIR, exist_ok=True)
    
    with open(VOICE_MAP_PATH, 'r', encoding='utf-8') as f:
        voice_map = json.load(f)
        
    total = len(voice_map)
    print(f"Loaded voice map with {total} entries. Starting generation...")
    
    count = 0
    for hash_val, data in voice_map.items():
        text = data.get("english_text", "")
        if not text:
            text = data.get("text", "")
        # Remove SCUMM escape sequences like \255, \001, \015, and literal \255
        clean_text = re.sub(r'\\[0-9]{3}', ' ', text)
        clean_text = clean_text.replace('\x01', ' ').replace('\xff', ' ').replace('+', '').replace('/', '').replace('`', '').replace('<', '')
        # Remove multiple spaces
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        suggested_file = data.get("suggested_file")
        
        if not clean_text or not suggested_file or len(clean_text) == 0:
            continue
            
        output_wav = os.path.join(PORTABLE_GAME_DIR, suggested_file)
        
        # Skip if already exists
        if os.path.exists(output_wav):
            count += 1
            continue
            
        print(f"[{count+1}/{total}] Generating: {suggested_file} -> {clean_text[:30]}...")
        
        try:
            await generate_voice(clean_text, output_wav)
        except Exception as e:
            print(f"Error generating {suggested_file}: {e}")
            
        count += 1
        
    print(f"Generation complete! Saved {count} audio files to {PORTABLE_GAME_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
