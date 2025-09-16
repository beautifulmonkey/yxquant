import pandas as pd
import backtrader as bt

class CSVData:
    """
    CSV data loader
    
    CSV format required: date,open,close,high,low,volume
    """
    
    @staticmethod
    def load(path: str):
        return bt.feeds.PandasData(
            dataname=pd.read_csv(path, parse_dates=[0], index_col=0)
        )

class PGDBData:
    @staticmethod
    def load():
        ...


