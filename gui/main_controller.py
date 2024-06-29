"""Main controller for the Atron Mining Expedition."""

from __future__ import annotations

import os
import random
import sys
import tkinter as tk

from utils import MapData
from utils.game_data import GameData

from .dashboard import Dashboard
from .graphic_tile import GraphicTile
from .label_counter import LabeledCounter

DEFAULT_TICKS = 100
DEFAULT_REFINED = 100


class MainController(tk.Tk):
    """Main game controller."""

    def __init__(self, map_dir: str | None) -> None:
        """Root window that contains fields for initial values."""
        super().__init__()
        self.title("Atron Mining Expedition")
        # self.geometry("400x150+0+0")
        self._initialize_values(map_dir)

    def _initialize_values(self, map_dir: str | None) -> None:
        """Initialize game values from the GUI."""
        self._ticks = LabeledCounter(
            self, "Ticks:", value=DEFAULT_TICKS, max_value=DEFAULT_TICKS
        )
        self._refined = LabeledCounter(
            self,
            "Refined Minerals:",
            value=DEFAULT_REFINED,
            max_value=DEFAULT_REFINED,
        )
        self._start_button = tk.Button(
            self, command=self._start_button_handler, text="Start"
        )
        self._tick_tracer = ""

        self._game_data = GameData(self)
        self._map_dir = map_dir
        self._dashboard = Dashboard(self, self._game_data.player)
        self._map_frame = tk.Frame(self)

        self._ticks.pack()
        self._refined.pack()
        self._start_button.pack()
        self._map_frame.pack()

        self.bind("<<PlayerMoved>>", self._process_tick)

    def _start_button_handler(self) -> None:
        """Start the game."""
        self._set_new_map()

        self._ticks.counter.reset()
        self._tick_tracer = self._ticks.counter.trace_add(
            "write", self._finish_mining
        )
        self._refined.counter.reset()

    def _process_tick(self, event: tk.Event) -> None:
        """Process a tick of the game.

        Args:
            event (tk.Event): The event that triggered the tick.
        """
        if not (mining_map := self._game_data.current_map):
            return

        overlord = self._game_data.overlord
        action, _, opts = overlord.order_drones().partition(" ")
        match action:
            case "RETURN":
                drone_id = next(map(int, opts.split()))
                mining_map.remove_atron(overlord.drones[drone_id])
            case "DEPLOY":
                drone_id, _ = map(int, opts.split())
                # check if drone is already deployed
                mining_map.deploy_atron(overlord.drones[drone_id])
            case "":
                pass  # Do nothing
            case _:  # Ignore other actions
                print(f"Unknown action: {action}", file=sys.stderr)

        deployed_drones = list(
            filter(lambda drone: drone.deployed, overlord.drones.values())
        )
        mining_map.tick(deployed_drones)
        print(mining_map, file=sys.stderr)
        self._ticks.counter.count(-1)

    def _reset_map(self) -> None:
        """Reset the mining map."""
        if self._tick_tracer:
            self._ticks.counter.trace_remove("write", self._tick_tracer)
            self._tick_tracer = ""
        self._game_data.undeploy_player()
        self._game_data.current_map = None

    def _finish_mining(self, var: str, index: str, mode: str) -> None:
        """Finish the mining expedition.

        Args:
            var (str): The variable that was modified.
            index (str): The index of the variable.
            mode (str): The mode of the variable.
        """
        # TODO: health checked at end of tick. need to check after player moves
        player = self._game_data.player
        if self._ticks.counter.get() == 0 or player.health.get() <= 0:
            self._reset_map()
            print(
                "Total mined:", self._game_data.total_refined, file=sys.stderr
            )

    def _set_new_map(self) -> None:
        """Set the mining map."""
        if self._map_dir:
            random_file = random.choice(os.listdir(self._map_dir))
            map_file = os.path.join(self._map_dir, random_file)
        else:
            map_file = None
        mining_map = MapData(map_file)

        for widget in self._map_frame.winfo_children():
            widget.destroy()
        for tile in iter(mining_map):
            GraphicTile(self._map_frame, tile)

        self._game_data.current_map = mining_map
