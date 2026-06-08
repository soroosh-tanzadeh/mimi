import sys
import threading
import time
import itertools


class Spinner:
    def __init__(self, message="Thinking..."):
        """
        Initialize the Spinner with an optional message.

        Parameters
        ----------
        message : str
            The message to display while the spinner is running.

        """
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])

    def spin(self):
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.write("\033[2K\r") 
        sys.stdout.flush()

    def start(self):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()