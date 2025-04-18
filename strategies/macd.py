import pandas as pd

def strategy(df: pd.DataFrame) -> dict:
    """
    MACD crossover strategy: buy when MACD crosses above signal line, sell on cross below.
    Returns a dict of timestamps to signals (1 for buy, -1 for sell).
    """
    # Calculate MACD and signal line
    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
    signals = {}
    prev_macd = prev_signal = 0.0
    for ts, row in df.iterrows():
        macd = row['macd']
        sig = row['signal_line']
        # bullish crossover: MACD crosses above signal line
        if prev_macd <= prev_signal and macd > sig:
            signals[ts] = 1
        # bearish crossover: MACD crosses below signal line
        elif prev_macd >= prev_signal and macd < sig:
            signals[ts] = -1
        prev_macd, prev_signal = macd, sig
    return signals