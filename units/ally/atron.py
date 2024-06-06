"""Abstract base class for all atron units."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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
        self._health = health
        self._MAX_HEALTH = health

    @property
    def health(self) -> int:
        """The current health of this atron.

        Returns:
            int: The current health.
        """
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        """Set the health of this atron.

        If set to a negative value, the health will be set to 0. The health
        also cannot exceed the maximum health, which is set at initialization.

        Args:
            value (int): The new health value.
        """
        self._health = value
        if self._health < 0:
            self._health = 0
        elif self._health > self._MAX_HEALTH:
            self._health = self._MAX_HEALTH

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
