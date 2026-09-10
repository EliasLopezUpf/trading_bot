import asyncio

from app.exchanges.binance import BinanceExchange


async def main():

    exchange = BinanceExchange()

    updates = []

    async def collect_updates():

        async for update in exchange.stream_order_book("BTC/USDT"):

            updates.append(update)

            print(
                f"WS update received: "
                f"{update['U']} -> {update['u']}"
            )

    # Start WebSocket in the background
    ws_task = asyncio.create_task(
        collect_updates()
    )

    # Wait a little so the WebSocket can connect
    await asyncio.sleep(2)

    print()
    print("Requesting REST snapshot...")

    # IMPORTANT:
    # CCXT is synchronous, so run it in a thread.
    snapshot = await asyncio.to_thread(
        exchange.get_order_book_snapshot,
        "BTC/USDT"
    )

    print("REST snapshot received.")
    print("Snapshot nonce:", snapshot["nonce"])

    # Give WebSocket a little more time
    await asyncio.sleep(2)

    print()
    print("Total buffered updates:", len(updates))

    # Stop WebSocket
    ws_task.cancel()


asyncio.run(main())