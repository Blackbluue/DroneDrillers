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

    def _build_maps(self, count: int) -> Mapping[int, MapData]:
        """Build maps based on count, width, and height.

        If map files are given on the command line, they will be used instead.

        Args:
            count (int): Number of maps to build

        Returns:
            MutableMapping[int, MapData]:
                Mapping of map id as key and MapData as value
        """
        maps: MutableMapping[int, MapData] = {}
        for map_number in range(count):
            if sys.argv[1:]:  # Overwrite from file if indicated
                maps[map_number] = MapData(map_number).from_file(
                    sys.argv.pop(1)
                )
            else:
                maps[map_number] = MapData(map_number).from_scratch(
                    randint(MIN_DIMENSION, MAX_DIMENSION),
                    randint(MIN_DIMENSION, MAX_DIMENSION),
                    uniform(MIN_DENSITY, MAX_DENSITY),
                )

            self.overlord.add_map(map_number, maps[map_number])
        return maps

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

    def _map_tick_updates(
        self, maps: Mapping[int, MapData], mined: int
    ) -> None:
        """Update the maps and print out the status.

        Args:
            maps (Mapping[int, MapData]): The maps to update.
            mined (int): The total mined minerals.
        """
        for map_id, a_map in maps.items():
            print(f"Map {map_id}", file=sys.stderr)
            for a_drone in a_map.d_contexts:
                print(
                    f"Drone ID: {id(a_drone.atron)} "
                    f"Actual Health: {a_drone.health} "
                    f"Your Health: {a_drone.atron.health}",
                    file=sys.stderr,
                )
            a_map.tick()
            print(a_map, file=sys.stderr)
        print("SubTotal mined:", mined, file=sys.stderr)

    def process_tick(
        self,
        maps: Mapping[int, MapData],
        drone_locations: MutableMapping[int, int | None],
        drone_healths: MutableMapping[int, int],
    ) -> int:
        """Process a tick of the game.

        Args:
            maps (Mapping[int, MapData]): The maps to process.
            drone_locations (MutableMapping[int, int  |  None]): The drone locations.
            drone_healths (MutableMapping[int, int]): The drone healths.

        Returns:
            int: The total mined minerals.
        """
        mined = 0
        action, _, opts = self.overlord.action().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                if (map_id := drone_locations[drone_id]) is not None:
                    if res := maps[map_id].remove_atron(drone_id):
                        extracted, health = res
                        drone_locations[drone_id] = None  # Not on map anymore
                        drone_healths[drone_id] = health
                        mined += extracted
            case "DEPLOY":
                drone_id, map_id = map(int, opts.split())
                # check if drone is already deployed
                if drone_locations[drone_id] is None and maps[
                    map_id
                ].add_atron(
                    self.overlord.drones[drone_id], drone_healths[drone_id]
                ):
                    drone_locations[drone_id] = map_id
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        self._map_tick_updates(maps, mined)
        time.sleep(DEFAULT_REFRESH)
        return mined

    def _start_mining(self) -> None:
        """Start the mining expedition."""
        self._print_drone_info()

        maps = self._build_maps(3)
        # Represents dictionary of drone id as key and map id as value
        drone_locations: dict[int, int | None] = {
            drone_id: None for drone_id in self.overlord.drones
        }
        drone_healths = {
            drone_id: each_drone.health
            for drone_id, each_drone in self.overlord.drones.items()
        }

        mined = 0
        for a_tick in range(DEFAULT_TICKS):
            txt = f"Tick Counter: {a_tick}"
            self.overlord.dashboard.master.string_var.set(txt)
            self.overlord.dashboard.master.update_idletasks()
            mined += self.process_tick(maps, drone_locations, drone_healths)

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


if __name__ == "__main__":
    try:
        MainController().mainloop()
    except (Exception, GeneratorExit, KeyboardInterrupt) as e:
        name = type(e).__name__
        print(
            f"Exception of type, {name}, prevented program from continuing",
            file=sys.stderr,
        )
