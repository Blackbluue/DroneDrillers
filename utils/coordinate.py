"""(X, Y) coordinates for a grid system."""

from __future__ import annotations

from typing import NamedTuple

from .directions import Directions


class Coordinate(NamedTuple):
    """(X, Y) coordinates for a grid system."""

    x: int
    y: int

    def difference(self, other_coord: Coordinate) -> tuple[int, int]:
        """Get the difference in distance between 2 coordinates.

        In relation to this coordinate, a positive/negative return value will
        indicate direction; a positive  x means the other coordinate is to the
        right of this one, while a positive y means the other coordinate is
        below this one, and reversed for negative values.

        Args:
            other_coord (Coordinate): The other coordinate.

        Returns:
            tuple[int, int]: The distance difference, as (x, y) tuple.
        """
        return (other_coord.x - self.x, other_coord.y - self.y)

    def direction(self, other_coord: Coordinate) -> str:
        """Get the direction of the other coordinate in relation to this one.

        Note that this only works if this coordinate and the other are on the
        same axis as each other. Otherwise an empty string will be returned.
        If the 2 coordinates are the same, 'center' will be returned.

        Args:
            other_coord (Coordinate): The other coordinate.

        Returns:
            str: The direction of the other coordinate.
        """
        x_offset, y_offset = self.difference(other_coord)
        if x_offset and y_offset:
            return ""  # can't determine direction
        if x_offset > 0:
            return "east"
        if x_offset < 0:
            return "west"
        if y_offset < 0:
            return "north"
        return "south" if y_offset > 0 else "center"

    def cardinals(
        self,
    ) -> tuple[Coordinate, Coordinate, Coordinate, Coordinate]:
        """Return translated coordinate objects in the 4 cardinal directions.

        The order returned is North, South, East, West.

        Returns:
            Tuple[Coordinate, Coordinate, Coordinate, Coordinate]:
                The translated coordinates.
        """
        return (
            self.translate_one(Directions.NORTH),
            self.translate_one(Directions.SOUTH),
            self.translate_one(Directions.EAST),
            self.translate_one(Directions.WEST),
        )

    def translate_one(self, direction: str | Directions) -> Coordinate:
        """Translate this coordinate in the given direction.

        Translation moves the coordinate by 1 space in the given direction.
        This method will always return a new object. If Directions.CENTER is
        given, this coordinate is copied and returned.

        Args:
            direction (str | Directions): The direction to translate.

        Returns:
            Coordinate: The translated coordinate object.
        """
        if isinstance(direction, str):
            try:
                direction = Directions[direction.upper()]
            except KeyError:
                raise ValueError(f"Unknown  direction: {direction}") from None
        match direction:
            case Directions.NORTH:
                return self._replace(y=self.y - 1)  # pylint: disable=no-member
            case Directions.SOUTH:
                return self._replace(y=self.y + 1)  # pylint: disable=no-member
            case Directions.EAST:
                return self._replace(x=self.x + 1)  # pylint: disable=no-member
            case Directions.WEST:
                return self._replace(x=self.x - 1)  # pylint: disable=no-member
            case _:  # Directions.CENTER
                return Coordinate(self.x, self.y)

    def translate(self, x_offset: int, y_offset: int) -> Coordinate:
        """Translate this coordinate in the given direction.

        Translation moves the coordinate by the given direction offset.
        This method will always return a new object. If both x_offset and
        y_offset are 0, this coordinate is copied and returned.

        Args:
            x_offset (int): The offset to move in the x direction.
            y_offset (int): The offset to move in the y direction.

        Returns:
            Coordinate: The translated coordinate object
        """
        return self._replace(  # pylint: disable=no-member
            x=self.x + x_offset, y=self.y + y_offset
        )
