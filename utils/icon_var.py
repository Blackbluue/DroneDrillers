"""An icon variable."""

import tkinter as tk

from .icon import Icon


class IconVar(tk.StringVar):
    """An icon variable."""

    def __init__(
        self,
        master: tk.Widget | None = None,
        value: Icon = Icon.UNKNOWN,
        name: str | None = None,
    ) -> None:
        """Create an icon variable.

        Args:
            master (tk.Widget | None, optional): The parent widget. Defaults to None.
            value (Icon, optional): The default icon value. Defaults to Icon.UNKNOWN.
            name (str | None, optional): The name of the icon var. Defaults to None.
        """
        super().__init__(master, value.value, name)

    def get(self) -> Icon:
        return Icon(super().get())

    def set(self, value: Icon) -> None:
        return super().set(value.value)
