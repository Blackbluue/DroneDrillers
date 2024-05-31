"""A single tile on the map."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .icon import Icon

if TYPE_CHECKING:
    from typing import Optional

    from units.ally.drones import Drone

    from .coordinate import Coordinate


class Tile:
    """A single tile on the map."""

    def __init__(self, coordinate: Coordinate, icon: Optional[Icon] = None):
        """Initialize the tile.

        Args:
            coordinate (Coordinate): The coordinate of this tile.
            icon (Optional[Icon], optional): The icon on this tile, if
                discovered. Defaults to None.
        """
        self._coordinate = coordinate
        self._icon = icon
        self._occupation: Optional[Drone] = None

    @property
    def coordinate(self) -> Coordinate:
        """The coordinates of this tile on the map."""
        return self._coordinate

    @property
    def icon(self) -> Optional[Icon]:
        """The icon for this tile.

        Setting the icon for a tile implicitly makes it discovered. If a tile
        is not discovered, the icon will always be None.
        """
        return self._occupation.icon if self._occupation else self._icon

    @icon.setter
    def icon(self, icon: Icon) -> None:
        if not icon:
            raise ValueError("Cannot set icon to None")
        self._icon = icon

    @property
    def discovered(self) -> bool:
        """True if the tile has been discovered and has an icon, else False."""
        return bool(self.icon)

    @property
    def occupied_drone(self) -> Optional[Drone]:
        """The drone occupying this tile, which may be None."""
        return self._occupation

    @occupied_drone.setter
    def occupied_drone(self, drone: Optional[Drone]):
        if drone:
            self._occupy(drone)
        else:
            self._unoccupy()

    def _occupy(self, drone: Drone) -> bool:
        """Occupy this tile with an atron drone.

        An occupied tile will return an atron icon for the icon property. An
        occupied tile will remember the icon that was on it before the atron
        occupied it. Trying to occupy a tile that is already occupied, or has
        a wall or mineral icon will fail. An undiscovered tile cannot be
        occupied. Trying to occupy an undiscovered tile will raise an exception

        Raises:
            RuntimeError: If the tile is undiscovered, and therefore cannot
                be occupied.

        Returns:
            bool: Whether occupation of the tile succeeded.
        """
        if not self.icon:
            raise RuntimeError("An undiscovered tile cannot be occupied")
        if not self.icon.traversable():
            return False
        # self._old_icon = self.icon
        # self._icon = Icon.ATRON
        self._occupation = drone
        return True

    def _unoccupy(self) -> bool:
        """Unoccupy this tile with an atron drone.

        Unoccupying a tile will cause the original icon on the tile to returned
        by the icon property. Trying to unoccupy a tile that was not unoccupied
        will fail with no operation happening. Trying to unoccupy an
        undiscovered tile will raise an exception.

        Raised:
            RuntimeError: If the tile is undiscovered, and therefor cannot be
                unoccupied.

        Returns:
            bool: Whether the tile was able to be unoccupied.
        """
        if not self.discovered:
            raise RuntimeError("An undiscovered tile cannot be unoccupied")
        if not self._occupation:
            return False
        # self._icon = self._old_icon
        self._occupation = None
        return True

    def __eq__(self, __o):
        """Compare if this object is equal to the other object.

        Args:
            __o : The other object.

        Returns:
            bool: If this object is equal to the other object
        """
        return (
            self._coordinate == __o._coordinate
            if isinstance(__o, Tile)
            else NotImplemented
        )

    def __lt__(self, __o):
        # it isn't actually sensible to ever see if a tile is 'less
        # than' another tile, but the built-in pqueue requires it
        # in the case that two priority values in the queue are the
        # same upon insertion.
        coord = self.coordinate
        other_coord = __o.coordinate
        return (
            self
            if abs(coord.x + coord.y) < abs(other_coord.x + other_coord.y)
            else __o
        )

    def __str__(self) -> str:
        icon_msg = f"Icon: {self.icon.value}" if self.icon else "Undiscovered"
        return f"Tile({self.coordinate}, {icon_msg})"

    def __repr__(self) -> str:
        return f"Tile({self.coordinate}, {self.icon})"

    def __hash__(self) -> int:
        """The hash value of this object.

        Returns:
            int: This object's hash value.
        """
        return hash(self.coordinate)
