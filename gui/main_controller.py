"""Main controller for the Atron Mining Expedition."""

from __future__ import annotations

import sys
import time
import tkinter as tk

from units.ally import Overlord
from utils import MapData

from .dashboard import Dashboard
from .label_counter import LabeledCounter

DEFAULT_TICKS = 10
DEFAULT_REFINED = 100


class MainController(tk.Tk):
    """Main game controller."""

    def __init__(self, refresh_delay: float, map_file: str | None) -> None:
        """Root window that contains fields for initial values."""
        super().__init__()
        self.title("Atron Mining Expedition")
        self.geometry("400x150+0+0")
        self._initialize_values(refresh_delay, map_file)

    def _initialize_values(
        self, refresh_delay: float, map_file: str | None
    ) -> None:
        """Initialize game values from the GUI."""
        self.ticks = LabeledCounter(
            self, "Ticks:", value=DEFAULT_TICKS, max_value=DEFAULT_TICKS
        )
        self.refined = LabeledCounter(
            self,
            "Refined Minerals:",
            value=DEFAULT_REFINED,
            max_value=DEFAULT_REFINED,
        )
        self._refresh_delay = refresh_delay
        self.start_button = tk.Button(
            self, command=self._start_button_handler, text="Start"
        )
        self.start_button.pack()

        self._mining_map = MapData(map_file)
        self._dashboard = Dashboard(self, self._mining_map)
        self._overlord = Overlord()
        self._overlord.set_map(self._mining_map)

    def _start_button_handler(self) -> None:
        """Start the game."""
        self.ticks.counter.reset()
        self.refined.counter.reset()
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
        action, _, opts = self._overlord.order_drones().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                mined += mining_map.remove_drone(
                    self._overlord.drones[drone_id]
                )
            case "DEPLOY":
                drone_id, _ = map(int, opts.split())
                # check if drone is already deployed
                mining_map.add_drone(self._overlord.drones[drone_id])
            case "":
                pass  # Do nothing
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        deployed_drones = list(
            filter(
                lambda drone: drone.deployed, self._overlord.drones.values()
            )
        )
        mining_map.tick(deployed_drones)
        print(mining_map, file=sys.stderr)
        print(f"SubTotal mined: {mined}", file=sys.stderr)
        time.sleep(self._refresh_delay)
        return mined

    def _start_mining(self) -> None:
        """Start the mining expedition."""
        self._print_drone_info()

        mined = 0
        for _ in range(DEFAULT_TICKS):
            self.ticks.counter.count(-1)
            self.update_idletasks()
            mined += self.process_tick(self._mining_map)

        print("Total mined:", mined, file=sys.stderr)
