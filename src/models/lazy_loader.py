# src/models/lazy_loader.py
import threading
from concurrent.futures import Future
from ortools.sat.python import cp_model  # This is the "heavy" import

# A Future that will be completed once loading is done
ortools_ready = Future()

def preload_ortools():
    try:
        _ = cp_model.CpModel()  # Dummy instantiation to trigger loading
        ortools_ready.set_result(True)
    except Exception as e:
        ortools_ready.set_exception(e)

# Start loading in background
threading.Thread(target=preload_ortools, daemon=True).start()
