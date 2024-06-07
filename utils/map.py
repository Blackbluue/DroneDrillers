"""A map made up of tiles."""

from __future__ import annotations

from queue import PriorityQueue
from random import randint
from typing import TYPE_CHECKING

from .context import Context
from .coordinate import Coordinate
from .directions import Directions
from .icon import Icon
from .tile import Tile

if TYPE_CHECKING:
    from collections.abc import (
        Iterable,
        MutableMapping,
        MutableSequence,
        MutableSet,
        Sequence,
    )

    from units.ally.drones import Drone

_NODE_WEIGHTS = {
    Icon.EMPTY: 1,
    Icon.ATRON: 1,
    Icon.DEPLOY_ZONE: 1,
    Icon.ACID: 10,
    None: 1,
}

DEFAULT_LANDING_ZONE = Coordinate(-1, -1)

class MapData:
    """A map object, used to describe the tile layout of an area."""

    def __init__(self) -> None:
        """Initialize a Map object."""
        self._width = 0
        self._height = 0
        self._total_coordinates = 0
        self._landing_zone: Coordinate = DEFAULT_LANDING_ZONE
        self._all_tiles: list[list[Tile]] = []
        self._visible_tiles_: MutableMapping[Coordinate, Tile] = {}
        self._total_minerals: MutableMapping[Coordinate, int] = {}
        self._acid: list[Coordinate] = []
        # a set of the coords of minerals and drone id tasked to mining it
        self.untasked_minerals: MutableSet[Coordinate] = set()
        self.tasked_minerals: MutableSet[Coordinate] = set()
        self.scout_count = 0

    @property
    def landing_zone(self) -> Coordinate:
        """The landing zone for drones."""
        return self._landing_zone

    def from_file(self, filename: str) -> MapData:
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
                tile_row: Sequence[Tile] = []
                for column, char in enumerate(destination):
                    cur_width += 1
                    coord = Coordinate(column, row)
                    if char == "~":
                        self._acid.append(coord)
                    elif char == "_":
                        self._landing_zone = coord
                    elif char in "0123456789":
                        destination[column] = "*"
                        self._total_minerals[coord] = int(char)
                    tile_row.append(Tile(coord, Icon(char)))
                self._width = max(self._width, cur_width)

                self._all_tiles.append(tile_row)

        self._total_coordinates = self._width * self._height
        return self

    def from_scratch(self, width: int, height: int, density: float) -> MapData:
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
        total_minerals = int(density * (self._total_coordinates - wall_count))
        for _ in range(total_minerals):
            self.add_mineral(randint(1, 9))

        # TODO: add acid
        return self

    def task_miner(self, miner: Drone) -> None:
        """Task the miner with mining an available mineral.

        The miner will have their path variable set, and the mineral
        they are tasked with will be removed from the untasked_minerals
        set.

        Args:
            miner (Drone): The miner to task.
        """
        mineral = self.untasked_minerals.pop()
        self.tasked_minerals.add(mineral)
        miner.path = self.dijkstra(self._landing_zone, mineral)

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
            for tile in self._visible_tiles_.values()
            if not tile.discovered
        ]

    def add_mineral(self, amt: int) -> None:
        """Adds a single mineral deposit to a random open spot in the map.

        Args:
            amt (int): The size of the mineral deposit.
        """
        coordinates = self._get_rand_coords()

        self._set_actual_tile(coordinates, Icon.MINERAL)
        self._total_minerals[coordinates] = amt

    def dijkstra(
        self, start: Coordinate, end: Coordinate
    ) -> MutableSequence[Coordinate]:
        """Apply Dijkstra's Algorithm to find a path between two points.

        Args:
            start (Coordinate): The start point for the search
            end (Coordinate): The end point for the search
        Returns:
            list[Coordinate]: Path in the form of a Coordinate list
        """
        visited: set[Coordinate] = set()
        parents_map: dict[Coordinate, Coordinate] = {}
        path_found = False
        pqueue: PriorityQueue[tuple[int, Coordinate]] = PriorityQueue()
        pqueue.put((0, start))
        while not pqueue.empty():
            _, node = pqueue.get()
            if node in visited:
                continue
            if node == end:
                path_found = True
                break

            neighbors = node.cardinals()
            if end in neighbors:
                path_found = True
                parents_map[end] = node
                break

            visited.add(node)
            neighbors_gen = (
                neighbor for neighbor in neighbors if neighbor not in visited
            )
            self._add_to_path(
                node,
                neighbors_gen,
                parents_map,
                pqueue,
            )
        return (
            self._build_final_path(start, end, parents_map)
            if path_found
            else []
        )

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
        self._visible_tiles_[coord] = tile

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
                    drone.health -= Icon.ACID.health_cost()
                if drone.health <= 0:
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
        self._total_coordinates = self._width * self._height

        for row in range(self._height):
            #  first/last columns are always a wall
            tile_row: Sequence[Tile] = [Tile(Coordinate(0, row), Icon.WALL)]
            for column in range(1, self._width - 1):
                coord = Coordinate(column, row)
                if row in [0, self._height - 1]:  # build top/bottom walls
                    tile_row.append(Tile(coord, Icon.WALL))
                else:  # build empty space between walls
                    tile_row.append(Tile(coord, Icon.EMPTY))
            tile_row.append(Tile(Coordinate(self._width - 1, row), Icon.WALL))

            self._all_tiles.append(tile_row)

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

    def _add_to_path(
        self,
        node: Coordinate,
        neighbors: Iterable[Coordinate],
        parents_map: MutableMapping[Coordinate, Coordinate],
        pqueue: PriorityQueue[tuple[int, Coordinate]],
    ) -> None:
        """Add neighbors to the path.

        Args:
            node (Coordinate): Starting node.
            neighbors (Iterable[Coordinate]): Neighbors of the node.
            parents_map (MutableMapping[Coordinate, Coordinate]): Map of path.
            pqueue (PriorityQueue[tuple[int, Coordinate]]): Final path.
        """
        for neighbor_coord in neighbors:
            if (neighbor := self.get(neighbor_coord, None)) is None:
                # tile not in map
                continue
            if neighbor.icon and neighbor.icon not in _NODE_WEIGHTS:
                # tile not pathable
                continue
            parents_map[neighbor.coordinate] = node
            pqueue.put((_NODE_WEIGHTS[neighbor.icon], neighbor.coordinate))

    def _build_final_path(
        self,
        start: Coordinate,
        end: Coordinate,
        parents_map: MutableMapping[Coordinate, Coordinate],
    ) -> MutableSequence[Coordinate]:
        """Build the final path from start to end.

        Args:
            start (Coordinate): The starting point.
            end (Coordinate): The ending point.
            parents_map (MutableMapping[Coordinate, Coordinate]): The path.

        Returns:
            MutableSequence[Coordinate]: The final path.
        """
        curr = end
        final_path: list[Coordinate] = [end]
        while curr != start:
            coord = parents_map[curr]
            final_path.append(coord)
            curr = coord
            if start in coord.cardinals():
                break
        final_path.append(start)
        final_path = final_path[::-1]
        return final_path

    def _track_mineral(self, icon: Icon, coordinate: Coordinate) -> None:
        """Track the mineral at the given coordinates.

        Args:
            icon (Icon): The icon of the mineral.
            coordinate (Coordinate): The coordinates of the mineral.
        """
        if icon == Icon.MINERAL and coordinate not in self.tasked_minerals:
            self.untasked_minerals.add(coordinate)

    def _build_context(self, location: Coordinate) -> Context:
        """Build a context object for the given location.

        Args:
            location (Coordinate): The location to build the context for.

        Returns:
            Context: The context object.
        """
        cardinals = [
            *map(lambda tile: self._get_actual_tile(tile).icon,
                 Coordinate(5, 5).cardinals())
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
                drone.health -= Icon.WALL.health_cost()
            case Icon.MINERAL:  # Drone mines a mineral
                self._total_minerals[new_location] -= 1
                drone.payload += 1
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
        return self._visible_tiles_[key]

    def __iter__(self):
        """Iterate over this map.

        Yields:
            _type_: The iterator.
        """
        yield from self._visible_tiles_.values()

    def __repr__(self) -> str:
        """Return a representation of this object.

        The string returned by this method is not valid for a call to eval.

        Returns:
            str: The string representation of this object.
        """
        return "\n".join(
            "".join(
                [tile.icon.value for tile in row if tile.icon]
            ) for row in self._all_tiles
        )
