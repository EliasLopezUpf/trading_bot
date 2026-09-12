import asyncio

from app.market_data.order_book import LocalOrderBook
from app.market_data.synchronization import (
    is_next_update,
    synchronize_order_book,
)


class MarketDataManager:

    def __init__(self, exchanges):
        self.exchanges = exchanges
        
        self.ready = {
            name: {}
            for name in exchanges
        }

        self.queues = {
            name: asyncio.Queue()
            for name in exchanges
        }

        self.order_books = {
            name: {}
            for name in exchanges
        }

        self.last_update_ids = {}

        self.tasks = []
        
        self.market_update = asyncio.Queue(maxsize=1)

    async def _collect(self, name, exchange, symbol):

        queue = self.queues[name]

        async for update in exchange.stream_order_book(symbol):
            await queue.put(update)
            

    async def _process(self,name,exchange,symbol):

        queue = self.queues[name]
        book = self.order_books[name][symbol]

        last_update_id = await exchange.initialize_order_book(
            symbol,
            queue,
            book
        )

        self.last_update_ids[name] = last_update_id
        self.ready[name][symbol] = True

        while True:

            update = await queue.get()

            if exchange.uses_sequence_numbers():
                result, new_last_update_id = (
                    exchange.process_order_book_update(
                        update,
                        book,
                        self.last_update_ids[name]
                    )
                )

                if result == "ok":
                    self.last_update_ids[name] = (
                        new_last_update_id
                    )
                    self._notify_market_update()

                elif result == "old":
                    continue

                elif result == "gap":

                    print(f"{name}: GAP DETECTED")

                    last_update_id = (
                        await exchange.initialize_order_book(
                            symbol,
                            queue,
                            book
                        )
                    )

                    self.last_update_ids[name] = (
                        last_update_id
                    )
            else:

                exchange.process_order_book_update(
                    update,
                    book,
                    None
                )
                
                self._notify_market_update()

    async def start_symbol(self, symbol):

        for name, exchange in self.exchanges.items():

            if not exchange.supports_symbol(symbol):
                continue
            
            self.queues[name] = asyncio.Queue()

            self.order_books[name][symbol] = LocalOrderBook()

            collector_task = asyncio.create_task(
                self._collect(
                    name,
                    exchange,
                    symbol
                )
            )

            processor_task = asyncio.create_task(
                self._process(
                    name,
                    exchange,
                    symbol
                )
            )
            self.tasks.append(collector_task)
            self.tasks.append(processor_task)

    def get_order_book(self, exchange_name, symbol):

        return self.order_books[exchange_name][symbol].get_order_book()

    async def stop(self):

        for task in self.tasks:
            task.cancel()

        await asyncio.gather(
            *self.tasks,
            return_exceptions=True
        )
        
    async def wait_until_ready(self, symbol):

        while True:

            all_ready = True

            for name, exchange in self.exchanges.items():

                if not exchange.supports_symbol(symbol):
                    continue

                if not self.ready[name].get(symbol, False):
                    all_ready = False
                    break

            if all_ready:
                return

            await asyncio.sleep(0.01)
            
            
    def _notify_market_update(self):

        if self.market_update.empty():

            try:
                self.market_update.put_nowait(True)
                print("MARKET UPDATE SIGNAL SENT")
            except asyncio.QueueFull:
                pass