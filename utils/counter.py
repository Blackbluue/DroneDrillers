"""A counter variable."""

import tkinter as tk


class Counter(tk.IntVar):
    """A counter variable."""

    def __init__(
        self,
        master: tk.Widget | None = None,
        value: int = 0,
        name: str | None = None,
        max_value: int = 0,
    ) -> None:
        """Create a counter variable.

        Args:
            master (tk.Widget): The parent widget.
            value (int): The default value for the counter.
            name (str): The name of the counter.
            max_value (int): The maximum value for the counter.
        """
        super().__init__(master, value, name)
        if value < 0:
            raise ValueError("Value must be non-negative.")
        if max_value < value:
            raise ValueError(
                "Max value must be greater than or equal to value."
            )
        self._start = value
        self._max_value = max_value

    def set(self, value: int) -> None:
        if value < 0:
            value = 0
        elif value > self._max_value:
            value = self._max_value
        return super().set(value)

    def count_up(self) -> None:
        """Increment the counter by 1."""
        super().set(self.get() + 1)

    def count_down(self) -> None:
        """Decrement the counter by 1."""
        super().set(self.get() - 1)

    def reset(self) -> None:
        """Reset the counter to its default value."""
        super().set(self._start)
