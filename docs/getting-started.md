# 快速开始

## 安装

```bash
pip install ashare-agent
```

## 配置

### 方式一：环境变量（推荐）

```bash
# PG 数据库连接（默认使用本地 socket，无需密码）
export ASHARE_AGENT_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public"

# 服务器配置（可选）
export ASHARE_AGENT_HOST="localhost"
export ASHARE_AGENT_PORT=8900
```

### 方式二：配置文件

创建 `~/.ashare-agent/config.yaml`：

```yaml
pg_uri: "postgresql://zrall@localhost/ashare?options=-c%20search_path=ashare,public"
host: "localhost"
port: 8900
log_level: "info"
```

## 启动 API 服务器

```bash
ashare-agent serve
```

访问 http://localhost:8900/docs 查看自动生成的 API 文档。

## 启动 MCP 服务器（用于 Claude Code / Cursor）

```bash
ashare-agent mcp
```

MCP 服务器运行在 `http://localhost:8901`。

## 测试

```bash
# 查询行情
curl http://localhost:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"宁德时代最近5个交易日行情"}]}'

# 通过 CLI 查询
ashare-agent query "宁德时代最近5个交易日行情"
```
