import os
import wave
import struct

def extract_cdda(cdda_path, wav_path):
    print(f"Opening {cdda_path}...")
    if not os.path.exists(cdda_path):
        print("CDDA.SOU not found!")
        return

    START_OF_CDDA_DATA = 800
    BLOCK_SIZE = 1177

    with open(cdda_path, 'rb') as f:
        file_size = os.path.getsize(cdda_path)
        f.seek(START_OF_CDDA_DATA)
        
        blocks = (file_size - START_OF_CDDA_DATA) // BLOCK_SIZE
        total_samples = blocks * 1176  # Each block has 1 byte shift, then 1176 bytes of data
        
        print(f"Total blocks: {blocks}, Total stereo samples: {total_samples // 2}")

        with wave.open(wav_path, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)

            buffer = bytearray()
            for b in range(blocks):
                block_data = f.read(BLOCK_SIZE)
                if len(block_data) < BLOCK_SIZE:
                    break
                
                shift_val = block_data[0]
                shift_left = shift_val >> 4
                shift_right = shift_val & 0x0F
                
                # Process 1176 bytes as pairs of L/R
                for i in range(1, BLOCK_SIZE, 2):
                    if i + 1 >= BLOCK_SIZE:
                        break
                    
                    # Read signed bytes
                    l_byte = block_data[i]
                    r_byte = block_data[i+1]
                    
                    if l_byte > 127: l_byte -= 256
                    if r_byte > 127: r_byte -= 256
                    
                    # Apply shift
                    l_val = l_byte << shift_left
                    r_val = r_byte << shift_right
                    
                    # Clamp to 16-bit signed
                    l_val = max(-32768, min(32767, l_val))
                    r_val = max(-32768, min(32767, r_val))
                    
                    buffer.extend(struct.pack('<hh', l_val, r_val))
                
                # Write to file in chunks
                if len(buffer) >= 1024 * 1024:
                    wav.writeframesraw(buffer)
                    buffer.clear()
                    
                if b % 10000 == 0:
                    print(f"Processed {b}/{blocks} blocks...")

            if buffer:
                wav.writeframesraw(buffer)
                
    print(f"Extraction complete! Saved to {wav_path}")

if __name__ == "__main__":
    cdda_file = r"D:\git\遊戲中文化\LOOM\from steam\LOOM\CDDA.SOU"
    out_wav = r"D:\git\遊戲中文化\LOOM\from steam\LOOM\Loom_FMTowns_Audio.wav"
    extract_cdda(cdda_file, out_wav)
