import ccxt
from app.exchanges.base import Exchange

import json
import websockets

class OKXExchange(Exchange):
    

    def __init__(self):
        self.exchange = ccxt.okx({"timeout": 30000})
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets
    
    def parse_order_book_snapshot(self, data):

        book_data = data["data"][0]

        bids = [
            [float(level[0]), float(level[1])]
            for level in book_data["bids"]
        ]

        asks = [
            [float(level[0]), float(level[1])]
            for level in book_data["asks"]
        ]

        return {
            "bids": bids,
            "asks": asks
        }
        
    def parse_order_book_update(self, data):

        book_data = data["data"][0]

        bids = [
            [float(level[0]), float(level[1])]
            for level in book_data["bids"]
        ]

        asks = [
            [float(level[0]), float(level[1])]
            for level in book_data["asks"]
        ]

        return bids, asks
    
    async def stream_order_books(self, symbols):

        url = "wss://ws.okx.com:8443/ws/v5/public"

        async with websockets.connect(url) as websocket:

            subscribe_message = {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "books",
                        "instId": symbol.replace("/", "-")
                    }
                    for symbol in symbols
                ]
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

            if update.get("action") != "snapshot":
                continue

            snapshot = self.parse_order_book_snapshot(
                update
            )

            local_book.load_snapshot(snapshot)

            sequence = update["data"][0]["seqId"]

            return sequence
    
    def process_order_book_update(
    self,
    update,
    local_book,
    last_seq_id
):

        if update.get("action") != "update":
            return "ignore", last_seq_id

        book_data = update["data"][0]

        seq_id = book_data["seqId"]
        prev_seq_id = book_data["prevSeqId"]

        if seq_id <= last_seq_id:
            return "old", last_seq_id

        if prev_seq_id != last_seq_id:
            return "gap", last_seq_id

        bids, asks = self.parse_order_book_update(
            update
        )

        local_book.apply_update(
            bids,
            asks
        )

        return "ok", seq_id
    
    def uses_sequence_numbers(self):
        return True
    
    def get_symbol_from_update(self, update):

        if not update.get("arg"):
            return None

        if not update["arg"].get("instId"):
            return None

        return update["arg"]["instId"].replace("-", "/")