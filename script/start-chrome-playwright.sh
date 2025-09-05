#!/bin/bash

# 设置脚本在遇到错误时立即退出
set -e

# ==============================================================================
#  优雅地关闭函数
# ==============================================================================
# 当脚本接收到退出信号时（例如 supervisorctl stop），会触发此函数
cleanup() {
    echo "接收到退出信号，正在关闭 Chrome 进程 (PID: $CHROME_PID)..."
    # 向 Chrome 进程发送 TERM 信号，如果存在的话
    if kill -0 "$CHROME_PID" 2>/dev/null; then
        kill -TERM "$CHROME_PID"
        wait "$CHROME_PID" # 等待 Chrome 真正关闭
    fi
    echo "Chrome 进程已关闭。"
    exit 0
}

# 捕获 TERM, INT, EXIT 信号，并调用 cleanup 函数
# 这确保了 `supervisorctl stop` 或 Ctrl+C 能够干净地关闭 Chrome
trap cleanup TERM INT EXIT

# ==============================================================================
#  主逻辑
# ==============================================================================
echo "========================================="
echo "启动Chrome调试模式并准备Playwright测试环境"
echo "========================================="

# 检查操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    # CHROME_USER_DATA_DIR="/tmp/chrome-debug-profile"
    CHROME_USER_DATA_DIR="/Users/mfeng/Documents/world/feng_ai/mcp-server/agent-mcp-browser/browser-profile"
    CONFIG_FILE="playwright.config.ts"
    
    if [ ! -f "$CHROME_PATH" ]; then
        echo "错误：未找到Chrome浏览器"
        exit 1
    fi
    
    CHROME_ARGS=(
        --remote-debugging-port=9222
        --user-data-dir="$CHROME_USER_DATA_DIR"
        --enable-logging
        --v=1
        --no-first-run
        --no-default-browser-check
    )
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CHROME_USER_DATA_DIR="/root/browser-profile"
    CHROME_PATH=$(which google-chrome || which google-chrome-stable || which chromium || which chromium-browser)
    CONFIG_FILE="playwright.config.ts"
    
    if [ -z "$CHROME_PATH" ]; then
        echo "错误：未找到Chrome或Chromium浏览器"
        exit 1
    fi
    
    CHROME_ARGS=(
        --remote-debugging-port=9222
        --user-data-dir="$CHROME_USER_DATA_DIR"
        --enable-logging
        --v=1
        --no-first-run
        --no-sandbox
        --disable-gpu
        --disable-dev-shm-usage
        --no-default-browser-check
    )
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "使用用户数据目录: $CHROME_USER_DATA_DIR"
mkdir -p "$CHROME_USER_DATA_DIR"

# 检查9222端口是否被占用
if lsof -i tcp:9222 -sTCP:LISTEN -t >/dev/null ; then
    echo "警告：端口 9222 已被占用"
    pid=$(lsof -i tcp:9222 -sTCP:LISTEN -t)
    echo "占用此端口的进程 PID: ${pid}"
    
    # 尝试确定这是否是Chrome进程
    if ps -p ${pid} | grep -q "Chrome"; then
        echo "这似乎是另一个Chrome实例。正在尝试关闭..."
        kill -TERM ${pid} 2>/dev/null || true
        sleep 2
        
        # 检查进程是否已关闭
        if lsof -i tcp:9222 -sTCP:LISTEN -t >/dev/null ; then
            echo "无法释放端口 9222，请手动关闭使用此端口的程序后重试"
            exit 1
        else
            echo "成功释放端口 9222"
        fi
    else
        echo "请关闭使用端口 9222 的应用后重试"
        exit 1
    fi
fi

# 在启动前尝试删除可能存在的锁定文件
echo "清理旧的锁定文件..."
rm -f "$CHROME_USER_DATA_DIR/SingletonLock" "$CHROME_USER_DATA_DIR/Lock"

# 启动Chrome调试模式，并在后台运行
echo "正在启动Chrome调试模式..."
"$CHROME_PATH" "${CHROME_ARGS[@]}" &

# <-- 核心改动 1: 立即获取后台 Chrome 进程的 PID
CHROME_PID=$!
echo "Chrome 进程已启动，PID: $CHROME_PID"

# 等待Chrome启动和调试端口打开
echo "等待Chrome启动和调试端口9222打开..."
for i in {1..15}; do
    # 在Linux上使用 `ss` 或 `netstat` 可能比 `lsof` 更快
    if lsof -n -P -i TCP:9222; then
        echo "✓ Chrome调试端口9222已开放"
        break
    else
        if [ $i -eq 15 ]; then
            echo "✗ Chrome调试端口未开放，请检查日志。"
            exit 1
        fi
        echo "等待Chrome启动... (${i}/15)"
        sleep 1
    fi
done

# 等待额外2秒，确保调试服务完全初始化
sleep 2

# 第2步：获取WebSocket端点并更新playwright.config.ts
echo ""
echo "正在获取Chrome调试WebSocket端点..."
CHROME_DEBUG_URL="http://localhost:9222/json/version"
MAX_RETRIES=5
for i in $(seq 1 $MAX_RETRIES); do
    # 使用 curl 的 --fail 选项，如果HTTP状态码不是2xx，则会失败
    WS_ENDPOINT=$(curl --fail -s $CHROME_DEBUG_URL | grep -o '"webSocketDebuggerUrl": "[^"]*"' | awk -F'"' '{print $4}')
    
    if [ -n "$WS_ENDPOINT" ]; then
        break
    fi
    
    if [ $i -eq $MAX_RETRIES ]; then
        echo "错误：经过多次尝试后仍无法获取WebSocket端点"
        exit 1
    fi
    
    echo "尝试获取WebSocket端点失败，重试中... (${i}/$MAX_RETRIES)"
    sleep 1
done

echo "检测到WebSocket端点: $WS_ENDPOINT"
BROWSER_ID=$(echo $WS_ENDPOINT | grep -o '/devtools/browser/[^/]*' | cut -d'/' -f4)

if [ -z "$BROWSER_ID" ]; then
    echo "错误：无法从WebSocket端点解析浏览器ID"
    exit 1
fi
echo "浏览器ID: $BROWSER_ID"

# 更新playwright.config.ts中的浏览器ID
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/\$(browserWSEndpoint)/$BROWSER_ID/g" $CONFIG_FILE
else
    sed -i "s/\$(browserWSEndpoint)/$BROWSER_ID/g" $CONFIG_FILE
fi

echo "已更新 $CONFIG_FILE 文件中的浏览器ID"
echo ""
echo "========================================="
echo "设置完成！环境已准备就绪。"
echo "此脚本将保持运行以监控 Chrome 进程。"
echo "按 Ctrl+C 或使用 'supervisorctl stop' 来关闭。"
echo "========================================="

# <-- 核心改动 2: 等待 Chrome 进程结束。脚本会阻塞在这里，直到 Chrome 关闭。
wait $CHROME_PID
