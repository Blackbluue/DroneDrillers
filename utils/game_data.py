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
        self._total_refined = 0

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
            map_file (MapData | None): The map data.
        """
        self._current_map = map_data
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
    def total_refined(self) -> int:
        """The total refined minerals."""
        return self._total_refined

    def undeploy_player(self) -> None:
        """Retrieve the player from the map."""
        if self._player.deployed:
            self._total_refined += self._player.undeploy()
