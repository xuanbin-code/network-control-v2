"""测试共享配置：确保能导入 app 与 shared 包"""

import sys
from pathlib import Path

# 将 packages/ 目录加入 Python 路径，与 app/main.py 保持一致
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
