FROM python:3.10-slim
LABEL "language"="python"
LABEL "framework"="fastapi"

WORKDIR /app

# 复制整个项目
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8000

# 从 backend 目录启动应用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
