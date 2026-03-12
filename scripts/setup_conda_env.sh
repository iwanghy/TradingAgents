#!/bin/bash
# TradingAgents Conda 环境安装脚本
# 用法: bash scripts/setup_conda_env.sh

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TradingAgents Conda 环境安装脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 配置
ENV_NAME="tradingagents"
PYTHON_VERSION="3.10"

# 检查 conda 是否可用
if ! command -v conda &> /dev/null; then
    echo -e "${RED}错误: 未找到 conda 命令。请先安装 Miniconda 或 Anaconda。${NC}"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo -e "${YELLOW}步骤 1: 创建 conda 环境${NC}"
# 检查环境是否已存在
if conda env list | grep -q "^${ENV_NAME} "; then
    echo -e "${YELLOW}环境 '${ENV_NAME}' 已存在。是否删除并重新创建? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "删除旧环境..."
        conda env remove -n ${ENV_NAME} -y
        conda create -n ${ENV_NAME} python=${PYTHON_VERSION} -y
    else
        echo "使用现有环境。"
    fi
else
    conda create -n ${ENV_NAME} python=${PYTHON_VERSION} -y
fi

echo -e "\n${YELLOW}步骤 2: 激活环境并安装依赖${NC}"
eval "$(conda shell.bash hook)"
conda activate ${ENV_NAME}

# 升级 pip
pip install --upgrade pip

# 安装项目依赖
echo "安装 requirements.txt 中的依赖..."
pip install -r requirements.txt

echo -e "\n${YELLOW}步骤 3: 配置环境变量${NC}"
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env 文件已创建${NC}"
    echo -e "${YELLOW}请编辑 .env 文件，添加你的 API 密钥${NC}"
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

echo -e "\n${YELLOW}步骤 4: 验证安装${NC}"
echo "运行快速验证..."

# 创建验证脚本
python << EOF
import sys

# 检查关键依赖
dependencies = [
    ("langchain_core", "langchain-core"),
    ("langgraph", "langgraph"),
    ("pandas", "pandas"),
    ("yfinance", "yfinance"),
]

missing = []
for module, package in dependencies:
    try:
        __import__(module)
        print(f"✓ {package}")
    except ImportError:
        missing.append(package)
        print(f"✗ {package} (未安装)")

if missing:
    print(f"\n错误: 以下依赖未正确安装: {', '.join(missing)}")
    sys.exit(1)
else:
    print("\n所有核心依赖已成功安装！")
EOF

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}安装完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "接下来的步骤:"
    echo "1. 激活环境: conda activate ${ENV_NAME}"
    echo "2. 编辑 .env 文件，添加你的 API 密钥"
    echo "3. 运行测试: python test.py"
    echo "4. 启动 CLI: python -m cli.main"
    echo ""
    echo -e "${YELLOW}注意: 每次使用前请先运行 'conda activate ${ENV_NAME}'${NC}"
else
    echo -e "\n${RED}安装验证失败！请检查错误信息。${NC}"
    exit 1
fi
