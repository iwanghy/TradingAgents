#!/bin/bash
# 直接加载 Conda 初始化脚本（无需 conda init）
source /home/why/miniforge3/etc/profile.d/conda.sh
conda activate tradingagents
python batch_generate_reports.py tickers.txt --segment