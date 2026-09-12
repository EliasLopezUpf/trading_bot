from math import isclose

from app.arbitrage.engine import (

    calculate_arbitrage,
    find_best_arbitrage,
)

from app.market_data.order_book import calculate_vwap, buy_with_budget, sell_assets, apply_slippage


def check(actual, expected, name, tolerance=1e-6):
    assert isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance), (
        f"{name}: expected {expected}, got {actual}"
    )


# ============================================================
# TEST 1 — VWAP
# ============================================================

def test_vwap():

    orders = [
        [100, 1],
        [101, 2],
        [102, 3],
    ]

    result = calculate_vwap(orders, 4)

    # 1 BTC at 100
    # 2 BTC at 101
    # 1 BTC at 102
    #
    # Total = 100 + 202 + 102 = 404
    # VWAP = 404 / 4 = 101

    check(result, 101.0, "VWAP")

    print("TEST 1 PASSED — VWAP")


# ============================================================
# TEST 2 — BUY WITH BUDGET
# ============================================================

def test_buy_with_budget():

    asks = [
        [100, 5],
        [110, 5],
    ]

    result = buy_with_budget(
        asks=asks,
        budget=1000,
        fee_rate=0
    )

    assert result is not None

    btc_bought, vwap, total_cost, fee = result

    # Buy:
    #
    # 5 BTC × 100 = 500
    # Remaining budget = 500
    #
    # 500 / 110 = 4.5454545 BTC
    #
    # Total BTC = 9.5454545

    expected_btc = 5 + (500 / 110)

    check(btc_bought, expected_btc, "BTC bought")
    check(total_cost, 1000, "Total cost")
    check(fee, 0, "Buy fee")

    expected_vwap = 1000 / expected_btc

    check(vwap, expected_vwap, "Buy VWAP")

    print("TEST 2 PASSED — buy_with_budget")


# ============================================================
# TEST 3 — SELL BTC
# ============================================================

def test_sell_assets():

    bids = [
        [102, 5],
        [101, 5],
    ]

    result = sell_assets(
        bids=bids,
        assets_amount=7,
        fee_rate=0
    )

    assert result is not None

    net_usdt, vwap, total_usdt, fee = result

    # Sell:
    #
    # 5 BTC × 102 = 510
    # 2 BTC × 101 = 202
    #
    # Total = 712 USDT

    check(total_usdt, 712, "Total revenue")
    check(net_usdt, 712, "Net revenue")
    check(fee, 0, "Sell fee")

    expected_vwap = 712 / 7

    check(vwap, expected_vwap, "Sell VWAP")

    print("TEST 3 PASSED — sell_assets")


# ============================================================
# TEST 4 — SLIPPAGE
# ============================================================

def test_slippage():

    buy_price = apply_slippage(
        price=100,
        slippage=0.01,
        side="buy"
    )

    sell_price = apply_slippage(
        price=100,
        slippage=0.01,
        side="sell"
    )

    # Buy becomes 1% more expensive
    check(buy_price, 101, "Buy slippage")

    # Sell becomes 1% cheaper
    check(sell_price, 99, "Sell slippage")

    print("TEST 4 PASSED — slippage")


# ============================================================
# TEST 5 — COMPLETE ARBITRAGE WITHOUT COSTS
# ============================================================

def test_arbitrage_without_costs():

    buy_orderbook = {
        "bids": [
            [99, 10]
        ],
        "asks": [
            [100, 10]
        ]
    }

    sell_orderbook = {
        "bids": [
            [102, 10]
        ],
        "asks": [
            [103, 10]
        ]
    }

    result = calculate_arbitrage(
        symbol="BTC/USDT",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        buy_orderbook=buy_orderbook,
        sell_orderbook=sell_orderbook,
        capital=1000,
        buy_fee=0,
        sell_fee=0,
        slippage=0
    )

    assert result is not None

    # Buy 10 BTC at 100 = 1000
    # Sell 10 BTC at 102 = 1020
    #
    # Profit = 20
    # Return = 2%

    check(result["assets_bought"], 10, "BTC bought")
    check(result["buy_vwap"], 100, "Buy VWAP")
    check(result["sell_vwap"], 102, "Sell VWAP")
    check(result["gross_revenue"], 1020, "Gross revenue")
    check(result["net_revenue"], 1020, "Net revenue")
    check(result["net_profit"], 20, "Net profit")
    check(result["net_return"], 2, "Net return")

    print("TEST 5 PASSED — complete arbitrage without costs")


# ============================================================
# TEST 6 — ARBITRAGE WITH FEES
# ============================================================

def test_arbitrage_with_fees():

    buy_orderbook = {
        "bids": [
            [99, 10]
        ],
        "asks": [
            [100, 10]
        ]
    }

    sell_orderbook = {
        "bids": [
            [102, 10]
        ],
        "asks": [
            [103, 10]
        ]
    }

    result = calculate_arbitrage(
        symbol="BTC/USDT",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        buy_orderbook=buy_orderbook,
        sell_orderbook=sell_orderbook,
        capital=1000,
        buy_fee=0.001,
        sell_fee=0.001,
        slippage=0
    )

    assert result is not None

    # We don't hard-code the expected profit here.
    # Instead, verify the important accounting relationships.

    assert result["buy_fee"] > 0
    assert result["sell_fee"] > 0

    assert result["net_profit"] < 20
    assert result["net_revenue"] < result["gross_revenue"]

    print("TEST 6 PASSED — arbitrage with fees")


# ============================================================
# TEST 7 — ARBITRAGE WITH FEES + SLIPPAGE
# ============================================================

def test_arbitrage_with_fees_and_slippage():

    buy_orderbook = {
        "bids": [
            [99, 10]
        ],
        "asks": [
            [100, 10]
        ]
    }

    sell_orderbook = {
        "bids": [
            [102, 10]
        ],
        "asks": [
            [103, 10]
        ]
    }

    result = calculate_arbitrage(
        symbol="BTC/USDT",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        buy_orderbook=buy_orderbook,
        sell_orderbook=sell_orderbook,
        capital=1000,
        buy_fee=0.001,
        sell_fee=0.001,
        slippage=0.001
    )

    assert result is not None

    # Costs should make the result worse than
    # the zero-cost case.

    assert result["buy_effective_price"] > result["buy_vwap"]
    assert result["sell_effective_price"] < result["sell_vwap"]

    assert result["net_profit"] < 20

    print("TEST 7 PASSED — fees + slippage")


# ============================================================
# TEST 8 — NO LIQUIDITY
# ============================================================

def test_insufficient_liquidity():

    buy_orderbook = {
        "bids": [
            [99, 1]
        ],
        "asks": [
            [100, 1]
        ]
    }

    sell_orderbook = {
        "bids": [
            [102, 1]
        ],
        "asks": [
            [103, 1]
        ]
    }

    result = calculate_arbitrage(
        symbol="BTC/USDT",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        buy_orderbook=buy_orderbook,
        sell_orderbook=sell_orderbook,
        capital=1000,
        buy_fee=0,
        sell_fee=0,
        slippage=0
    )

    # There isn't enough liquidity to spend the entire
    # 1000 USDT budget.

    assert result is None

    print("TEST 8 PASSED — insufficient liquidity")


# ============================================================
# TEST 9 — BOTH ARBITRAGE DIRECTIONS
# ============================================================

def test_find_best_arbitrage():

    orderbook_a = {
        "bids": [
            [99, 10]
        ],
        "asks": [
            [100, 10]
        ]
    }

    orderbook_b = {
        "bids": [
            [102, 10]
        ],
        "asks": [
            [103, 10]
        ]
    }

    result = find_best_arbitrage(
        symbol="BTC/USDT",
        exchange_a="ExchangeA",
        exchange_b="ExchangeB",
        orderbook_a=orderbook_a,
        orderbook_b=orderbook_b,
        capital=1000,
        fee_a=0,
        fee_b=0,
        min_net_return=0,
        slippage=0
    )

    assert result is not None

    best = result["best"]

    assert best["buy_exchange"] == "ExchangeA"
    assert best["sell_exchange"] == "ExchangeB"

    check(best["net_profit"], 20, "Best net profit")
    check(best["net_return"], 2, "Best net return")

    print("TEST 9 PASSED — best arbitrage direction")


# ============================================================
# TEST 10 — NEGATIVE ARBITRAGE
# ============================================================

def test_negative_arbitrage():

    buy_orderbook = {
        "bids": [
            [99, 10]
        ],
        "asks": [
            [102, 10]
        ]
    }

    sell_orderbook = {
        "bids": [
            [100, 10]
        ],
        "asks": [
            [101, 10]
        ]
    }

    result = calculate_arbitrage(
        symbol="BTC/USDT",
        buy_exchange="ExchangeA",
        sell_exchange="ExchangeB",
        buy_orderbook=buy_orderbook,
        sell_orderbook=sell_orderbook,
        capital=1000,
        buy_fee=0,
        sell_fee=0,
        slippage=0
    )

    assert result is not None

    # Buy at 102
    # Sell at 100
    # Therefore we lose money.

    assert result["net_profit"] < 0
    assert result["net_return"] < 0

    print("TEST 10 PASSED — negative arbitrage")


# ============================================================
# RUN ALL TESTS
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("ARBITRAGE ENGINE AUDIT")
    print("=" * 60)
    print()

    test_vwap()
    test_buy_with_budget()
    test_sell_assets()
    test_slippage()
    test_arbitrage_without_costs()
    test_arbitrage_with_fees()
    test_arbitrage_with_fees_and_slippage()
    test_insufficient_liquidity()
    test_find_best_arbitrage()
    test_negative_arbitrage()

    print()
    print("=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)