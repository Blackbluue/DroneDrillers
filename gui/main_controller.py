"""Main controller for the Atron Mining Expedition."""

from __future__ import annotations

import os
import random
import sys
import time
import tkinter as tk

from utils import MapData
from utils.game_data import GameData

from .dashboard import Dashboard
from .label_counter import LabeledCounter

DEFAULT_TICKS = 10
DEFAULT_REFINED = 100


class MainController(tk.Tk):
    """Main game controller."""

    def __init__(self, refresh_delay: float, map_dir: str | None) -> None:
        """Root window that contains fields for initial values."""
        super().__init__()
        self.title("Atron Mining Expedition")
        self.geometry("400x150+0+0")
        self._initialize_values(refresh_delay, map_dir)

    def _initialize_values(
        self, refresh_delay: float, map_dir: str | None
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

        self._game_data = GameData()
        self._dashboard = Dashboard(self)
        self._map_dir = map_dir

    def _start_button_handler(self) -> None:
        """Start the game."""
        if self._map_dir:
            random_file = random.choice(os.listdir(self._map_dir))
            map_file = os.path.join(self._map_dir, random_file)
        else:
            map_file = None
        mining_map = MapData(map_file)

        self._game_data.current_map = mining_map
        self._dashboard.set_map(mining_map, self._game_data.player)

        self.ticks.counter.reset()
        self.refined.counter.reset()
        self._start_mining()

    def _process_tick(self, mining_map: MapData) -> int:
        """Process a tick of the game.

        Args:
            maps (MapData): The map to process.

        Returns:
            int: The total mined minerals.
        """
        mined = 0
        overlord = self._game_data.overlord
        action, _, opts = overlord.order_drones().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                mined += mining_map.remove_drone(overlord.drones[drone_id])
            case "DEPLOY":
                drone_id, _ = map(int, opts.split())
                # check if drone is already deployed
                mining_map.add_drone(overlord.drones[drone_id])
            case "":
                pass  # Do nothing
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        deployed_drones = list(
            filter(lambda drone: drone.deployed, overlord.drones.values())
        )
        mining_map.tick(deployed_drones)
        print(mining_map, file=sys.stderr)
        time.sleep(self._refresh_delay)
        return mined

    def _start_mining(self) -> None:
        """Start the mining expedition."""
        if (mining_map := self._game_data.current_map) is None:
            raise ValueError("No mining map")

        total_mined = 0
        for _ in range(DEFAULT_TICKS):
            self.ticks.counter.count(-1)
            self.update_idletasks()
            total_mined += self._process_tick(mining_map)

        print("Total mined:", total_mined, file=sys.stderr)
