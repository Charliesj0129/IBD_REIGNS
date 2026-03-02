#!/bin/bash
# IBD REIGNS - 公開網際網路隧道腳本 (Public Internet Tunnel)
# 此腳本將在背景啟動 Streamlit，並利用 Cloudflare Tunnel 建立免費、安全的公開 HTTPS 網址，
# 讓全球任何人都可以透過該網址直接連線遊玩。

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}   腸道王權 (IBD REIGNS) - 全球公開網址生成器    ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# 1. 檢查並啟動背後的 Streamlit
APP_PORT=8503
if lsof -t -i:$APP_PORT > /dev/null; then
    echo -e "${YELLOW}發現舊的伺服器正在 Port $APP_PORT 運行，正在自動關閉以載入最新程式碼...${NC}"
    kill -9 $(lsof -t -i:$APP_PORT) > /dev/null 2>&1 || true
    sleep 2
fi

echo -e "${YELLOW}[1/3] 正在背景啟動 IBD REIGNS 遊戲伺服器...${NC}"
uv run streamlit run app.py --server.port=$APP_PORT --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false > /dev/null 2>&1 &
STREAMLIT_PID=$!
sleep 3

# 設定 Trap，當腳本退出時(例如 Ctrl+C)，順便自動關閉背景的 Streamlit
trap "kill -9 $STREAMLIT_PID > /dev/null 2>&1 || true" EXIT

# 2. 啟動對外 Tunnel
# 2026-02-22 實測：Cloudflare Quick Tunnel 可正常互動；某些環境下 localtunnel 會讓 Streamlit 互動元件卡成 skeleton。
if command -v cloudflared &> /dev/null; then
    echo -e "${YELLOW}[2/2] 正在透過 Cloudflare Quick Tunnel 生成公開 HTTPS 網址...${NC}"
    cloudflared tunnel --url http://127.0.0.1:$APP_PORT
elif command -v lt &> /dev/null; then
    echo -e "${YELLOW}[2/2] 正在透過 Localtunnel 生成公開網域...${NC}"
    echo -e "${YELLOW}⚠️ 注意：部分環境下 localtunnel 可能導致 Streamlit 按鈕/互動元件顯示為空白骨架。若發生，請改裝 cloudflared。${NC}"
    lt --port $APP_PORT
else
    echo -e "${RED}[錯誤] 找不到 cloudflared 與 localtunnel (lt)！${NC}"
    echo "建議安裝 Cloudflare Tunnel（優先）："
    echo -e "${BLUE}https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/${NC}"
    echo ""
    echo "或安裝 Localtunnel（備援）："
    echo -e "${BLUE}npm install -g localtunnel${NC}"
    exit 1
fi
