import asyncio
import json
import ccxt
import websockets

from app.exchanges.base import Exchange

from app.market_data.synchronization import synchronize_order_book, is_next_update

class BinanceExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.binance({"timeout": 30000})
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def get_order_book_snapshot(self, symbol):
        return self.exchange.fetch_order_book(symbol, limit=1000)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets
    
    async def stream_order_books(self, symbols):

        streams = "/".join(
            f"{symbol.replace('/', '').lower()}@depth@100ms"
            for symbol in symbols
        )

        url = (
            "wss://stream.binance.com:9443/stream"
            f"?streams={streams}"
        )

        async with websockets.connect(url) as websocket:

            while True:
                message = await websocket.recv()

                data = json.loads(message)

                yield data["data"]
    
    
    async def initialize_order_book(self,symbol,queue,local_book):
        
        return await synchronize_order_book(
            self,
            symbol,
            queue,
            local_book
        )
    
    def process_order_book_update(self,update,local_book,last_update_id):

        U = update["U"]
        u = update["u"]

        if u <= last_update_id:
            return "old", last_update_id

        if not is_next_update(
            update,
            last_update_id
        ):
            return "gap", last_update_id

        local_book.apply_update(
            update["b"],
            update["a"]
        )
        return "ok", u
    
    def uses_sequence_numbers(self):
        return True
    
    def get_symbol_from_update(self, update):

        raw_symbol = update["s"]

        return raw_symbol[:-4] + "/" + raw_symbol[-4:]