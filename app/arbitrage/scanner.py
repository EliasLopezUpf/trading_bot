from itertools import combinations

from app.arbitrage.engine import find_best_arbitrage


class ArbitrageScanner:

    def __init__(
        self,
        market_data,
        fees,
        capital,
        slippage,
        min_net_return
    ):
        self.market_data = market_data
        self.fees = fees
        self.capital = capital
        self.slippage = slippage
        self.min_net_return = min_net_return

    def scan_symbol(self, symbol):

        available_exchanges = []

        for exchange_name in self.fees:

            try:
                self.market_data.get_order_book(
                    exchange_name,
                    symbol
                )

                available_exchanges.append(
                    exchange_name
                )

            except KeyError:
                continue

        exchange_pairs = combinations(
            available_exchanges,
            2
        )

        opportunities = []

        for exchange_a, exchange_b in exchange_pairs:

            orderbook_a = self.market_data.get_order_book(
                exchange_a,
                symbol
            )

            orderbook_b = self.market_data.get_order_book(
                exchange_b,
                symbol
            )

            result = find_best_arbitrage(
                symbol=symbol,

                exchange_a=exchange_a,
                exchange_b=exchange_b,

                orderbook_a=orderbook_a,
                orderbook_b=orderbook_b,

                capital=self.capital,

                fee_a=self.fees[exchange_a],
                fee_b=self.fees[exchange_b],

                min_net_return=self.min_net_return,

                slippage=self.slippage
            )

            if result is not None:
                opportunities.append(result["best"])

        if not opportunities:
            return None

        return max(
            opportunities,
            key=lambda opportunity: opportunity["net_return"]
        )