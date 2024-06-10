"""Abstract base class for all atron units."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from utils import Context, Coordinate, Counter, Icon

if TYPE_CHECKING:
    from gui.map_window import MapWindow

DEFAULT_CONTEXT = Context(Coordinate(-1, -1), *[Icon.UNKNOWN] * 4)


class Atron(ABC):
    """Abstract base class for all atron units."""

    def __init__(self, health: int, capacity: int = 0) -> None:
        """Initialize a atron unit.

        The atron's health must be at least 1.

        Raises:
            ValueError: if the passed in health is less than 1

        Args:
            health (int): The atron's maximum health.
            capacity (int, optional): The atron's maximum mineral capacity.
        """
        if health <= 0:
            raise ValueError("Atron health must be 1 or greater")
        self._health = Counter(value=health, max_value=health)
        self._payload = Counter(value=0, max_value=capacity)
        self._context: Context = DEFAULT_CONTEXT

    @property
    def health(self) -> Counter:
        """The current health of this atron.

        Returns:
            Counter: The current health.
        """
        return self._health

    @property
    def payload(self) -> Counter:
        """The atron's mineral payload.

        Returns:
            Counter: The mineral payload.
        """
        return self._payload

    @property
    def deployed(self) -> bool:
        """Whether this drone has been deployed.

        Returns:
            bool: True if deployed, False otherwise.
        """
        return self._context != DEFAULT_CONTEXT

    @property
    def context(self) -> Context:
        """The context surrounding this atron.

        Returns:
            Context: The context.
        """
        return self._context

    @context.setter
    def context(self, new_context: Context) -> None:
        """Set the context surrounding this atron.

        Args:
            new_context (Context): The new context.
        """
        self._context = new_context

    @property
    @abstractmethod
    def icon(self) -> Icon:
        """The icon of this atron."""
        raise NotImplementedError("Atron subtypes must implement icon")

    def deploy(self, map_window: MapWindow) -> None:
        """Deploy the atron on the map.

        Args:
            map_window (MapWindow): The map window to deploy the atron on.
        """
        if not (map_data := map_window.map_data):
            raise ValueError("Map data not set")
        map_data.deploy_atron(self)

    def undeploy(self) -> int:
        """Retrieve the atron from the map and extract the payload.

        Returns:
            int: The payload of this atron.
        """
        if not self.deployed:
            raise ValueError("Unit not deployed")
        self._context = DEFAULT_CONTEXT
        payload = self._payload.get()
        self._payload.reset()
        return payload

    def __str__(self) -> str:
        """Return the string representation of this atron.

        Returns:
            str: The string representation of this atron.
        """
        return f"{self.__class__.__name__}"
