class PaperTrader:

    def __init__(self, initial_usdt=5000, initial_assets=0):

        self.balances = {}

        self.initial_usdt = initial_usdt
        self.initial_assets = initial_assets

        self.trades = []

    def add_exchange(self, exchange):

        self.balances[exchange] = {
            "USDT": self.initial_usdt,
            "assets": {}
        }

    def get_balance(self, exchange, symbol):

        asset = symbol.split("/")[0]

        if asset not in self.balances[exchange]["assets"]:
            self.balances[exchange]["assets"][asset] = (
                self.initial_assets
            )

        return {
            "USDT": self.balances[exchange]["USDT"],
            asset: self.balances[exchange]["assets"][asset]
        }

    def execute_trade(self, opportunity):

        symbol = opportunity["symbol"]

        asset = symbol.split("/")[0]

        buy_exchange = opportunity["buy_exchange"]
        sell_exchange = opportunity["sell_exchange"]

        assets_bought = opportunity["assets_bought"]

        buy_cost = opportunity["buy_cost"]
        buy_fee = opportunity["buy_fee"]

        net_revenue = opportunity["net_revenue"]

        total_buy_cost = buy_cost + buy_fee

        # Check BUY exchange has enough USDT

        if self.balances[buy_exchange]["USDT"] < total_buy_cost:
            return False

        # Initialize asset balances if necessary

        if asset not in self.balances[buy_exchange]["assets"]:
            self.balances[buy_exchange]["assets"][asset] = (
                self.initial_assets
            )

        if asset not in self.balances[sell_exchange]["assets"]:
            self.balances[sell_exchange]["assets"][asset] = (
                self.initial_assets
            )

        # Check SELL exchange has enough asset

        if (
            self.balances[sell_exchange]["assets"][asset]
            < assets_bought
        ):
            return False

        # ------------------------------------------------
        # BUY LEG
        # ------------------------------------------------

        self.balances[buy_exchange]["USDT"] -= total_buy_cost

        self.balances[buy_exchange]["assets"][asset] += (
            assets_bought
        )

        # ------------------------------------------------
        # SELL LEG
        # ------------------------------------------------

        self.balances[sell_exchange]["assets"][asset] -= (
            assets_bought
        )

        self.balances[sell_exchange]["USDT"] += net_revenue

        # ------------------------------------------------
        # P&L
        # ------------------------------------------------

        profit = net_revenue - total_buy_cost

        trade = {
            "symbol": symbol,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "assets_bought": assets_bought,
            "buy_cost": total_buy_cost,
            "sell_revenue": net_revenue,
            "profit": profit
        }

        self.trades.append(trade)

        return True

    def get_total_usdt(self):

        total = 0

        for exchange in self.balances:

            total += self.balances[exchange]["USDT"]

        return total

    def get_asset_balance(self, exchange, symbol):

        asset = symbol.split("/")[0]

        if asset not in self.balances[exchange]["assets"]:
            self.balances[exchange]["assets"][asset] = (
                self.initial_assets
            )

        return self.balances[exchange]["assets"][asset]

    def get_trade_count(self):

        return len(self.trades)

    def get_total_pnl(self):
        return sum(
            trade["profit"]
            for trade in self.trades
        )


    def get_profitable_trades(self):
        return sum(
            1
            for trade in self.trades
            if trade["profit"] > 0
        )


    def get_unprofitable_trades(self):
        return sum(
            1
            for trade in self.trades
            if trade["profit"] <= 0
        )


    def get_portfolio_summary(self):
        return {
            "total_usdt": self.get_total_usdt(),
            "total_pnl": self.get_total_pnl(),
            "trade_count": self.get_trade_count(),
            "profitable_trades": self.get_profitable_trades(),
            "unprofitable_trades": self.get_unprofitable_trades(),
        }
        
    def get_portfolio_value(self, market_data):
        total_value = self.get_total_usdt()

        for exchange in self.balances:

            for asset, amount in self.balances[exchange]["assets"].items():

                if amount <= 0:
                    continue

                symbol = f"{asset}/USDT"

                try:
                    orderbook = market_data.get_order_book(
                        exchange,
                        symbol
                    )

                    if not orderbook["bids"]:
                        continue

                    current_price = orderbook["bids"][0][0]

                    total_value += amount * current_price

                except Exception:
                    continue

        return total_value