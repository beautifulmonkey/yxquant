# -*- coding: utf-8 -*-
"""
异常定义

异常层次：
- YXQuantError：框架级基类，便于统一捕获
- 回测相关：数据、配置、回测执行
- 实盘相关：许可证、券商、风控、订单
- 策略/数据源：通用逻辑与数据异常
"""


# -----------------------------------------------------------------------------
# 基类
# -----------------------------------------------------------------------------


class YXQuantError(Exception):
    """yxquant 框架异常基类。捕获此类可处理所有框架抛出的业务异常。"""

    pass


# -----------------------------------------------------------------------------
# 许可证与实盘授权
# -----------------------------------------------------------------------------


class LicenseError(YXQuantError):
    """专业版功能未授权时抛出。相关组件需要专业版许可证方可使用。"""

    pass


# -----------------------------------------------------------------------------
# 回测相关
# -----------------------------------------------------------------------------


class BacktestError(YXQuantError):
    """回测流程中的通用异常基类。"""

    pass


class BacktestConfigError(BacktestError):
    """回测配置非法。如时间区间颠倒、标的未配置、手续费/保证金参数不合法等。"""

    pass


class InsufficientDataError(BacktestError):
    """回测数据不足。例如 warmup 周期未满、某标的缺失、数据长度短于策略要求等。"""

    pass


class BacktestDataError(BacktestError):
    """回测数据异常。如 OHLCV 字段缺失、时间索引乱序、存在 NaN/Inf 等。"""

    pass


class InvalidBarError(BacktestError):
    """单根 K 线/Bar 数据无效。如 high < low、volume 为负、时间戳异常等。"""

    pass


class BacktestRuntimeError(BacktestError):
    """回测执行期错误。如引擎状态不一致、策略与数据时间未对齐、观测器/分析器异常等。"""

    pass


# -----------------------------------------------------------------------------
# 实盘 / 执行相关
# -----------------------------------------------------------------------------


class LiveTradingError(YXQuantError):
    """实盘交易流程中的通用异常基类。"""

    pass


class BrokerConnectionError(LiveTradingError):
    """与券商/交易网关连接失败或断开。如 MT5/IB 未连接、网络超时、登录失败等。"""

    pass


class OrderRejectedError(LiveTradingError):
    """订单被券商或风控拒绝。可携带订单 ID、拒绝原因等上下文。"""

    pass


class OrderTimeoutError(LiveTradingError):
    """订单提交或成交等待超时。"""

    pass


class PositionSyncError(LiveTradingError):
    """本地持仓与券商/交易所记录不一致。需人工或程序介入对账。"""

    pass


class RiskLimitExceededError(LiveTradingError):
    """触达风控限制。如单日亏损上限、单笔最大手数、总敞口限制等。"""

    pass


class MarketClosedError(LiveTradingError):
    """当前非可交易时段或品种已闭市。"""

    pass


class LiquidityError(LiveTradingError):
    """流动性不足。如点差过大、盘口深度不足、无法按市价成交等。"""

    pass


class MarginError(LiveTradingError):
    """保证金不足或强平相关。如开仓所需保证金不足、接近强平线等。"""

    pass


# -----------------------------------------------------------------------------
# 数据源 / Feed
# -----------------------------------------------------------------------------


class FeedError(YXQuantError):
    """数据源通用异常。如历史数据加载失败、实时流断连、格式不兼容等。"""

    pass


class ResampleError(FeedError):
    """K 线重采样失败。如周期不支持、时间索引类型错误、聚合列缺失等。"""

    pass


class FeedTimeoutError(FeedError):
    """数据源拉取或等待超时。"""

    pass


# -----------------------------------------------------------------------------
# 策略与配置
# -----------------------------------------------------------------------------


class StrategyError(YXQuantError):
    """策略逻辑或状态异常。如未实现必要方法、内部状态不一致、指标未就绪等。"""

    pass


class SignalError(YXQuantError):
    """交易信号无效。如信号价格/数量不合法、与当前持仓冲突、重复信号等。"""

    pass


class ParameterError(YXQuantError):
    """策略或组件参数不合法。如必填项缺失、数值越界、类型错误等。"""

    pass


class ProfileError(YXQuantError):
    """运行配置（Profile）异常。如 BacktestProfile / LiveProfile 参数错误、数据与 Broker 不匹配等。"""

    pass
