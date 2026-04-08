#!/usr/bin/env python3
"""
Brain Bee Demo 启动脚本
-----------------------
无需安装即可直接运行交互式演示。
"""

import os
import sys
from pathlib import Path

# 自动将 src 目录添加到 Python 路径
repo_root = Path(__file__).parent.absolute()
src_path = repo_root / "src"

if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from brain_bee.main import main
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在项目根目录下运行此脚本。")
    sys.exit(1)

if __name__ == "__main__":
    # 强制设置控制台编码（针对某些旧版终端）
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

    main()
