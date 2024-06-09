#!/usr/bin/env python3
"""Starting point for the game."""


import sys

from gui.main_controller import MainController

DEFAULT_REFRESH = 0.1  # refresh delay in seconds


def main():
    """Collect settings from the command line and start the game."""
    map_file = sys.argv.pop(1) if sys.argv[1:] else None
    MainController(DEFAULT_REFRESH, map_file).mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"Exiting due to interrupt: {e}", file=sys.stderr)
