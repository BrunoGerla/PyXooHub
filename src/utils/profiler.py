import time
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

from utils.logger import get_logger

logger = get_logger("Profiler")

P = ParamSpec('P')
R = TypeVar('R')

def time_it(threshold_ms: float = 5.0) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    A decorator that profiles a function and logs a debug message ONLY if 
    the execution time exceeds the specified threshold in milliseconds.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_time: float = time.perf_counter()

            result = func(*args, **kwargs)

            duration_ms: float = (time.perf_counter() - start_time) * 1000.0

            # Log if it exceeds the threshold
            if duration_ms > threshold_ms:
                logger.debug(
                    f"SLOW EXECUTION: '{func.__name__}' took {duration_ms:.2f} ms"
                )
                
            return result
        return wrapper
    return decorator