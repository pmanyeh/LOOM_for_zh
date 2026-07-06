# Skill: LOOM FM-Towns Translation & Voice Update Pipeline

This skill instructs the agent on how to execute the complete workflow for updating the Traditional Chinese translation, rebuilding the font and string assets, generating updated voice maps, and automatically downloading missing TTS audio files.

---

## Prerequisites
- **Python 3** with `pillow`, `edge-tts`, and `ffmpeg` available.
- Input translation file: `translation\fm_towers_flow\loomtowns_strings.csv`

---

## Pipeline Execution Steps

When a user modifies the translation in `loomtowns_strings.csv`, follow these steps exactly in order:

### 1. Set Working Directory
All scripts must be run from the automation directory:
`d:\git\遊戲中文化\LOOM\translation\fm_towers_flow`

### 2. Compile Translation, Font, and Voice Map
Run the master packaging script:
```bash
python compile_and_package.py
```
**What this does:**
1. **Generates Font ROM (`FMT_FNT.ROM`)**: Parses new characters and renders them into the custom SJIS-mapped ROM.
2. **Compiles Text Strings**: Converts the CSV translation into the custom-encoded `loomtowns_zh_injected.txt` format with proper SCUMM control codes.
3. **Generates Voice Map (`voice_map.json`)**: Automatically calculates the FNV-1a hash (ignoring control codes) for all translated dialogue lines.
4. **Distributes Assets**: Automatically copies the ROM, injected text, and voice map to the `LOOM_FM-TOWNS_ZH_Portable\game` directory.

### 3. Generate Missing TTS Audio
Run the Edge-TTS generation script:
```bash
python generate_edge_tts.py
```
**What this does:**
1. Loads the newly generated `voice_map.json`.
2. Checks the `LOOM_FM-TOWNS_ZH_Portable\game\voice` directory.
3. **CRITICAL**: It automatically skips any `.wav` files that already exist. It will *only* connect to the cloud and download audio for the newly modified or added sentences (which have new hashes).
4. Converts the downloaded audio to 22050Hz, Mono, 16-bit WAV files compatible with the ScummVM engine.

---

## Expanding the Voice Map (Missing Lines)

By default, only scripts marked as `SC` (Script) or `LS` (Local Script) in the CSV's Context column are extracted for voice generation to prevent system menus from being spoken.

If a specific dialogue line is missing from `voice_map.json`:
1. Open `generate_voice_map.py`.
2. Locate the prefix filter around line 81:
   ```python
   if prefix not in ("SC", "LS", "OC", "EN"):
   ```
3. Add the required prefix (e.g., `OC` for Object Comment) to the tuple.
4. Re-run `compile_and_package.py` and `generate_edge_tts.py` to generate the newly included voices.

---

## Future Expansion: Multi-Actor Voice Cloning

When transitioning from Single-Actor TTS to Multi-Actor Voice Cloning (RVC/ElevenLabs):
1. **Update CSV**: Add an `Actor` column to `loomtowns_strings.csv` (e.g., Bobbin, Elder).
2. **Update JSON Map**: Modify `generate_voice_map.py` to include the `Actor` field in `voice_map.json`.
3. **Route Audio Generation**: Modify `generate_edge_tts.py` to read the `Actor` field and switch voice models/API keys dynamically based on the character speaking. The generated `.wav` files will perfectly overwrite the old single-actor files without requiring any C++ engine changes.
