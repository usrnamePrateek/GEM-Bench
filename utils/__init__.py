"""Timer utility for tracking execution time of pipeline stages."""

import time
from contextlib import contextmanager
from datetime import timedelta


class Timer:
    """Simple timer to track execution time of code blocks.
    
    Usage:
        timer = Timer()
        
        # As context manager:
        with timer.track("generation"):
            do_generation()
        
        with timer.track("evaluation"):
            do_evaluation()
        
        timer.summary()
    """

    def __init__(self):
        self._records: dict[str, float] = {}
        self._start_time: float = time.time()

    @contextmanager
    def track(self, label: str):
        """Context manager to time a labeled block."""
        print(f"\n⏱  [{label}] started...")
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            self._records[label] = elapsed
            print(f"⏱  [{label}] finished in {self._format(elapsed)}")

    def summary(self):
        """Print a summary of all tracked stages."""
        total = time.time() - self._start_time
        print("\n" + "=" * 50)
        print("⏱  TIMING SUMMARY")
        print("=" * 50)
        for label, elapsed in self._records.items():
            print(f"  {label:<30s} {self._format(elapsed):>12s}")
        print("-" * 50)
        print(f"  {'Total wall time':<30s} {self._format(total):>12s}")
        print("=" * 50)

    @staticmethod
    def _format(seconds: float) -> str:
        """Format seconds into human-readable string."""
        td = timedelta(seconds=int(seconds))
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes, secs = divmod(int(seconds), 60)
            return f"{minutes}m {secs}s"
        else:
            hours, remainder = divmod(int(seconds), 3600)
            minutes, secs = divmod(remainder, 60)
            return f"{hours}h {minutes}m {secs}s"
