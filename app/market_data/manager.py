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
            name: {}
            for name in exchanges
        }

        self.order_books = {
            name: {}
            for name in exchanges
        }

        self.last_update_ids = {
            name: {}
            for name in exchanges
        }

        self.tasks = []
        
        self.market_update = asyncio.Queue(maxsize=1)
        
        self.init_semaphore = {
            "Binance": asyncio.Semaphore(5)
        }

    async def _collect(self, name, exchange, symbol):

        queue = self.queues[name][symbol]

        async for update in exchange.stream_order_book(symbol):
            await queue.put(update)
            

    async def _process(self,name,exchange,symbol):

        queue = self.queues[name][symbol]
        book = self.order_books[name][symbol]
        
        if name in self.init_semaphore:

            async with self.init_semaphore[name]:

                last_update_id = (
                    await exchange.initialize_order_book(
                        symbol,
                        queue,
                        book
                    )
                )

        else:

            last_update_id = (
                await exchange.initialize_order_book(
                    symbol,
                    queue,
                    book
                )
            )
        self.last_update_ids[name][symbol] = last_update_id
        self.ready[name][symbol] = True
        
        while True:

            update = await queue.get()

            if exchange.uses_sequence_numbers():
                result, new_last_update_id = (
                    exchange.process_order_book_update(
                        update,
                        book,
                        self.last_update_ids[name][symbol]
                    )
                )

                if result == "ok":
                    self.last_update_ids[name][symbol] = (
                        new_last_update_id
                    )
                    self._notify_market_update(name, symbol)

                elif result == "old":
                    continue

                elif result == "gap":

                    print(f"{name} {symbol}: GAP DETECTED")

                    last_update_id = (
                        await exchange.initialize_order_book(
                            symbol,
                            queue,
                            book
                        )
                    )

                    self.last_update_ids[name][symbol] = (
                        last_update_id
                    )
            else:

                exchange.process_order_book_update(
                    update,
                    book,
                    None
                )
                
                self._notify_market_update(name, symbol)

    async def start_symbol(self, symbol):

        for name, exchange in self.exchanges.items():

            if not exchange.supports_symbol(symbol):
                continue
            
            self.queues[name][symbol] = asyncio.Queue()

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
        
    async def wait_until_ready(self, symbols):

        while True:

            ready_count = 0
            total_supported = 0

            for name, exchange in self.exchanges.items():

                for symbol in symbols:

                    if not exchange.supports_symbol(symbol):
                        continue

                    total_supported += 1

                    if self.ready[name].get(symbol, False):
                        ready_count += 1

            # Start strategy once we have at least
            # one market ready on every exchange
            all_exchanges_ready = True

            for name, exchange in self.exchanges.items():

                exchange_has_ready_market = any(
                    self.ready[name].get(symbol, False)
                    for symbol in symbols
                    if exchange.supports_symbol(symbol)
                )

                if not exchange_has_ready_market:
                    all_exchanges_ready = False
                    break

            if all_exchanges_ready:
                return

            await asyncio.sleep(1)
                
            
    def _notify_market_update(self, exchange_name, symbol):

        if self.market_update.empty():

            try:
                self.market_update.put_nowait(
                    {
                        "exchange": exchange_name,
                        "symbol": symbol
                    }
                )
                #print("MARKET UPDATE SIGNAL SENT")
            except asyncio.QueueFull:
                pass
            
    def get_available_exchanges(self, symbol):

        available = []

        for name in self.exchanges:

            if symbol in self.order_books.get(name, {}):

                available.append(name)

        return available
    
    async def start_symbols(self, symbols):

        tasks = []

        for name, exchange in self.exchanges.items():

            task = asyncio.create_task(
                self.start_exchange(
                    name,
                    exchange,
                    symbols
                )
            )

            tasks.append(task)

        await asyncio.gather(*tasks)
        
    async def _collect_symbols(
    self,
    name,
    exchange,
    symbols
):

        async for update in exchange.stream_order_books(symbols):

            try:
                symbol = exchange.get_symbol_from_update(
                    update
                )
            except (KeyError, IndexError, TypeError):
                continue

            if symbol is None:
                continue

            if symbol not in self.queues[name]:
                continue
            

            await self.queues[name][symbol].put(update)
    
    async def start_exchange(
    self,
    name,
    exchange,
    symbols
):

        supported_symbols = [
            symbol
            for symbol in symbols
            if exchange.supports_symbol(symbol)
        ]

        if not supported_symbols:
            return

        for symbol in supported_symbols:

            self.queues[name][symbol] = asyncio.Queue()

            self.order_books[name][symbol] = (
                LocalOrderBook()
            )

            processor_task = asyncio.create_task(
                self._process(
                    name,
                    exchange,
                    symbol
                )
            )

            self.tasks.append(processor_task)

        collector_task = asyncio.create_task(
            self._collect_symbols(
                name,
                exchange,
                supported_symbols
            )
        )

        self.tasks.append(collector_task)