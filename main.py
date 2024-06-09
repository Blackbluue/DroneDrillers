#!/usr/bin/env python3
"""Main controller for the Atron Mining Expedition."""


import sys

from gui.main_controller import MainController

DEFAULT_REFRESH = 0.1  # refresh delay in seconds


def main():
    """Root window that contains fields for initial values."""
    MainController(DEFAULT_REFRESH).mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"Exiting due to interrupt: {e}", file=sys.stderr)
