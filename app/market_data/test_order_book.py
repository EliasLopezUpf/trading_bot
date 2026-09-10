from app.market_data.order_book import LocalOrderBook


order_book = LocalOrderBook()

snapshot = {
    "bids": [
        [100, 1.0],
        [99, 2.0],
        [98, 3.0]
    ],
    "asks": [
        [101, 1.5],
        [102, 2.5],
        [103, 3.5]
    ]
}

order_book.load_snapshot(snapshot)

print("INITIAL BOOK")
print(order_book.get_order_book())


order_book.apply_update(
    bids=[
        [100, 0.5],
        [97, 4.0],
        [99, 0]
    ],
    asks=[
        [101, 2.0],
        [100.5, 1.0],
        [103, 0]
    ]
)

print()
print("UPDATED BOOK")
print(order_book.get_order_book())