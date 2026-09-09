from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange


binance = BinanceExchange()
kraken = KrakenExchange()

symbols = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
]

for symbol in symbols:
    print()
    print(symbol)

    print(
        "Binance:",
        binance.supports_symbol(symbol)
    )

    print(
        "Kraken:",
        kraken.supports_symbol(symbol)
    )