from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange
from app.exchanges.coinbase import CoinbaseExchange
from app.exchanges.okx import OKXExchange
from app.exchanges.bybit import BybitExchange


exchanges = {
    "Binance": BinanceExchange(),
    "Kraken": KrakenExchange(),
    "Coinbase": CoinbaseExchange(),
    "OKX": OKXExchange(),
    "Bybit": BybitExchange()
}


SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "DOT/USDT",
    "LTC/USDT",
    "BCH/USDT",
    "UNI/USDT",
    "ATOM/USDT",
    "ETC/USDT",
    "FIL/USDT",
    "NEAR/USDT",
    "APT/USDT",
    "ARB/USDT",
    "OP/USDT",
    "SUI/USDT",
    "AAVE/USDT",
    "MATIC/USDT",
    "ALGO/USDT",
    "XLM/USDT",
    "TRX/USDT",
    "ICP/USDT",
    "INJ/USDT",
    "SEI/USDT",
    "HBAR/USDT",
    "PEPE/USDT"
]


for symbol in SYMBOLS:

    print()
    print(symbol)

    for name, exchange in exchanges.items():

        print(
            f"  {name:<10} "
            f"{exchange.supports_symbol(symbol)}"
        )