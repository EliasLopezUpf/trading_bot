class MarketDataCollector:

    def __init__(self, exchanges):
        self.exchanges = exchanges

    def get_order_books(self, symbol):

        order_books = {}

        for name, exchange in self.exchanges.items():
            
            if not exchange.supports_symbol(symbol):
                continue

            order_books[name] = exchange.get_order_book(symbol)

        return order_books