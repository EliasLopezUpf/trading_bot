from app.market_data.order_book import buy_with_budget, sell_assets, apply_slippage


def calculate_arbitrage(
    buy_exchange,
    sell_exchange,
    buy_orderbook,
    sell_orderbook,
    capital,
    buy_fee,
    sell_fee,
    slippage
):
    """
    Simulates buying on one exchange and selling on another.
    """

    # BUY
    buy_result = buy_with_budget(
        buy_orderbook["asks"],
        capital,
        buy_fee
    )

    if buy_result is None:
        return None

    assets_bought, buy_vwap, buy_cost, buy_fee_amount = buy_result
    
    buy_effective_price = apply_slippage(buy_vwap, slippage, "buy")
    
    assets_bought_after_slippage = (buy_cost / buy_effective_price)
    
    # SELL
    sell_result = sell_assets(
        sell_orderbook["bids"],
        assets_bought_after_slippage,
        sell_fee
    )

    if sell_result is None:
        return None

    _, sell_vwap, _, _ = sell_result
    
    sell_effective_price = apply_slippage(sell_vwap, slippage, "sell")
    
    #Revenue before sell fee
    gross_revenue = assets_bought_after_slippage*sell_effective_price
    
    # Sell fee
    sell_fee_amount = gross_revenue* sell_fee
    
    net_revenue = gross_revenue - sell_fee_amount
    
    # PROFIT
    net_profit = net_revenue - capital
    net_return = (net_profit / capital) * 100

    return {
        "buy_exchange": buy_exchange,
        "sell_exchange": sell_exchange,

        "capital": capital,

        "assets_bought": assets_bought_after_slippage,

        "buy_vwap": buy_vwap,
        "buy_effective_price": buy_effective_price,
        "buy_cost": buy_cost,
        "buy_fee": buy_fee_amount,

        "sell_vwap": sell_vwap,
        "sell_effective_price": sell_effective_price,
        "gross_revenue": gross_revenue,
        "sell_fee": sell_fee_amount,

        "net_revenue": net_revenue,

        "net_profit": net_profit,
        "net_return": net_return
    }
    
    
def find_best_arbitrage(
    exchange_a,
    exchange_b,
    orderbook_a,
    orderbook_b,
    capital,
    fee_a,
    fee_b,
    min_net_return,
    slippage
):
    """
    Checks both arbitrage directions and returns the best one.
    """

    # Direction 1:
    # A → B
    opportunity_ab = calculate_arbitrage(
        buy_exchange=exchange_a,
        sell_exchange=exchange_b,
        buy_orderbook=orderbook_a,
        sell_orderbook=orderbook_b,
        capital=capital,
        buy_fee=fee_a,
        sell_fee=fee_b,
        slippage=slippage
    )

    # Direction 2:
    # B → A
    opportunity_ba = calculate_arbitrage(
        buy_exchange=exchange_b,
        sell_exchange=exchange_a,
        buy_orderbook=orderbook_b,
        sell_orderbook=orderbook_a,
        capital=capital,
        buy_fee=fee_b,
        sell_fee=fee_a,
        slippage=slippage
    )

    opportunities = [
        opportunity
        for opportunity in [opportunity_ab, opportunity_ba]
        if opportunity is not None
    ]

    if not opportunities:
        return None

    # Select the opportunity with the highest net return
    best_opportunity = max(
        opportunities,
        key=lambda opportunity: opportunity["net_return"]
    )
    
    best_opportunity["profitable"] = (
        best_opportunity["net_return"] >= min_net_return
    )

    return {
        "best": best_opportunity,
        "all": opportunities
    }