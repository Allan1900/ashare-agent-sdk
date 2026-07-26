# StockPulse 云端部署可行性报告

> 现状：StockPulse 运行在 WSL 本地，PostgreSQL（5.8GB/3400万行）在 localhost。
> 目标：将 API + 数据库部署到云上，为用户提供远程访问的托管服务。

---

## 一、架构方案

```
用户 → HTTPS → 云服务器 → StockPulse API (:8900)
                       → MCP Server (:8901)
                       → PostgreSQL (本地云磁盘)
                       → 每日数据更新 (cron)
```

## 二、云平台选型对比

| 平台 | 轻量服务器 (2C4G) | 云数据库 PG | 月总成本 | 国内访问 | 适合 |
|------|------------------|------------|---------|---------|------|
| **腾讯云 Lighthouse** | **99元/年** (2C2G) | 内置 | **~8元/月** | ✅ 最优 | 🇨🇳 **首选** |
| **阿里云 ECS** | 99元/年 (2C2G) | RDS PG 227元/年 | **~27元/月** | ✅ | 备选 |
| **Supabase** (海外) | 免费 (2C1G) | 免费 (500MB) | **$0** 起步 | ⚠️ 需代理 | 开发/测试 |
| **Railway** (海外) | 按量 $5起 | 内置 PG | **$5+/月** | ⚠️ 需代理 | 海外用户 |
| **华为云** | 89元/年 (2C2G) | 内置 | **~7元/月** | ✅ | 备选 |

### 推荐方案：腾讯云 Lighthouse

```
配置：2核2G / 4M带宽 / 50G SSD → 99元/年
部署：
  ① 安装 Docker + docker compose
  ② docker-compose up -d (API + PG 全在一台机器上)
  ③ Nginx 反向代理 + HTTPS (免费证书)
  ④ crontab 每日收盘后运行数据更新

优势：
  - 99元/年 ≈ 一杯奶茶钱
  - 4M 带宽够 API 调用（返回数据是纯文本，每次几KB）
  - 国内访问无网络问题
  - 腾讯云 BGP 线路覆盖三大运营商

不足：
  - 2核2G 跑 PG + API 稍紧，建议起步用
  - 如需更大规格，4C8G ≈ 300元/年
```

## 三、成本估算

### 起步配置（最低成本）

| 项目 | 费用 | 说明 |
|------|------|------|
| 腾讯云 Lighthouse 2C2G/4M/50G | **99元/年** | 一台机器跑全部 |
| 域名 (可选) | ~30元/年 | 如 stockpulse.cn |
| SSL 证书 | **免费** | 腾讯云/Let's Encrypt |
| 合计 | **~129元/年 ≈ 10元/月** | |

### 生产配置（正式上线）

| 项目 | 费用 | 说明 |
|------|------|------|
| 腾讯云 Lighthouse 4C8G/8M/120G | **~300元/年** | 更大并发 |
| 域名 | ~30元/年 | stockpulse.cn |
| SSL | 免费 | — |
| 合计 | **~330元/年 ≈ 27元/月** | |

### 与竞争对手对比

| 服务 | 月费 | 说明 |
|------|------|------|
| MCP.so 托管 | 未公开 | 仅目录，无数据托管 |
| **自托管（推荐）** | **~10元/月** | 99元/年全包 |
| 阿里云 RDS PG 单独托管 | ~19元/月 | 仅数据库，还需服务器 |
| Supabase Pro | $25/月 | 海外，国内需代理 |
| 自购服务器托管 | 300-500元/月 | 不划算 |

## 四、数据迁移方案

当前 PG 数据 5.8GB / 3400万行，迁移方式：

```
方式一：pg_dump 导出 → scp 到云服务器 → pg_restore（推荐）

步骤：
  1. 本地执行：pg_dump -U zrall -d ashare -f ashare_dump.sql
  2. scp 到云服务器：scp ashare_dump.sql root@云服务器IP:~/
  3. 云端执行：psql -U zrall -d ashare -f ashare_dump.sql
  4. 重建物化视图：REFRESH MATERIALIZED VIEW ...;

耗时估计：
  SQL 导出：~2-3 分钟
  scp 传输：~1-2 分钟（5.8GB 压缩后更小）
  PG 恢复：~5-10 分钟
  总计：~10-15 分钟

方式二：rsync 增量同步（日常更新用）
  rsync -avz --partial 数据库文件 root@IP:/data/
```

## 五、带宽估算

| 场景 | 每次响应大小 | 并发 | 月流量 |
|------|------------|------|--------|
| CLI 查询 | 1-5 KB | 低 | 忽略 |
| AI 报告 | 2-5 KB | 低 | 忽略 |
| Dashboard 页面 | 50-100 KB | 低 | ~1GB |
| MCP 工具调用 | 1-10 KB | 中 | ~5GB |
| **合计** | | | **~10GB/月** |

4M 带宽足够支撑 50+ 并发 API 调用，每月流量约 10GB，远低于 Lighthouse 的 1000GB+ 流量包。

## 六、部署步骤（简化）

```
1. 购买腾讯云 Lighthouse → 登录控制台
2. 安装 Docker：apt install docker.io docker-compose -y
3. 拉代码：git clone https://github.com/Allan1900/stockpulse.git
4. 配置 Nginx：反向代理 :8900 + SSL
5. 导入数据：pg_dump → scp → pg_restore
6. 启动：docker compose up -d
7. 设置 crontab：每日收盘自动更新数据
8. 验证：curl https://stockpulse.cn/health
```

## 七、可行性结论

```
✅ 技术可行 — Python/FastAPI + PostgreSQL 都是标准云部署方案
✅ 成本极低 — 99元/年起，比一杯咖啡/月还便宜
✅ 国内友好 — 腾讯云灯塔，无需备案加速
✅ 迁移简单 — pg_dump 一键迁移，10分钟完成
✅ 运维轻松 — Docker 化部署，重启/升级一行命令
✅ 可扩展 — 用户量上来后，升级配置/读写分离都方便

建议：先买一台腾讯云 Lighthouse 99元/年起步，
      把 API 部署上去跑通，后续根据用户量再升级。
```