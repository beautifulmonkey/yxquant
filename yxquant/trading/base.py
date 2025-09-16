import backtrader as bt

class BaseStrategy(bt.Strategy):
    params = dict()

    # def bind_services(self, exec=None, risk=None, sizer=None, ctx=None):
    #     self.exec = exec
    #     self.risk = risk
    #     self.sizer = sizer
    #     self.ctx = ctx or {}
    #
    # # 常用便捷方法（示例）
    # def buy_bracket(self, size, limit=None, stop=None):
    #     return self.exec.buy_bracket(size=size, limit=limit, stop=stop)

    def next(self):
        pass
