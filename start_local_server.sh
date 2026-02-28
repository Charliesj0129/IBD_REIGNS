#!/bin/bash
# IBD REIGNS Local Hosted Deployment Script
# 此腳本將確認本地環境，並將應用程式綁定到 0.0.0.0 讓相同區域網路內的設備 (如手機、平板) 可以連線遊玩。

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}   腸道王權 (IBD REIGNS) 伺服器啟動腳本  ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# 1. Check for Python & uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}[錯誤] 找不到 uv 指令。請確保您已安裝 uv (Python package manager)。${NC}"
    echo "安裝指令: pip install uv"
    exit 1
fi

echo -e "${YELLOW}[系統檢查] 正在檢查依賴套件...${NC}"
uv sync --no-dev
echo -e "${GREEN}[系統檢查] 依賴套件已就緒。${NC}"
echo ""

# 2. Get local IP address (works for Linux/macOS)
if command -v ip &> /dev/null; then
    LOCAL_IP=$(ip route get 1.1.1.1 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
elif command -v ifconfig &> /dev/null; then
    LOCAL_IP=$(ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}' | head -n 1)
else
    LOCAL_IP="您的區域網路 IP"
fi

echo -e "${YELLOW}[網路設定] 準備啟動伺服器...${NC}"
echo -e "伺服器將綁定於所有網卡 (0.0.0.0)。同一個 WiFi (區網) 內的設備皆可連線。"
echo ""
echo -e "${BLUE}👉 【本機遊玩】 請在瀏覽器開啟: ${NC}http://localhost:8501"
if [ "$LOCAL_IP" != "您的區域網路 IP" ] && [ -n "$LOCAL_IP" ]; then
    echo -e "${GREEN}📱 【手機/平板遊玩】 請在設備瀏覽器開啟: ${NC}http://$LOCAL_IP:8501"
else
    echo -e "${GREEN}📱 【手機/平板遊玩】 請確認本機 IP，然後在設備瀏覽器開啟: http://<你的IP>:8501${NC}"
fi
echo ""
echo -e "${YELLOW}📝 備註：若同網段的其他設備無法連線，請確認本機防火牆是否已開放 8501 Port (TCP)。${NC}"
echo "    - Ubuntu/Linux 防火牆開放: sudo ufw allow 8501/tcp"
echo "    - Windows: 請至控制台 > Windows Defender 防火牆 > 進階設定 中新增「輸入規則」"
echo ""
echo -e "${BLUE}按 Ctrl+C 可以隨時關閉伺服器。${NC}"
echo "--------------------------------------------------------"

# 3. Launch Streamlit binding to 0.0.0.0
# --server.headless=true is optional, but common for hosted deployments
uv run streamlit run app.py --server.port=8501 --server.address=0.0.0.0
