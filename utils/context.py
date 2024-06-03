"""A context object, used to describe the surrounding's of a drone."""

from typing import NamedTuple

from .coordinate import Coordinate
from .icon import Icon


class Context(NamedTuple):
    """A context object, used to describe the surrounding's of a drone.

    Attributes:
        x (int, optional): The X coordinate of the drone. Defaults to 0.
        y (int, optional): The Y coordinate of the drone. Defaults to 0.
        north (Icon, optional): The tile to the north of the drone.
            Defaults to Icon.EMPTY.
        south (Icon, optional): The tile to the south of the drone.
            Defaults to Icon.EMPTY.
        east (Icon, optional): The tile to the east of the drone.
            Defaults to Icon.EMPTY.
        west (Icon, optional): The tile to the west of the drone.
            Defaults to Icon.EMPTY.
    """

    coord: Coordinate = Coordinate(0, 0)
    north: Icon | None = Icon.EMPTY
    south: Icon | None = Icon.EMPTY
    east: Icon | None = Icon.EMPTY
    west: Icon | None = Icon.EMPTY
