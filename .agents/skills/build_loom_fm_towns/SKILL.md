---
name: build_loom_fm_towns
description: "Build LOOM FM-TOWNS localization packages (Portable, Windows Patch, Mac Patch)."
---

# Instructions

When the user asks you to rebuild or compile the FM-TOWNS localization packages for LOOM, follow this workflow:

1. **Verify Translation Files**: 
   Ensure `translation/fm_towers_flow/loomtowns_strings.csv` contains the latest translation text.

2. **Run the Build Script**: 
   Execute the `compile_and_package.py` script from its directory.
   ```powershell
   cd translation\fm_towers_flow
   python compile_and_package.py
   cd ..\..
   ```
   This script will automatically:
   - Generate `FMT_FNT.ROM` (Chinese Font ROM).
   - Compile `loomtowns_strings.csv` into `loomtowns_zh_injected.txt` using the Shift-JIS charmap.
   - Generate `voice_map.json` to synchronize audio timings.
   - Copy these three artifacts into the pre-existing target directories: `FM-TOWNS_Patch`, `FM-TOWNS_Mac_Patch`, and `LOOM_FM-TOWNS_ZH_Portable/game`.
   - Normalize line endings for `play.bat` and `安裝中文化.bat` to `CRLF` + `UTF-8 BOM`.

3. **Zip the Packages**:
   After the script runs successfully, package the output directories into zip files using PowerShell compression:
   ```powershell
   Remove-Item "FM-TOWNS_Patch.zip", "FM-TOWNS_Mac_Patch.zip", "LOOM_FM-TOWNS_ZH_Portable_Final.zip" -Force -ErrorAction SilentlyContinue
   Add-Type -AssemblyName System.IO.Compression.FileSystem

   [System.IO.Compression.ZipFile]::CreateFromDirectory("$PWD\FM-TOWNS_Patch", "$PWD\FM-TOWNS_Patch.zip")
   [System.IO.Compression.ZipFile]::CreateFromDirectory("$PWD\FM-TOWNS_Mac_Patch", "$PWD\FM-TOWNS_Mac_Patch.zip")
   [System.IO.Compression.ZipFile]::CreateFromDirectory("$PWD\LOOM_FM-TOWNS_ZH_Portable", "$PWD\LOOM_FM-TOWNS_ZH_Portable_Final.zip")
   ```

4. **Report**:
   Inform the user that the FM-TOWNS translation has been fully compiled and packaged for all three distribution formats.
