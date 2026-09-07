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

def buy_with_budget(asks, budget):
    remaining_budget = budget
    total_btc = 0
    total_cost = 0

    for order in asks:
        price = order[0]
        amount = order[1]

        cost_of_order = price * amount

        if cost_of_order <= remaining_budget:
            btc_bought = amount
            cost = cost_of_order

        else:
            btc_bought = remaining_budget / price
            cost = remaining_budget

        total_btc += btc_bought
        total_cost += cost
        remaining_budget -= cost

        if remaining_budget <= 0:
            break

    if total_btc == 0:
        return None

    vwap = total_cost / total_btc

    return total_btc, vwap