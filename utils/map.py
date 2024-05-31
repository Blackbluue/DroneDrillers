"""A map made up of tiles."""

from __future__ import annotations

from queue import PriorityQueue
from typing import TYPE_CHECKING, overload

from .coordinate import Coordinate
from .icon import Icon
from .tile import Tile

if TYPE_CHECKING:
    from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

    from units.ally.drones import Drone

    from .context import Context


class Map:
    """A map object, used to describe the tile layout of an area."""

    NODE_WEIGHTS = {
        Icon.EMPTY: 1,
        Icon.ATRON: 1,
        Icon.DEPLOY_ZONE: 1,
        Icon.ACID: 10,
        None: 1,
    }

    def __init__(self, map_id: int, density: float) -> None:
        """Initialize a Map with a context object.

        Args:
            context (Context): The origin of the map.
        """
        self.map_id = map_id
        self.density = density
        # a set of the coords of minerals and drone id tasked to mining it
        self.untasked_minerals: Set[Coordinate] = set()
        self.tasked_minerals: Set[Coordinate] = set()
        self._stored_tiles_: Dict[Coordinate, Tile] = {}
        self.scout_count = 0

    def dijkstra(self, start: Coordinate, end: Coordinate) -> List[Coordinate]:
        """Apply Dijkstra's Algorithm to find a path between two points.

        Args:
            start (Coordinate): The start point for the search
            end (Coordinate): The end point for the search
        Returns:
            list(Coordinate): Path in the form of a Coordinate list
        """
        visited: Set[Coordinate] = set()
        parents_map: Dict[Coordinate, Coordinate] = {}
        path_found = False
        pqueue: PriorityQueue[Tuple[int, Coordinate]] = PriorityQueue()
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

    def _add_to_path(
        self,
        node: Coordinate,
        neighbors: Iterable[Coordinate],
        parents_map: Dict[Coordinate, Coordinate],
        pqueue: PriorityQueue[Tuple[int, Coordinate]],
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
        parents_map: Dict[Coordinate, Coordinate],
    ) -> list[Coordinate]:
        curr = end
        final_path: List[Coordinate] = [end]
        while curr != start:
            coord = parents_map[curr]
            final_path.append(coord)
            curr = coord
            if start in coord.cardinals():
                break
        final_path.append(start)
        final_path = final_path[::-1]
        return final_path

    def update_context(self, context: Context) -> None:
        """Update the adjacency list for the Map with a context object.

        Arguments:
            context (Context): The context object to use to update
                the Map.
            origin (bool): Whether or not the passed context object
                is the origin of the map.
        """
        x = context.x
        y = context.y
        symbols = [context.north, context.south, context.east, context.west]
        atron_position = Coordinate(x, y)
        if len(self._stored_tiles_) == 0:
            self.origin = atron_position
            self.add_tile(Tile(self.origin, Icon.DEPLOY_ZONE))

        for symbol, coordinate in zip(symbols, atron_position.cardinals()):
            icon = Icon(symbol)
            tile = Tile(coordinate, icon)
            self._stored_tiles_[coordinate] = tile
            self._track_mineral(icon, coordinate)
            for neighbor_coordinate in coordinate.cardinals():
                if self.get(neighbor_coordinate, None) is None:
                    neighbor_tile = Tile(neighbor_coordinate)
                    self._stored_tiles_[neighbor_coordinate] = neighbor_tile

    def add_tile(self, tile: Tile) -> None:
        """Add tile to map.

        Args:
            tile (Tile): The tile to add.
        """
        self._stored_tiles_[tile.coordinate] = tile

    def _track_mineral(self, icon: Icon, coordinate: Coordinate) -> None:
        if icon == Icon.MINERAL and coordinate not in self.tasked_minerals:
            self.untasked_minerals.add(coordinate)

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
        miner.path = self.dijkstra(self.origin, mineral)

    @overload
    def get(
        self, key: Union[Tile, Coordinate], default: None
    ) -> Optional[Tile]:
        pass

    @overload
    def get(self, key: Union[Tile, Coordinate], default: Tile) -> Tile:
        pass

    def get(self, key, default):
        """Get the tile with the specified coordinates from the map.

        A Tile or Coordinate object may be passed in as the key; if a Tile is
        given, only it's coordinate attribute will be used in look up.

        Args:
            key (Union[Tile, Coordinate]): The key to look up.
            default (Optional[Tile], optional): A value to return if the
                key is not found. Defaults to None.

        Returns:
            Optional[Tile]: The Tile within this map.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def get_unexplored_tiles(self) -> List[Tile]:
        """Return a list of all unexplored tiles on the map.

        Returns:
            List[Tile]: The unexplored tile list.
        """
        return [
            tile
            for tile in self._stored_tiles_.values()
            if not tile.discovered
        ]

    def __getitem__(self, key: Union[Tile, Coordinate]) -> Tile:
        """Get the tile with the specified coordinates from the map.

        A Tile or Coordinate object may be passed in as the key; if a Tile is
        given, only it's coordinate attribute will be used in look up.

        Args:
            key (Union[Tile, Coordinate]): The key to look up.

        Raises:
            KeyError: If no Tile with the given coordinates exists in this map.

        Returns:
            Tile: The Tile within this map.
        """
        if isinstance(key, Tile):
            key = key.coordinate
        return self._stored_tiles_[key]

    def __iter__(self):
        """Iterate over this map.

        Yields:
            _type_: The iterator.
        """
        yield from self._stored_tiles_

    def __repr__(self) -> str:
        """Return a representation of this object.

        The string returned by this method is not valid for a call to eval.

        Returns:
            str: The string representation of this object.
        """
        return f"Map({list(self._stored_tiles_)})"
