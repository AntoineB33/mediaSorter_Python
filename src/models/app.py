# app.py

import threading
from queue import Queue, Empty
from time import sleep

# Sync primitives
ortools_loaded = threading.Event()
shutdown_signal = threading.Event()

# Separate queues for tasks and results
tasks_queue = Queue()
results_queue = Queue()

def load_ortools():
    global find_valid_sortings
    from generate_sortings import find_valid_sortings
    ortools_loaded.set()

def task_worker():
    """Process tasks sequentially and populate results queue"""
    while not shutdown_signal.is_set():
        try:
            args = tasks_queue.get(timeout=0.1)
            print(f"Processing task with args: {args}")
            sleep(3)  # Simulate computation
            results_queue.put(args[0])  # Store actual result
            tasks_queue.task_done()
        except Empty:
            continue

def call_find_valid_sortings_then_store_result(*args):
    ortools_loaded.wait()
    tasks_queue.put(args)

def display_last_result():
    while not shutdown_signal.is_set():
        try:
            result = results_queue.get(timeout=0.1)
            print("Result:", result)
            results_queue.task_done()
        except Empty:
            continue

def main():
    # Start critical components as non-daemon threads
    ortools_thread = threading.Thread(target=load_ortools)
    worker_thread = threading.Thread(target=task_worker)
    display_thread = threading.Thread(target=display_last_result)

    ortools_thread.start()
    worker_thread.start()
    display_thread.start()

    # ---- Execution Flow ----
    print("Code A running")
    threading.Thread(
        target=call_find_valid_sortings_then_store_result,
        args=('some_args',),
        daemon=True
    ).start()

    print("Code B running")
    threading.Thread(
        target=call_find_valid_sortings_then_store_result,
        args=('other_args',),
        daemon=True
    ).start()

    print("Code C running")
    threading.Thread(target=display_last_result, daemon=True).start()

    print("Code D running")
    threading.Thread(target=display_last_result, daemon=True).start()
    
    print("Code E running")
    
    # Wait for all tasks to complete
    ortools_loaded.wait()
    tasks_queue.join()
    results_queue.join()
    
    # Signal shutdown to worker threads
    shutdown_signal.set()
    
    # Wait for non-daemon threads to finish
    worker_thread.join()
    display_thread.join()
    ortools_thread.join()
    
    print("Code E ending")

if __name__ == "__main__":
    main()