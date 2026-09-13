from app.execution.paper_trader import PaperTrader


def print_result(test_name, result):
    print(f"{test_name}: {'PASS' if result else 'FAIL'}")


# ============================================================
# TEST 1 — Initial balances
# ============================================================

trader = PaperTrader(
    initial_usdt=5000,
    initial_assets=1
)

trader.add_exchange("Binance")
trader.add_exchange("Kraken")

balance_binance = trader.get_balance(
    "Binance",
    "BTC/USDT"
)

balance_kraken = trader.get_balance(
    "Kraken",
    "BTC/USDT"
)

result = (
    balance_binance["USDT"] == 5000
    and balance_binance["BTC"] == 1
    and balance_kraken["USDT"] == 5000
    and balance_kraken["BTC"] == 1
)

print_result("TEST 1 - Initial balances", result)


# ============================================================
# TEST 2 — Profitable trade
# ============================================================

opportunity = {
    "symbol": "BTC/USDT",
    "buy_exchange": "Binance",
    "sell_exchange": "Kraken",

    "assets_bought": 0.01,

    "buy_cost": 1000,
    "buy_fee": 1,

    "net_revenue": 1050
}

result = trader.execute_trade(opportunity)

print_result("TEST 2 - Profitable trade", result)


# ============================================================
# TEST 3 — Unprofitable trade
# ============================================================

opportunity = {
    "symbol": "BTC/USDT",
    "buy_exchange": "Binance",
    "sell_exchange": "Kraken",

    "assets_bought": 0.01,

    "buy_cost": 1000,
    "buy_fee": 1,

    "net_revenue": 950
}

result = trader.execute_trade(opportunity)

print_result("TEST 3 - Unprofitable trade", result)


# ============================================================
# TEST 4 — Insufficient USDT
# ============================================================

opportunity = {
    "symbol": "BTC/USDT",
    "buy_exchange": "Binance",
    "sell_exchange": "Kraken",

    "assets_bought": 0.01,

    "buy_cost": 6000,
    "buy_fee": 6,

    "net_revenue": 6100
}

result = not trader.execute_trade(opportunity)

print_result("TEST 4 - Insufficient USDT", result)


# ============================================================
# TEST 5 — Insufficient BTC
# ============================================================

# Create a new trader with ZERO BTC inventory

trader_no_btc = PaperTrader(
    initial_usdt=5000,
    initial_assets=0
)

trader_no_btc.add_exchange("Binance")
trader_no_btc.add_exchange("Kraken")


opportunity = {
    "symbol": "BTC/USDT",
    "buy_exchange": "Binance",
    "sell_exchange": "Kraken",

    "assets_bought": 0.01,

    "buy_cost": 1000,
    "buy_fee": 1,

    "net_revenue": 1050
}

result = not trader_no_btc.execute_trade(opportunity)

print_result("TEST 5 - Insufficient BTC", result)


# ============================================================
# TEST 6 — Total USDT
# ============================================================

total_usdt = trader.get_total_usdt()

result = total_usdt > 0

print_result("TEST 6 - Total USDT", result)


# ============================================================
# TEST 7 — Multiple symbols
# ============================================================

trader_multi = PaperTrader(
    initial_usdt=5000,
    initial_assets=1
)

trader_multi.add_exchange("Binance")
trader_multi.add_exchange("Kraken")


btc_opportunity = {
    "symbol": "BTC/USDT",
    "buy_exchange": "Binance",
    "sell_exchange": "Kraken",

    "assets_bought": 0.01,

    "buy_cost": 1000,
    "buy_fee": 1,

    "net_revenue": 1050
}


eth_opportunity = {
    "symbol": "ETH/USDT",
    "buy_exchange": "Kraken",
    "sell_exchange": "Binance",

    "assets_bought": 0.5,

    "buy_cost": 1000,
    "buy_fee": 1,

    "net_revenue": 1050
}


btc_result = trader_multi.execute_trade(btc_opportunity)
eth_result = trader_multi.execute_trade(eth_opportunity)


btc_balance = trader_multi.get_asset_balance(
    "Binance",
    "BTC/USDT"
)

eth_balance = trader_multi.get_asset_balance(
    "Binance",
    "ETH/USDT"
)

result = (
    btc_result
    and eth_result
    and btc_balance == 1.01
    and eth_balance == 0.5
)

print_result("TEST 7 - Multiple symbols", result)


# ============================================================
# FINAL
# ============================================================

print("\nALL PAPER TRADER TESTS COMPLETED")