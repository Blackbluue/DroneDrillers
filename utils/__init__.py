"""Series of classes and functions to help with the game."""

from .context import Context
from .coordinate import Coordinate
from .counter import Counter
from .directions import Directions
from .icon import Icon
from .map_data import MapData
from .tile import Tile

# static constants that others may need
DEFAULT_COORDINATE = Coordinate(-1, -1)
DEFAULT_TILE = Tile(DEFAULT_COORDINATE, Icon.UNKNOWN)
DEFAULT_CONTEXT = Context(DEFAULT_COORDINATE, *[Icon.UNKNOWN] * 4)
