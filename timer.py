"""Easy way to start timing and get current elapsed"""

from time import time


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    """Simple timer designed for maximum brevity.  Clock starts the
    moment the class is instantiated."""

    def __init__(self, sig_digits=0):
        self._digits = sig_digits
        self._start_time = time()
        self._last = 0


    def elapsed(self):
        """Return the elapsed time in whole seconds."""
        self._last = round(time() - self._start_time, self._digits)
        return self._last

    def __repr__(self) -> str:
        return str(self.elapsed())

    def stop(self):
        """There's no reason to stop a timer since no work happens if no methods are called."""

    def last(self):
        """Returns previous elapsed time, not current elapsed time."""
        return self._last

    # Aliases
    e = elapsed
