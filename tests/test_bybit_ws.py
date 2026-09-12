import asyncio

from app.exchanges.bybit import BybitExchange
from app.market_data.manager import MarketDataManager


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
    "ALGO/USDT",
    "XLM/USDT",
    "TRX/USDT",
    "ICP/USDT",
    "INJ/USDT",
    "SEI/USDT",
    "HBAR/USDT",
    "PEPE/USDT",
    "MATIC/USDT",
]


async def main():

    exchange = BybitExchange()

    exchanges = {
        "Bybit": exchange
    }

    manager = MarketDataManager(exchanges)

    await manager.start_symbols(SYMBOLS)

    print("=" * 60)
    print("Bybit MULTI-SYMBOL TEST")
    print("=" * 60)

    supported = [
        symbol
        for symbol in SYMBOLS
        if exchange.supports_symbol(symbol)
    ]

    print(f"Requested: {len(SYMBOLS)}")
    print(f"Supported: {len(supported)}")

    print("\nWaiting for markets...\n")

    try:

        while True:

            update = await manager.market_update.get()

            symbol = update["symbol"]
            exchange_name = update["exchange"]

            book = manager.get_order_book(
                exchange_name,
                symbol
            )

            print(f"READY/UPDATE: {symbol}")
            print(f"  Bid: {book['bids'][0]}")
            print(f"  Ask: {book['asks'][0]}")

    finally:

        await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())