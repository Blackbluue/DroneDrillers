"""Player unit class."""

from units.ally.atron import Atron
from utils import MapData

DEFAULT_HEALTH = 100


class Player(Atron):
    """Player unit class."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_HEALTH)
        self._mining_map: MapData | None = None
