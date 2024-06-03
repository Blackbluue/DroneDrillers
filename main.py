#!/usr/bin/env python3

from __future__ import annotations

import sys
import time
import tkinter as tk
from random import uniform
from typing import TYPE_CHECKING

from gui import Dashboard
from units.ally import Overlord
from utils import MapData

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping

MIN_DENSITY = 0.1
MAX_DENSITY = 0.5


class MainController(tk.Tk):
    """Sample code controller."""

    default_ticks = "100"
    default_refined = "100"
    default_refresh = "0.1"  # refresh delay in seconds

    def __init__(self):
        """Root window that contains fields for initial values."""
        super().__init__()
        self.title("Atron Mining Expedition")
        self.geometry("400x150+0+0")

        self.ticks = LabeledEntry.create(
            self, "Ticks:", MainController.default_ticks
        )
        self.refined = LabeledEntry.create(
            self, "Refined Minerals:", MainController.default_refined
        )
        self.refresh = LabeledEntry.create(
            self, "Refresh Delay (sec):", MainController.default_refresh
        )

        self.message = tk.Label(self, text=" ")
        self.message.pack()

        self.start_button = tk.Button(
            self, command=self._get_the_ball_rolling, text="Start"
        )

        self.string_var = tk.StringVar()
        self.string_var.set("Tick Counter:")
        tk.Entry(self, textvariable=self.string_var, width=30).pack()

        self.start_button.pack()

        self.dashboard = Dashboard(self)

    def _initialize_values(self):
        self.tick_count = int(self.ticks.entry.get())
        self.refined_count = int(self.refined.entry.get())
        self.refresh_delay = float(self.refresh.entry.get())

    def _reset_entry(self, widget, default_value):
        widget.delete(0, tk.END)
        widget.insert(tk.END, default_value)
        widget["fg"] = "Red"

    def _reset_entries(self):
        self._reset_entry(self.ticks.entry, MainController.default_ticks)
        self._reset_entry(self.refined.entry, MainController.default_refined)
        self._reset_entry(self.refresh.entry, MainController.default_refresh)

    def _initialize_user_values(self):
        try:
            self._initialize_values()
        except Exception:
            self.message["text"] = "Invalid Value(s) : Reset to Defaults"
            self.message["fg"] = "Red"

            self._reset_entries()
            self._initialize_values()

    def _get_the_ball_rolling(self):
        """Registered with start button"""
        self.start_button.destroy()
        self._initialize_user_values()
        self.overlord = Overlord(
            self.tick_count, self.refined_count, self.dashboard
        )
        self._start_mining()

    def _build_maps(
        self, count: int, width: int, height: int
    ) -> dict[int, MapData]:
        """Build maps based on count, width, and height.

        If map files are given on the command line, they will be used instead.

        Args:
            count (int): Number of maps to build
            width (int): Width of each map
            height (int): Height of each map

        Returns:
            dict[int, Map]: Dictionary of map id as key and Map as value
        """
        maps: dict[int, MapData] = {}
        for map_number in range(count):
            if sys.argv[1:]:  # Overwrite from file if indicated
                maps[map_number] = MapData(map_number).from_file(
                    sys.argv.pop(1)
                )
            else:
                maps[map_number] = MapData(map_number).from_scratch(
                    width, height, uniform(MIN_DENSITY, MAX_DENSITY)
                )

            self.overlord.add_map(map_number, maps[map_number])
        return maps

    def _print_drone_info(self):
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
        mined = 0
        action = self.overlord.action()
        if action.startswith("DEPLOY"):
            drone_id, map_id = action[6:].split()
            drone_id = int(drone_id)
            map_id = int(map_id)

            if drone_locations[drone_id] is None:
                if maps[map_id].add_atron(
                    self.overlord.drones[drone_id], drone_healths[drone_id]
                ):
                    drone_locations[drone_id] = map_id
        elif action.startswith("RETURN"):
            drone_id = int(action[6:])
            if (map_id := drone_locations[drone_id]) is not None:
                if res := maps[map_id].remove_atron(drone_id):
                    extracted, health = res
                    drone_locations[drone_id] = None  # Not on map anymore
                    drone_healths[drone_id] = health
                    mined += extracted

        self._map_tick_updates(maps, mined)
        try:
            time.sleep(self.refresh_delay)
            return mined
        except KeyboardInterrupt:
            exit(-1)

    def _start_mining(self) -> None:
        # Print out each drone's id and type
        self._print_drone_info()

        maps = self._build_maps(3, 10, 5)
        # Represents dictionary of drone id as key and map id as value
        drone_locations: dict[int, int | None] = {
            drone_id: None for drone_id in self.overlord.drones
        }
        drone_healths: dict[int, int] = {
            drone_id: each_drone.health
            for drone_id, each_drone in self.overlord.drones.items()
        }

        mined = 0
        for a_tick in range(self.tick_count):
            txt = f"Tick Counter: {a_tick}"
            self.overlord.dashboard.master.string_var.set(txt)
            self.overlord.dashboard.master.update_idletasks()

            mined += self.process_tick(maps, drone_locations, drone_healths)

        print("Total mined:", mined, file=sys.stderr)


class LabeledEntry(tk.Frame):
    def __init__(self, owner, label, default):
        super().__init__(owner)
        self.label = tk.Label(self, text=label, width=20)
        self.label.pack(side=tk.LEFT)
        self.entry = tk.Entry(self, width=5)
        self.entry.insert(tk.END, default)
        self.entry.pack(side=tk.LEFT)

    @staticmethod
    def create(owner, label, default):
        """Factory method to create and pack with label and default text"""
        labeled_entry = LabeledEntry(owner, label, default)
        labeled_entry.pack()
        return labeled_entry


if __name__ == "__main__":
    try:
        MainController().mainloop()
    except (Exception, GeneratorExit, KeyboardInterrupt) as e:
        name = type(e).__name__
        print(
            f"Exception of type, {name}, prevented program from continuing",
            file=sys.stderr,
        )
