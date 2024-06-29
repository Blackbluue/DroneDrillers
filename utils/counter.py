"""A counter variable."""

import tkinter as tk

DEFAULT_VALUE = -1


class Counter(tk.IntVar):
    """A counter variable."""

    def __init__(
        self,
        master: tk.Widget | None = None,
        name: str | None = None,
        value: int | None = None,
        max_value: int | None = None,
    ) -> None:
        """Create a counter variable.

        Args:
            master (tk.Widget | None, optional): The parent widget. Defaults to None.
            name (str | None, optional): The name of the counter.. Defaults to None.
            value (int): The default value for the counter.
            max_value (int): The maximum value for the counter.
        """
        super().__init__(master, value, name)
        if value is not None and value < 0:
            raise ValueError("Value must be non-negative.")
        if value is None:
            value = 0
        if max_value is not None and max_value < value:
            raise ValueError(
                "Max value must be greater than or equal to value."
            )
        if max_value is None:
            max_value = DEFAULT_VALUE
        self._start = value

        self._max_value = max_value

    def set(self, value: int) -> None:
        if value < 0:
            value = 0
        elif self._max_value != DEFAULT_VALUE and value > self._max_value:
            value = self._max_value
        return super().set(value)

    def count(self, value: int) -> None:
        """Add the given value to the counter.

        Args:
            value (int): The value to add to the counter.
        """
        self.set(self.get() + value)

    def reset(self) -> None:
        """Reset the counter to its default value."""
        self.set(self._start)
