# bili2txt-agent Docker 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 you-get
RUN pip install --no-cache-dir you-get

# 复制项目文件
COPY *.py ./
COPY .env.example .env.example

# 创建临时目录
RUN mkdir -p /app/temp

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口（如果需要）
# EXPOSE 8080

# 启动命令
CMD ["python", "main.py"]
