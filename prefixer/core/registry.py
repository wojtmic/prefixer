from typing import Callable

task_registry = {}

def task(func: Callable):
    """Registers a function as a task"""
    task_registry[func.__name__] = func
    return func
