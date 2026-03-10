"""
    cta交易类
"""
import backtrader as bt
import uuid
import logging
from .base import BaseStrategy
from yxquant.exceptions import LicenseError

logger = logging.getLogger()


class CTAStrategyBase(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.open_order = {}  # open的订单
        self.last_complete_order = None  # 最新成交订单

    def notify_order(self, order):
        if order.status == order.Rejected:
            logger.error(f'{self.name} Order Rejected!!')
            return

        if order.status in [order.Completed]:
            self.last_complete_order = order

        if order.status in [order.Created, order.Submitted, order.Accepted]:
            self.open_order[order.ref] = order
        else:
            self.open_order.pop(order.ref)

    def close_all_position(self):
        position_size = self.getstrategyposition().size
        for order in self.open_order.values():
            self.cancel(order)
            logger.debug(f'{self.name} cancel time@{self._stime} tradeid:{order.tradeid}')

        if position_size == 0: return

        tid = self.last_complete_order.tradeid
        if position_size > 0:
            self.sell(tradeid=tid, exectype=bt.Order.Market)
            logger.debug(f'{self.name} sell2close time@{self._stime} tradeid:{tid}')
        elif position_size < 0:
            self.buy(tradeid=tid, exectype=bt.Order.Market)
            logger.debug(f'{self.name} buy2close time@{self._stime} tradeid:{tid}')

    @BaseStrategy.entry_guard
    def long(self, price=None, tp_price=None, sl_price=None):
        """做多"""
        current_close = price or self.data.close[0]
        exectype = bt.Order.Limit if price else bt.Order.Market
        position_size = self.getstrategyposition().size
        trade_id = uuid.uuid1().hex
        if position_size == 0:
            main_order = self.buy(price=current_close, exectype=exectype, tradeid=trade_id)
            sl_order = self.sell(price=sl_price, exectype=bt.Order.Stop, tradeid=trade_id)
            tp_order = self.sell(price=tp_price, exectype=bt.Order.Limit, tradeid=trade_id, oco=sl_order)
            logger.debug('------------------------------------')
            logger.debug(
                f'{self.name} long@{current_close} time@{str(self._time)} st@{sl_order} tp@{tp_order} ref:{main_order.ref}/{sl_order.ref}/{tp_order.ref} tradeid:{trade_id}')
        elif position_size < 0:  # 持有空仓
            self.close_all_position()

    @BaseStrategy.entry_guard
    def short(self, price=None, tp_price=None, sl_price=None):
        """做空"""
        current_close = price or self.data.close[0]
        exectype = bt.Order.Limit if price else bt.Order.Market
        position_size = self.getstrategyposition().size
        trade_id = uuid.uuid1().hex
        if position_size == 0:
            main_order = self.sell(price=current_close, exectype=exectype, tradeid=trade_id)
            sl_order = self.buy(price=sl_price, exectype=bt.Order.Stop, tradeid=trade_id)
            tp_order = self.buy(price=tp_price, exectype=bt.Order.Limit, tradeid=trade_id, oco=sl_order)
            logger.debug('------------------------------------')
            logger.debug(
                f'{self.name} short@{current_close} time@{str(self._time)} st@{sl_price} tp@{tp_price} ref:{main_order.ref}/{sl_order.ref}/{tp_order.ref} tradeid:{trade_id}')
        elif position_size > 0:  # 持有多仓
            self.close_all_position()

    def unrealized_pnl(self):
        position_size = self.getstrategyposition().size
        position_price = self.last_complete_order.executed.price
        if position_size < 0:
            pnl = position_price - self.data.close[0]
        if position_size > 0:
            pnl = self.data.close[0] - position_price
        return pnl

    def close_all(self):
        self.close_all_position()


class CTAStrategyAdvanced(CTAStrategyBase):
    """CTA 高级功能，需专业版许可证。"""

    def __init__(self, **kwargs):
        raise LicenseError("该功能需要专业版许可证，请联系获取授权。")
