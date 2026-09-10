import asyncio

from app.exchanges.binance import BinanceExchange
from app.market_data.order_book import LocalOrderBook

from app.market_data.synchronization import (
    is_next_update,
    synchronize_order_book
)

async def main():

    # 1. Start WebSocket and buffer updates
    exchange = BinanceExchange()
    symbol = "BTC/USDT"

    updates = asyncio.Queue()
    
    async def collect_updates():

        async for update in exchange.stream_order_book(symbol):
            
            print(f"Received WS update: {update['U']} -> {update['u']}")
            await updates.put(update)

    # Start receiving WebSocket updates
    ws_task = asyncio.create_task(
        collect_updates()
    )

    # Give the WebSocket time to connect
    await asyncio.sleep(5)

    print()
    print("Synchronizing order book...")

    local_book = LocalOrderBook()

    last_update_id = await synchronize_order_book(
        exchange,
        symbol,
        updates,
        local_book
    )

    print("Book synchronized!")
    print("Last update ID:", last_update_id)
    
    try:

        while True:

            update = await updates.get()

            U = update["U"]
            u = update["u"]

            print(f"Received live update: {U} -> {u}")

            if u <= last_update_id:

                print("Old update. Ignoring.")

            elif is_next_update(update, last_update_id):

                local_book.apply_update(
                    update["b"],
                    update["a"]
                )

                last_update_id = u

                print("Update applied.")

            else:
                print("GAP DETECTED!")
                print("Resynchronizing...")

                last_update_id = await synchronize_order_book(
                    exchange,
                    symbol,
                    updates,
                    local_book
                )

                print("Resynchronized!")
                print("New last update ID:", last_update_id)
    finally:
        ws_task.cancel()


try:
    asyncio.run(main())

except KeyboardInterrupt:
    print()
    print("Program stopped by user.")