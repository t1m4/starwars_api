import asyncio
import functools
import logging
import time
from typing import Any, Callable, List, Set, Union


def async_timed():
    """Decorator that check how much time an async function will execute"""

    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f"starting {func} with args {args} {kwargs}")
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f"finished {func} in {total:.4f} second(s)")

        return wrapped

    return wrapper


async def cancel_tasks(pending_tasks):
    """Cancel all given tasks"""
    for pending_task in pending_tasks:
        pending_task.cancel()
    return []


async def execute(awaitables: List[asyncio.Task], result_callback: Callable):
    """Execute tasks with wait() until first exception. If there is some pending tasks, turn them off."""
    results = []
    done_tasks, pending_tasks = await asyncio.wait(awaitables, return_when=asyncio.FIRST_EXCEPTION)
    await cancel_tasks(pending_tasks)
    for done_task in done_tasks:
        if done_task.exception() is None:
            result = result_callback(done_task.result())
            results.append(result)
        else:
            logging.error("Request got an exception", exc_info=done_task.exception())
    return results


async def execute_until_first_exception(awaitables: List[asyncio.Task], result_callback: Callable):
    """Execute tasks with wait(return_when=asyncio.FIRST_COMPLETED).
    If there is some exception cancel all pending tasks and return resutls immediately"""
    results = []
    pending_tasks: Union[List, Set] = awaitables
    while pending_tasks:
        done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
        for done_task in done_tasks:
            if done_task.exception() is None:
                result = result_callback(done_task.result())
                results.append(result)
            else:
                logging.error("Request got an exception", exc_info=done_task.exception())
                pending_tasks = await cancel_tasks(pending_tasks)
                break
    return results
