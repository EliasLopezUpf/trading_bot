import asyncio

from app.exchanges.binance import BinanceExchange
from app.exchanges.kraken import KrakenExchange
from app.exchanges.coinbase import CoinbaseExchange
from app.exchanges.okx import OKXExchange
from app.exchanges.bybit import BybitExchange

from app.market_data.manager import MarketDataManager
from app.arbitrage.scanner import ArbitrageScanner


# =========================
# CONFIGURATION
# =========================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "ADA/USDT",
    "DOGE/USDT",
    "AVAX/USDT",
    "LINK/USDT",
    "DOT/USDT",
    "LTC/USDT",
    "BCH/USDT",
    "UNI/USDT",
    "ATOM/USDT",
    "ETC/USDT",
    "FIL/USDT",
    "NEAR/USDT",
    "APT/USDT",
    "ARB/USDT",
    "OP/USDT",
    "SUI/USDT",
    "AAVE/USDT",
    "ALGO/USDT",
    "XLM/USDT",
    "TRX/USDT",
    "ICP/USDT",
    "INJ/USDT",
    "SEI/USDT",
    "HBAR/USDT",
    "PEPE/USDT",
    "MATIC/USDT",
]

CAPITAL = 100

FEES = {
    "Binance": 0.0010,
    "Kraken": 0.0026,
    "Coinbase": 0.0060,
    "OKX": 0.0035,
    "Bybit": 0.0010,
}

SLIPPAGE = 0.001

MIN_NET_RETURN = -0.3


async def main():

    # =========================
    # EXCHANGES
    # =========================

    exchanges = {
        "Binance": BinanceExchange(),
        "Kraken": KrakenExchange(),
        "Coinbase": CoinbaseExchange(),
        "OKX": OKXExchange(),
        "Bybit": BybitExchange(),
    }


    # =========================
    # MARKET DATA
    # =========================

    manager = MarketDataManager(exchanges)

    await manager.start_symbols(SYMBOLS)

    print("Waiting for market data...")

    await manager.wait_until_ready(SYMBOLS)

    print("Market data ready.")
    
    # =========================
    # SHOW AVAILABLE MARKETS
    # =========================

    print()
    print("AVAILABLE MARKETS")
    print("-" * 60)

    for symbol in SYMBOLS:

        available = manager.get_available_exchanges(symbol)

        print(
            f"{symbol:<12}"
            f"{len(available)} exchanges: "
            f"{', '.join(available)}"
        )
        
    # =========================
    # ARBITRAGE SCANNER
    # =========================

    scanner = ArbitrageScanner(
                    market_data=manager,
                    fees=FEES,
                    capital=CAPITAL,
                    slippage=SLIPPAGE,
                    min_net_return=MIN_NET_RETURN
                )
    
    # =========================
    # STRATEGY LOOP
    # =========================

    try:

        while True:

            update = await manager.market_update.get()

            symbol = update["symbol"]
            exchange = update["exchange"]

            # Scan only the symbol that changed
            best = scanner.scan_symbol(symbol)

            # No valid arbitrage calculation
            if best is None:
                continue

            # =========================
            # OUTPUT
            # =========================

            print()
            print("=" * 60)
            print("LIVE ARBITRAGE CHECK")
            print("=" * 60)

            print(f"Market update: {exchange} {symbol}")
            print(f"Symbol:       {best['symbol']}")
            print(f"Buy:          {best['buy_exchange']}")
            print(f"Sell:         {best['sell_exchange']}")

            print()
            print(f"Amount:       "f"{best['assets_bought']:.8f}")
            print(f"Buy VWAP:     {best['buy_vwap']:.2f}")
            print(f"Sell VWAP:    {best['sell_vwap']:.2f}")

            print()
            print(f"Net profit:   {best['net_profit']:.4f} USDT")
            print(f"Net return:   {best['net_return']:.4f}%")
            print(f"Profitable:   "f"{best['profitable']}")

            print("=" * 60)

    finally:

        await manager.stop()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Program stopped.")