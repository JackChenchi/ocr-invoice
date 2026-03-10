# Railway 部署指南

## 前置要求

1. GitHub 账号
2. Railway 账号（可使用 GitHub 登录）
3. 代码已推送到 GitHub 仓库

## 部署步骤

### 第一步：推送代码到 GitHub

```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 第二步：登录 Railway

1. 访问 [Railway.app](https://railway.app/)
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权 Railway 访问您的 GitHub 仓库

### 第三步：创建 Redis 服务

Railway 需要先创建 Redis 服务供后端使用：

1. 在项目页面点击 "+ New"
2. 选择 "Database" → "Add Redis"
3. Redis 会自动创建并生成连接信息

### 第四步：部署 Backend 服务

1. 点击 "+ New" → "GitHub Repo"
2. 选择您的仓库
3. **Root Directory 设置为 `backend`**
4. Railway 会自动检测到 `railway.json` 和 `Dockerfile`
5. 点击 "Deploy"

**配置环境变量**（在 Variables 标签页）：

```
DATABASE_URL=sqlite:///./ocr.db
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
```

**注意**：Railway 会自动注入 Redis 的连接信息，使用 `${{Redis.REDIS_HOST}}` 语法引用。

### 第五步：部署 Worker 服务

1. 点击 "+ New" → "GitHub Repo"
2. 选择同一个仓库
3. **Root Directory 设置为 `backend`**
4. 在 "Settings" → "Start Command" 设置：
   ```
   celery -A app.core.celery_app worker --loglevel=info
   ```
5. 配置与 Backend 相同的环境变量

### 第六步：部署 Frontend 服务

1. 点击 "+ New" → "GitHub Repo"
2. 选择同一个仓库
3. **Root Directory 设置为 `frontend`**
4. Railway 会自动检测到 `railway.json` 和 `Dockerfile`
5. 点击 "Deploy"

### 第七步：配置域名

1. 在 Frontend 服务页面，点击 "Settings"
2. 找到 "Domains" 部分
3. 点击 "Generate Domain" 生成 `.railway.app` 域名
4. 或添加自定义域名

### 第八步：更新 Backend API 地址

如果 Frontend 需要直接访问 Backend API（而不是通过 nginx 代理），需要：

1. 在 Frontend 服务的环境变量中添加：
   ```
   VITE_API_BASE_URL=https://your-backend-url.railway.app
   ```
2. 重新部署 Frontend

## 服务架构

```
┌─────────────┐
│   Frontend  │ (nginx + Vue.js)
│   :80       │
└──────┬──────┘
       │ /api/
       ↓
┌─────────────┐
│   Backend   │ (FastAPI + PaddleOCR)
│   :8000     │
└──────┬──────┘
       │
       ↓
┌─────────────┐     ┌─────────────┐
│    Redis    │←────│   Worker    │ (Celery)
│   :6379     │     │             │
└─────────────┘     └─────────────┘
```

## 常见问题

### 1. Backend 健康检查失败

确保 `/api/health` 端点可访问。检查日志：
```bash
railway logs
```

### 2. PaddleOCR 内存不足

Railway 免费层内存有限（512MB-1GB）。如果遇到内存问题：
- 升级到付费计划（$5/月起）
- 或使用 VPS 部署

### 3. 数据持久化

Railway 容器重启后数据会丢失。需要配置持久化存储：
1. 在 Backend 服务添加 Volume
2. 挂载到 `/app/uploads` 和 `/app/ocr.db`

### 4. Worker 无法连接 Redis

检查环境变量是否正确引用 Redis 服务：
```
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
```

## 成本估算

- **免费层**：$0/月（有限制，适合测试）
- **Hobby 计划**：$5/月（推荐用于生产）
- **Pro 计划**：$20/月（更高配置）

## 下一步

部署完成后：
1. 访问生成的域名测试功能
2. 上传发票图片测试 OCR 功能
3. 监控日志确保服务稳定运行
