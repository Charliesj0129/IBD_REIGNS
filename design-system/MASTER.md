# IBD REIGNS - Design System Master

> 根據 `.agent/skills/ui-design.skill.md` 定義的 Single Source of Truth。

## 全域 Token

以下變數皆宣佈於 `:root`，所有元件與頁面應直接參照此變數，**禁止**在 CSS 內硬編碼 Hex 色碼。

### 色彩 (Colors)

| 用途      | CSS 變數          | 預設值 (深色主題) | 說明                 |
| --------- | ----------------- | ----------------- | -------------------- |
| 主色      | `--color-primary` | `#E8D5B7`         | 主要視覺字體色       |
| 強調色    | `--color-accent`  | `#D4A574`         | 主要按鈕、標題點綴   |
| 背景色    | `--color-bg`      | `#1A1A2E`         | 應用背景色           |
| 卡片背景  | `--color-card-bg` | `#16213E`         | 遊戲卡片、選單背景   |
| 次要文字  | `--color-muted`   | `#8A7A6A`         | 輔助提示文字         |
| 成功方向  | `--color-success` | `#81C784`         | 綠色，同意或心理數值 |
| 錯誤/惡化 | `--color-danger`  | `#E57373`         | 紅色，拒絕或生命數值 |
| 警告      | `--color-warning` | `#FFB74D`         | 橘黃色，財富數值     |
| 資訊      | `--color-info`    | `#64B5F6`         | 藍色，免疫數值       |

### 圓角與陰影

| 名稱   | CSS 變數      | 值                            |
| ------ | ------------- | ----------------------------- |
| 大圓角 | `--radius-lg` | `20px` (用於卡片)             |
| 中圓角 | `--radius-md` | `12px` (用於按鈕、框線)       |
| 中陰影 | `--shadow-md` | `0 10px 30px rgba(0,0,0,0.4)` |

### 無障礙規範 (Accessibility)

- 動態支援：必須引入 `@media (prefers-reduced-motion: reduce)` 來移除暈眩感動畫。
- 此系統實作於 `ibd_reigns/ui_styles.py` 與前端相關 HTML/CSS 區塊。
