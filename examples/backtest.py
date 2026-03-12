from yxquant.data import CSVData
from yxquant.utils import start_static_server
from yxquant.engine import CoreEngine
from yxquant.profiles import DataFeed, BacktestMode, BacktestProfile, Broker, OHLCV
from yxquant.trading import CTAStrategyBase
import backtrader as bt

class EMA9Strategy(CTAStrategyBase):
    name = 'EMA9'
    params = dict(
        period=9,  # EMA 计算周期
        tp=10,  # 止盈点数
        sl=7  # 止损点数
    )

    def __init__(self):
        super().__init__()
        self.ema9 = bt.indicators.EMA(self.datas[0], period=self.p.period)

    def on_data(self):
        o, h, l, c = self.data.open[0], self.data.high[0], self.data.low[0], self.data.close[0]

        if self.ema9[0] > l >= self.ema9[-1]:
            self.long(tp_price=c + self.p.tp, sl_price=c - self.p.sl)


if __name__ == '__main__':
    # 定义一个最小可运行的 CTA 回测配置：模式、数据源和初始资金。
    BACKTEST_CTA_PROFILE = BacktestProfile(
        mode=BacktestMode.CTA,
        data=[DataFeed(name="ES", feed=CSVData, params=dict(path="ES_5min.csv"), schema=OHLCV)],
        broker=Broker(cash=10000)
    )
    engine = CoreEngine({})
    # 注册策略，并导出 ema9 指标到可视化结果中。
    engine.add_strategy(EMA9Strategy, exported_indicators=['ema9'])
    engine.attach(BACKTEST_CTA_PROFILE)
    results, ctx = engine.run()

    # 读取回测结束后的账户净值，并启动静态页面查看结果。
    final_value = engine.cerebro.broker.getvalue()
    print(f"Final portfolio value: 💰💰💰{final_value:.2f}")
    start_static_server()

