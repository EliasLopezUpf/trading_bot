import asyncio

from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange

from app.market_data.order_book import LocalOrderBook
from app.market_data.synchronization import (
    is_next_update,
    synchronize_order_book
)


async def main():

    binance = BinanceExchange()
    kraken = KrakenExchange()

    symbol = "BTC/USDT"

    binance_updates = asyncio.Queue()
    kraken_updates = asyncio.Queue()

    binance_book = LocalOrderBook()
    kraken_book = LocalOrderBook()
    
    
    async def collect_binance():

            async for update in binance.stream_order_book(symbol):
                await binance_updates.put(update)


    async def collect_kraken():

        async for update in kraken.stream_order_book(symbol):
            await kraken_updates.put(update)
            
            
    binance_ws_task = asyncio.create_task(
        collect_binance()
    )

    kraken_ws_task = asyncio.create_task(
        collect_kraken()
    )
    
    await asyncio.sleep(5)

    print("Synchronizing Binance...")

    binance_last_update_id = await synchronize_order_book(
        binance,
        symbol,
        binance_updates,
        binance_book
    )

    print("Binance synchronized!")
    print("Binance update ID:", binance_last_update_id)
    
    
    
    print("Synchronizing Kraken...")

    while True:

        update = await kraken_updates.get()

        if update["type"] == "snapshot":

            snapshot = kraken.parse_order_book_snapshot(
                update
            )

            kraken_book.load_snapshot(snapshot)

            break

    print("Kraken synchronized!")
    
    
    print()
    print("Both order books synchronized!")
    
    async def process_binance():

        nonlocal binance_last_update_id

        while True:

            update = await binance_updates.get()

            U = update["U"]
            u = update["u"]

            if u <= binance_last_update_id:
                continue

            if is_next_update(
                update,
                binance_last_update_id
            ):

                binance_book.apply_update(
                    update["b"],
                    update["a"]
                )

                binance_last_update_id = u

            else:

                print("BINANCE GAP DETECTED")

                binance_last_update_id = await synchronize_order_book(
                    binance,
                    symbol,
                    binance_updates,
                    binance_book
                )
                
                
    async def process_kraken():

        while True:

            update = await kraken_updates.get()

            if update["type"] != "update":
                continue

            bids, asks = kraken.parse_order_book_update(
                update
            )

            kraken_book.apply_update(
                bids,
                asks
            )
        
    binance_processor = asyncio.create_task(process_binance())
    kraken_processor = asyncio.create_task(process_kraken())

    async def monitor_books():

        while True:

            await asyncio.sleep(1)

            binance_data = binance_book.get_order_book()
            kraken_data = kraken_book.get_order_book()

            print()
            print(
                "BINANCE:",
                binance_data["bids"][0],
                binance_data["asks"][0]
            )

            print(
                "KRAKEN:",
                kraken_data["bids"][0],
                kraken_data["asks"][0]
            )
        
    monitor_task = asyncio.create_task(monitor_books())
    
    try:
        await asyncio.gather(binance_processor,kraken_processor,monitor_task)

    finally:
        tasks = [binance_ws_task,kraken_ws_task,binance_processor,kraken_processor,monitor_task]

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks,return_exceptions=True)
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program stopped.")