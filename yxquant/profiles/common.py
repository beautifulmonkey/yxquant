from typing import Any, Dict, List, Optional, Sequence, Union, Type
from dataclasses import dataclass, field

@dataclass
class DataFeed:
    feed: Union[str, Type]    # 类对象或 "pkg.mod:Class" 字符串
    params: Dict[str, Any]    # 传给 feed 的 kwargs（CSV/PG 等）
    name: Optional[str] = None



@dataclass
class Broker:
    commission: float = 0.0
    cash: Optional[float] = None      # 初始资金（可选）
    slip_perc: Optional[float] = None # 简单百分比滑点（可选）

