from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange
from app.market_data.collector import MarketDataCollector


binance = BinanceExchange()
kraken = KrakenExchange()

collector = MarketDataCollector({
    "Binance": binance,
    "Kraken": kraken
})


symbol = "BTC/USDT"

order_books = collector.get_order_books(symbol)


for exchange, orderbook in order_books.items():

    print()
    print(exchange)

    print("Best bid:", orderbook["bids"][0])
    print("Best ask:", orderbook["asks"][0])