import asyncio
from asyncio import Queue
from typing import TypeVar, Generic, Callable, Awaitable, Optional
''' 
    Creates a class that repeatedly executes "loop" as an asynchronous task.
    This will execute until the task is cancelled.
'''  
Input = TypeVar('Input')
class ContinuousTask(Generic[Input]):
    def __init__(self, queue: Queue[Input], task_fn: Callable[[Input], Awaitable[None]]):
        self._task_fn = task_fn 
        self._queue = queue
        self._loop = asyncio.create_task(self.run())

    async def run(self):
        try:
            while not self._queue.empty():
                item = await self._queue.get()
                await self._task_fn(item)
                self._queue.task_done()
                await asyncio.sleep(0.1)  # Adjust the sleep time as needed
        except asyncio.CancelledError:
            print("ContinuousTask cancelled.")
            while not self._queue.empty():
                item = await self._queue.get()
                self._queue.task_done()
        finally:
            print("ContinuousTask finished.")

    async def put(self, item: Input):
        '''
        Puts an item into the queue for processing.
        '''
        await self._queue.put(item)
    
    async def close(self):
        '''
        Cancels the task and waits for it to finish.
        '''
        if self._loop:
            self._loop.cancel()
            try:
                await self._loop
            except asyncio.CancelledError:
                pass
    
    async def join(self):
        '''
        Waits for all items in the queue to be processed.
        '''
        await self._queue.join()
        print("All items processed.")