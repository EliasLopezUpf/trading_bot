import asyncio

from app.exchanges.coinbase import CoinbaseExchange
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

    exchange = CoinbaseExchange()

    manager = MarketDataManager({
        "Coinbase": exchange
    })

    await manager.start_symbols(SYMBOLS)

    supported = [
        symbol
        for symbol in SYMBOLS
        if exchange.supports_symbol(symbol)
    ]

    print("=" * 60)
    print("COINBASE MULTI-SYMBOL TEST")
    print("=" * 60)

    print(f"Requested: {len(SYMBOLS)}")
    print(f"Supported: {len(supported)}")

    print("\nWaiting for markets...\n")

    try:

        while True:

            update = await manager.market_update.get()

            symbol = update["symbol"]

            book = manager.get_order_book(
                "Coinbase",
                symbol
            )

            print(f"READY/UPDATE: {symbol}")
            print(f"  Bid: {book['bids'][0]}")
            print(f"  Ask: {book['asks'][0]}")

    finally:

        await manager.stop()


if __name__ == "__main__":
    asyncio.run(main())