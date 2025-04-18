# Kraken Medium Trading Bot

![Trading Bot Status](https://img.shields.io/badge/status-active-green)
![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-yellow)

A lightweight and straightforward trading bot for the Kraken cryptocurrency exchange that provides simple limit order functionality.

## Features

- **Limit Buy Orders**: Place limit buy orders for cryptocurrencies
- **Limit Sell Orders**: Place limit sell orders for cryptocurrencies
- **Secure Authentication**: Uses Kraken's API authentication mechanism
- **Simple Interface**: Easy-to-use functions for trading operations

## Prerequisites

- Python 3.6 or higher
- A Kraken account with API keys
- Basic understanding of cryptocurrency trading

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/krakenmedium.git
   cd krakenmedium
   ```

2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # On Windows
   .\.venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API credentials:
   - Copy `.env.example` to `.env`
   - Add your Kraken API key and secret to the `.env` file

## Configuration

Create a `.env` file in the root directory with the following content:

```
KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_api_secret_here
```

Replace `your_api_key_here` and `your_api_secret_here` with your actual Kraken API credentials.

## Usage

### Command-line Interface
Use the unified `main.py` entrypoint for backtesting, paper or live trading modes.

```bash
python main.py \
  --strategy macd \
  --mode backtest \
  --pair XBTUSD \
  --start 2025-01-01 \
  --end   2025-03-31 \
  --initial-cash 10000
```
- `--strategy` (`-s`): name of a strategy module under `strategies/` (e.g. `macd`)
- `--mode` (`-m`): `backtest`, `paper`, or `live`
- `--pair`  (`-p`): trading pair (e.g. `XBTUSD`)
- `--start`, `--end`: ISO dates for backtest period
- `--initial-cash`: starting cash for backtests (default 10000)

Add these examples to illustrate paper and live modes:
```bash
# Paper trading simulation (15-min bars, $100k default)
python main.py \
  --strategy macd \
  --mode paper \
  --pair XBTUSD

# Live trading (requires implementing order loop)
python main.py \
  --strategy macd \
  --mode live \
  --pair XBTUSD
```

Parameters in other modes:
- `--interval` (`-i`): minutes between data fetch for paper/live (default 15)
- `--initial-cash`: starting cash for paper mode (default 100000)

You can still run the legacy interactive example:
```bash
python example.py
```

### Adding New Strategies
Create a new file `strategies/your_name.py` exporting a `strategy(df: pd.DataFrame) -> dict` function that returns `{timestamp: signal}`. The CLI will auto-discover it via `--strategy your_name`.

### Common Kraken Ticker Symbols

- XBTUSD - Bitcoin/USD
- ETHUSD - Ethereum/USD
- XLTCZUSD - Litecoin/USD
- XXRPZUSD - Ripple/USD
- DOTUSD - Polkadot/USD

## Response Format

Successful API responses are returned as Python dictionaries with the following structure:

```python
{
    'error': [],
    'result': {
        'txid': ['OE4MQV-4KRYL-KKMHPF'],  # Transaction ID(s)
        'descr': {
            'order': 'buy 0.01000000 XBTUSD @ limit 40000'
        }
    }
}
```

## Error Handling

The bot will raise exceptions with helpful error messages if:
- API credentials are missing or invalid
- The API request fails
- The API returns an error response

## Project Structure

- `kraken_bot.py`    - Main bot implementation with trading API wrapper
- `backtester.py`   - Historical backtesting engine for strategies
- `main.py`         - Command-line interface for backtest/paper/live modes
- `strategies/`     - Directory of strategy modules (e.g. `macd.py`)
- `example.py`      - Interactive menu example (legacy)
- `requirements.txt`- Required Python packages
- `.env.example`    - Template for API credentials
- `LICENSE`         - MIT license
- `README.md`       - This documentation

## Security Considerations

- Never share your API keys or include them in version control
- Consider restricting your API keys to only the necessary permissions
- Use small amounts for testing before executing larger trades

## Limitations

- This is a minimalist implementation focused on limit orders only
- Advanced trading features (stop-loss, trailing stops, etc.) are not implemented
- No automatic trading strategies or technical analysis tools are included

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms included in the LICENSE file.

## Disclaimer

Trading cryptocurrencies involves significant risk. This tool is provided for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred while using this software.