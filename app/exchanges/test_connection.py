import ccxt
import time
from app.arbitrage.engine import find_best_arbitrage

# =========================
# CONFIGURATION
# =========================

BINANCE_TAKER_FEE = 0.0010   
KRAKEN_TAKER_FEE = 0.0080    
MIN_NET_RETURN = 0.0
SLIPPAGE = 0.0010
SCAN_INTERVAL = 1
CAPITAL = 100

# =========================
# EXCHANGES
# =========================

binance = ccxt.binance()
kraken = ccxt.kraken()

symbol = "BTC/USDT"


# =========================
# CONTINUOUS SCANNER
# =========================

print("Starting arbitrage scanner...")
print(f"Symbol: {symbol}")
print(f"Capital: {CAPITAL} USDT")
print(f"Minimum return: {MIN_NET_RETURN}%")
print()

while True:

    try:

        # =========================
        # GET FRESH ORDER BOOKS
        # =========================

        binance_orderbook = binance.fetch_order_book(symbol)
        kraken_orderbook = kraken.fetch_order_book(symbol)


        # =========================
        # CALCULATE ARBITRAGE
        # =========================

        result = find_best_arbitrage(
            exchange_a="Binance",
            exchange_b="Kraken",
            orderbook_a=binance_orderbook,
            orderbook_b=kraken_orderbook,
            capital=CAPITAL,
            fee_a=BINANCE_TAKER_FEE,
            fee_b=KRAKEN_TAKER_FEE,
            min_net_return=MIN_NET_RETURN,
            slippage=SLIPPAGE
        )


        # =========================
        # ONLY PRINT OPPORTUNITIES
        # =========================

        if result is not None:

            best = result["best"]

            if best["net_return"] >= MIN_NET_RETURN:

                print()
                print("=" * 60)
                print("🚨 ARBITRAGE OPPORTUNITY")
                print("=" * 60)

                print(
                    f"BUY:        {best['buy_exchange']}"
                )

                print(
                    f"SELL:       {best['sell_exchange']}"
                )

                print(
                    f"Capital:    {best['capital']:.2f} USDT"
                )

                print(
                    f"BTC:        {best['btc_bought']:.8f}"
                )

                print(
                    f"Buy VWAP:   {best['buy_vwap']:.2f}"
                )

                print(
                    f"Sell VWAP:  {best['sell_vwap']:.2f}"
                )

                print(
                    f"Net profit: +{best['net_profit']:.4f} USDT"
                )

                print(
                    f"Net return: +{best['net_return']:.4f}%"
                )

                print("=" * 60)


        # =========================
        # WAIT
        # =========================

        time.sleep(SCAN_INTERVAL)


    except KeyboardInterrupt:

        print()
        print("Scanner stopped.")

        break


    except Exception as e:

        print()
        print("Error:", e)
        print("Retrying...")
        time.sleep(SCAN_INTERVAL)