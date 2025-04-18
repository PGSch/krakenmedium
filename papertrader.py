import time
from datetime import datetime, timedelta

from backtester import Backtester

class PaperTrader:
    """
    PaperTrader simulates live (paper) trading using historical OHLC data as if streaming in real time.

    Uses Backtester.fetch_ohlc to retrieve new bars at a fixed interval, applies the given strategy,
    and simulates buy/sell orders against a paper cash balance.

    Parameters
    ----------
    pair : str
        Trading pair, e.g. 'XBTUSD'.
    strategy_func : callable
        Function accepting a DataFrame and returning {timestamp: signal}.
    interval : int, optional
        Bar interval in minutes for data fetching (default 15).
    initial_cash : float, optional
        Starting cash in USD for paper simulation (default 100000.0).

    Attributes
    ----------
    pair : str
    strategy : callable
    interval : int
    cash : float
    position : float
    bt : Backtester
        Internal backtester for fetching OHLC.
    last_timestamp : datetime or None
        Timestamp of last processed bar.
    """
    def __init__(self, pair, strategy_func, interval=15, initial_cash=100000.0):
        """
        Initialize the PaperTrader.

        Parameters
        ----------
        pair : str
            Trading pair, e.g. 'XBTUSD'.
        strategy_func : callable
            Strategy function that returns {timestamp: signal}.
        interval : int, optional
            Data bar interval in minutes (default 15).
        initial_cash : float, optional
            Starting paper cash (default 100000.0).
        """
        self.pair = pair
        self.strategy = strategy_func
        self.interval = interval
        self.cash = initial_cash
        self.position = 0.0
        self.bt = Backtester(pair, interval)
        self.last_timestamp = None

    def run(self):
        """
        Execute the paper trading loop.

        Fetches OHLC bars at each interval, applies strategy to new data,
        simulates orders, and prints trade actions. Interrupt with Ctrl+C.

        Returns
        -------
        None
        """
        print(f"Starting paper trading for {self.pair} at {self.interval}-min interval with ${self.cash:.2f}")
        try:
            while True:
                now = datetime.utcnow()
                if self.last_timestamp:
                    start = self.last_timestamp + timedelta(seconds=1)
                else:
                    # initialize to fetch at least one bar
                    start = now - timedelta(minutes=self.interval)
                df = self.bt.fetch_ohlc(start, now)
                if not df.empty:
                    signals = self.strategy(df)
                    for ts, signal in signals.items():
                        if self.last_timestamp and ts <= self.last_timestamp:
                            continue
                        price = df.loc[ts, 'open']
                        if signal == 1 and self.position == 0:
                            self.position = self.cash / price
                            self.cash = 0.0
                            print(f"{datetime.utcnow()} BUY  @ {price:.2f} (bar {ts})")
                        elif signal == -1 and self.position > 0:
                            self.cash = self.position * price
                            self.position = 0.0
                            print(f"{datetime.utcnow()} SELL @ {price:.2f} (bar {ts})")
                        self.last_timestamp = ts
                # wait until next bar
                time.sleep(self.interval * 60)
        except KeyboardInterrupt:
            print("\nPaper trading stopped by user.")
            if self.position > 0:
                last_price = df['close'].iloc[-1]
                self.cash = self.position * last_price
                print(f"Closed position @ {last_price:.2f}")
                self.position = 0.0
            print(f"Final cash: ${self.cash:.2f}")