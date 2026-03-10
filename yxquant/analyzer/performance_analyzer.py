from collections import defaultdict
import numpy as np

def get_performance(trade_record_df, date_list):
    hour_returns_distribution = defaultdict(int)
    hour_trades_distribution = defaultdict(int)

    sorted_hour = [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

    time_returns_distribution = {hour: defaultdict(float) for hour in sorted_hour}
    time_trades_distribution = {hour: defaultdict(int) for hour in sorted_hour}
    duration_list = []

    days_pnl = defaultdict(float)
    month_pnl = defaultdict(float)
    _return = []

    for row in trade_record_df.itertuples(index=True):
        open_time = row.open_time
        close_time = row.close_time
        duration = row.duration_sec
        pnl = row.pnl

        time_returns_distribution[open_time.hour][open_time.minute] += pnl
        time_trades_distribution[open_time.hour][open_time.minute] += 1
        duration_list.append(duration)

        _return.append(pnl)
        hour_returns_distribution[str(open_time.hour) + "点"] += pnl
        hour_trades_distribution[str(open_time.hour) + "点"] += 1
        days_pnl[str(close_time.date())] += pnl
        month_pnl[str(close_time.date())[:-2] + "01"] += pnl

    # 分离盈利和亏损交易
    _win_trades = [i for i in _return if i > 0]
    _loss_trades = [i for i in _return if i <= 0]
    _trading_day = len(set(date_list)) if date_list else 0

    # 计算基础统计指标
    total_trades = len(_return)
    num_win_trades = len(_win_trades)
    num_loss_trades = len(_loss_trades)
    total_return = sum(_return)
    total_win = sum(_win_trades)
    total_loss = sum(_loss_trades)

    # 计算平均值（处理边界情况）
    avg_trade = round(total_return / total_trades, 2) if total_trades > 0 else 0.0
    avg_win_trade = round(total_win / num_win_trades, 2) if num_win_trades > 0 else 0.0
    avg_loss_trade = round(abs(total_loss / num_loss_trades), 2) if num_loss_trades > 0 else 0.0
    avg_duration = int(np.array(duration_list).mean() / 60) if duration_list else 0
    percent_profitable = round(num_win_trades / total_trades * 100, 1) if total_trades > 0 else 0.0

    # 计算比率（处理边界情况）
    win_loss_ratio = (
        round(avg_win_trade / avg_loss_trade, 2)
        if num_win_trades > 0 and num_loss_trades > 0 and avg_loss_trade > 0
        else 0.0
    )
    avg_days_pnl = round(total_return / _trading_day, 1) if _trading_day > 0 else 0.0
    frequency_day = round(total_trades / _trading_day, 3) if _trading_day > 0 else 0.0

    # 处理日期边界情况
    start_date = str(date_list[0]) if date_list else ""
    end_date = str(date_list[-1]) if date_list else ""

    # 构建性能指标字典
    _performance = {
        # 基础统计
        "Total net profit": round(total_return, 2),
        "Gross profit": int(total_win),
        "Gross loss": int(abs(total_loss)),
        "Start date": start_date,
        "End date": end_date,
        "Years": list(range(date_list[0].year,date_list[-1].year + 1)),
        "Trading day": _trading_day,
        "Total of trades": total_trades,
        "#winning trades": num_win_trades,
        "#losing trades": num_loss_trades,
        "Percent profitable": percent_profitable,
        "Avg. duration": avg_duration,
        "Avg. trade": avg_trade,
        "Avg. winning trade": avg_win_trade,
        "Avg. losing trade": avg_loss_trade,
        "Avg. days PnL": avg_days_pnl,
        "Ratio avg.win / avg.loss": win_loss_ratio,
        "Frequency day": frequency_day,

        # 分布数据
        "hour_returns_distribution": hour_returns_distribution,  # 时间收益分布
        "hour_trades_distribution": hour_trades_distribution,  # 时间交易次数分布
        "time_returns_distribution": [
            [hour, sorted(data.items(), key=lambda x: x[0])]
            for hour, data in time_returns_distribution.items()
        ],
        "time_trades_distribution": [
            [hour, sorted(data.items(), key=lambda x: x[0])]
            for hour, data in time_trades_distribution.items()
        ],
        "days_pnl": [
            [_d, _pnl] for _d, _pnl in sorted(days_pnl.items(), key=lambda x: x[0])
        ],
        "month_pnl": [
            [_d, _pnl] for _d, _pnl in sorted(month_pnl.items(), key=lambda x: x[0])
        ],
        "sorted_hour": [f"{i}点" for i in sorted_hour]
    }
    return _performance
