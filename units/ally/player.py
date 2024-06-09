"""Player unit class."""

from units.ally.atron import Atron
from utils.map import MapData

DEFAULT_HEALTH = 100


class Player(Atron):
    """Player unit class."""

    def __init__(self, mining_map: MapData) -> None:
        super().__init__(DEFAULT_HEALTH)
        self._mining_map = mining_map
