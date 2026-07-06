# Skill: LOOM FM-Towns Patch Compilation & Packaging Pipeline

This skill instructs the agent on how to compile the Traditional Chinese translation, generate the custom Japanese SJIS-mapped font (`FMT_FNT.ROM`), copy the output assets to the distribution folders, and normalize batch file encodings.

---

## Prerequisites
- **Python 3** with `pillow` library (PIL) installed for rendering the custom font ROM.
- Input translation file: `translation\fm_towers_flow\loomtowns_strings.csv`

---

## Automated Compilation & Packaging

The entire process is automated via the Python script:
`translation\fm_towers_flow\compile_and_package.py`

### Steps to Execute
1. Set the working directory to:
   `d:\git\遊戲中文化\LOOM\translation\fm_towers_flow`
2. Run the pipeline script:
   ```bash
   python compile_and_package.py
   ```

### What this script does automatically:
1. **Generates Font ROM (`FMT_FNT.ROM`)**: Parses all unique Chinese characters in the CSV, renders them onto a 16x16 grid with MingLiU font, and writes them into a 288KB (294,912 bytes) binary ROM file.
2. **Compiles Text Strings**: Converts the CSV translation into the custom-encoded `loomtowns_zh_injected.txt` format, adjusting padding and control characters for injection.
3. **Copies Outputs**: Distributes `FMT_FNT.ROM` and `loomtowns_zh_injected.txt` to:
   - `FM-TOWNS_Patch\` (Standard patch pack)
   - `LOOM_FM-TOWNS_ZH_Portable\game\` (Portable免安裝版 game folder)
4. **Normalizes Batch Files**: Normalizes the line endings and encodings of `play.bat` and `安裝中文化.bat` in `LOOM_FM-TOWNS_ZH_Portable\` to **UTF-8 with BOM** and **CRLF (Windows)** to prevent command prompt encoding crashes.

---

## Verification
- Confirm that `FMT_FNT.ROM` is exactly **294,912 bytes** in size in both destination folders.
- Verify `play.bat` and `安裝中文化.bat` can be opened in Notepad showing correct Chinese characters.

---

## Troubleshooting
### Error: `Bad escaping in line X`
- **Cause**: A stray backslash `\` was written in the Chinese translation column of `loomtowns_strings.csv` (e.g. `如果那個火爐\熄滅了`). In SCUMM text, `\` is treated as a control escape prefix.
- **Solution**: Open `loomtowns_strings.csv`, search for the line, and ensure backslashes are only used for official engine codes (like `\255\001` or `\015`). Replace any accidental backslashes with normal slashes `/` or remove them. Re-run `compile_and_package.py`.
