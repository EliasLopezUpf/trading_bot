import asyncio

from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange

from app.market_data.manager import MarketDataManager

from app.arbitrage.engine import find_best_arbitrage


# =========================
# CONFIGURATION
# =========================

SYMBOL = "BTC/USDT"

CAPITAL = 100

FEES = {
    "Binance": 0.0010,
    "Kraken": 0.0026,
}

SLIPPAGE = 0.001

MIN_NET_RETURN = -0.6


async def main():

    # =========================
    # EXCHANGES
    # =========================

    exchanges = {
        "Binance": BinanceExchange(),
        "Kraken": KrakenExchange(),
    }


    # =========================
    # MARKET DATA
    # =========================

    manager = MarketDataManager(exchanges)

    await manager.start_symbol(SYMBOL)

    print("Waiting for market data...")

    await manager.wait_until_ready(SYMBOL)

    print("Market data ready.")


    # =========================
    # MAIN LOOP
    # =========================

    try:

        while True:

            print("WAITING FOR MARKET UPDATE...")
            await manager.market_update.get()
            print("MARKET UPDATE RECEIVED!")

            binance_book = manager.get_order_book(
                "Binance",
                SYMBOL
            )

            kraken_book = manager.get_order_book(
                "Kraken",
                SYMBOL
            )


            # =========================
            # ARBITRAGE
            # =========================

            result = find_best_arbitrage(
                symbol=SYMBOL,

                exchange_a="Binance",
                exchange_b="Kraken",

                orderbook_a=binance_book,
                orderbook_b=kraken_book,

                capital=CAPITAL,

                fee_a=FEES["Binance"],
                fee_b=FEES["Kraken"],

                min_net_return=MIN_NET_RETURN,

                slippage=SLIPPAGE
            )


            if result is None:
                continue


            best = result["best"]


            # =========================
            # OUTPUT
            # =========================

            print()
            print("=" * 60)
            print("LIVE ARBITRAGE CHECK")
            print("=" * 60)

            print(f"Symbol:       {best['symbol']}")
            print(f"Buy:          {best['buy_exchange']}")
            print(f"Sell:         {best['sell_exchange']}")

            print()
            print(f"Buy VWAP:     {best['buy_vwap']:.2f}")
            print(f"Sell VWAP:    {best['sell_vwap']:.2f}")

            print()
            print(f"Net profit:   {best['net_profit']:.4f} USDT")
            print(f"Net return:   {best['net_return']:.4f}%")

            print("=" * 60)

    finally:

        await manager.stop()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Program stopped.")