"""Contains the Drone class and the drone State class"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING

from units.ally.atron import Atron
from utils import DEFAULT_CONTEXT, Context, Coordinate

if TYPE_CHECKING:
    from collections.abc import MutableSequence

    from units.ally.overlord import Overlord


DEFAULT_HEALTH = 40
DEFAULT_CAPACITY = 10
DEFAULT_MOVES = 1


class Drone(Atron, ABC):
    """Parent class for all drone atron units."""

    def __init__(self, overlord: Overlord) -> None:
        """Initialize a Drone."""
        super().__init__(DEFAULT_HEALTH, DEFAULT_CAPACITY)
        self._overlord = overlord
        self._moves = DEFAULT_MOVES
        self._path_to_goal: MutableSequence[Coordinate] = []

    @property
    def moves(self) -> int:
        """The max moves this drone can take in 1 tick.

        Returns:
            int: The drone's max moves.
        """
        return self._moves

    @property
    def deployed(self) -> bool:
        """Whether this drone has been deployed.

        Returns:
            bool: True if deployed, False otherwise.
        """
        return self._context != DEFAULT_CONTEXT

    @property
    def path(self) -> MutableSequence[Coordinate]:
        """The path this drone will take to its destination.

        The destination of this drone will always be the final element of this
        list. Setting the path implicitly sets the destination.
        """
        return self._path_to_goal

    @path.setter
    def path(self, new_path: MutableSequence[Coordinate]) -> None:
        self._path_to_goal = new_path
        self._path_traveled: MutableSequence[Coordinate] = []
        # traveling if path length is greater than 2 (start, dest)
        self.state = State.TRAVELING if len(new_path) > 2 else State.WAITING

    @abstractmethod
    def action(self, context: Context) -> str:
        """Perform some action, based on the type of drone.

        The drone will internally have it's own orders set by the overlord.
        These orders may take the context into account.

        Args:
            context (Context): The context surrounding the drone.

        Returns:
            str: The action the drone wants to take.
        """
        raise NotImplementedError("Drone subtypes must implement action")

    def deploy_drone(self, context: Context) -> None:
        """Deploy the drone to the map."""
        if self.deployed:
            raise ValueError("Drone already deployed")
        self._context = context

    def undeploy_drone(self) -> int:
        """Retrieve the drone from the map and extract the payload.

        Returns:
            int: The payload of this drone.
        """
        if not self.deployed:
            raise ValueError("Drone not deployed")
        self._context = DEFAULT_CONTEXT
        payload = self._payload.get()
        self._payload.reset()
        return payload


class State(Enum):
    """States that an atron Drone can be in."""

    TRAVELING = auto()
    WORKING = auto()
    WAITING = auto()
    REVERSING = auto()
