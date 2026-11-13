# SpotKit-SouthGrid · 免 Python 环境一键跑通四件套
# 用法见 README 「不想装 Python？用 Docker 跑」
FROM python:3.11-slim

WORKDIR /app

# 仅标准库，无需第三方依赖；matplotlib 为可选，不装也能跑
COPY . .

# 预跑一次，校验演示可正常生成（产物在 /app/demo_out）
RUN python run_demo.py

# 默认容器启动时再跑一次，便于把产物挂到本机卷
CMD ["python", "run_demo.py"]
