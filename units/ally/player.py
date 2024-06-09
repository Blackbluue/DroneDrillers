"""Player unit class."""

from __future__ import annotations

from tkinter import Event
from typing import TYPE_CHECKING

from units.ally.atron import Atron

if TYPE_CHECKING:
    from gui.map_window import MapWindow
    from utils import MapData


DEFAULT_HEALTH = 100


class Player(Atron):
    """Player unit class."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_HEALTH)
        self._mining_map: MapData | None = None

    def deploy_player(self, map_window: MapWindow) -> None:
        """Deploy the player on the map.

        Args:
            map_window (MapWindow): The map window to deploy the player on.
        """
        self._mining_map = map_window.map_data
        map_window.bind("<Left>", self.move_player, add=True)
        map_window.bind("<Right>", self.move_player, add=True)
        map_window.bind("<Up>", self.move_player, add=True)
        map_window.bind("<Down>", self.move_player, add=True)

    def move_player(self, event: Event) -> None:
        print(f"clicked {event.keysym}")
