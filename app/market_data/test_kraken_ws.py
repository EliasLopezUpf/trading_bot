import asyncio

from app.exchanges.kraken import KrakenExchange
from app.market_data.order_book import LocalOrderBook


async def main():

    exchange = KrakenExchange()
    symbol = "BTC/USDT"

    local_book = LocalOrderBook()

    async for update in exchange.stream_order_book(symbol):

        if update["type"] == "snapshot":

            snapshot = exchange.parse_order_book_snapshot(update)

            local_book.load_snapshot(snapshot)

            book = local_book.get_order_book()

            print("Snapshot loaded!")
            print("Best bid:", book["bids"][0])
            print("Best ask:", book["asks"][0])

        elif update["type"] == "update":

            bids, asks = exchange.parse_order_book_update(update)

            local_book.apply_update(bids, asks)

            book = local_book.get_order_book()

            print("Update applied.")
            print("Best bid:", book["bids"][0])
            print("Best ask:", book["asks"][0])


try:
    asyncio.run(main())

except KeyboardInterrupt:
    print()
    print("Program stopped by user.")