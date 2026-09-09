import time

from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange
from app.exchanges.bybit import BybitExchange
from app.exchanges.coinbase import CoinbaseExchange
from app.exchanges.okx import OKXExchange

from app.market_data.collector import MarketDataCollector

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
    "DOGE/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "DOT/USDT",
    "LTC/USDT",
    "BCH/USDT",
    "UNI/USDT",
    "ATOM/USDT",
    "ETC/USDT",
    "FIL/USDT",
    "NEAR/USDT",
    "APT/USDT",
    "ARB/USDT",
    "OP/USDT",
    "SUI/USDT",
    "AAVE/USDT",
    "MATIC/USDT",
    "ALGO/USDT",
    "XLM/USDT",
    "TRX/USDT",
    "ICP/USDT",
    "INJ/USDT",
    "SEI/USDT",
    "HBAR/USDT",
    "PEPE/USDT"
]
CAPITAL = 100

fees = {
    "Binance": 0.0010,
    "Kraken": 0.0026,
    "Bybit": 0.0010,
    "OKX": 0.0035,
    "Coinbase": 0.0060
}

SLIPPAGE = 0.001
MIN_NET_RETURN = -0.3

SCAN_INTERVAL = 1


# =========================
# SETUP
# =========================
paper_trader = PaperTrader()

binance = BinanceExchange()
kraken = KrakenExchange()
bybit = BybitExchange()
coinbase = CoinbaseExchange()
okx = OKXExchange()

exchanges = {
    "Binance": binance,
    "Kraken": kraken,
    "Bybit": bybit,
    "Coinbase": coinbase,
    "OKX": okx
}

collector = MarketDataCollector(exchanges)
exchange_pairs = generate_exchange_pairs(exchanges.keys())

print("Starting arbitrage scanner...")
print(f"Symbols: {', '.join(SYMBOLS)}")
print(f"Exchanges: {', '.join(exchanges.keys())}")
print(f"Exchange pairs: {len(exchange_pairs)}")
print(f"Potential comparisons: {len(exchange_pairs) * len(SYMBOLS)}")
print(f"Capital: {CAPITAL} USDT")
print()



# =========================
# SCANNER
# =========================
scan_number = 0

while True:

    try:
        scan_number += 1

        opportunities_found = 0
        profitable_opportunities = 0
        best_opportunity = None
        comparisons = 0
        
        for symbol in SYMBOLS:
            # Get fresh market data
            order_books = collector.get_order_books(symbol)
            
            for exchange_a, exchange_b in exchange_pairs:
                if exchange_a not in order_books or exchange_b not in order_books:
                    continue
                comparisons += 1
                # Calculate arbitrage
                result = find_best_arbitrage(
                    symbol=symbol,
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
                    opportunities_found += 1
                    
                    best = result["best"]
                    
                    if (best_opportunity is None or best["net_return"] > best_opportunity["net_return"]):
                        best_opportunity = best

                    if best["profitable"]:
                        profitable_opportunities += 1
                        
                    #print(f"{exchange_a}-{exchange_b}: {symbol}")
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
        
        print()
        print("=" * 60)
        print(f"SCAN #{scan_number}")
        print("=" * 60)
        print(f"Symbols:              {len(SYMBOLS)}")
        print(f"Exchanges:            {len(exchanges)}")
        print(f"Potential comparisons: {len(exchange_pairs) * len(SYMBOLS)}")
        print(f"Actual comparisons:    {comparisons}")
        print(f"Opportunities found:   {opportunities_found}")
        print(f"Profitable:            {profitable_opportunities}")

        if best_opportunity is not None:
            print()
            print("BEST OPPORTUNITY")
            print(f"Symbol:       {best_opportunity['symbol']}")
            print(f"Buy:          {best_opportunity['buy_exchange']}")
            print(f"Sell:         {best_opportunity['sell_exchange']}")
            print(f"Net return:   {best_opportunity['net_return']:.4f}%")
            print(f"Net profit:   {best_opportunity['net_profit']:.4f} USDT")

        print("=" * 60)

        print("\nScanner stopped.")
        break

    except Exception as e:

        print(f"\nError: {e}")
        time.sleep(SCAN_INTERVAL)