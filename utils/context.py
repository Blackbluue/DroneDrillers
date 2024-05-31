"""A context object, used to describe the surrounding's of a drone."""

from typing import NamedTuple

from .icon import Icon


class Context(NamedTuple):
    """A context object, used to describe the surrounding's of a drone.

    Attributes:
        x (int, optional): The X coordinate of the drone. Defaults to 0.
        y (int, optional): The Y coordinate of the drone. Defaults to 0.
        north (str, optional): The tile to the north of the drone as a string.
            Defaults to Icon.EMPTY.value.
        south (str, optional): The tile to the south of the drone as a string.
            Defaults to Icon.EMPTY.value.
        east (str, optional): The tile to the east of the drone as a string.
            Defaults to Icon.EMPTY.value.
        west (str, optional): The tile to the west of the drone as a string.
            Defaults to Icon.EMPTY.value.
    """

    x: int = 0
    y: int = 0
    north: str = Icon.EMPTY.value
    south: str = Icon.EMPTY.value
    east: str = Icon.EMPTY.value
    west: str = Icon.EMPTY.value
