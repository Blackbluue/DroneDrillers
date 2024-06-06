"""Contains the Drone class and the drone State class"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from units.ally.atron import Atron
from utils import Context, Coordinate, Icon

if TYPE_CHECKING:
    from collections.abc import MutableSequence

    from units.ally.overlord import Overlord


DEFAULT_CONTEXT = Context()


class Drone(Atron):
    """Parent class for all drone atron units."""

    max_health = 40
    max_capacity = 10
    max_moves = 1

    def __init__(self, overlord: Overlord) -> None:
        """Initialize a Drone."""
        super().__init__(self.max_health)
        self._overlord = overlord
        self._payload = 0
        self._path_to_goal: MutableSequence[Coordinate] = []
        self._context: Context = DEFAULT_CONTEXT

    @property
    def capacity(self) -> int:
        """The max mineral capacity for this drone.

        Returns:
            int: The max capacity.
        """
        return self.max_capacity

    @property
    def payload(self) -> int:
        return self._payload

    @payload.setter
    def payload(self, value: int) -> None:
        """Set the payload of this atron.

        If set to a negative value, the payload will be set to 0. The payload
        also cannot exceed the maximum payload, which is set at initialization.

        Args:
            value (int): The new payload value.
        """
        self._payload = value
        if self._payload < 0:
            self._payload = 0
        elif self._payload > self._MAX_HEALTH:
            self._payload = self._MAX_HEALTH

    @property
    def moves(self) -> int:
        """The max moves this drone can take in 1 tick.

        Returns:
            int: The drone's max moves.
        """
        return self.max_moves

    @property
    def deployed(self) -> bool:
        """Whether this drone has been deployed.

        Returns:
            bool: True if deployed, False otherwise.
        """
        return self._context != DEFAULT_CONTEXT

    @property
    def context(self) -> Context:
        """The context surrounding this drone.

        Returns:
            Context: The context.
        """
        return self._context

    @context.setter
    def context(self, new_context: Context) -> None:
        """Set the context surrounding this drone.

        Args:
            new_context (Context): The new context.
        """
        self._context = new_context

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
        self._path_traveled = []
        # traveling if path length is greater than 2 (start, dest)
        self.state = State.TRAVELING if len(new_path) > 2 else State.WAITING

    @property
    def icon(self) -> Icon:
        """The icon of this drone type."""
        raise NotImplementedError("Drone subtypes must implement icon")

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
        payload = self._payload
        self._payload = 0
        return payload


class State(Enum):
    """States that an atron Drone can be in."""

    TRAVELING = auto()
    WORKING = auto()
    WAITING = auto()
    REVERSING = auto()
