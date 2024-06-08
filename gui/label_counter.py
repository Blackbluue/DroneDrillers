from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main_controller import MainController


class LabeledCounter(tk.Frame):
    """A labeled entry widget to count resources."""

    def __init__(
        self, owner: MainController, label: str, default: int
    ) -> None:
        """Create a labeled counter.

        Args:
            owner (MainController): The owner of the counter.
            label (str): The label to put on the counter.
            default (int): The default value for the counter.
        """
        super().__init__(owner)
        self._label = tk.Label(self, text=f"{label}", width=20)
        self._label.pack(side=tk.LEFT)

        self._counter = tk.Label(self, text=f"{default}/{default}", width=10)
        self._counter.pack(side=tk.RIGHT)

        self._default = default
        self._value = default

        self.pack()

    @property
    def value(self) -> int:
        """The value of the counter."""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        """Set the value of the counter.

        Args:
            value (int): The new value to set.
        """
        if value < 0:
            value = 0
        elif value > self._default:
            value = self._default
        self._value = value
        self._counter.config(text=f"{value}/{self._default}")

    def reset(self) -> None:
        """Reset the counter to its default value."""
        self._value = self._default
        self._counter.config(text=f"{self._default}/{self._default}")
