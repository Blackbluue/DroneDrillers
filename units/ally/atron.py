"""Abstract base class for all atron units."""

from __future__ import annotations

from typing import TYPE_CHECKING

from utils import DEFAULT_CONTEXT, Context, Counter

if TYPE_CHECKING:
    from utils import Icon


class Atron:
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
    def icon(self) -> Icon:
        """The icon of this atron."""
        raise NotImplementedError("Drone subtypes must implement icon")

    def __str__(self):
        """Return the string representation of this object.

        Returns:
            _type_: The string representation of this object.
        """
        return f"{self.__class__.__name__}"
