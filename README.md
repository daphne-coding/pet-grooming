# petgrooming

利用 `google-2025-12-28.csv` 與 `寵物美容detail.csv` 產生 GitHub Pages 的靜態網站。執行 `generate_pages.py` 會將每一家店的獨立分頁與索引頁輸出到 `docs/` 資料夾（適用 GitHub Pages 的 `/docs` 來源）。

## 重新產生頁面

```bash
python generate_pages.py
```

產出的內容包含：
- `docs/index.html`：所有店家的清單卡片，連結到各自的獨立頁面。
- `docs/<店家 slug>/index.html`：單一店家頁面，提供地圖、地址、電話、官網與特色標籤。
- `docs/assets/style.css`：共用樣式（自動建立）。

如需更新資料，只要替換 CSV 後再次執行腳本即可重新輸出網頁。
