"""An icon on the map."""

from enum import Enum
from typing import Mapping


class Icon(Enum):
    """An icon on the map."""

    ATRON = "A"
    SCOUT = "S"
    MINER = "M"
    WALL = "#"
    DEPLOY_ZONE = "_"
    MINERAL = "*"
    ACID = "~"
    EMPTY = " "
    UNKNOWN = "?"

    def traversable(self) -> bool:
        """Whether a tile with this icon is traversable by a drone.

        Returns:
            bool: True if traversable, else False.
        """
        return self in [Icon.DEPLOY_ZONE, Icon.ACID, Icon.EMPTY]

    def health_cost(self) -> int:
        """Return the health cost for traversing over this tile.

        If the tile is not traversable, a value of -1 will be returned.

        Returns:
            int: A non-negative number representing the health cost, or -1.
        """
        if self is Icon.WALL:
            return 1
        elif self is Icon.ACID:
            return 3
        else:
            return 0

    def unicode(self) -> str:
        """Return the unicode representation of this icon.

        Returns:
            str: The icon as a unicode character.
        """
        return {
            Icon.WALL: "\u039E",
            Icon.ACID: "\u05e1",
            Icon.SCOUT: "\u00A7",
            Icon.MINER: "\u00A3",
            Icon.MINERAL: "\u0275",
            Icon.ATRON: "\u00C4",
            Icon.DEPLOY_ZONE: "\u02c5",
            Icon.EMPTY: " ",
            Icon.UNKNOWN: "\u02D1",
        }[self]

    @classmethod
    def unicode_mappings(cls) -> Mapping[str, str]:
        """Return a mapping of Icon name to Icon unicode representation.

        Returns:
            Mapping[str, str]: The unicode mappings.
        """
        return {icon.name: icon.unicode() for icon in cls.__members__.values()}
