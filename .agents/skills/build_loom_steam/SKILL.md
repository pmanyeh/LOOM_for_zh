---
name: build_loom_steam
description: "Build LOOM Steam (Talkie/CD) localization packages (Portable, Windows Patch, Mac Patch)."
---

# Instructions

When the user asks you to rebuild or compile the Steam (Talkie/CD) localization packages for LOOM, follow this workflow:

1. **Verify Translation Files**: 
   Ensure `translation/steam_flow/loom_strings.csv` contains the latest translation text.

2. **Run the Build Script**: 
   Execute the `compile_and_package_steam.py` script.
   ```powershell
   cd translation\steam_flow
   python compile_and_package_steam.py
   cd ..\..
   ```
   This script will automatically:
   - Generate the pixel font `chinese_gb16x12.fnt` using `Fusion_Pixel_10px.ttf` with standard offset parameters to perfect the baseline.
   - Compile `loom_strings.csv` into `loom_strings_translated.txt` via `helper.py`. This step translates strings into custom GB2312 mapped bytes, handles equal-padding for multi-line strings, and guarantees exact byte-length preservation for SCUMM v4 pointer injection logic.
   - Extract and build the target directories (`Steam_Patch`, `Steam_Mac_Patch`, and `LOOM_Steam_ZH_Portable`) including copying the necessary 000.LFL file directly.
   - Build `play.bat` and `使用說明.txt` (Readmes) which prominently document the requirement to change ScummVM language settings to `cn` or `Chinese (Simplified)`.

3. **Zip the Packages**:
   After the script runs successfully, package the output directories into zip files using PowerShell compression:
   ```powershell
   Remove-Item "Steam_Patch.zip", "Steam_Mac_Patch.zip", "LOOM_Steam_ZH_Portable_Final.zip" -Force -ErrorAction SilentlyContinue
   Add-Type -AssemblyName System.IO.Compression.FileSystem

   [System.IO.Compression.ZipFile]::CreateFromDirectory("$PWD\Steam_Patch", "$PWD\Steam_Patch.zip")
   [System.IO.Compression.ZipFile]::CreateFromDirectory("$PWD\Steam_Mac_Patch", "$PWD\Steam_Mac_Patch.zip")
   [System.IO.Compression.ZipFile]::CreateFromDirectory("$PWD\LOOM_Steam_ZH_Portable", "$PWD\LOOM_Steam_ZH_Portable_Final.zip")
   ```

4. **Report**:
   Inform the user that the Steam CD translation has been fully compiled and packaged into the three ZIP archives.
