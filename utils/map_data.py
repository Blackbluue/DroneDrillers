"""A map made up of tiles."""

from __future__ import annotations

from random import randint, uniform
from typing import TYPE_CHECKING

from .context import Context
from .coordinate import Coordinate
from .directions import Directions
from .icon import Icon
from .tile import Tile

if TYPE_CHECKING:
    from collections.abc import (
        Iterable,
        Iterator,
        MutableMapping,
        MutableSequence,
        Sequence,
    )

    from units.ally.drones import Drone

DEFAULT_LANDING_ZONE = Coordinate(-1, -1)

MIN_DIMENSION = 10
MAX_DIMENSION = 20

MIN_DENSITY = 0.1
MAX_DENSITY = 0.5

ACID_DENSITY = 0.1


class MapData:
    """A map object, used to describe the tile layout of an area."""

    def __init__(self, map_file: str | None) -> None:
        """Initialize a Map object."""
        self._width = 0
        self._height = 0
        self._landing_zone: Coordinate = DEFAULT_LANDING_ZONE
        self._all_tiles: list[MutableSequence[Tile]] = []
        self._visible_tiles: MutableMapping[Coordinate, Tile] = {}
        self._total_minerals: MutableMapping[Coordinate, int] = {}
        self._acid: MutableSequence[Coordinate] = []
        if map_file:
            self._with_file(map_file)
        else:
            self._no_file(
                randint(MIN_DIMENSION, MAX_DIMENSION),
                randint(MIN_DIMENSION, MAX_DIMENSION),
                uniform(MIN_DENSITY, MAX_DENSITY),
            )

    @property
    def landing_zone(self) -> Coordinate:
        """The landing zone for drones."""
        return self._landing_zone

    def _with_file(self, filename: str) -> MapData:
        """Read a map from a file.

        Args:
            filename (str): The name of the file to read.

        Returns:
            MapData: The map object.
        """
        with open(filename, encoding="utf-8") as file_handle:
            for row, line in enumerate(file_handle):
                self._height += 1
                destination = list(line.rstrip())
                cur_width = 0
                tile_row: MutableSequence[Tile] = []
                for column, char in enumerate(destination):
                    cur_width += 1
                    coord = Coordinate(column, row)
                    icon = Icon.MINERAL if char.isdigit() else Icon(char)
                    match icon:
                        case Icon.ACID:
                            self._acid.append(coord)
                        case Icon.DEPLOY_ZONE:
                            self._landing_zone = coord
                        case Icon.MINERAL:
                            self._total_minerals[coord] = int(char)
                    tile_row.append(Tile(coord, icon))
                self._width = max(self._width, cur_width)

                self._all_tiles.append(tile_row)

        return self

    def _no_file(self, width: int, height: int, density: float) -> MapData:
        """Create a map from scratch.

        Args:
            width (int): The width of the map.
            height (int): The height of the map.
            density (float): The density of minerals in the map.

        Returns:
            MapData: The map object.
        """
        self._create_box(width, height)

        self._landing_zone = self._get_rand_coords()
        self._set_actual_tile(self._landing_zone, Icon.DEPLOY_ZONE)

        wall_count = ((width * 2) + (height * 2)) - 4
        total_coordinates = self._width * self._height
        total_minerals = int(density * (total_coordinates - wall_count))
        for _ in range(total_minerals):
            self._add_mineral()

        total_acid = int(
            ACID_DENSITY
            * (total_coordinates - len(self._total_minerals) - wall_count)
        )
        for _ in range(total_acid):
            self._add_acid()
        return self

    def get(self, key: Coordinate, default: Tile | None) -> Tile | None:
        """Get the tile with the specified coordinates from the map.

        Args:
            key (Coordinate): The key to look up.
            default (Tile, optional): A value to return if the
                key is not found. Defaults to None.

        Returns:
            Tile | None: The Tile within this map, or the default value if not found.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_unexplored_tiles(self) -> Sequence[Tile]:
        """Return a list of all unexplored tiles on the map.

        Returns:
            Sequence[Tile]: The unexplored tile list.
        """
        return [
            tile
            for tile in self._visible_tiles.values()
            if not tile.discovered
        ]

    def remove_drone(self, drone: Drone) -> int:
        """Removes drone from map and returns the mined minerals.

        Args:
            drone (Drone): The drone to be removed.

        Returns:
            int: The mined mineral count.
        """
        payload = drone.undeploy_drone()
        self._clear_tile(drone.context.coord)
        return payload

    def reveal_tile(self, coord: Coordinate) -> None:
        """Reveal a tile on the map.

        Args:
            coord (Coordinate): The coordinates of the tile to reveal.
        """
        tile = self._all_tiles[coord.x][coord.y]
        self._visible_tiles[coord] = tile

    def add_drone(self, drone: Drone) -> None:
        """Add a drone to the map.

        The drone cannot be added to the map if the deploy zone is occupied.

        Args:
            drone (Drone): The drone to add to the map.
        """
        # Check if the landing zone is available
        if self._get_actual_tile(self._landing_zone).icon != Icon.DEPLOY_ZONE:
            raise ValueError("Landing zone is occupied")

        drone.deploy_drone(self._build_context(self._landing_zone))
        self._set_actual_tile(self._landing_zone, drone.icon)

    def tick(self, drones: Iterable[Drone]) -> None:
        """Do one tick of the map."""
        for drone in drones:
            for _ in range(drone.moves):
                # acid damage is applied before movement
                if drone.context.coord in self._acid:
                    drone.health.count(-Icon.ACID.health_cost())
                if drone.health.get() <= 0:
                    self._clear_tile(drone.context.coord)
                    drone.undeploy_drone()  # mined minerals lost
                    break  # atron is dead move on to next

                direction = drone.action(drone.context)
                if direction != Directions.CENTER.value:
                    self._move_to(drone, direction)

    def _create_box(self, width: int, height: int) -> None:
        """Create a box around the map.

        This function is used to create a box around the map, with walls
        on the outer edges and empty space inside.

        Args:
            width (int): The width of the map.
            height (int): The height of the map.
        """
        self._width = width
        self._height = height

        for row in range(self._height):
            #  first/last columns are always a wall
            tile_row = [Tile(Coordinate(0, row), Icon.WALL)]
            for column in range(1, self._width - 1):
                coord = Coordinate(column, row)
                if row in [0, self._height - 1]:  # build top/bottom walls
                    tile_row.append(Tile(coord, Icon.WALL))
                else:  # build empty space between walls
                    tile_row.append(Tile(coord, Icon.EMPTY))
            tile_row.append(Tile(Coordinate(self._width - 1, row), Icon.WALL))

            self._all_tiles.append(tile_row)

    def _add_mineral(self) -> None:
        """Adds a single mineral deposit to a random open spot in the map."""
        coordinates = self._get_rand_coords()

        self._set_actual_tile(coordinates, Icon.MINERAL)
        self._total_minerals[coordinates] = randint(1, 9)

    def _add_acid(self) -> None:
        """Adds a single acid tile to a random open spot in the map."""
        coordinates = self._get_rand_coords()

        self._set_actual_tile(coordinates, Icon.ACID)
        self._acid.append(coordinates)

    def _get_actual_tile(self, coord: Coordinate) -> Tile:
        """Get the actual tile at the given coordinates.

        Args:
            coord (Coordinate): The coordinates to look up.

        Returns:
            Tile: The tile at the given coordinates.
        """
        return self._all_tiles[coord.y][coord.x]

    def _set_actual_tile(self, coord: Coordinate, icon: Icon) -> None:
        """Set the actual icon of a tile at the given coordinates.

        Args:
            coord (Coordinate): The coordinates to set.
            icon (Icon): The icon to set.
        """
        self._all_tiles[coord.y][coord.x].icon = icon

    def _get_rand_coords(self) -> Coordinate:
        """Get a random set of coordinates on the map.

        Returns:
            Coordinate: A set of coordinates on the map.
        """
        x_coords: int = self._width - 2
        y_coords: int = self._height - 2
        coordinates = Coordinate(0, 0)
        while self._get_actual_tile(coordinates).icon != Icon.EMPTY:
            # Choose a random location on map excluding walls
            coordinates = Coordinate(
                randint(1, x_coords),
                randint(1, y_coords),
            )
        return coordinates

    def _build_context(self, location: Coordinate) -> Context:
        """Build a context object for the given location.

        Args:
            location (Coordinate): The location to build the context for.

        Returns:
            Context: The context object.
        """
        cardinals = [
            *map(
                lambda tile: self._get_actual_tile(tile).icon,
                location.cardinals(),
            )
        ]
        return Context(location, *cardinals)

    def _clear_tile(self, pos: Coordinate) -> None:
        """Clear the tile at the given coordinates.

        Args:
            pos (Coordinate): The coordinates of the tile to update.
        """
        if pos == self._landing_zone:
            self._set_actual_tile(pos, Icon.DEPLOY_ZONE)
        elif pos in self._acid:
            self._set_actual_tile(pos, Icon.ACID)
        else:
            self._set_actual_tile(pos, Icon.EMPTY)

    def _move_to(self, drone: Drone, dirc: str) -> None:
        """Move the drone in the given direction.

        Args:
            d_context (Drone): The drone to move.
            dirc (str): The direction to move the drone.
        """
        cur_loc = drone.context.coord
        new_location = cur_loc.translate_one(dirc)

        match self._get_actual_tile(new_location):
            case Icon.ATRON | Icon.MINER | Icon.SCOUT:
                pass  # Another Drone is already there
            case (
                Icon.DEPLOY_ZONE | Icon.ACID | Icon.EMPTY
            ):  # Drone can move here
                self._clear_tile(cur_loc)
                self._set_actual_tile(new_location, drone.icon)
                drone.context = self._build_context(new_location)
            case Icon.WALL:  # Drone hits a wall
                drone.health.count(-Icon.WALL.health_cost())
            case Icon.MINERAL:  # Drone mines a mineral
                self._total_minerals[new_location] -= 1
                drone.payload.count(1)
                if self._total_minerals[new_location] <= 0:
                    self._clear_tile(new_location)
                    del self._total_minerals[new_location]

    def __getitem__(self, key: Coordinate) -> Tile:
        """Get the tile with the specified coordinates from the map.

        Args:
            key (Coordinate): The key to look up.

        Raises:
            KeyError: If no Tile with the given coordinates exists in this map.

        Returns:
            Tile: The Tile within this map.
        """
        return self._visible_tiles[key]

    def __iter__(self) -> Iterator[Tile]:
        """Iterate over the visible tiles in this map.

        Yields:
            Iterator[Tile]: The visible tiles in this map.
        """
        yield from self._visible_tiles.values()

    def __repr__(self) -> str:
        """Return a representation of this object.

        The string returned by this method is not valid for a call to eval.

        Returns:
            str: The string representation of this object.
        """
        return "\n".join(
            "".join([tile.icon.value for tile in row if tile.icon])
            for row in self._all_tiles
        )
