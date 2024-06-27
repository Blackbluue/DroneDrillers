"""A labeled counter widget."""

from __future__ import annotations

import tkinter as tk

from utils import Counter


class LabeledCounter(tk.Frame):
    """A labeled counter widget."""

    def __init__(
        self,
        owner: tk.Misc,
        label: str,
        counter: Counter | None = None,
        value: int = 0,
        max_value: int = 0,
    ) -> None:
        """Create a labeled counter.

        Args:
            owner (tk.Misc): The owner of the counter.
            label (str): The label to put on the counter.
            counter (Counter, optional): The counter to use.
                Defaults to None
            value (int, optional): The initial value of the counter.
                Defaults to 0.
            max_value (int, optional): The maximum value of the counter.
                Defaults to 0.
        """
        super().__init__(owner)

        if counter:
            self._counter = counter
        else:
            self._counter = Counter(
                master=self, value=value, max_value=max_value
            )

        self._text_label = tk.Label(self, text=f"{label}")
        self._text_label.pack(side=tk.LEFT)

        self._counter_label = tk.Label(self, textvariable=self._counter)
        self._counter_label.pack(side=tk.RIGHT)

    @property
    def counter(self) -> Counter:
        """Return the counter."""
        return self._counter
