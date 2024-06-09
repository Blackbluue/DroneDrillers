#!/usr/bin/env python3
"""Starting point for the game."""


import argparse
import os.path
import sys

from gui.main_controller import MainController


def get_args() -> argparse.Namespace:
    """Get command line arguments."""
    parser = argparse.ArgumentParser(description="Atron Mining Expedition")
    # command line arguments are for testing. eventually will move these
    # to a configuration file
    parser.add_argument(
        "map_directory",
        metavar="map_directory",
        type=str,
        nargs="?",
        help="Directory to find map files",
    )
    parser.add_argument(
        "-r",
        "--refresh",
        type=float,
        default=0.1,
        help="Refresh delay in seconds (default: %(default)s)",
    )
    args = parser.parse_args()
    if args.map_directory and not os.path.isdir(args.map_directory):
        parser.error(f"Map directory {args.map_directory} does not exist")
    return args


def main() -> None:
    """Collect settings from the command line and start the game."""
    args = get_args()
    map_directory: str | None = args.map_directory
    print(f"Starting game with map directory: {map_directory}")
    MainController(args.refresh, map_directory).mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print(f"Exiting due to interrupt: {e}", file=sys.stderr)
