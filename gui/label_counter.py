"""A labeled counter widget."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from utils import Counter

if TYPE_CHECKING:
    from .main_controller import MainController


class LabeledCounter(tk.Frame):
    """A labeled counter widget."""

    def __init__(
        self,
        owner: MainController,
        label: str,
        value: int = 0,
        max_value: int = 0,
    ) -> None:
        """Create a labeled counter.

        Args:
            owner (MainController): The owner of the counter.
            label (str): The label to put on the counter.
            default (int): The default value for the counter.
        """
        super().__init__(owner)

        self._counter = Counter(master=self, value=value, max_value=max_value)

        self._text_label = tk.Label(self, text=f"{label}")
        self._text_label.pack(side=tk.LEFT)

        self._counter_label = tk.Label(self, textvariable=self._counter)
        self._counter_label.pack(side=tk.RIGHT)

        self.pack()

    @property
    def counter(self) -> Counter:
        """Return the counter."""
        return self._counter
