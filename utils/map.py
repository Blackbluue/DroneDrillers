"""A map made up of tiles."""

from __future__ import annotations

from queue import PriorityQueue
from random import randint
from typing import TYPE_CHECKING, overload

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


class MineralContext:
    def __init__(self, location: Coordinate, amt: int) -> None:
        self.loc: Coordinate = location
        self.amt: int = amt

    def __repr__(self) -> str:
        return f"MineralContext({repr(self.loc)}, {self.amt})"


class DroneContext:
    def __init__(self, context: Context, atron: Drone, health: int) -> None:
        self.context: Context = context
        self.atron: Drone = atron
        # TODO: This should be maintained independent of whichever map they are on
        self.health: int = health
        self.mined_mineral = 0


class MapData:
    """A map object, used to describe the tile layout of an area."""

    NODE_WEIGHTS = {
        Icon.EMPTY: 1,
        Icon.ATRON: 1,
        Icon.DEPLOY_ZONE: 1,
        Icon.ACID: 10,
        None: 1,
    }

    def __init__(self, map_id: int) -> None:
        """Initialize a Map object.

        Args:
            map_id (int): The ID of the map.
        """
        self.map_id = map_id
        self.d_contexts: list[DroneContext] = []
        self._all_icons: list[list[Icon]] = []
        self._total_minerals: list[MineralContext] = []
        self._acid: list[Coordinate] = []
        # a set of the coords of minerals and drone id tasked to mining it
        self.untasked_minerals: MutableSet[Coordinate] = set()
        self.tasked_minerals: MutableSet[Coordinate] = set()
        self._visible_tiles_: MutableMapping[Coordinate, Tile] = {}
        self.scout_count = 0

    def from_file(self, filename: str) -> MapData:
        with open(filename) as fh:
            for row, line in enumerate(fh):
                destination = list(line.rstrip())
                for column, char in enumerate(destination):
                    coord = Coordinate(column, row)
                    if char == "~":
                        self._acid.append(coord)
                    elif char == "_":
                        self.landing_zone = coord
                    elif char in "0123456789":
                        destination[column] = "*"
                        mineral_context = MineralContext(coord, int(char))
                        self._total_minerals.append(mineral_context)

                self._all_icons.append([Icon(char) for char in destination])

        self._set_dimensions(column, row)
        return self

    def from_scratch(self, width: int, height: int, density: float) -> MapData:
        self._set_dimensions(width, height)
        self._create_box()

        self.landing_zone = self._get_rand_coords()
        self._set_actual_icon(self.landing_zone, Icon.DEPLOY_ZONE)

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
        miner.path = self.dijkstra(self.landing_zone, mineral)

    @overload
    def get(self, key: Tile | Coordinate, default: None) -> Tile | None:
        pass

    @overload
    def get(self, key: Tile | Coordinate, default: Tile) -> Tile:
        pass

    def get(self, key, default):
        """Get the tile with the specified coordinates from the map.

        A Tile or Coordinate object may be passed in as the key; if a Tile is
        given, only it's coordinate attribute will be used in look up.

        Args:
            key (Tile | Coordinate): The key to look up.
            default (Tile, optional): A value to return if the
                key is not found. Defaults to None.

        Returns:
            Tile | None: The Tile within this map, or None if not found.
        """
        try:
            return self.__getitem__(key)
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

        self._set_actual_icon(coordinates, Icon.MINERAL)
        mineral_context = MineralContext(coordinates, amt)
        self._total_minerals.append(mineral_context)

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

    def summary(self) -> float:
        """Ratio of total minerals to reachable tiles.

        Returns:
            float: The ratio of total minerals to reachable tiles.
        """
        wall_count = sum(row.count(Icon.WALL) for row in self._all_icons)
        total_minerals = sum(mineral.amt for mineral in self._total_minerals)
        return total_minerals / (self._total_coordinates - wall_count)

    def remove_atron(self, atron_id: int) -> tuple[int, int] | None:
        """Removes atron from map and returns the mineral and health.

        Args:
            atron_id (int): The id of the atron to be removed.

        Returns:
            tuple[int, int] | None:
                The mined mineral count and health of the removed drone, or None.
        """
        for drone_context in self.d_contexts:
            if (
                atron_id == id(drone_context.atron)
                and drone_context.context.coord == self.landing_zone
            ):
                self._set_actual_icon(
                    drone_context.context.coord, Icon.DEPLOY_ZONE
                )
                self.d_contexts.remove(drone_context)
                return drone_context.mined_mineral, drone_context.health

    def add_atron(self, atron: Drone, health: int) -> bool:
        """Add an atron to the map.

        The atron cannot be added to the map if the deploy zone is occupied.

        Args:
            atron (Drone): The atron to add to the map.
            health (int): The health of the atron.

        Returns:
            bool: True if the atron was added, else False.
        """
        # Check if the landing zone is available
        if self._get_actual_icon(self.landing_zone) != Icon.DEPLOY_ZONE:
            return False
        self._set_actual_icon(self.landing_zone, atron.icon)

        context = self._build_context(self.landing_zone)
        drone_context = DroneContext(context, atron, health)
        self.d_contexts.append(drone_context)
        return True

    def tick(self) -> None:
        for d_context in self.d_contexts:
            for _ in range(d_context.atron.moves):
                # acid damage is applied before movement
                if d_context.context.coord in self._acid:
                    d_context.health -= Icon.ACID.health_cost()
                if d_context.health <= 0:
                    self._clear_tile(d_context.context.coord)
                    self.d_contexts.remove(d_context)
                    break  # atron is dead move on to next

                direction = d_context.atron.action(d_context.context)
                if direction != Directions.CENTER.value:
                    self._move_to(d_context, direction)

    def _set_dimensions(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._total_coordinates = self._width * self._height

    def _create_box(self) -> None:
        """Create a box around the map.

        This function is used to create a box around the map, with walls
        on the outer edges and empty space inside.
        """
        self._all_icons.append([Icon(char) for char in ["#"] * self._width])
        for _ in range(self._height):
            self._all_icons.append(
                [Icon(char) for char in f"#{' ' * (self._width - 2)}#"]
            )
        self._all_icons.append([Icon(char) for char in ["#"] * self._width])

    def _get_actual_icon(self, coord: Coordinate) -> Icon:
        """Get the actual icon at the given coordinates.

        Args:
            coord (Coordinate): The coordinates to look up.

        Returns:
            Icon: The icon at the given coordinates.
        """
        return self._all_icons[coord.y][coord.x]

    def _set_actual_icon(self, coord: Coordinate, icon: Icon) -> None:
        """Set the actual icon at the given coordinates.

        Args:
            coord (Coordinate): The coordinates to set.
            icon (Icon): The icon to set.
        """
        self._all_icons[coord.y][coord.x] = icon

    def _get_rand_coords(self) -> Coordinate:
        """Get a random set of coordinates on the map.

        Returns:
            Coordinate: A set of coordinates on the map.
        """
        x_coords: int = self._width - 2
        y_coords: int = self._height - 2
        coordinates = Coordinate(0, 0)
        while self._get_actual_icon(coordinates) != Icon.EMPTY:
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
        for neighbor_coord in neighbors:
            if (neighbor := self.get(neighbor_coord, None)) is None:
                # tile not in map
                continue
            if neighbor.icon and neighbor.icon not in self.NODE_WEIGHTS:
                # tile not pathable
                continue
            parents_map[neighbor.coordinate] = node
            pqueue.put((self.NODE_WEIGHTS[neighbor.icon], neighbor.coordinate))

    def _build_final_path(
        self,
        start: Coordinate,
        end: Coordinate,
        parents_map: MutableMapping[Coordinate, Coordinate],
    ) -> MutableSequence[Coordinate]:
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
        if icon == Icon.MINERAL and coordinate not in self.tasked_minerals:
            self.untasked_minerals.add(coordinate)

    def _build_context(self, location: Coordinate) -> Context:
        cardinals = [
            *map(
                lambda coord: self._get_actual_icon(coord),
                Coordinate(5, 5).cardinals(),
            )
        ]
        return Context(location, *cardinals)

    def _clear_tile(self, pos: Coordinate) -> None:
        """Update the tile at the given coordinates.

        This function is used when an object moves off of the given tile.

        Args:
            pos (Coordinate): The coordinates of the tile to update.
        """
        if pos == self.landing_zone:
            self._set_actual_icon(pos, Icon.DEPLOY_ZONE)
        elif pos in self._acid:
            self._set_actual_icon(pos, Icon.ACID)
        else:
            self._set_actual_icon(pos, Icon.EMPTY)

    def _find_mineral_context_at(
        self, pos: Coordinate
    ) -> MineralContext | None:
        for mineral_context in self._total_minerals:
            if mineral_context.loc == pos:
                return mineral_context

    def _find_atron_context_at(self, pos: Coordinate) -> DroneContext | None:
        for drone_context in self.d_contexts:
            if drone_context.context.coord == pos:
                return drone_context

    def _move_to(self, d_context: DroneContext, dirc: str) -> None:
        cur_loc = d_context.context.coord
        new_location = cur_loc.translate_one(dirc)

        match self._get_actual_icon(new_location):
            case Icon.ATRON | Icon.MINER | Icon.SCOUT:
                pass  # Another Drone is already there
            case (
                Icon.DEPLOY_ZONE | Icon.ACID | Icon.EMPTY
            ):  # Drone can move here
                self._clear_tile(cur_loc)
                self._set_actual_icon(new_location, d_context.atron.icon)
                d_context.context = self._build_context(new_location)
            case Icon.WALL:  # Drone hits a wall
                d_context.health -= Icon.WALL.health_cost()
            case Icon.MINERAL:  # Drone mines a mineral
                if mineral := self._find_mineral_context_at(new_location):
                    if mineral.amt > 0:
                        mineral.amt -= 1
                        d_context.mined_mineral += 1

                        if mineral.amt <= 0:
                            self._clear_tile(mineral.loc)
                            self._total_minerals.remove(mineral)

    def __getitem__(self, key: Tile | Coordinate) -> Tile:
        """Get the tile with the specified coordinates from the map.

        A Tile or Coordinate object may be passed in as the key; if a Tile is
        given, only it's coordinate attribute will be used in look up.

        Args:
            key (Tile | Coordinate): The key to look up.

        Raises:
            KeyError: If no Tile with the given coordinates exists in this map.

        Returns:
            Tile: The Tile within this map.
        """
        if isinstance(key, Tile):
            key = key.coordinate
        return self._visible_tiles_[key]

    def __setitem__(self, key: Coordinate, val: Icon) -> None:
        self._visible_tiles_[key].icon = val
        column, row = key
        self._all_icons[row][column] = val

    def __iter__(self):
        """Iterate over this map.

        Yields:
            _type_: The iterator.
        """
        yield from self._visible_tiles_

    def __repr__(self) -> str:
        """Return a representation of this object.

        The string returned by this method is not valid for a call to eval.

        Returns:
            str: The string representation of this object.
        """
        return f"Map({list(self._visible_tiles_)})"

    def __str__(self) -> str:
        return "\n".join(
            "".join([char.value for char in row]) for row in self._all_icons
        )
