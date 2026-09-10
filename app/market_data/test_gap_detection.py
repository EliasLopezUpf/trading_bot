from app.market_data.synchronization import is_next_update


last_update_id = 105

updates = [
    {"U": 106, "u": 110},
    # We intentionally remove 111 -> 115
    {"U": 116, "u": 120},
]

for update in updates:

    U = update["U"]
    u = update["u"]

    print(f"Checking update: {U} -> {u}")

    if u <= last_update_id:
        print("Old update. Ignoring.")

    elif is_next_update(update, last_update_id):
        last_update_id = u
        print("Update is valid.")
        print("New last_update_id:", last_update_id)

    else:
        print("GAP DETECTED!")

    print()