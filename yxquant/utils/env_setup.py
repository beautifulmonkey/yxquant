import sys
from pathlib import Path
from dotenv import load_dotenv


def setup_environment(script_path: str, mode: str = None):
    """
    设置项目环境和加载环境变量
    
    Args:
        script_path: 当前脚本的路径 (通常使用 __file__)
        mode: 环境模式，如 'backtest', 'live' 等，用于加载对应的 .env.{mode} 文件
    """
    # 计算项目根目录
    project_root = Path(script_path).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # 加载环境变量
    base_env = project_root / "env" / ".env"
    if base_env.exists():
        load_dotenv(dotenv_path=base_env)
    
    # 加载模式特定的环境变量
    if mode:
        mode_env = project_root / "env" / f".env.{mode}"
        if mode_env.exists():
            load_dotenv(dotenv_path=mode_env, override=True)