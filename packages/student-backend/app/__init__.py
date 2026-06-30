"""学生端后端根包"""

import sys
from pathlib import Path

# 将 packages 目录加入路径，确保能找到 shared 包
_packages_dir = Path(__file__).resolve().parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))
