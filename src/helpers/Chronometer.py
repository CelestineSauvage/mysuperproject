import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class Chronometer:
    # Class for calculate the processing time of any called method

    def timeit(self, func):
        @wraps(func)
        def timeit_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = end_time - start_time
            logger.info(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
            return result
        return timeit_wrapper