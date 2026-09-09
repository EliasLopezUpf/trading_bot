import ccxt
from app.exchanges.base import Exchange

class BinanceExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.binance()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)