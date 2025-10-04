# 螢幕即時翻譯器 Screen Translator

一個強大的桌面應用程式，能夠即時擷取螢幕上的英文文字並自動翻譯成中文。非常適合觀看英文影片、閱讀英文文章或玩外語遊戲時使用。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## ✨ 主要功能

- 🖥️ **多螢幕支援** - 可選擇任何顯示器進行擷取
- 🎯 **區域選擇** - 拖曳選擇特定螢幕區域，提升識別準確度
- 🔄 **即時翻譯** - 使用 Google 翻譯 API 自動將英文翻譯成繁體中文
- 🎨 **圖形化介面** - 簡潔易用的 GUI，無需任何程式知識
- ⚡ **影像增強** - 自動優化擷取的影像，提高 OCR 準確度
- ⏱️ **可調整更新頻率** - 自訂擷取間隔時間（建議 2-5 秒）

## 📸 截圖

```
┌─────────────────────────────────────────┐
│  螢幕即時翻譯器                          │
├─────────────────────────────────────────┤
│  [選擇監視器 ▼]  [選擇擷取區域]         │
│  更新間隔: [2] 秒  ☑ 影像增強           │
│  [▶ 開始擷取]  [⏸ 停止]  [清空]        │
├─────────────────────────────────────────┤
│  擷取的英文                              │
│  ┌───────────────────────────────────┐  │
│  │ Hello World! This is a test.     │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  中文翻譯                                │
│  ┌───────────────────────────────────┐  │
│  │ 你好世界！這是一個測試。          │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🚀 快速開始

### 前置需求

1. **Python 3.7 或更高版本**
   - [下載 Python](https://www.python.org/downloads/)

2. **Tesseract OCR**
   - Windows: [下載安裝程式](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

### 安裝步驟

1. **下載程式碼**
```bash
git clone https://github.com/weilun-chiu/Windows-screen-capture-translator.git
cd Windows-screen-capture-translator
```

2. **安裝依賴套件**
```bash
pip install -r requirements.txt
```

3. **設定 Tesseract 路徑**（僅限 Windows）

如果 Tesseract 沒有加入系統 PATH，請在 `screen_translator.py` 開頭加入：
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

4. **執行程式**
```bash
python screen_translator.py
```

## 📦 打包成執行檔

想要建立獨立的 .exe 檔案嗎？

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包成單一執行檔
pyinstaller --onefile --windowed --name "螢幕翻譯器" screen_translator.py

# 執行檔將會在 dist 資料夾中
```

**注意**：使用者仍需要另外安裝 Tesseract OCR。

## 📖 使用說明

### 基本使用流程

1. **選擇監視器** - 從下拉選單選擇要監控的顯示器
2. **選擇區域** - 點擊「選擇擷取區域」，用滑鼠拖曳選擇要擷取的範圍
3. **開始擷取** - 點擊「▶ 開始擷取」按鈕
4. **查看翻譯** - 程式會自動顯示擷取的英文和中文翻譯

### 最佳效能建議

#### 📏 理想的擷取區域大小

| 用途 | 建議尺寸 |
|------|---------|
| 字幕/對話框 | 800 × 150 像素 |
| 文章段落 | 600 × 300 像素 |
| 單行文字 | 500 × 80 像素 |

- ✅ **最佳範圍**：寬 300-1920px，高 100-300px
- ⚠️ **最小值**：不小於 200×50 像素
- ⚠️ **最大值**：不超過 2000×1000 像素

#### 💡 提升準確度的技巧

- 選擇背景單純、對比明顯的區域
- 避免選擇有複雜圖案或漸層的背景
- 確保文字大小至少 12pt 以上
- 保持「影像增強」選項開啟
- 對於快速變化的內容，可將更新間隔調短

## 🛠️ 技術細節

### 使用的技術

- **OCR 引擎**: Tesseract 4.0+
- **翻譯 API**: Google Translate (via deep-translator)
- **螢幕擷取**: MSS (Multiple Screen Shot)
- **圖形介面**: Tkinter
- **影像處理**: Pillow (PIL)

### 專案結構

```
screen-translator/
├── screen_translator.py      # 主程式檔案
├── requirement.txt           # Python 依賴套件
└── README.md                 # 專案說明文件
```

### requirements.txt

```
pytesseract>=0.3.10
Pillow>=9.0.0
mss>=6.1.0
deep-translator>=1.11.0
```

## ⚙️ 進階設定

### 更改翻譯語言

在 `screen_translator.py` 中修改：

```python
self.translator = GoogleTranslator(source='en', target='zh-TW')
```

支援的語言代碼：
- `zh-TW`: 繁體中文
- `zh-CN`: 簡體中文
- `ja`: 日文
- `ko`: 韓文
- 更多語言請參考 [deep-translator 文件](https://github.com/nidhaloff/deep-translator)

### 調整 OCR 設定

可以修改 OCR 配置以適應不同的文字類型：

```python
# PSM 模式：
# 3 = 完全自動分頁（預設）
# 6 = 單一文字區塊
# 11 = 稀疏文字，無特定順序
custom_config = r'--oem 3 --psm 6'
```

## 🐛 常見問題

### Q: 程式無法啟動或顯示 Tesseract 錯誤？
**A**: 請確認 Tesseract OCR 已正確安裝，且路徑設定正確。

### Q: OCR 識別不準確？
**A**: 
- 選擇更小、更集中的擷取區域
- 確保文字清晰，背景單純
- 開啟「影像增強」選項
- 增加文字大小（如果可能）

### Q: 翻譯速度很慢？
**A**: 
- 增加更新間隔時間
- 選擇更小的擷取區域
- 檢查網路連線（翻譯需要網路）

### Q: 可以離線使用嗎？
**A**: OCR 功能可以離線使用，但翻譯功能需要網路連線。

## 📝 待辦事項

- [ ] 支援更多語言選項
- [ ] 加入歷史記錄功能
- [ ] 支援離線翻譯模型
- [ ] 加入快捷鍵支援
- [ ] 優化記憶體使用
- [ ] 加入自動儲存翻譯結果

## 🤝 貢獻

歡迎提交 Pull Request 或回報 Issue！

1. Fork 此專案
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - 強大的 OCR 引擎
- [deep-translator](https://github.com/nidhaloff/deep-translator) - 簡單易用的翻譯庫
- [python-mss](https://github.com/BoboTiG/python-mss) - 高效能螢幕擷取工具

---

⭐ 如果這個專案對您有幫助，請給個星星！

💬 有任何問題或建議？歡迎開 Issue 討論！
