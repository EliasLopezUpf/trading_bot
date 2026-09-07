import ccxt
from app.market_data.order_book import calculate_vwap, buy_with_budget


#GET TOP BIDS/ASKS
binance = ccxt.binance()
kraken = ccxt.kraken()

symbol = "BTC/USDT"

binance_orderbook = binance.fetch_order_book(symbol)
kraken_orderbook = kraken.fetch_order_book(symbol)

binance_bid = binance_orderbook["bids"][0][0]
binance_ask = binance_orderbook["asks"][0][0]

kraken_bid = kraken_orderbook["bids"][0][0]
kraken_ask = kraken_orderbook["asks"][0][0]

print("BINANCE")
print("Best bid:", binance_orderbook["bids"][0])
print("Best ask:", binance_orderbook["asks"][0])

print()

print("KRAKEN")
print("Best bid:", kraken_orderbook["bids"][0])
print("Best ask:", kraken_orderbook["asks"][0])



#AMOUNT OF BTC WE CAN BUY
target_amount = 0.01

binance_buy_vwap = calculate_vwap(
    binance_orderbook["asks"],
    target_amount
)

kraken_sell_vwap = calculate_vwap(
    kraken_orderbook["bids"],
    target_amount
)

print()
print("VWAP FOR", target_amount, "BTC")

print("Binance buy VWAP:", binance_buy_vwap)
print("Kraken sell VWAP:", kraken_sell_vwap)


#USD DISPONIBLE TO GET BTC
capital = 100

buy_result = buy_with_budget(
    binance_orderbook["asks"],
    capital
)

btc_bought, buy_vwap = buy_result

print()
print("BUY ON BINANCE")
print("Capital:", capital, "USDT")
print("BTC bought:", btc_bought)
print("VWAP:", buy_vwap)