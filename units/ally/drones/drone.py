"""Contains the Drone class and the drone State class"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from units.ally.atron import Atron
from utils import Coordinate, Icon

if TYPE_CHECKING:
    from typing import List

    from units.ally.overlord import Overlord


class Drone(Atron):
    """Parent class for all drone atron units."""

    max_health = 40
    max_capacity = 10
    max_moves = 1

    def __init__(self, overlord: Overlord) -> None:
        """Initialize a Drone."""
        super().__init__(self.max_health)
        self._overlord = overlord
        self._path_to_goal: List["Coordinate"] = []

    @property
    def capacity(self) -> int:
        """The max mineral capacity for this drone.

        Returns:
            int: The max capacity.
        """
        return self.max_capacity

    @property
    def moves(self) -> int:
        """The max moves this drone can take in 1 tick.

        Returns:
            int: The drone's max moves.
        """
        return self.max_moves

    @property
    def path(self) -> List["Coordinate"]:
        """The path this drone will take to its destination.

        The destination of this drone will always be the final element of this
        list. Setting the path implicitly sets the destination.
        """
        return self._path_to_goal

    @path.setter
    def path(self, new_path: List[Coordinate]) -> None:
        self._path_to_goal = new_path
        self._path_traveled = []
        # traveling if path length is greater than 2 (start, dest)
        self.state = State.TRAVELING if len(new_path) > 2 else State.WAITING

    @property
    def icon(self) -> Icon:
        """The icon of this drone type."""
        raise NotImplementedError("Drone subtypes must implement icon")


class State(Enum):
    """States that an atron Drone can be in."""

    TRAVELING = auto()
    WORKING = auto()
    WAITING = auto()
    REVERSING = auto()
