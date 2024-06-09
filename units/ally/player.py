"""Player unit class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from units.ally.atron import Atron
from utils import DEFAULT_CONTEXT, Context, Icon
from utils.directions import Directions

if TYPE_CHECKING:
    from tkinter import Event

    from gui.map_window import MapWindow

DEFAULT_HEALTH = 100
DEFAULT_CAPACITY = 50


class Player(Atron):
    """Player unit class."""

    def __init__(self) -> None:
        super().__init__(DEFAULT_HEALTH, DEFAULT_CAPACITY)
        self._map_window: MapWindow | None = None
        self._l_bind: str | None = None
        self._r_bind: str | None = None
        self._u_bind: str | None = None
        self._d_bind: str | None = None

    @property
    def icon(self) -> Icon:
        """The icon of the player."""
        return Icon.PLAYER

    def deploy_player(self, map_window: MapWindow) -> None:
        """Deploy the player on the map.

        Args:
            map_window (MapWindow): The map window to deploy the player on.
        """
        self._map_window = map_window
        map_data = map_window.map_data
        self._context = map_data.build_context(map_data.landing_zone)

        self._l_bind = map_window.bind("<Left>", self.move_player, add=True)
        self._r_bind = map_window.bind("<Right>", self.move_player, add=True)
        self._u_bind = map_window.bind("<Up>", self.move_player, add=True)
        self._d_bind = map_window.bind("<Down>", self.move_player, add=True)

    def retrieve_player(self) -> None:
        """Retrieve the player from the map."""
        if self._map_window is None:
            return
        self._map_window.unbind("<Left>", self._l_bind)
        self._map_window.unbind("<Right>", self._r_bind)
        self._map_window.unbind("<Up>", self._u_bind)
        self._map_window.unbind("<Down>", self._d_bind)
        self._map_window = None
        self._context: Context = DEFAULT_CONTEXT

    def move_player(self, event: Event) -> None:
        """Move the player on the map.

        Args:
            event (Event): The event that triggered the player movement.
        """
        if self._map_window is None:
            return

        match event.keysym:
            case "Left":
                direction = Directions.WEST
            case "Right":
                direction = Directions.EAST
            case "Up":
                direction = Directions.NORTH
            case "Down":
                direction = Directions.SOUTH
            case _:
                direction = Directions.CENTER
        if direction is not Directions.CENTER:
            new_location = self.context.coord.translate_one(direction)
            self._map_window.map_data.move_to(self, new_location)
        self._map_window.event_generate("<<PlayerMoved>>")
