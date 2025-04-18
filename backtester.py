import requests
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt

class Backtester:
    """
    Backtester simulates trading strategies over historical Kraken OHLC data.

    Parameters
    ----------
    pair : str
        Trading pair, e.g. 'XBTUSD'.
    interval : int, optional
        OHLC bar interval in minutes (default is 60).

    Attributes
    ----------
    pair : str
        Trading pair passed by user.
    interval : int
        Interval in minutes for fetched OHLC bars.
    """
    def __init__(self, pair: str, interval: int = 60):
        self.pair = pair
        self.interval = interval

    def fetch_ohlc(self, start: datetime, end: datetime) -> pd.DataFrame:
        """
        Download OHLC bars for the given time range.

        Parameters
        ----------
        start : datetime
            Start of the fetch window (inclusive).
        end : datetime
            End of the fetch window (inclusive).

        Returns
        -------
        pd.DataFrame
            DataFrame indexed by timestamp with columns ['open','high','low','close','vwap','volume','count'].
        """
        # Convert common ticker (e.g. XBTUSD, ETHUSD) into Kraken pair codes (e.g. XXBTZUSD, XETHZUSD)
        base = self.pair[:-3]
        quote = self.pair[-3:]
        # handle base asset code
        if base.upper() == 'XBT':
            base_code = 'XXBT'
        elif base[0] not in ('X','Z'):
            base_code = 'X' + base.upper()
        else:
            base_code = base.upper()
        # handle quote asset code
        if quote[0] not in ('X','Z'):
            quote_code = 'Z' + quote.upper()
        else:
            quote_code = quote.upper()
        pair_code = base_code + quote_code
        since = int(start.timestamp())
        all_data = []
        while True:
            resp = requests.get(
                'https://api.kraken.com/0/public/OHLC',
                params={'pair': pair_code, 'interval': self.interval, 'since': since}
            )
            res = resp.json().get('result', {})
            # Kraken result includes 'last' field; drop it
            result = res.get(pair_code, [])
            if not result:
                break
            all_data.extend(result)
            last_ts = int(result[-1][0])
            if last_ts >= int(end.timestamp()):
                break
            since = last_ts + 1
            time.sleep(1)
        df = pd.DataFrame(all_data, columns=[
            'time','open','high','low','close','vwap','volume','count'
        ])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df[df['time'] <= end]
        for col in ['open','high','low','close','vwap','volume','count']:
            df[col] = df[col].astype(float)
        df.set_index('time', inplace=True)
        return df

    def run(self, strategy_func, start: datetime, end: datetime, initial_cash: float = 10000):
        """
        Execute a backtest: apply strategy to historical data and simulate trades.

        Parameters
        ----------
        strategy_func : callable
            Function taking a DataFrame and returning {timestamp: signal}.
        start : datetime
            Backtest start time.
        end : datetime
            Backtest end time.
        initial_cash : float, optional
            Starting cash for simulation (default 10000).

        Returns
        -------
        dict
            Dictionary with keys:
            - 'start', 'end', 'initial_cash', 'final_cash', 'returns', 'trades', 'data'.
        """
        df = self.fetch_ohlc(start, end)
        signals = strategy_func(df.copy())
        cash = initial_cash
        position = 0.0
        trades = []
        for timestamp, row in df.iterrows():
            price = row['open']
            signal = signals.get(timestamp, 0)
            if signal == 1 and position == 0:
                position = cash / price
                cash = 0
                trades.append(('buy', timestamp, price))
            elif signal == -1 and position > 0:
                cash = position * price
                position = 0
                trades.append(('sell', timestamp, price))
        # close any open position at end
        if position > 0:
            final_price = df['close'].iloc[-1]
            cash = position * final_price
            trades.append(('sell', df.index[-1], final_price))
        return {
            'start': start,
            'end': end,
            'initial_cash': initial_cash,
            'final_cash': cash,
            'returns': (cash - initial_cash) / initial_cash,
            'trades': trades,
            'data': df
        }

    def plot(self, result: dict):
        """
        Plot the backtest results: close price line with buy/sell markers.

        Parameters
        ----------
        result : dict
            Backtest output from `run`, containing 'data' and 'trades'.

        Returns
        -------
        None
        """
        df = result['data']
        trades = result['trades']
        plt.figure(figsize=(12,6))
        plt.plot(df.index, df['close'], label='Close Price')
        for action, ts, price in trades:
            if action == 'buy':
                plt.scatter(ts, price, marker='^', color='g')
            else:
                plt.scatter(ts, price, marker='v', color='r')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title(f"{self.pair} Backtest {result['start'].date()} to {result['end'].date()}")
        plt.legend()
        plt.show()