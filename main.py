#!/usr/bin/env python3
"""Main controller for the Atron Mining Expedition."""

from __future__ import annotations

import sys
import time
import tkinter as tk
from random import randint, uniform
from typing import TYPE_CHECKING

from gui import Dashboard
from units.ally import Overlord
from utils import MapData

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

    from .units.ally.drones import Drone

MIN_DENSITY = 0.1
MAX_DENSITY = 0.5

MIN_DIMENSION = 10
MAX_DIMENSION = 20

DEFAULT_TICKS = 10
DEFAULT_REFINED = 100
DEFAULT_REFRESH = 0.1  # refresh delay in seconds


class MainController(tk.Tk):
    """Sample code controller."""

    def __init__(self) -> None:
        """Root window that contains fields for initial values."""
        super().__init__()
        self.title("Atron Mining Expedition")
        self.geometry("400x150+0+0")
        self._initialize_values()

    def _initialize_values(self) -> None:
        """Initialize game values from the GUI."""
        self.ticks = LabeledEntry(self, "Ticks:", DEFAULT_TICKS)
        self.refined = LabeledEntry(self, "Refined Minerals:", DEFAULT_REFINED)
        self.refresh = LabeledEntry(
            self, "Refresh Delay (sec):", DEFAULT_REFRESH
        )
        self.string_var = tk.StringVar()
        self.string_var.set("Tick Counter:")
        tk.Entry(self, textvariable=self.string_var, width=30).pack()
        self.start_button = tk.Button(
            self, command=self._start_button_handler, text="Start"
        )
        self.start_button.pack()
        self._overlord = Overlord()
        if sys.argv[1:]:  # Overwrite from file if indicated
            self._mining_map = MapData().from_file(sys.argv.pop(1))
        else:
            self._mining_map = MapData().from_scratch(
                randint(MIN_DIMENSION, MAX_DIMENSION),
                randint(MIN_DIMENSION, MAX_DIMENSION),
                uniform(MIN_DENSITY, MAX_DENSITY),
            )

        self._dashboard = Dashboard(self, self._mining_map)
        self._overlord.set_map(self._mining_map)

    def _start_button_handler(self) -> None:
        """Start the game."""
        self.start_button.destroy()
        self._start_mining()

    def _print_drone_info(self) -> None:
        """Print out drone information."""
        fmt_string = "{0:<18}{1:12}"
        print(
            (fmt_string * 3).format("Drone ID", "Drone Type"), file=sys.stderr
        )

        for idx, a_drone in enumerate(self._overlord.drones.values()):
            print(
                fmt_string.format(id(a_drone), type(a_drone).__name__),
                file=sys.stderr,
                end="",
            )
            if idx % 3 == 2:
                print(file=sys.stderr)
        print("-" * 100, file=sys.stderr)


    def process_tick(
        self,
        mining_map: MapData,
    ) -> int:
        """Process a tick of the game.

        Args:
            maps (MapData): The map to process.

        Returns:
            int: The total mined minerals.
        """
        mined = 0
        action, _, opts = self._overlord.action().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                mined +=mining_map.remove_drone(self._overlord.drones[drone_id])
            case "DEPLOY":
                drone_id, _ = map(int, opts.split())
                # check if drone is already deployed
                mining_map.add_drone(self._overlord.drones[drone_id])
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        deployed_drones = list(
            filter(lambda drone: drone.deployed, self._overlord.drones.values()))
        map_tick_updates(mining_map, deployed_drones)
        print("SubTotal mined:", mined, file=sys.stderr)
        time.sleep(DEFAULT_REFRESH)
        return mined

    def _start_mining(self) -> None:
        """Start the mining expedition."""
        self._print_drone_info()

        mined = 0
        for a_tick in range(DEFAULT_TICKS):
            self.string_var.set(f"Tick Counter: {a_tick}")
            self.update_idletasks()
            mined += self.process_tick(self._mining_map)

        print("Total mined:", mined, file=sys.stderr)


class LabeledEntry(tk.Frame):
    """A labeled entry widget."""

    def __init__(
        self, owner: MainController, label: str, default: Any
    ) -> None:
        """Create a labeled entry.

        Args:
            owner (MainController): The owner of the LabeledEntry.
            label (str): The name of the label.
            default (Any): The default value for the label.
        """
        super().__init__(owner)
        self.label = tk.Label(self, text=label, width=20)
        self.label.pack(side=tk.LEFT)
        self.entry = tk.Entry(self, width=5)
        self.entry.insert(tk.END, str(default))
        self.entry.pack(side=tk.LEFT)
        self.pack()


def map_tick_updates(mining_map: MapData, drones: Iterable[Drone]) -> None:
    """Process map tick and print out the status.

    Args:
        maps (MapData): The map to update.
    """
    for a_drone in drones:
        print(
            f"Drone ID: {id(a_drone)} Your Health: {a_drone.health}",
            file=sys.stderr,
        )
    mining_map.tick(drones)
    print(mining_map, file=sys.stderr)

if __name__ == "__main__":
    try:
        MainController().mainloop()
    except KeyboardInterrupt as e:
        print("Exiting due to interrupt", file=sys.stderr)
