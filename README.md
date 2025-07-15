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
docker build -t mcp-browser .

-- 使用docker hub sse
docker mcp gateway run --port 8080 --transport sse
```

### Start service

```
docker compose -p support -f docker-compose.dev.yml up -d

noVnx: http://localhost:6901/vnc.html?password=headless
noVnx: http://localhost:6902/vnc.html?password=headless
n8n MCP Client - SSE Endpoint: http://mcp-browser:8088/sse
```
