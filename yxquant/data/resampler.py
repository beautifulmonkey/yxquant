import pandas as pd
from typing import Optional, Dict

def resample_ohlcv(
    df: pd.DataFrame,
    timeframe: str,
    agg_dict: Optional[Dict[str, str]] = None,
    dropna: bool = True
) -> pd.DataFrame:
    """
    对 OHLCV 数据进行降采样
    Examples:
        >>> df = pd.read_csv('data.csv', parse_dates=True, index_col=0)
        >>> df_5min = resample_ohlcv(df, '5T')
        >>> df_15min = resample_ohlcv(df, '15T')
        >>> df_1h = resample_ohlcv(df, '1H')
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame 索引必须是 DatetimeIndex")
    
    # 默认聚合规则
    if agg_dict is None:
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
    
    available_cols = {col: agg_dict[col] for col in agg_dict.keys() if col in df.columns}
    
    if not available_cols:
        raise ValueError("DataFrame 中未找到可聚合的列")
    
    df_resampled = df.resample(timeframe).agg(available_cols)
    
    if dropna:
        df_resampled = df_resampled.dropna()
    
    return df_resampled


def resample_to_minutes(df: pd.DataFrame, minutes: int, **kwargs) -> pd.DataFrame:
    """
    将数据降采样到指定分钟周期（便捷函数）
    Examples:
        >>> df_5min = resample_to_minutes(df, 5)
        >>> df_15min = resample_to_minutes(df, 15)
    """
    timeframe = f'{minutes}T'
    return resample_ohlcv(df, timeframe, **kwargs)


def resample_to_hours(df: pd.DataFrame, hours: int, **kwargs) -> pd.DataFrame:
    """
    将数据降采样到指定小时周期（便捷函数）
    Examples:
        >>> df_1h = resample_to_hours(df, 1)
        >>> df_4h = resample_to_hours(df, 4)
    """
    timeframe = f'{hours}H'
    return resample_ohlcv(df, timeframe, **kwargs)
