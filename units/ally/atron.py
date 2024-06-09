"""Abstract base class for all atron units."""

from utils import Counter


class Atron:
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

    def __str__(self):
        """Return the string representation of this object.

        Returns:
            _type_: The string representation of this object.
        """
        return f"{self.__class__.__name__}"
