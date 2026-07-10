# LOOM for zh-TW — 專案規則

## 批次腳本 (.bat) 格式規範

- **所有 `.bat` 檔案必須使用 Windows CRLF (`\r\n`) 換行格式**，不可使用 Unix LF (`\n`)。
- 若使用 Python 或其他工具生成或寫入 `.bat` 檔案，必須明確指定 `newline='\r\n'` 或在寫入後進行轉換，否則 Windows 命令提示字元執行時會發生錯誤。
- 建議同時使用 UTF-8 BOM (`utf-8-sig`) 編碼，以確保中文字元在命令提示字元中正確顯示。

範例（Python 寫入方式）：
```python
with open("script.bat", "w", encoding="utf-8-sig", newline="\r\n") as f:
    f.write(content)
```
