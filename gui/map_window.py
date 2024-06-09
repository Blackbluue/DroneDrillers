"""A window that displays the map of the game."""

from __future__ import annotations

import itertools
import tkinter
from typing import TYPE_CHECKING

from utils import Icon, Tile

if TYPE_CHECKING:
    from utils import MapData


MAX_SIZE = 76


class MapWindow(tkinter.Toplevel):
    """A window that displays the map of the game."""

    def __init__(
        self, parent: tkinter.Toplevel, title: str, map_data: MapData
    ) -> None:
        """Initialize the GUI map.

        Args:
            parent (tkinter.Toplevel): The parent window.
            title (str): The title of this window.
            physical_map (MapWindow): The actual data for the map window.
        """
        super().__init__(parent)
        self._photo = tkinter.PhotoImage(file="icon.png")
        self.wm_iconphoto(False, self._photo)
        self.geometry("300x300+0+0")
        self.minsize(600, 600)
        self.title(title)
        self._map_data = map_data
        self._log = tkinter.Text(
            self, width=100, height=100, state="normal", wrap="none"
        )
        self._log.pack()

    def prepare_window(self) -> None:
        """Prepare map by filling it with unknown characters."""
        self._log.config(state="normal")
        for x_axis, y_axis in itertools.product(
            range(1, MAX_SIZE), range(1, MAX_SIZE)
        ):
            self._log.insert(f"{x_axis}.{y_axis}", Icon.UNKNOWN.unicode())
            self._log.insert(tkinter.END, "\n")

        self._log.config(state="disabled")

    def refresh_window(self) -> None:
        """Refresh MapWindow with any updated coordinates."""
        for tile in iter(self._map_data):
            self.translate_tile(tile)

    def translate_tile(self, new_tile: Tile) -> None:
        """Write a tile object to the map.

        new_tile (Tile) : Specifies the tile that should be written into the
            map
        """
        self._log.config(state="normal")
        unicode_character = (
            new_tile.icon.unicode() if new_tile.icon else "\u2061"
        )
        coordinates = f"{new_tile.coordinate[1]}.{new_tile.coordinate[0]}"
        self._log.delete(coordinates)
        self._log.insert(coordinates, unicode_character)
        self._log.config(state="disabled")
