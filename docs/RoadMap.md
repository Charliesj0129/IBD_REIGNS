# IBD REIGNS 開發地圖 (RoadMap)

## 🛠 技術棧 (Tech Stack)

### 後端與核心邏輯

- **語言**: Python (>=3.10)
- **架構平台**: [Streamlit](https://streamlit.io/) (>=1.32.0)
- **資料庫 (DB)**: SQLite 搭配自行封裝的 `sql_engine.py` (包含 Differential Privacy 差分隱私資料處理技術)
- **依賴管理與虛擬環境**: `uv` (新一代極速 Python 依賴管理工具)

### 前端與 UI 元件

- **核心框架**: Streamlit 內建 UI 元件
- **Swipe 卡片互動模組**: 自定義的 Streamlit Custom Component (使用原生 HTML/CSS/JavaScript 開發)，實作真正的平滑拖曳物理引擎 (Physics Engine)。
- **樣式 (Styling)**: 原生 CSS (`ibd_reigns/ui_styles.py`)，搭配 Noto Serif TC 與 Inter 字體，深色中世紀暗黑主題搭配 Glassmorphism 季節光暈效果。

### 測試與交付

- **測試框架**: `pytest` (>=7.4.0) 與 `pytest-cov` (測試覆蓋率 ≥ 90%)
- **容器化部署**: Docker (`Dockerfile`, `docker-compose.yml`)

---

## 🚩 開發里程碑 (Milestones)

### Phase 1: MVP 與基礎架構建立 (已完成)

- [x] 配置 `pyproject.toml` 與 Streamlit 基礎運行環境。
- [x] 建立 SQLite 數據庫與基本遊戲循環架構 (Game Loop)。
- [x] 建立牌組與事件庫 (`assets/`)，實作四大屬性的加減運算與邊界判定。
- [x] 達成基本的 Pytest 測試自動化環境。

### Phase 2: 沉浸感優化與教育深化 (已完成)

- [x] **REIGNS 體驗強化**: 導入卡片登場動畫、死亡特效與季節切換視覺。
- [x] **IBD 教育深度**: 加入小知識 (Micro-Tips)、嚴重等級標籤與成就系統。
- [x] **隱私與儀表板 (Analytics)**: 實作差分隱私架構，加入隱私預算 Tracker 以及長期趨勢分析報表。

### Phase 3: 劇本擴展、進階醫療機制與部署 (已完成)

- [x] 整合新劇本模組 (Workplace, Travel, Family Planning)。
- [x] 重構並增強醫療機制：添加藥物依從性追蹤、營養不良連鎖反應及術後狀態池。
- [x] 新版的 UI Swipe 組件：根除預測提示光暈，恢復完美的無提示極簡設計與紙牌物理手把手感。
- [x] 完成容器化設定 (`Dockerfile`, `docker-compose.yml`)，支援快速部署。

### Phase 4: 深度在地化與全面精緻化 (已完成)

- [x] **純繁體中文底層優化**: 移除多國語言的切換架構，全線系統文本與介面深度寫死並優化為純繁體中文。
- [x] **高階音效與沉浸感 (Voice & SFX)**: Web Audio API 合成實體紙牌摩擦、蓋章音與點擊回饋。
- [x] **細緻化玩家關卡決策分析 (Fine-grained Event Analytics)**: 每張卡牌的選擇比例、存活率差異與行為漏斗。
- [x] **本機營運環境部署 (Local Hosted Deployment)**: 啟動腳本、防火牆配置教學、Cloudflare Tunnel 公網方案。
- [x] **UI 全面升級**: 深色中世紀主題、Glassmorphism 季節光暈、透明卡牌背景、Streamlit 原生元件覆蓋。
- [x] **卡牌內容全面中文化**: 83 張卡牌的劇情、角色、選項與衛教資訊全部翻譯為繁體中文。

### Phase 5: 前後端狀態一致性 (規劃中)

- [ ] 每個前端 action 帶 `turn_id` / `card_id` 防止狀態不同步
- [ ] 後端驗證不符就拒絕並回傳最新 state
- [ ] 前端只渲染後端 state，不自行推進回合
- [ ] 為關鍵流程寫 E2E 測試（進入遊戲 → 做選擇 → 週數 +1 → 結局出現）
- [ ] 防止連點/重送導致回合被多次結算
