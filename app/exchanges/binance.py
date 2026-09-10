import asyncio
import json
import ccxt
import websockets

from app.exchanges.base import Exchange

class BinanceExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.binance()
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def get_order_book_snapshot(self, symbol):
        return self.exchange.fetch_order_book(symbol, limit=1000)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets
    
    async def stream_order_book(self, symbol):
        symbol = symbol.lower().replace("/", "")

        url = f"wss://stream.binance.com:9443/ws/{symbol}@depth"

        async with websockets.connect(url) as websocket:

            while True:
                message = await websocket.recv()

                data = json.loads(message)

                yield data