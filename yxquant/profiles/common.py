import backtrader as bt
from typing import Any, Dict, Optional, Union, Type, List
from enum import Enum
from dataclasses import dataclass, field
from yxquant.schemas import OHLCV

@dataclass
class DataFeed:
    """单路数据源配置：数据类、参数、名称、是否预加载及数据 schema。"""
    feed: Union[str, Type]
    params: Dict[str, Any]
    name: Optional[str] = None
    need_load: bool = True
    schema: Type = OHLCV  # 数据格式：OHLCV | MBP1 | MBPN | Trade | TBBO. （ 回测模式目前仅支持 OHLCV）


@dataclass
class CommissionInfo:
    """单品种手续费配置：佣金、乘数、保证金等，对应 Backtrader CommInfo。"""
    commission: float = 0.0  # 单边佣金
    mult: float = 1.0
    name: Optional[str] = None
    margin: Optional[float] = None
    commtype: Optional[int] = bt.CommInfoBase.COMM_FIXED


@dataclass
class Broker:
    """回测/优化用经纪商配置：初始资金、滑点、手续费列表、是否 COC。"""
    cash: Optional[float] = 1000000
    slip_perc: Optional[float] = None
    coc: Optional[bool] = False
    commissions: List[CommissionInfo] = field(default_factory=list)


class BacktestMode(Enum):
    """策略模式"""
    CTA = "CTA"             # CTA(单品种)
    ARB = "ARB"             # 套利(配对交易)


class RunningMode(Enum):
    """运行模式"""
    BACKTEST = "BACKTEST"   # 回测
    LIVE = "LIVE"           # 实盘
    OPT = "OPT"             # 参数优化
