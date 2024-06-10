"""Graphical representation of a tile on the map."""

from __future__ import annotations

from tkinter import Label
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tkinter import Frame

    from utils.tile import Tile


class GraphicTile(Label):
    """Graphical representation of a tile on the map."""

    def __init__(self, master: Frame, tile: Tile) -> None:
        """Initialize the tile.

        Args:
            master: The parent widget.
            tile (Tile): The Tile.
        """
        super().__init__(master, textvariable=tile.icon_var)
        self._map_frame = master
        self._tile = tile

        self.grid(row=tile.coordinate.y, column=tile.coordinate.x)

    @property
    def tile(self):
        """The tile."""
        return self._tile
