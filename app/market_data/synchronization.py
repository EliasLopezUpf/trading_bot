import asyncio

def find_sync_update(updates, last_update_id):

    for update in updates:

        U = update["U"]
        u = update["u"]

        if U <= last_update_id + 1 <= u:
            return update

    return None

def is_next_update(update, last_update_id):

    U = update["U"]
    u = update["u"]

    return U <= last_update_id + 1 <= u


def has_gap(update, last_update_id):

    U = update["U"]
    u = update["u"]

    if u <= last_update_id:
        return False

    return U > last_update_id + 1

async def synchronize_order_book(exchange, symbol, updates, local_book):

    while True:

        snapshot = await asyncio.to_thread(
            exchange.get_order_book_snapshot,
            symbol
        )

        last_update_id = snapshot["nonce"]

        local_book.load_snapshot(snapshot)

        print(
            f"Snapshot received: {last_update_id}"
        )

        while True:

            update = await updates.get()

            U = update["U"]
            u = update["u"]

            # Update happened before our snapshot
            if u <= last_update_id:
                continue

            # Correct synchronization event
            if is_next_update(update, last_update_id):

                local_book.apply_update(
                    update["b"],
                    update["a"]
                )

                last_update_id = u

                return last_update_id

            # The first useful event is already
            # ahead of the snapshot.
            if U > last_update_id + 1:

                print(
                    "Snapshot is too old. "
                    "Getting a new snapshot..."
                )

                break


