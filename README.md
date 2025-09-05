# Agent Mcp Browser

Natural language driven internet recognition and manipulation project

## Features

- **Environment**: Docker

- **Key Technology**: Browser + Playwright Mcp + local deployment n8n

## Quick Start

### Download project

```
git clone 
```

### Install image

```
-- 使用docker hub sse(无法使用)
docker mcp gateway run --port 8080 --host 0.0.0.0  --transport sse

-- 无头模式
npx playwright test --ui

-- 有头模式
npx playwright test --headed

-- 启动mcp服务
fastmcp run --transport sse --host 0.0.0.0 --port 8000 mcp-server.py

-- 启动服务检查
<!-- typescript -->
npx playwright codegen --browser chromium --channel chrome --user-data-dir /Users/mfeng/Documents/world/feng_ai/mcp-server/agent-mcp-browser/codegen-profile
<!-- python -->
uv run playwright codegen --user-data-dir /root/my-browser-profile
uv run playwright codegen --browser chromium --channel chrome


-- 打包
docker build -t registry.cn-hangzhou.aliyuncs.com/rjxai/mcp-browser:0.0.5 .
docker push registry.cn-hangzhou.aliyuncs.com/rjxai/mcp-browser:0.0.5

-- 本地构建
docker compose -p support -f docker-compose.dev.yml up -d

-- 远程构建
docker login --username=heiyexinghai registry.cn-hangzhou.aliyuncs.com
<!-- password: fengX_429 -->

docker-compose -p support -f works/support/docker-compose.dev.yml pull
docker-compose -p support -f works/support/docker-compose.dev.yml up -d
```

### 将现有的n8n镜像发送到阿里云中
'''
docker tag n8nio/n8n:latest registry.cn-hangzhou.aliyuncs.com/rjxai/n8n:latest

docker push registry.cn-hangzhou.aliyuncs.com/rjxai/n8n:latest
'''

### 使用Playwright测试UI连接远程浏览器

#### 方法一：一键启动（推荐）

1. 在VS Code中一键启动Chrome和Playwright测试：
   - 打开VS Code的运行和调试面板（快捷键：Cmd+Shift+D）
   - 选择"一键启动 Chrome+Playwright"配置
   - 点击"开始调试"按钮

2. 或者使用任务运行（快捷键：Cmd+Shift+P，然后输入"Tasks: Run Task"）：
   - 选择"一键启动Chrome+Playwright"任务

#### 方法二：分步启动

1. 启动Chrome浏览器的调试模式：

```bash
# 启动Chrome的调试模式并自动配置Playwright
./script/start-chrome-playwright.sh
```

2. 在VS Code中启动Playwright测试：
   - 打开VS Code的运行和调试面板（快捷键：Cmd+Shift+D）
   - 选择"Playwright Tests (连接远程浏览器)"配置
   - 点击"开始调试"按钮

#### 远程调试说明
- 通过CDP协议（Chrome DevTools Protocol）连接到浏览器
- 可以查看测试执行过程并进行调试
- 支持UI模式下的实时交互
- 测试执行在已打开的Chrome实例中进行，可以保留登录状态和Cookies
