import asyncio

task_queue = asyncio.Queue()

async def add_task(task_name):
    await task_queue.put(task_name)
    print(f"Task added: {task_name}")

async def task_worker():
    while True:
        task = await task_queue.get()
        print(f"Processing {task}")
        await asyncio.sleep(5)  # Simulate async work
        print(f"Completed {task}")
        task_queue.task_done()

async def main():
    # Start the background worker
    asyncio.create_task(task_worker())

    # Add tasks
    await add_task("Task 1")
    await asyncio.sleep(1)
    await add_task("Task 2")
    print("Tasks submitted to the background.")

    # Optionally wait for tasks to complete before exiting
    await task_queue.join()

if __name__ == "__main__":
    asyncio.run(main())
    import time
    print("hey")
    time.sleep(10)  # Keep the script running to observe background processing
