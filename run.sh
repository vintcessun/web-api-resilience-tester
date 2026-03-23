#!/bin/bash

# ==========================================
# 配置区域
# ==========================================
PYTHON_BIN=$(which python3.12)  # 自动获取 python3.12 路径
SCRIPT_NAME="main.py"            # 你的脚本文件名

# 检查 Python 路径是否存在
if [ -z "$PYTHON_BIN" ]; then
    echo "[!] 错误: 未找到 python3.12，请检查是否安装。"
    exit 1
fi

echo "======================================================"
echo "  正义执行启动器 (Linux Server 版)"
echo "  Python 版本: $($PYTHON_BIN --version)"
echo "======================================================"

# 开始无限循环
while true
do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 正在发动新一轮投毒..."
    
    # 执行脚本
    $PYTHON_BIN $SCRIPT_NAME
    
    # 检查退出状态码
    if [ $? -eq 0 ]; then
        echo "[√] 本轮注入成功。"
        # 正常冷却时间（秒）
        sleep 30
    else
        echo "[!] 脚本运行出错，可能是服务器崩了。等待 60 秒后重试..."
        sleep 60
    fi
    
    echo "------------------------------------------------------"
done