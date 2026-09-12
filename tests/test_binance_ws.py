# app/market_data/test/test_binance_multi.py

import asyncio

from app.exchanges.binance import BinanceExchange
from app.market_data.order_book import LocalOrderBook


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

    exchange = BinanceExchange()

    queues = {
        symbol: asyncio.Queue()
        for symbol in SYMBOLS
        if exchange.supports_symbol(symbol)
    }

    books = {
        symbol: LocalOrderBook()
        for symbol in queues
    }

    initialized = set()

    print("=" * 60)
    print("BINANCE MULTI-SYMBOL TEST")
    print("=" * 60)

    print(f"Requested: {len(SYMBOLS)}")
    print(f"Supported: {len(queues)}")

    async for update in exchange.stream_order_books(SYMBOLS):

        symbol = exchange.get_symbol_from_update(update)

        if symbol not in queues:
            continue

        await queues[symbol].put(update)

        # Initialize from the first update only for this test.
        #
        # We are deliberately NOT using the full manager yet.
        if symbol not in initialized:

            book = books[symbol]

            # For Binance, the actual REST snapshot
            # is still needed for correct synchronization.
            snapshot = await asyncio.to_thread(
                exchange.get_order_book_snapshot,
                symbol
            )

            book.load_snapshot(snapshot)

            initialized.add(symbol)

            print(
                f"READY: {symbol}"
            )

            print(
                f"  Bid: {book.get_order_book()['bids'][0]}"
            )

            print(
                f"  Ask: {book.get_order_book()['asks'][0]}"
            )

        if len(initialized) == len(queues):

            print()
            print("=" * 60)
            print("ALL BINANCE SYMBOLS INITIALIZED")
            print("=" * 60)

            break


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")