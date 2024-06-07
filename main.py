#!/usr/bin/env python3
"""Main controller for the Atron Mining Expedition."""


import sys

from gui.main_controller import MainController

MIN_DENSITY = 0.1
MAX_DENSITY = 0.5

MIN_DIMENSION = 10
MAX_DIMENSION = 20

DEFAULT_TICKS = 10
DEFAULT_REFINED = 100
DEFAULT_REFRESH = 0.1  # refresh delay in seconds


def main():
    """Root window that contains fields for initial values."""
    MainController(DEFAULT_REFRESH).mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print("Exiting due to interrupt", file=sys.stderr)
