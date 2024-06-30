"""Store game data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from units.ally import Overlord, Player
from utils.counter import Counter

if TYPE_CHECKING:
    from collections.abc import Mapping
    from tkinter import Tk

    from units.ally.atron import Atron
    from units.ally.drones import Drone
    from utils import MapData

STARTING_REFINED = 100


class GameData:
    """Store game data."""

    def __init__(self, root_window: Tk) -> None:
        self._current_map: MapData | None = None
        self._player = Player(root_window)
        self._overlord = Overlord()
        self._drones = self._overlord.drones
        self._total_refined = Counter(value=STARTING_REFINED)
        self._total_unrefined = Counter(value=0)

    @property
    def player(self) -> Player:
        """The player."""
        return self._player

    @property
    def current_map(self) -> MapData | None:
        """The current mining map."""
        return self._current_map

    @current_map.setter
    def current_map(self, map_data: MapData | None) -> None:
        """Set the mining map.

        Args:
            map_data (MapData | None): The map data.
        """
        self._current_map = map_data
        if map_data is not None:
            self._player.deploy(map_data)
            self._player.health.reset()
            # self._overlord.deploy(self._current_map)

    @property
    def overlord(self) -> Overlord:
        """The overlord."""
        return self._overlord

    @property
    def drones(self) -> Mapping[int, Drone]:
        """The drones."""
        return self._drones

    @property
    def total_unrefined(self) -> Counter:
        """The total unrefined minerals."""
        return self._total_unrefined

    @property
    def total_refined(self) -> Counter:
        """The total refined minerals."""
        return self._total_refined

    def finish_excavation(self) -> None:
        """Finish the excavation on the current map."""
        self._total_refined.count(self._total_unrefined.get())
        self._total_unrefined.reset()
        self._player.undeploy()

    def collect_minerals(self, atron: Atron) -> None:
        """Extract the minerals from the player."""
        self._total_unrefined.count(atron.extract_minerals())
