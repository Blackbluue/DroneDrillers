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
    from collections.abc import Mapping, MutableMapping
    from typing import Any

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
        self.dashboard = Dashboard(self)
        self.overlord = Overlord(
            DEFAULT_TICKS, DEFAULT_REFINED, self.dashboard
        )

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

        for idx, a_drone in enumerate(self.overlord.drones.values()):
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
        drone_deployed: MutableMapping[int, bool],
    ) -> int:
        """Process a tick of the game.

        Args:
            maps (MapData): The map to process.
            drone_locations (MutableMapping[int, bool]): The drone locations.

        Returns:
            int: The total mined minerals.
        """
        mined = 0
        action, _, opts = self.overlord.action().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                if drone_deployed[drone_id]:
                    if extracted := mining_map.remove_atron(drone_id):
                        drone_deployed[drone_id] = False  # Not on map anymore
                        mined += extracted
            case "DEPLOY":
                drone_id, _ = map(int, opts.split())
                # check if drone is already deployed
                if not drone_deployed[drone_id] and mining_map.add_atron(
                    self.overlord.drones[drone_id]
                ):
                    drone_deployed[drone_id] = True
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        map_tick_updates(mining_map, mined)
        time.sleep(DEFAULT_REFRESH)
        return mined

    def _start_mining(self) -> None:
        """Start the mining expedition."""
        self._print_drone_info()

        mining_map = build_map(self.overlord)
        # Represents dictionary of drone id as key and map id as value
        drone_deployed = {drone_id: False for drone_id in self.overlord.drones}

        mined = 0
        for a_tick in range(DEFAULT_TICKS):
            txt = f"Tick Counter: {a_tick}"
            self.string_var.set(txt)
            self.update_idletasks()
            mined += self.process_tick(mining_map, drone_deployed)

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


def build_map(overlord: Overlord) -> MapData:
    """Build a map to add to the overlord.

    If a map file is given on the command line, it will be used. Otherwise,
    a random map will be generated.

    Args:
        overlord (Overlord): The overlord to add the map to.

    Returns:
        MapData: The MapData object.
    """
    mining_map = MapData()
    if sys.argv[1:]:  # Overwrite from file if indicated
        mining_map.from_file(sys.argv.pop(1))
    else:
        mining_map.from_scratch(
            randint(MIN_DIMENSION, MAX_DIMENSION),
            randint(MIN_DIMENSION, MAX_DIMENSION),
            uniform(MIN_DENSITY, MAX_DENSITY),
        )

    overlord.add_map(0, mining_map)
    return mining_map

def map_tick_updates(mining_map: MapData, mined: int) -> None:
    """Process map tick and print out the status.

    Args:
        maps (MapData): The map to update.
        mined (int): The total mined minerals.
    """
    for a_drone in mining_map.drones:
        print(
            f"Drone ID: {id(a_drone)} Your Health: {a_drone.health}",
            file=sys.stderr,
        )
    mining_map.tick()
    print(mining_map, file=sys.stderr)
    print("SubTotal mined:", mined, file=sys.stderr)

if __name__ == "__main__":
    try:
        MainController().mainloop()
    except KeyboardInterrupt as e:
        print("Exiting due to interrupt", file=sys.stderr)
