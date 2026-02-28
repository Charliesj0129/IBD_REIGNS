#!/bin/bash
# IBD REIGNS - Docker 叢集一鍵啟動腳本 (水平擴展 3 副本 + Nginx)

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${GREEN}   腸道王權 (IBD REIGNS) - 水平擴展叢集啟動腳本   ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# 1. 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[錯誤] 找不到 Docker！請先安裝 Docker。${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}[錯誤] Docker daemon 未啟動或權限不足！請確認 Docker 正在運行（可能需要 sudo）。${NC}"
    exit 1
fi

COMPOSE_CMD=""
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}[錯誤] 找不到 docker-compose 或 docker compose！${NC}"
    exit 1
fi

# 2. 啟動叢集
echo -e "${YELLOW}[1/3] 正在背景啟動 IBD REIGNS Docker 叢集 (Nginx + 3x App)...${NC}"
$COMPOSE_CMD up -d --build

# 3. 取得本機 IP
LOCAL_IP=$(ip -4 route get 8.8.8.8 2>/dev/null | awk '{print $7}' | tr -d '\n' || echo "localhost")
if [ -z "$LOCAL_IP" ] || [ "$LOCAL_IP" == "localhost" ]; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
fi

echo -e "${GREEN}[2/3] 叢集啟動完成！容器狀態：${NC}"
$COMPOSE_CMD ps

# 4. 輸出連線資訊
echo ""
echo -e "${BLUE}=================================================${NC}"
echo -e "伺服器已將所有流量綁定至 Nginx (Port 80) 並自動負責負載均衡。"
echo ""
echo -e "👉 【本機遊玩】 請在瀏覽器開啟: http://localhost"
echo -e "📱 【手機/平板遊玩】 請在設備瀏覽器開啟: http://${LOCAL_IP}"
echo ""
echo -e "📝 若要對外網際網路開放，請執行: ${YELLOW}./start_public_tunnel.sh${NC}"
echo -e "   (若已運行中的隧道需要重啟開在 Port 80，請將隧道腳本中的 APP_PORT 改為 80)"
echo -e "${BLUE}=================================================${NC}"
echo ""
