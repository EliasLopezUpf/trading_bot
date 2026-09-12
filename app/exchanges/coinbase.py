import ccxt
from app.exchanges.base import Exchange

import json
import websockets

class CoinbaseExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.coinbase({"timeout": 30000})
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets
    
    async def stream_order_books(self, symbols):

        product_ids = [
            symbol.replace("/", "-")
            for symbol in symbols
        ]

        url = "wss://advanced-trade-ws.coinbase.com"

        async with websockets.connect(url) as websocket:

            subscribe_message = {
                "type": "subscribe",
                "product_ids": product_ids,
                "channel": "level2"
            }

            await websocket.send(
                json.dumps(subscribe_message)
            )

            while True:

                message = await websocket.recv()

                data = json.loads(message)

                yield data
                
    def parse_order_book_snapshot(self, data):

        updates = data["events"][0]["updates"]

        bids = []
        asks = []

        for update in updates:

            price = float(update["price_level"])
            quantity = float(update["new_quantity"])

            if update["side"] == "bid":
                bids.append([price, quantity])

            elif update["side"] == "offer":
                asks.append([price, quantity])

        return {
            "bids": bids,
            "asks": asks
        }
        
    def parse_order_book_update(self, data):

        updates = data["events"][0]["updates"]

        bids = []
        asks = []

        for update in updates:

            price = float(update["price_level"])
            quantity = float(update["new_quantity"])

            if update["side"] == "bid":
                bids.append([price, quantity])

            elif update["side"] == "offer":
                asks.append([price, quantity])

        return bids, asks
    
    async def initialize_order_book(
    self,
    symbol,
    queue,
    local_book
):

        # Wait for snapshot
        while True:

            update = await queue.get()

            if update.get("channel") != "l2_data":
                continue

            event = update["events"][0]

            if event.get("type") != "snapshot":
                continue

            snapshot = self.parse_order_book_snapshot(
                update
            )

            local_book.load_snapshot(snapshot)

            break

        # Wait for first live update
        while True:

            update = await queue.get()

            if update.get("channel") != "l2_data":
                continue

            event = update["events"][0]

            if event.get("type") != "update":
                continue

            bids, asks = self.parse_order_book_update(
                update
            )

            local_book.apply_update(
                bids,
                asks
            )

            return update["sequence_num"]
    
    def process_order_book_update(
    self,
    update,
    local_book,
    last_sequence
):

        if update.get("channel") != "l2_data":
            return "ignore", last_sequence

        event = update["events"][0]

        if event["type"] != "update":
            return "ignore", last_sequence

        bids = []
        asks = []

        for change in event["updates"]:

            price = float(change["price_level"])
            quantity = float(change["new_quantity"])

            if change["side"] == "bid":
                bids.append([price, quantity])

            elif change["side"] == "offer":
                asks.append([price, quantity])

        local_book.apply_update(
            bids,
            asks
        )

        return "ok", update["sequence_num"]
    
    def uses_sequence_numbers(self):
        return True
    
    def get_symbol_from_update(self, update):

        if update.get("channel") != "l2_data":
            return None

        if not update.get("events"):
            return None

        event = update["events"][0]

        if not event.get("updates"):
            return None

        return event["product_id"].replace("-", "/")