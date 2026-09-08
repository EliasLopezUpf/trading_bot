import ccxt
from app.arbitrage.engine import find_best_arbitrage

# =========================
# FEES
# =========================

BINANCE_TAKER_FEE = 0.0010   
KRAKEN_TAKER_FEE = 0.0080    
MIN_NET_RETURN = 0.10
SLIPPAGE = 0.0010

# =========================
# EXCHANGES
# =========================

binance = ccxt.binance()
kraken = ccxt.kraken()

symbol = "BTC/USDT"


# =========================
# ORDERBOOKS
# =========================

binance_orderbook = binance.fetch_order_book(symbol)
kraken_orderbook = kraken.fetch_order_book(symbol)


# =========================
# ARBITRAGE
# =========================

capital = 100

result = find_best_arbitrage(
    exchange_a="Binance",
    exchange_b="Kraken",

    orderbook_a=binance_orderbook,
    orderbook_b=kraken_orderbook,

    capital=capital,

    fee_a=BINANCE_TAKER_FEE,
    fee_b=KRAKEN_TAKER_FEE,
    
    min_net_return=MIN_NET_RETURN,
    slippage=SLIPPAGE
)

# =========================
# PRINT RESULT
# =========================

if result is None:

    print("Couldn't calculate arbitrage.")

else:

    print()
    print("===== ARBITRAGE SCAN =====")

    for opportunity in result["all"]:

        print()
        print(
            opportunity["buy_exchange"],
            "→",
            opportunity["sell_exchange"]
        )

        print(
            "Net return:",
            opportunity["net_return"],
            "%"
        )

        print(
            "Net profit:",
            opportunity["net_profit"],
            "USDT"
        )

    print()
    print("===== BEST OPPORTUNITY =====")

    best = result["best"]

    print(
        "Buy:",
        best["buy_exchange"]
    )

    print(
        "Sell:",
        best["sell_exchange"]
    )

    print(
        "Net return:",
        best["net_return"],
        "%"
    )

    print(
        "Minimum required:",
        MIN_NET_RETURN,
        "%"
    )

    print()

    if best["profitable"]:
        print("STATUS: PROFITABLE")
    else:
        print("STATUS: NO TRADE")