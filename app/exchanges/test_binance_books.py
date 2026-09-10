import asyncio

from app.exchanges.binance import BinanceExchange
from app.market_data.order_book import LocalOrderBook


async def main():

    exchange = BinanceExchange()
    symbol = "BTC/USDT"

    local_book = LocalOrderBook()

    # WebSocket stream
    websocket = exchange.stream_order_book(symbol)

    # Buffer for incoming updates
    updates = []

    async def collect_updates():

        async for update in websocket:
            updates.append(update)

    # Start WebSocket in background
    ws_task = asyncio.create_task(
        collect_updates()
    )

    # Give WebSocket a moment to connect
    await asyncio.sleep(0.1)

    # Get REST snapshot while WebSocket
    # continues receiving updates
    print("Getting REST snapshot...")

    snapshot = await asyncio.to_thread(exchange.get_order_book_snapshot,symbol)

    last_update_id = snapshot["nonce"]

    print("Snapshot nonce:", last_update_id)

    # Give the WebSocket a moment to receive
    # anything that arrived during snapshot request
    await asyncio.sleep(0.1)

    print("Buffered updates:", len(updates))

    # Load snapshot
    local_book.load_snapshot(snapshot)

    # Find synchronization event
    sync_update = None

    for update in updates:

        U = update["U"]
        u = update["u"]

        if U <= last_update_id + 1 <= u:
            sync_update = update
            break

    if sync_update is None:

        print()
        print("Could not synchronize.")

        ws_task.cancel()

        return

    print()
    print("SYNC SUCCESSFUL")

    print("U:", sync_update["U"])
    print("u:", sync_update["u"])

    # Apply the synchronization update
    local_book.apply_update(
        sync_update["b"],
        sync_update["a"]
    )

    print()
    print("LOCAL BOOK")

    book = local_book.get_order_book()

    print("Best bid:", book["bids"][0])
    print("Best ask:", book["asks"][0])

    # Stop websocket
    ws_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())