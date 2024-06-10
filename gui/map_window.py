"""A window that displays the map of the game."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from .graphic_tile import GraphicTile

if TYPE_CHECKING:
    from utils import MapData


class MapWindow(tk.Toplevel):
    """A window that displays the map of the game."""

    def __init__(
        self, parent: tk.Toplevel, title: str, map_data: MapData
    ) -> None:
        """Initialize the GUI map.

        Args:
            parent (tk.Toplevel): The parent window.
            title (str): The title of this window.
            physical_map (MapWindow): The actual data for the map window.
        """
        super().__init__(parent)
        self._photo = tk.PhotoImage(file="icon.png")
        self.wm_iconphoto(False, self._photo)
        self.geometry("300x300+0+0")
        self.minsize(600, 600)
        self.title(title)
        self._map_data = map_data
        self._map_frame = tk.Frame(self)
        for tile in iter(self._map_data):
            GraphicTile(self._map_frame, tile)
        self._map_frame.pack()

    @property
    def map_data(self) -> MapData:
        """The map data for this window."""
        return self._map_data
