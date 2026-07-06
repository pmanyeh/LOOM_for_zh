import wave
import math
import struct
import os

def create_beep_wav(filepath, duration_seconds=1.0, frequency_hz=440.0, sample_rate=22050):
    # Generates a simple sine wave beep
    num_samples = int(duration_seconds * sample_rate)
    
    # Open WAV file
    with wave.open(filepath, 'wb') as wav_file:
        # Mono, 2 bytes per sample (16-bit), sample_rate
        wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
        
        for i in range(num_samples):
            # Calculate sine value
            t = float(i) / sample_rate
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency_hz * t))
            # Pack value to 16-bit signed integer
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)
            
    print(f"Generated test beep wav at {filepath}")

def main():
    flow_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(flow_dir))
    
    # Path to game voice directory in portable folder
    voice_dir = os.path.join(base_dir, "LOOM_FM-TOWNS_ZH_Portable", "game", "voice")
    os.makedirs(voice_dir, exist_ok=True)
    
    # Target file: 63f4f1bf.wav ("一個使者仙女！")
    target_wav = os.path.join(voice_dir, "63f4f1bf.wav")
    create_beep_wav(target_wav, duration_seconds=1.5, frequency_hz=600.0)
    
    # Let's also create a copy in the root folder just in case
    create_beep_wav(os.path.join(voice_dir, "a1", "63f4f1bf.wav") if os.path.exists(os.path.join(voice_dir, "a1")) else os.path.join(voice_dir, "63f4f1bf.wav"))

if __name__ == "__main__":
    main()
