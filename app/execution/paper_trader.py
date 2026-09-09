class PaperTrader:

    def __init__(self):
        self.trades = []

    def execute(self, opportunity, symbol):

        trade = {
            "symbol": symbol,
            "buy_exchange": opportunity["buy_exchange"],
            "sell_exchange": opportunity["sell_exchange"],
            "capital": opportunity["capital"],
            "assets_amount": opportunity["assets_amount"],
            "buy_price": opportunity["buy_effective_price"],
            "sell_price": opportunity["sell_effective_price"],
            "profit": opportunity["net_profit"],
            "return_pct": opportunity["net_return"]
        }

        self.trades.append(trade)

        return trade