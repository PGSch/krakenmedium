#!/usr/bin/env python3
from kraken_bot import KrakenBot
from backtester import Backtester
import pandas as pd  # needed for new strategy
from datetime import datetime

# MACD crossover strategy: buy when MACD crosses above signal line, sell on cross below
def macd_strategy(df):
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
        # generate buy signal on bullish crossover
        if prev_macd <= prev_signal and macd > sig:
            signals[ts] = 1
        # generate sell signal on bearish crossover
        elif prev_macd >= prev_signal and macd < sig:
            signals[ts] = -1
        prev_macd, prev_signal = macd, sig
    return signals

def main():
    """Example usage of the Kraken trading bot"""
    try:
        # Create a new bot instance
        bot = KrakenBot()
        
        # Display a simple menu
        print("\nKraken Mini Trading Bot Example")
        print("===============================")
        print("1. Place a limit buy order")
        print("2. Place a limit sell order")
        print("3. Exit")
        print("4. Backtest sample strategy")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            # Get parameters for limit buy
            ticker = input("Enter ticker (e.g., XBTUSD): ")
            price = input("Enter price: ")
            amount = input("Enter amount: ")
            
            # Confirm the order
            print(f"\nYou are about to place a LIMIT BUY order:")
            print(f"Buy {amount} {ticker.split('USD')[0]} at ${price} USD")
            confirm = input("Confirm? (y/n): ")
            
            if confirm.lower() == 'y':
                result = bot.limit_buy(ticker, price, amount)
                print("\nOrder placed successfully!")
                print(f"Transaction ID: {result.get('result', {}).get('txid', ['Unknown'])[0]}")
            else:
                print("\nOrder cancelled.")
                
        elif choice == '2':
            # Get parameters for limit sell
            ticker = input("Enter ticker (e.g., XBTUSD): ")
            price = input("Enter price: ")
            amount = input("Enter amount: ")
            
            # Confirm the order
            print(f"\nYou are about to place a LIMIT SELL order:")
            print(f"Sell {amount} {ticker.split('USD')[0]} at ${price} USD")
            confirm = input("Confirm? (y/n): ")
            
            if confirm.lower() == 'y':
                result = bot.limit_sell(ticker, price, amount)
                print("\nOrder placed successfully!")
                print(f"Transaction ID: {result.get('result', {}).get('txid', ['Unknown'])[0]}")
            else:
                print("\nOrder cancelled.")
                
        elif choice == '3':
            print("\nExiting program. Goodbye!")
        
        elif choice == '4':
            # Real backtest using Kraken historical OHLC data
            pair = input("Enter pair for backtest (e.g., XBTUSD): ")
            start = datetime(2025, 1, 1)
            end = datetime(2025, 3, 31)
            bt = Backtester(pair)
            result = bt.run(macd_strategy, start, end)
            print(f"\nBacktest from {start.date()} to {end.date()}")
            print(f"Initial cash: ${result['initial_cash']:.2f}")
            print(f"Final cash: ${result['final_cash']:.2f}")
            print(f"Returns: {result['returns']*100:.2f}%")
            # Print individual trades
            print("\nTrades:")
            for action, ts, price in result['trades']:
                print(f"{action.title()} at {ts} — price {price:.2f}")
            bt.plot(result)
        
        else:
            print("\nInvalid choice. Please run the program again.")
            
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()