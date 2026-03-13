"""
数据库模型定义
使用Peewee ORM定义Trade和Order表结构
"""

from peewee import *
from datetime import datetime

database_proxy = DatabaseProxy()


class BaseModel(Model):
    """基础模型类"""
    created_at = DateTimeField(default=datetime.now, help_text="创建时间")

    class Meta:
        database = database_proxy


class Order(BaseModel):
    """订单表"""
    account = CharField(null=True, help_text="账户")
    strategy = CharField(help_text="策略名称")
    symbol = CharField(help_text="交易品种")
    order_id = CharField(null=True, help_text="本地/券商订单ID")
    broker_order_id = CharField(null=True, help_text="券商回报订单ID")

    action = CharField(help_text="BUY/SELL")
    size = DecimalField(max_digits=15, decimal_places=2, help_text="数量")
    order_type = CharField(null=True, help_text="MKT/LMT/STP/STPLMT等")
    limit_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="限价")
    stop_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="触发价")

    # 延迟计算
    data_pub_time = DateTimeField(null=True, help_text="数据源推送时间")
    data_sub_time = DateTimeField(null=True, help_text="量化接收到时间")

    bid1price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="下单前买一价")
    bid1size = DecimalField(null=True, max_digits=15, decimal_places=2, help_text="下单前买一量")
    ask1price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="下单前卖一价")
    ask1size = DecimalField(null=True, max_digits=15, decimal_places=2, help_text="下单前卖一量")

    bid_depth = TextField(null=True, help_text="下单前买盘深度JSON: [[price,size],...]")
    ask_depth = TextField(null=True, help_text="下单前卖盘深度JSON: [[price,size],...]")

    # 信号价格与成交价格对比
    signal_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="信号价格")
    signal_time = DateTimeField(null=True, help_text="信号时间")

    status = CharField(null=True, help_text="Submitted/Filled/Cancelled/Rejected等")
    filled_size = DecimalField(null=True, max_digits=15, decimal_places=2, help_text="成交数量")
    avg_fill_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="成交均价")
    commission = DecimalField(null=True, max_digits=15, decimal_places=8, help_text="手续费")

    submitted_at = DateTimeField(null=True, help_text="提交时间")
    filled_at = DateTimeField(null=True, help_text="成交时间")
    cancelled_at = DateTimeField(null=True, help_text="撤单时间")

    remarks = TextField(null=True, help_text="备注")

    class Meta:
        table_name = 'orders'
        indexes = (
            (('order_id',), False),
            (('strategy',), False),
            (('submitted_at',), False),
            (('status',), False),
        )


class Trade(BaseModel):
    """交易记录表"""
    account = CharField(null=True, help_text="账户")
    strategy = CharField(help_text="策略名称")
    symbol = CharField(help_text="交易品种")
    action = CharField(help_text="操作类型")
    size = DecimalField(max_digits=15, decimal_places=2, help_text="数量")

    trade_id = CharField(null=True, help_text="交易ID")
    open_order_id = IntegerField(null=True, help_text="开仓订单ID(Order.id)")
    close_order_id = IntegerField(null=True, help_text="平仓订单ID(Order.id)")

    lmt_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="限价价格")
    sl_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="止损价格")
    tp_price = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="止盈价格")

    fill_price_open = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="成交开仓价格")
    fill_time_open = DateTimeField(null=True, help_text="成交开仓时间")

    fill_price_close = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="成交平仓价格")
    fill_time_close = DateTimeField(null=True, help_text="成交平仓时间")

    max_drawdown = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="最大回撤金额")
    commission = DecimalField(null=True, max_digits=15, decimal_places=8, help_text="手续费")
    fee = DecimalField(null=True, max_digits=15, decimal_places=8, help_text="其他费用")
    duration = IntegerField(null=True, help_text="持仓时长(秒)")
    pnl = DecimalField(null=True, max_digits=20, decimal_places=8, help_text="盈亏")
    account_balance_new = DecimalField(null=True, max_digits=20, decimal_places=2, help_text="账户余额")
    account_equity_new = DecimalField(null=True, max_digits=20, decimal_places=2, help_text="账户净值")

    lmt_perm_id = CharField(null=True, help_text="现价单ID")
    tp_perm_id = CharField(null=True, help_text="止盈单ID")
    sl_perm_id = CharField(null=True, help_text="止损单ID")

    remarks = TextField(null=True, help_text="备注信息")

    class Meta:
        table_name = 'trades'
        indexes = (
            (('created_at',), False),
            (('account',), False),
            (('strategy',), False),
            (('symbol',), False),
            (('trade_id',), False),
        )

