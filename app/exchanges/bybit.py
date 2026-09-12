import ccxt
from app.exchanges.base import Exchange

import json
import websockets

class BybitExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.bybit({"timeout": 30000})
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets
    
    def parse_order_book_snapshot(self, data):

        book_data = data["data"]

        bids = [
            [float(level[0]), float(level[1])]
            for level in book_data["b"]
        ]

        asks = [
            [float(level[0]), float(level[1])]
            for level in book_data["a"]
        ]

        return {
            "bids": bids,
            "asks": asks
        }
        
    def parse_order_book_update(self, data):

        book_data = data["data"]

        bids = [
            [float(level[0]), float(level[1])]
            for level in book_data["b"]
        ]

        asks = [
            [float(level[0]), float(level[1])]
            for level in book_data["a"]
        ]

        return bids, asks
    
    async def stream_order_books(self, symbols):
        url = "wss://stream.bybit.com/v5/public/spot"

        async with websockets.connect(url) as websocket:

            topics = [
                f"orderbook.50.{symbol.replace('/', '')}"
                for symbol in symbols
            ]

            for i in range(0, len(topics), 10):

                batch = topics[i:i + 10]

                subscribe_message = {
                    "op": "subscribe",
                    "args": batch
                }

                await websocket.send(
                    json.dumps(subscribe_message)
                )

            while True:

                message = await websocket.recv()

                data = json.loads(message)

                yield data
                
    async def initialize_order_book(
    self,
    symbol,
    queue,
    local_book
):

        while True:

            update = await queue.get()

            if update.get("type") != "snapshot":
                continue

            snapshot = self.parse_order_book_snapshot(
                update
            )

            local_book.load_snapshot(snapshot)

            return update["data"]["u"]
    
    def process_order_book_update(
    self,
    update,
    local_book,
    last_update_id
):

        if update.get("type") != "delta":
            return "ignore", last_update_id

        update_id = update["data"]["u"]

        if update_id <= last_update_id:
            return "old", last_update_id

        if update_id != last_update_id + 1:
            return "gap", last_update_id

        bids, asks = self.parse_order_book_update(
            update
        )

        local_book.apply_update(
            bids,
            asks
        )

        return "ok", update_id
    
    def uses_sequence_numbers(self):
       return True
   
    def get_symbol_from_update(self, update):

        if not update.get("data"):
            return None

        raw_symbol = update["data"].get("s")

        if not raw_symbol:
            return None

        return raw_symbol[:-4] + "/" + raw_symbol[-4:]