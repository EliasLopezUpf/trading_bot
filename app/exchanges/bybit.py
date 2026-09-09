import ccxt
from app.exchanges.base import Exchange

class BybitExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.bybit()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)