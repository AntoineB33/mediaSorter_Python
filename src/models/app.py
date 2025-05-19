# app.py

import threading
from queue import Queue
from time import sleep

# Sync primitives
ortools_loaded = threading.Event()

# Task queue to manage ordered processing
task_queue = Queue()

def load_ortools():
    global find_valid_sortings
    from generate_sortings import find_valid_sortings
    ortools_loaded.set()

def call_find_valid_sortings_then_store_result(*args):
    ortools_loaded.wait()  # Wait for ortools to load
    
    # Create per-task synchronization and storage
    task_event = threading.Event()
    result_container = {'result': None}
    
    # Add task to queue
    task_queue.put((task_event, result_container))
    
    # Simulate long computation (replace with actual logic)
    result = args[0]
    print(f"Processing task with args: {args}")
    sleep(3)
    result_container['result'] = result
    task_event.set()

def display_last_result():
    # Retrieve and process the next task in order
    task_event, result_container = task_queue.get()
    task_event.wait()  # Wait for this specific task
    print("Result:", result_container['result'])

def main():
    # Start ortools loading in background
    threading.Thread(target=load_ortools, daemon=True).start()

    # ---- code A ----
    print("Code A running")

    # First sorting (non-blocking)
    threading.Thread(
        target=call_find_valid_sortings_then_store_result,
        args=('some_args',),
        daemon=True
    ).start()

    # ---- code B ----
    print("Code B running")

    # First display (non-blocking)
    threading.Thread(target=display_last_result, daemon=True).start()

    # ---- code C ----
    print("Code C running")

    # Second sorting (non-blocking)
    threading.Thread(
        target=call_find_valid_sortings_then_store_result,
        args=('other_args',),
        daemon=True
    ).start()

    # ---- code D ----
    print("Code D running")

    # Second display (non-blocking)
    threading.Thread(target=display_last_result, daemon=True).start()
    
    # ---- code E ----
    print("Code E running")
    sleep(10)
    print("Code E ending")

if __name__ == "__main__":
    main()