import time

from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange
from app.market_data.collector import MarketDataCollector
from app.exchanges.bybit import BybitExchange

from app.arbitrage.engine import find_best_arbitrage
from app.arbitrage.pairs import generate_exchange_pairs

from app.execution.paper_trader import PaperTrader


# =========================
# CONFIGURATION
# =========================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT"
]
CAPITAL = 100

fees = {
    "Binance": 0.0010,
    "Kraken": 0.0080,
    "Bybit": 0.0010
}

SLIPPAGE = 0.001
MIN_NET_RETURN = 0.0

SCAN_INTERVAL = 1


# =========================
# SETUP
# =========================
paper_trader = PaperTrader()

binance = BinanceExchange()
kraken = KrakenExchange()
bybit = BybitExchange()

exchanges = {
    "Binance": binance,
    "Kraken": kraken,
    "Bybit": bybit
}

collector = MarketDataCollector(exchanges)
exchange_pairs = generate_exchange_pairs(exchanges.keys())

print("Starting arbitrage scanner...")
print(f"Symbols: {', '.join(SYMBOLS)}")
print(f"Exchanges: {', '.join(exchanges.keys())}")
print(f"Capital: {CAPITAL} USDT")
print()



# =========================
# SCANNER
# =========================

while True:

    try:
        for symbol in SYMBOLS:
            # Get fresh market data
            order_books = collector.get_order_books(symbol)
            
            for exchange_a, exchange_b in exchange_pairs:

                # Calculate arbitrage
                result = find_best_arbitrage(
                    exchange_a=exchange_a,
                    exchange_b=exchange_b,
                    orderbook_a=order_books[exchange_a],
                    orderbook_b=order_books[exchange_b],
                    capital=CAPITAL,
                    fee_a=fees[exchange_a],
                    fee_b=fees[exchange_b],
                    min_net_return=MIN_NET_RETURN,
                    slippage=SLIPPAGE
                )

                # Only show profitable opportunities
                if result is not None:

                    best = result["best"]
                    print(f"{exchange_a}-{exchange_b}: {symbol}")
                    if best["net_return"] >= MIN_NET_RETURN:
                        
                        trade = paper_trader.execute(best,symbol)

                        print()
                        print("=" * 60)
                        print("📄 PAPER TRADE")
                        print("=" * 60)

                        print(f"Symbol:      {trade['symbol']}")
                        print(f"BUY:         {trade['buy_exchange']}")
                        print(f"SELL:        {trade['sell_exchange']}")
                        print(f"Capital:     {trade['capital']:.2f} USDT")
                        print(f"Amount:      {trade['assets_amount']:.8f}")
                        print(f"Profit:      {trade['profit']:.4f} USDT")
                        print(f"Return:      {trade['return_pct']:.4f}%")

                        print("=" * 60)
        time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:

        print("\nScanner stopped.")
        break

    except Exception as e:

        print(f"\nError: {e}")
        time.sleep(SCAN_INTERVAL)