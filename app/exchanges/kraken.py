import ccxt
from app.exchanges.base import Exchange

class KrakenExchange(Exchange):

    def __init__(self):
        self.exchange = ccxt.kraken()
        self.exchange.load_markets()

    def get_order_book(self, symbol):
        return self.exchange.fetch_order_book(symbol)
    
    def supports_symbol(self, symbol):
        return symbol in self.exchange.markets