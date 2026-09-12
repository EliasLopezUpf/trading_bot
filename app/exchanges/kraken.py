import ccxt
from app.exchanges.base import Exchange

import json
import websockets

class KrakenExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.kraken()
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets
    
    async def stream_order_book(self, symbol):

        pair = symbol.replace("/", "/")

        url = "wss://ws.kraken.com/v2"

        async with websockets.connect(url) as websocket:

            subscribe_message = {
                "method": "subscribe",
                "params": {
                    "channel": "book",
                    "symbol": [pair],
                    "depth": 10
                }
            }

            await websocket.send(
                json.dumps(subscribe_message)
            )

            while True:

                message = await websocket.recv()

                data = json.loads(message)
                
                if data.get("channel") != "book":
                    continue

                yield data
                
    def parse_order_book_update(self, data):

        book_data = data["data"][0]

        bids = [
            [level["price"], level["qty"]]
            for level in book_data["bids"]
        ]

        asks = [
            [level["price"], level["qty"]]
            for level in book_data["asks"]
        ]

        return bids, asks
    
    def parse_order_book_snapshot(self, data):

        book_data = data["data"][0]

        return {
            "bids": [
                [level["price"], level["qty"]]
                for level in book_data["bids"]
            ],
            "asks": [
                [level["price"], level["qty"]]
                for level in book_data["asks"]
            ]
        }
        
        
    async def initialize_order_book(self,symbol,queue,local_book):

        while True:

            update = await queue.get()

            if update["type"] != "snapshot":
                continue

            snapshot = self.parse_order_book_snapshot(
                update
            )

            local_book.load_snapshot(snapshot)

            return None
        
    def process_order_book_update(self,update,local_book,last_update_id=None):

        if update["type"] != "update":
            return "ignore", None

        bids, asks = self.parse_order_book_update(
            update
        )

        local_book.apply_update(
            bids,
            asks
        )
        
        return "ok", None
    
    def uses_sequence_numbers(self):
        return False