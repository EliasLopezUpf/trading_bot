import asyncio

from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange

from app.market_data.manager import MarketDataManager

from app.arbitrage.engine import find_best_arbitrage


async def main():

    binance = BinanceExchange()
    kraken = KrakenExchange()

    exchanges = {
        "Binance": binance,
        "Kraken": kraken
    }

    manager = MarketDataManager(exchanges)

    symbol = "BTC/USDT"

    await manager.start_symbol(symbol)

    print("Waiting for market data...")

    await manager.wait_until_ready(symbol)

    print("Market data manager started.")

    try:

                while True:

                    await asyncio.sleep(1)

                    binance_book = manager.get_order_book(
                        "Binance",
                        symbol
                    )

                    kraken_book = manager.get_order_book(
                        "Kraken",
                        symbol
                    )

                    # =========================
                    # BINANCE → KRAKEN
                    # =========================

                    result = find_best_arbitrage(
                        symbol=symbol,
                        exchange_a="Binance",
                        exchange_b="Kraken",
                        orderbook_a=binance_book,
                        orderbook_b=kraken_book,
                        capital=100,
                        fee_a=0.0010,
                        fee_b=0.0026,
                        min_net_return=-0.5,
                        slippage=0.001
                    )

                    # =========================
                    # DISPLAY
                    # =========================

                    if result is None:
                        continue

                    best = result["best"]

                    print()
                    print("=" * 60)
                    print("LIVE ARBITRAGE")
                    print("=" * 60)

                    print(f"Symbol:      {best['symbol']}")
                    print(f"BUY:         {best['buy_exchange']}")
                    print(f"SELL:        {best['sell_exchange']}")
                    print(f"Amount:      {best['assets_bought']:.8f}")
                    print(f"Buy VWAP:    {best['buy_vwap']:.2f}")
                    print(f"Sell VWAP:   {best['sell_vwap']:.2f}")
                    print(f"Net profit:  {best['net_profit']:.4f} USDT")
                    print(f"Net return:  {best['net_return']:.4f}%")
                    print("=" * 60)

    finally:

        await manager.stop()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Program stopped.")