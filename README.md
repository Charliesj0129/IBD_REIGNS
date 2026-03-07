# 腸道王權 (IBD REIGNS) 👑

**腸道王權** 是一款結合了《REIGNS》左右滑動卡片機制與嚴肅 IBD（炎症性腸道疾病）醫療衛教的生存模擬遊戲。
玩家將扮演一名剛確診 IBD 的患者，在日常生活的健康、免疫、心理與經濟資本之間取得平衡。

---

## ✨ 遊戲特色

- 🃏 **REIGNS 風格滑卡**：原生物理引擎驅動的左右滑動互動，搭配動畫教學引導新手上手
- 🏥 **硬核醫療模擬**：發炎週期、藥物依從性、營養不良連鎖、術後狀態池等真實 IBD 機制
- 📖 **沉浸式衛教**：83+ 張繁體中文卡牌內含 IBD 知識點、嚴重等級標籤與里程碑教學系統
- 🎨 **中世紀暗黑主題**：深色 Glassmorphism 季節光暈 + 12 種 REIGNS 風格角色 SVG 剪影
- 🔒 **差分隱私 Analytics**：Epsilon Budget 追蹤、行為漏斗、單卡決策比例與存活率分析
- ♿ **熟齡友善設計**：放大按鈕、移除負面詞彙、Fallback 按鈕操作、`prefers-reduced-motion` 支援

---

## 🚀 本機營運與區域連線遊玩指引 (Local Hosted Deployment)

專案目前預設為**本地營運環境 (Local Hosted Deployment)** 架構。您可以將此程式庫放在一台筆記型電腦或地端伺服器上運行，並讓同一區域網路 (Wifi / LAN) 內的其他人拿著手機或平板連線遊玩，非常適合醫療展會、病友會或診間的衛教展示。

### 步驟 1: 依賴準備

請確保主機已經安裝：

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv) (極速 Python 依賴管理工具)

### 步驟 2: 執行伺服器啟動腳本

在專案根目錄中，直接執行我們為您準備好的本機營運啟動腳本。此腳本會自動安裝所有缺失的 dependencies，並強迫伺服器綁定至所有網卡 (`0.0.0.0`)：

```bash
./start_local_server.sh
```

### 步驟 3: 同區網設備連線

一旦腳本啟動，終端機畫面會主動印出您的區域網路 IP，例如：

> `📱 【手機/平板遊玩】 請在設備瀏覽器開啟: http://192.168.1.105:8503`

此時，只要確保您的手機/平板與這台筆電連在**同一個 Wifi 網路**下，就能夠直接經由手機瀏覽器存取這個 IP 進入遊戲！

#### ⚠️ 疑難排解 (Troubleshooting: 連不上伺服器？)

如果您在手機上輸入網址後卻呈現「無法連線」，100% 是被**主機的作業系統防火牆**給擋住了。
請針對您的情境開放 `8503 (TCP)`：

- **Linux (Ubuntu)**:
  ```bash
  sudo ufw allow 8503/tcp
  sudo ufw reload
  ```
- **macOS**:
  請至「系統設定 > 網路 > 防火牆」中，確保沒有阻擋傳入連線，您可以暫時關閉來做測試。
- **Windows**:
  請至「控制台 > Windows Defender 防火牆 > 進階設定」，並在「輸入規則 (Inbound Rules)」中，新增一個允許通訊埠 (Port) 為 `8503 TCP` 的規則。

---

## 🌍 全球網際網路公開體驗 (Public Internet Access)

如果您想讓不在同一個 WiFi 內的親友或任何人「像上網一樣，點個網址就能玩」，我們也為您準備了打通公網的快捷腳本。它利用安全的 Localtunnel 技術，能在一鍵之間給您一個臨時的 `https://...` 網域：

```bash
./start_public_tunnel.sh
```

執行後，稍等數秒鐘，畫面中會出現一組亂碼般的網址（例如：`https://xxxxx.loca.lt`）。
只要這個腳本在跑，任何人點開這組網址都能直接連進您電腦上的遊戲，**您完全不需去處理路由器設定與防火牆！**

> 💡 **提示**: Tunnel 腳本已相容 Docker 叢集模式 (Port 80) 與單機模式 (Port 8503)，會自動偵測正在運行的環境。

---

## 🛳️ Docker 架構 (進階部署)

### 單機模式

如果您有安裝 Docker，不喜歡污染本機環境，也可以透過 Docker 直接建構並背景執行：

```bash
docker build -t ibd-reigns .
docker run -d -p 8501:8501 ibd-reigns
```

### 叢集模式 (水平擴展 + 負載均衡)

專案內建 Nginx + 3 副本 Streamlit 的水平擴展架構（`ip_hash` session affinity），適合展會或多人同時遊玩場景。一鍵啟動：

```bash
./start_docker_cluster.sh
```

此腳本會透過 `docker-compose up -d --build` 啟動 Nginx 反向代理 + 3 個 Streamlit 容器，統一在 `Port 80` 提供服務。

停止叢集：

```bash
docker compose down
```

---

## 📁 專案結構

```text
IBD_REIGNS/
├── app.py                     # Streamlit 主應用程式 (UI + Game Loop)
├── ibd_reigns/                # 核心遊戲邏輯模組
│   ├── engine.py              # 回合引擎、醫療模擬、衛教機制
│   ├── deck.py                # 牌組抽牌與權重系統
│   ├── models.py              # 資料模型 (Card, GameState, Ending)
│   ├── schema.py              # JSON 資料載入 (卡牌、結局、規則)
│   ├── constants.py           # 全域常數與遊戲參數
│   ├── cta.py                 # 遊戲結束 Call-to-Action 資源連結
│   ├── analytics.py           # 分析事件追蹤 (JSONL Sink)
│   ├── analytics_summary.py   # 差分隱私統計摘要
│   ├── event_analytics.py     # 行為漏斗、單卡決策、存活率分析
│   ├── sql_engine.py          # SQLite 持久化引擎
│   ├── hints.py               # Micro-Tips 提示系統
│   ├── ui_styles.py           # 全域 CSS 主題 (深色中世紀風格)
│   └── ui/                    # 自定義 Streamlit 元件
│       ├── __init__.py        # StreamlitRenderer
│       ├── swipe.py           # Swipe 卡片元件橋接層
│       └── swipe_component_v2/ # 原生 HTML/CSS/JS 物理引擎
├── assets/                    # 遊戲資源
│   ├── events.json            # 主事件卡牌資料 (83+ 張)
│   ├── scenarios_expansion.json # 擴展劇本 (職場、旅行、家庭計畫)
│   ├── endings.json           # 結局定義
│   ├── game_rules.json        # 動態權重與規則設定
│   ├── characters/            # 12 組 REIGNS 風格 SVG 角色剪影
│   ├── icons/                 # 四大屬性 SVG 圖示
│   └── fonts/                 # 字型資源
├── design-system/MASTER.md    # 設計系統 Token 定義 (SSOT)
├── scripts/                   # 工具腳本
│   ├── generate_svg_assets.py # 角色 SVG 自動產生器
│   ├── translate_cards.py     # 卡牌翻譯腳本
│   └── load_test.py           # Locust 壓力測試腳本
├── tests/                     # Pytest 測試套件 (32 個測試檔案)
├── specs/                     # BDD Feature 規格 (Gherkin)
├── Dockerfile                 # 容器映像定義
├── docker-compose.yml         # Nginx + 3 副本叢集定義
├── nginx.conf                 # Nginx 反向代理與 WebSocket 設定
├── start_local_server.sh      # 本機啟動腳本
├── start_public_tunnel.sh     # 公網 Tunnel 腳本
├── start_docker_cluster.sh    # Docker 叢集一鍵啟動腳本
└── pyproject.toml             # 專案 metadata 與依賴
```

---

## 📄 授權

© 台灣炎症性腸道疾病病友協會 — 僅供衛教與學術用途。
