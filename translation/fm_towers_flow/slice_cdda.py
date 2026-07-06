import os
import subprocess
import re
import sys

def main():
    flow_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_exe = os.path.join(flow_dir, "ffmpeg.exe")
    
    if not os.path.exists(ffmpeg_exe):
        print(f"Error: {ffmpeg_exe} not found.")
        sys.exit(1)
        
    input_wav = os.path.abspath(os.path.join(flow_dir, "..", "..", "from steam", "LOOM", "Loom_FMTowns_Audio.wav"))
    
    if not os.path.exists(input_wav):
        print(f"Error: {input_wav} not found.")
        sys.exit(1)
        
    output_dir = os.path.abspath(os.path.join(flow_dir, "..", "..", "CDDA_Slices"))
    os.makedirs(output_dir, exist_ok=True)
    
    print("Step 1: Running silence detection (this may take a few minutes)...")
    
    # Run silencedetect
    # -35dB is a good threshold for CD audio rips. 0.5s is a good silence duration.
    cmd = [
        ffmpeg_exe, "-i", input_wav,
        "-af", "silencedetect=noise=-35dB:d=0.5",
        "-f", "null", "-"
    ]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    stderr_output = process.communicate()[1]
    
    print("Step 2: Parsing silence intervals...")
    
    # Parse ffmpeg output
    silence_starts = []
    silence_ends = [0.0] # start of file
    
    for line in stderr_output.split('\n'):
        match_start = re.search(r'silence_start:\s+([\d\.]+)', line)
        if match_start:
            silence_starts.append(float(match_start.group(1)))
            
        match_end = re.search(r'silence_end:\s+([\d\.]+)', line)
        if match_end:
            silence_ends.append(float(match_end.group(1)))
            
    # The last segment goes until the end of the file, we can get duration if we want,
    # but we can just let ffmpeg cut until EOF if we don't specify duration for the last one.
    
    segments = []
    # If file starts with silence, silence_ends[1] is the first actual audio start
    for i in range(len(silence_starts)):
        start = silence_ends[i]
        end = silence_starts[i]
        segments.append((start, end))
        
    # Check if there is audio after the last silence
    if len(silence_ends) > len(silence_starts):
        segments.append((silence_ends[-1], None))
        
    print(f"Found {len(segments)} potential voice segments.")
    print("Step 3: Slicing audio files...")
    
    count = 0
    # Process segments
    for i, (start, end) in enumerate(segments):
        # Calculate duration
        if end is not None:
            duration = end - start
        else:
            duration = 999 # arbitrary large number for the last segment
            
        # Filter: Skip segments shorter than 0.5 seconds (likely noise/clicks)
        # Note: Per user request, we DO NOT filter long segments (>10s) anymore!
        if duration < 0.5:
            continue
            
        count += 1
        out_file = os.path.join(output_dir, f"voice_{count:04d}.wav")
        
        # Skip if already exists
        if os.path.exists(out_file):
            continue
            
        print(f"[{count}] Slicing {start:.2f}s to {end if end else 'EOF'} (Duration: {duration:.2f}s)...")
        
        # Fast seeking requires -ss BEFORE -i
        slice_cmd = [ffmpeg_exe, "-y", "-ss", str(start)]
        if end is not None:
            slice_cmd.extend(["-t", str(duration)])
        slice_cmd.extend(["-i", input_wav, "-c", "copy", out_file])
        
        subprocess.run(slice_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    print(f"Complete! Extracted {count} voice segments to {output_dir}")

if __name__ == "__main__":
    main()
