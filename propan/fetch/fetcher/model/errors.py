from typing import Optional


class MaxRetriesExceeded(Exception):
    def __init__(self, max_tries: int, message: Optional[str] = None):
        if message is None:
            message = f"Max retries '{max_tries}' exceeded"
        super().__init__(message)
