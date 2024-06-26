"""A context object, used to describe the surrounding's of a drone."""

from typing import NamedTuple

from .tile import Tile


class Context(NamedTuple):
    """A context object, used to describe the surrounding's of a drone.

    Attributes:
        x (int, optional): The X coordinate of the drone. Defaults to -1.
        y (int, optional): The Y coordinate of the drone. Defaults to -1.
        north (Icon, optional): The tile to the north of the drone.
            Defaults to Icon.UNKNOWN.
        south (Icon, optional): The tile to the south of the drone.
            Defaults to Icon.UNKNOWN.
        east (Icon, optional): The tile to the east of the drone.
            Defaults to Icon.UNKNOWN.
        west (Icon, optional): The tile to the west of the drone.
            Defaults to Icon.UNKNOWN.
    """

    center: Tile
    north: Tile
    south: Tile
    east: Tile
    west: Tile
