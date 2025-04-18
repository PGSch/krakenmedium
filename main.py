#!/usr/bin/env python3
"""
Command-line interface for Kraken trading bot and backtesting.

Allows users to backtest a strategy over a historical period, simulate paper trading, or run in live mode.

Functions
---------
parse_args : Parse command-line arguments.
main       : Entry point; dispatches based on mode.
"""
import argparse
import importlib
from datetime import datetime
from backtester import Backtester
from kraken_bot import KrakenBot


def parse_args():
    """
    Parse CLI arguments for strategy, mode, pair, dates, etc.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Kraken trading bot / backtester')
    parser.add_argument('--strategy', '-s', required=True,
                        help='Name of the strategy module in strategies/ (e.g. macd)')
    parser.add_argument('--mode', '-m', choices=['backtest', 'paper', 'live'], default='backtest',
                        help='Operation mode: backtest vs paper vs live trading')
    parser.add_argument('--pair', '-p', required=True,
                        help='Trading pair, e.g. XBTUSD')
    parser.add_argument('--start', help='Backtest start date YYYY-MM-DD')
    parser.add_argument('--end', help='Backtest end date YYYY-MM-DD')
    parser.add_argument('--initial-cash', type=float, default=100000,
                        help='Initial cash for backtesting')
    parser.add_argument('--interval', '-i', type=int, default=15,
                        help='Fetch interval in minutes for paper/live modes')
    return parser.parse_args()


def main():
    """
    Main entrypoint: load strategy and execute backtest, paper, or live trading.
    """
    args = parse_args()

    # Dynamically load strategy
    module = importlib.import_module(f'strategies.{args.strategy}')
    strategy_func = getattr(module, 'strategy')

    if args.mode == 'backtest':
        if not args.start or not args.end:
            raise ValueError('Start and end dates required for backtest')
        start = datetime.fromisoformat(args.start)
        end = datetime.fromisoformat(args.end)
        bt = Backtester(args.pair)
        result = bt.run(strategy_func, start, end, args.initial_cash)
        # Print summary
        print(f"Backtest {args.strategy} on {args.pair}: {args.start} to {args.end}")
        print(f"Initial cash: ${result['initial_cash']:.2f}")
        print(f"Final cash:   ${result['final_cash']:.2f}")
        print(f"Returns:      {result['returns']*100:.2f}%")
        print("Trades:")
        for action, ts, price in result['trades']:
            print(f"  {action.title():4s} at {ts} price {price:.2f}")
        bt.plot(result)
    else:
        if args.mode == 'paper':
            from papertrader import PaperTrader
            trader = PaperTrader(args.pair, strategy_func,
                                 interval=args.interval,
                                 initial_cash=args.initial_cash)
            trader.run()
        else:  # live trading mode
            bot = KrakenBot()
            print(f"Running {args.strategy} in live mode on {args.pair}")
            # TODO: implement live data feed and order execution


if __name__ == '__main__':
    main()