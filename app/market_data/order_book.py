def calculate_vwap(orders, target_amount):
    remaining = target_amount
    total_cost = 0

    for order in orders:
        price = order[0]
        amount = order[1]
        
        amount_to_take = min(amount, remaining)

        total_cost += amount_to_take * price
        remaining -= amount_to_take

        if remaining <= 0:
            break

    if remaining > 0:
        return None

    return total_cost / target_amount

def buy_with_budget(asks, budget, fee_rate=0):
    #reserve money for trading fee
    available_budget = budget / (1 + fee_rate)
    
    remaining_budget = available_budget
    total_assets = 0
    total_cost = 0

    for order in asks:
        price = order[0]
        amount = order[1]

        cost_of_order = price * amount

        if cost_of_order <= remaining_budget:
            assets_bought = amount
            cost = cost_of_order

        else:
            assets_bought = remaining_budget / price
            cost = remaining_budget

        total_assets += assets_bought
        total_cost += cost
        remaining_budget -= cost

        if remaining_budget <= 0:
            break

    if total_assets == 0:
        return None
    
    # Check if the order book had enough liquidity
    if remaining_budget > 0:
        return None

    vwap = total_cost / total_assets
    fee = total_cost * fee_rate

    return total_assets, vwap, total_cost, fee


def sell_assets(bids, assets_amount, fee_rate=0):
    remaining_assets = assets_amount
    total_usdt = 0

    for order in bids:
        price = order[0]
        amount = order[1]

        assets_to_sell = min(amount, remaining_assets)

        total_usdt += assets_to_sell * price
        remaining_assets -= assets_to_sell

        if remaining_assets <= 0:
            break

    if remaining_assets > 0:
        return None
    
    fee = total_usdt * fee_rate
    net_usdt = total_usdt - fee

    vwap = total_usdt / assets_amount

    return net_usdt, vwap, total_usdt, fee


def apply_slippage(price, slippage, side):
    if side == "buy":
        return price * (1 + slippage)

    elif side == "sell":
        return price * (1 - slippage)

    else:
        raise ValueError("side must be 'buy' or 'sell'")