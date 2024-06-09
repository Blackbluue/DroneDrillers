"""Store game data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from units.ally import Overlord, Player
from utils import MapData

if TYPE_CHECKING:
    from collections.abc import Mapping

    from units.ally.drones import Drone


class GameData:
    """Store game data."""

    def __init__(self) -> None:
        self._current_map: MapData | None = None
        self._player = Player()
        self._overlord = Overlord()
        self._drones = self._overlord.drones

    @property
    def player(self) -> Player:
        """The player."""
        return self._player

    @property
    def current_map(self) -> MapData | None:
        """The current mining map."""
        return self._current_map

    @current_map.setter
    def current_map(self, map_data: MapData) -> None:
        """Set the mining map.

        Args:
            map_file (MapData): The map data.
        """
        self._current_map = map_data
        self._overlord.set_map(self._current_map)

    @property
    def overlord(self) -> Overlord:
        """The overlord."""
        return self._overlord

    @property
    def drones(self) -> Mapping[int, Drone]:
        """The drones."""
        return self._drones