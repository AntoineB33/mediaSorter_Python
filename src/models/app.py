# app.py

import threading
from time import sleep

# Sync primitives
ortools_loaded = threading.Event()
result_ready = threading.Event()

# Shared state
last_result = None

def load_ortools():
    global find_valid_sortings
    from generate_sortings import find_valid_sortings
    ortools_loaded.set()  # mark ortools as loaded

def call_find_valid_sortings_then_store_result(*args):
    ortools_loaded.wait()  # wait for ortools to load
    global last_result
    result = args[0]
    sleep(3)
    last_result = result
    result_ready.set()

def display_last_result():
    result_ready.wait()  # wait for sorting result
    print("Result:", last_result)


def main():
    # Start ortools loading in background
    threading.Thread(target=load_ortools, daemon=True).start()

    # ---- code A ----
    print("Code A running")

    # Run sorting (non-blocking)
    threading.Thread(target=call_find_valid_sortings_then_store_result, args=('some_args',), daemon=True).start()

    # ---- code B ----
    print("Code B running")

    # Display result (non-blocking)
    threading.Thread(target=display_last_result, daemon=True).start()

    # ---- code C ----
    print("Code C running")

    # Run another sorting (non-blocking)
    threading.Thread(target=call_find_valid_sortings_then_store_result, args=('other_args',), daemon=True).start()

    # ---- code D ----
    print("Code D running")

    # Display result (non-blocking)
    threading.Thread(target=display_last_result, daemon=True).start()
    
    # ---- code E ----
    print("Code E running")
    sleep(10)
    print("Code E ending")


if __name__ == "__main__":
    main()
