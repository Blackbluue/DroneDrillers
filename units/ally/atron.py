"""Abstract base class for all atron units."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from utils import Counter

if TYPE_CHECKING:
    from utils import Context


class Atron(ABC):
    """Abstract base class for all atron units."""

    def __init__(self, health: int) -> None:
        """Initialize a atron unit.

        The atron's health must be at least 1.

        Raises:
            ValueError: if the passed in health is less than 1

        Args:
            health (int): The atron's maximum health.
        """
        if health <= 0:
            raise ValueError("Atron health must be 1 or greater")
        self._health = Counter(value=health, max_value=health)

    @property
    def health(self) -> Counter:
        """The current health of this atron.

        Returns:
            Counter: The current health.
        """
        return self._health

    @abstractmethod
    def action(self, context: Context) -> str:
        """Perform some action, based on the type of atron.

        Args:
            context (Context): The context surrounding the atron.

        Returns:
            str: The action the atron wants to take.
        """
        raise NotImplementedError("Atron subtypes must implement action")

    def __str__(self):
        """Return the string representation of this object.

        Returns:
            _type_: The string representation of this object.
        """
        return f"{self.__class__.__name__}"
