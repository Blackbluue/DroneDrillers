#!/usr/bin/env python3
"""Starting point for the game."""


import argparse
import sys

from gui.main_controller import MainController


def get_args() -> argparse.Namespace:
    """Get command line arguments."""
    parser = argparse.ArgumentParser(description="Atron Mining Expedition")
    # command line arguments are for testing. eventually will move these
    # to a configuration file
    parser.add_argument(
        "map_file",
        metavar="map_file",
        type=str,
        nargs="?",
        help="Map file to load",
    )
    parser.add_argument(
        "-r",
        "--refresh",
        type=float,
        default=0.1,
        help="Refresh delay in seconds (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    """Collect settings from the command line and start the game."""
    args = get_args()
    map_file: str | None = args.map_file
    print(f"Starting game with map file: {map_file}")
    MainController(args.refresh, map_file).mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"Exiting due to interrupt: {e}", file=sys.stderr)
