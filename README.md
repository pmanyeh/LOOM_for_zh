# LOOM 繁體中文化與 AI 語音模組專案 (LOOM for zh-TW)

![LOOM Localization Project](https://img.shields.io/badge/Game-LOOM-blue.svg)
![Platform](https://img.shields.io/badge/Platform-ScummVM%20%7C%20Steam%20%7C%20FM--TOWNS-lightgrey.svg)
![Language](https://img.shields.io/badge/Language-%E7%B9%81%E9%AB%94%E4%B8%AD%E6%96%87-success.svg)

## 📖 專案簡介

本專案旨在為 LucasArts 經典冒險遊戲《紗之器》(LOOM) 打造最完善的繁體中文化體驗，同時針對缺乏全語音的版本導入創新的 **AI 語音模組**。

目前專案涵蓋了 **Steam 語音版 (Talkie)** 與 **FM-TOWNS 版** 雙版本的在地化工程，從文本翻譯、字型渲染優化，一路到透過 RVC (Retrieval-based Voice Conversion) 技術重新合成角色語音，並對 ScummVM 引擎進行底層修改以支援外掛語音，提供從開發、封裝到執行的自動化工作流。

> **⚠️ 注意事項**：本 Git 儲存庫僅包含中文化程式碼、翻譯文本、修改腳本與自訂字型檔，**嚴禁且不包含任何遊戲本體資產 (如大型音訊檔或版權檔案)**。玩家需自行合法取得遊戲本體。

---

## ✨ 核心特色

- 🌐 **雙版本全面中文化**
  同時支援 Steam 語音版與具備高畫質的 FM-TOWNS 版本，並修正原版翻譯語句，統一「織杖」等專有名詞。
  
- 🔤 **像素級字型渲染優化**
  整合 10px **Fusion Pixel (縫合像素字體)**，透過自訂的 Python 腳本動態生成字庫 (`FMT_FNT.ROM` / `.fnt`)，修正中文在 12x12 SCUMM 引擎中的行距與垂直對齊問題，達成完美閱讀體驗。

- 🎙️ **AI 語音合成與掛載 (FM-TOWNS 版)**
  為 FM-TOWNS 版訓練了專屬的 Bobbin RVC 語音模型。利用 Edge TTS 進行初始語音生成，再透過 RVC 自動化批次轉換，讓原本無語音的對白擁有生動的配音。
  
- ⚙️ **特製 ScummVM 引擎 (Hook Patch)**
  專案內附對 ScummVM 原始碼的修改補丁 (`patches/scummvm_loom_voice.patch`)，實作了 `playChtVoice` 邏輯，使引擎能夠攔截文字並完美對應、播放外部的 AI 中文配音檔案。

- 🤖 **自動化工作流 (Pipeline)**
  內建一系列 Python 腳本與 ScummTR 工具的整合。一鍵實現「文本提取 ➡️ 自動翻譯 ➡️ 封裝注入 ➡️ 生成整合包」的自動化流程。

---

## 📂 專案目錄結構

```text
LOOM/
├── .gitignore               # 排除大型音訊檔、遊戲本體與暫存檔案
├── FM-TOWNS_Patch/          # FM-TOWNS 版的中文化修正檔與自訂字庫 (FMT_FNT.ROM)
├── patches/                 # ScummVM 引擎修改補丁
├── tools/                   # 包含 ScummTR 等 SCUMM 引擎專用修改工具
└── translation/             # 核心開發與自動化腳本資料夾
    ├── fm_towers_flow/      # FM-TOWNS 版本專屬的自動化處理流程 (TTS、RVC、封裝)
    ├── loom_strings.csv     # Steam 版文本主檔
    ├── generate_fnt.py      # 字型轉換與間距調整工具
    ├── Fusion_Pixel_10px.ttf# 使用的基礎開源像素字型
    └── ...
```

---

## 🛠️ 開發與編譯指南

如果您想參與開發或自行編譯整合包，請參考以下工具鏈：

### 1. 文本解包與封裝
專案使用 `ScummTR` 進行 `.LFL` 等遊戲檔案的解包與字串注入。相關指令已整合在 `translation/fm_towers_flow/` 中的 Python 腳本內。

### 2. AI 語音生成流程
1. 使用 `generate_edge_tts.py` 產生初始的配音音檔。
2. 使用 `prepare_rvc.py` 與 `apply_rvc.py` 將 TTS 語音過濾並轉換為自訂 RVC 模型的音色。
3. 產生對應的 `voice_map.json` 以供修改版的 ScummVM 讀取。

### 3. 編譯特製 ScummVM
如需支援 FM-TOWNS 的語音模組，必須套用 `patches/scummvm_loom_voice.patch` 並重新編譯 ScummVM 引擎，編譯出來的執行檔方可支援外部中文語音播放。

---

## 📜 授權聲明與致謝

- **中文化腳本與修改**：本專案開發之程式碼採開源釋出。
- **字型**：使用 [Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font) (SIL Open Font License)。
- **工具**：感謝 ScummVM 團隊與 ScummTR 工具作者。
- **遊戲版權**：LOOM 及相關角色版權均屬 LucasArts (現歸 Disney/Lucasfilm Games 所有)，本專案為粉絲自製之非官方修改。
