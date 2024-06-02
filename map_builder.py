from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from units.ally.drones import Drone


class Location:
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def __repr__(self) -> str:
        return f"Location({self.x}, {self.y})"

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


class MineralContext:
    def __init__(self, location: Location, amt: int) -> None:
        self.loc: Location = location
        self.amt: int = amt

    def __repr__(self) -> str:
        return f"MineralContext({repr(self.loc)}, {self.amt})"


class DroneContext:
    def __init__(self, location: Location, atron: Drone, health: int) -> None:
        self.loc: Location = location
        self.atron: Drone = atron
        # TODO: This should be maintained independent of whichever map they are on
        self.health: int = health
        self.mineral = 0


class Map:
    def __init__(self) -> None:
        """Instantiates a map with dimensions x, y and populates it with
        a landing zone, minerals, acids and such
        """
        self.d_contexts: list[DroneContext] = []
        self._data: list[list[str]] = []
        self._minerals: list[MineralContext] = []
        self._acid: list[tuple[int, int]] = []

    def from_file(self, filename: str) -> Map:
        with open(filename) as fh:
            for row, line in enumerate(fh):
                destination = list(line.rstrip())
                for column, char in enumerate(destination):
                    if char == "~":
                        self._acid.append((column, row))
                    elif char == "_":
                        self.landing_zone = (column, row)
                    elif char in "0123456789":
                        destination[column] = "*"
                        mineral_context = MineralContext(
                            Location(column, row), int(char)
                        )
                        self._minerals.append(mineral_context)

                self._data.append(destination)

        self._set_dimensions(column, row)
        return self

    def from_scratch(self, width: int, height: int, density: float) -> Map:
        # create the box
        self._data.append(["#"] * width)
        for _ in range(height):
            self._data.append(list(f"#{' ' * (width - 2)}#"))
        self._data.append(["#"] * width)

        self._set_dimensions(width, height)
        wall_count = ((width * 2) + (height * 2)) - 4
        total_minerals = int(density * (self._total_coordinates - wall_count))
        for _ in range(total_minerals):
            self.add_mineral(randint(1, 9))
        return self

    def _set_dimensions(self, width: int, height: int) -> None:
        self._width = width
        self._height = height
        self._total_coordinates = self._width * self._height

    def _get_coordinates(self) -> tuple[int, int]:
        """Get a random set of coordinates on the map.

        Returns:
            tuple[int, int]: A set of coordinates on the map.
        """
        coordinates = (0, 0)
        x_coords: int = self._width - 2
        y_coords: int = self._height - 2
        while self[coordinates] != " ":
            # Choose a random location on map excluding walls
            coordinates = (
                randint(1, x_coords),
                randint(1, y_coords),
            )
        return coordinates

    def summary(self) -> float:
        """Ratio of total minerals to reachable tiles.

        Returns:
            float: The ratio of total minerals to reachable tiles.
        """
        wall_count = sum(row.count("#") for row in self._data)
        total_minerals = sum(mineral.amt for mineral in self._minerals)
        return total_minerals / (self._total_coordinates - wall_count)

    def __str__(self):
        return "\n".join("".join(row) for row in self._data)

    def __getitem__(self, key: tuple[int, int]):
        column, row = key
        return self._data[row][column]

    def __setitem__(self, key: tuple[int, int], val: str):
        column, row = key
        self._data[row][column] = val

    def what_is_at(self, key) -> str:
        for drone_context in self.d_contexts:
            if drone_context.loc == key:
                return "A"
        return self[key]

    def add_mineral(self, amt: int) -> None:
        """Adds a single mineral deposit to a random open spot in the map.

        Args:
            amt (int): The size of the mineral deposit.
        """
        coordinates = self._get_coordinates()

        self[coordinates] = "*"
        mineral_context = MineralContext(Location(*coordinates), amt)
        self._minerals.append(mineral_context)

    def remove_atron(self, atron_id: int):
        """Removes atron from map and returns the mineral and health.

        Args:
            atron_id (int): The id of the atron to be removed.

        Returns:
            tuple[int, int] | None: The mineral and health of the removed drone, or None.
        """
        for drone_context in self.d_contexts:
            if (
                atron_id == id(drone_context.atron)
                and (drone_context.loc.x, drone_context.loc.y)
                == self.landing_zone
            ):
                self[drone_context.loc.x, drone_context.loc.y] = "_"
                self.d_contexts.remove(drone_context)
                return drone_context.mineral, drone_context.health

    def add_atron(self, atron: Drone, health: int):
        coordinates = self.landing_zone
        if self[coordinates] != "_":
            return False

        location = Location(*coordinates)
        self.update_location_adjacent(location)

        drone_context = DroneContext(location, atron, health)
        self[location.x, location.y] = "A"
        self.d_contexts.append(drone_context)

        return True

    def update_location_adjacent(self, location):
        location.north = self[(location.x, location.y - 1)]
        location.south = self[(location.x, location.y + 1)]
        location.east = self[(location.x + 1, location.y)]
        location.west = self[(location.x - 1, location.y)]
        return location

    def find_mineral_context_at(self, pos) -> MineralContext | None:
        for mineral_context in self._minerals:
            if (
                mineral_context.loc.x == pos[0]
                and mineral_context.loc.y == pos[1]
            ):
                return mineral_context

        return None

    def find_atron_context_at(self, x: int, y: int) -> DroneContext | None:
        for drone_context in self.d_contexts:
            if drone_context.loc.x == x and drone_context.loc.y == y:
                return drone_context
        return None

    def _pick_direction(self, cur_loc: Location, dest: str) -> tuple[int, int]:
        if dest == "NORTH":
            return cur_loc.x, cur_loc.y - 1
        elif dest == "EAST":
            return cur_loc.x + 1, cur_loc.y
        elif dest == "SOUTH":
            return cur_loc.x, cur_loc.y + 1
        elif dest == "WEST":
            return cur_loc.x - 1, cur_loc.y
        else:
            return cur_loc.x, cur_loc.y

    def move_to(self, cur_loc: Location, dirc: str) -> None:
        new_location = self._pick_direction(cur_loc, dirc)

        if new_location == (cur_loc.x, cur_loc.y):
            pass  # No movement
        elif self[new_location] == "A":
            pass  # Drone is already there
        elif self[new_location] in " _~":  # Drone can move here
            self.update_tile(cur_loc.x, cur_loc.y)
            cur_loc.x, cur_loc.y = new_location[0], new_location[1]
            self[new_location] = "A"
            self.update_location_adjacent(cur_loc)
        elif self[new_location] == "#":  # Drone hits a wall
            if atron := self.find_atron_context_at(cur_loc.x, cur_loc.y):
                atron.health -= 1
        elif self[new_location] == "*":  # Drone mines a mineral
            if mineral := self.find_mineral_context_at(new_location):
                if mineral.amt > 0:
                    mineral.amt -= 1
                    if atron := self.find_atron_context_at(
                        cur_loc.x, cur_loc.y
                    ):
                        atron.mineral += 1

                    if mineral.amt <= 0:
                        self.update_tile(mineral.loc.x, mineral.loc.y)
                        self._minerals.remove(mineral)
        else:
            raise Exception("UNKNOWN TERRAIN")

    def update_tile(self, x: int, y: int) -> None:
        """Update the tile at the given coordinates.

        This function is used when an object moves off of the given tile.

        Args:
            x (int): The x coordinate of the tile.
            y (int): The y coordinate of the tile.
        """
        if (x, y) == self.landing_zone:
            self[x, y] = "_"
        elif (x, y) in self._acid:
            self[x, y] = "~"
        else:
            self[x, y] = " "

    # This may be duplicate and unnecessary now that the act of mining
    # could remove the minerals.
    def tick(self) -> None:
        for d_context in self.d_contexts:
            destination = "CENTER"
            for _ in range(d_context.atron.moves):
                self.update_location_adjacent(d_context.loc)
                pos = d_context.loc.x, d_context.loc.y

                for mineral in self._minerals:
                    if mineral.amt <= 0:
                        self.update_tile(mineral.loc.x, mineral.loc.y)
                        self._minerals.remove(mineral)

                if (d_context.loc.x, d_context.loc.y) in self._acid:
                    d_context.health -= 3  # Acid is -3
                if d_context.health <= 0:
                    self[d_context.loc.x, d_context.loc.y] = " "
                    self.update_tile(d_context.loc.x, d_context.loc.y)
                    if d_context in self.d_contexts:
                        self.d_contexts.remove(d_context)

                destination = d_context.atron.action(d_context.loc)

                # Reset location position so that the atron
                # cannot track or abuse it
                d_context.loc = Location(pos[0], pos[1])
                self.update_location_adjacent(d_context.loc)

                if d_context in self.d_contexts:
                    self.move_to(d_context.loc, destination)

                if d_context.atron.health <= 0:
                    break  # atron is dead move on to next
