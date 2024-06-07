"""A window that displays the map of the game."""

from __future__ import annotations

import tkinter
from typing import TYPE_CHECKING

from utils import Icon, Tile

if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterable, Mapping
    from utils import MapData


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
        self.photo = tkinter.PhotoImage(file="icon.png")
        self.wm_iconphoto(False, self.photo)
        self.geometry("300x300+0+0")
        self.minsize(600, 600)
        self.title(title)
        self._map_data = map_data
        self.log = tkinter.Text(
            self, width=100, height=100, state="normal", wrap="none"
        )
        self.log.pack()

    def prepare_MapWindow(self) -> None:
        """Prepare map by filling it with unknown characters."""
        self.log.config(state="normal")
        for x in range(1, 76):
            for y in range(1, 76):
                self.log.insert(f"{x}.{y}", Icon.UNKNOWN.unicode())
                self.log.insert(tkinter.END, "\n")

        self.log.config(state="disabled")

    def refresh_window(self, zerg_on_map: Iterable[Mapping[str, Any]]) -> None:
        """Refresh MapWindow with any updated coordinates.

        Args:
            zerg_on_map (Iterable[Mapping[str, Any]]): A list of dictionaries
                containing the coordinates and icons of zerg units.
        """
        for tile in self._map_data._visible_tiles_.values():
            self.translate_tile(tile)
        for drone_info in zerg_on_map:
            zerg_tile = Tile(drone_info["coord"], drone_info["icon"])
            self.translate_tile(zerg_tile)

    def translate_tile(self, new_tile: Tile) -> None:
        """Write a tile object to the map.

        new_tile (Tile) : Specifies the tile that should be written into the
            map
        """
        self.log.config(state="normal")
        unicode_character = (
            new_tile.icon.unicode() if new_tile.icon else "\u2061"
        )
        coordinates = f"{new_tile.coordinate[1]}.{new_tile.coordinate[0]}"
        self.log.delete(coordinates)
        self.log.insert(coordinates, unicode_character)
        self.log.config(state="disabled")
