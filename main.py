#!/usr/bin/env python3
import sys


def main():
    pass


if __name__ == "__main__":
    try:
        main()
    except (Exception, GeneratorExit, KeyboardInterrupt) as e:
        name = type(e).__name__
        print(
            f"Exception of type, {name}, prevented program from continuing",
            file=sys.stderr,
        )
