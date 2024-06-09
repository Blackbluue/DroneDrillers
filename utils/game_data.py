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

    def __init__(self, map_file: str | None) -> None:
        self._mining_map = MapData(map_file)
        self._player = Player(self._mining_map)
        self._overlord = Overlord()
        self._overlord.set_map(self._mining_map)
        self._drones = self._overlord.drones

    @property
    def player(self) -> Player:
        """The player."""
        return self._player

    @property
    def mining_map(self) -> MapData:
        """The mining map."""
        return self._mining_map

    @property
    def overlord(self) -> Overlord:
        """The overlord."""
        return self._overlord

    @property
    def drones(self) -> Mapping[int, Drone]:
        """The drones."""
        return self._drones
