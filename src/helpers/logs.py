import time
from datetime import datetime


# a wrapper to print starting time and end time of a function, with starting and ending messages
def log_message(start_message=None, end_message=None):
    def wrapper(func, *args, **kwargs):
        def inner(*args, **kwargs):
            start = time.time()
            print()
            if start_message:
                print(start_message)
            else:
                print(f"Starting {func.__name__} at {datetime.now()}")
            result = func(*args, **kwargs)
            end = time.time()
            if end_message:
                print(end_message)
            else:
                print(f"Finished {func.__name__} at {datetime.now()}")    
            print(f"Total time: {end - start:.4f} seconds")
            return result
        return inner
    return wrapper
