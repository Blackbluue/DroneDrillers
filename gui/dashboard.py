"""This serves to define the dashboard class.

Defines the attributes it has along with the methods that it uses.
"""

from __future__ import annotations

import tkinter
from tkinter import ttk
from typing import TYPE_CHECKING

from utils.icon import Icon

from .map_window import MapWindow

if TYPE_CHECKING:
    from typing import Any, Dict, Iterable, Mapping

    from units.ally.drones import Drone
    from utils import MapData


class Dashboard(tkinter.Toplevel):
    """Serves as blueprint for the dashboard class.

    This outlines the attributes and methods needed.
    """

    def __init__(self, parent: tkinter.Tk) -> None:
        """Serve as the constructor for the Dashboard object.

        Arguments:
            parent (tkinter.Tk): Takes in a tkinter top level window
        """
        super().__init__(parent)
        self.photo = tkinter.PhotoImage(file="icon.png")

        self.configure(bg="#2C292C")
        self.map_dict: Dict[MapWindow, MapData] = {}
        # Configure the style of Heading in Treeview widget
        self.wm_iconphoto(False, self.photo)
        self._prep_dashboard_trees()
        self.legend_insertion()
        self.title("Overlord's Dashboard")

    def _make_tree(self, column_dictionary: Dict[str, int]) -> ttk.Treeview:
        """Build trees for the dashboard to use.

        Dashboards typically serve as spreadsheets in the gui.
        https://www.geeksforgeeks.org/python-tkinter-treeview-scrollbar/
        Arguments:
            column_dictionary (Dict[str, int]): Contains dictionaries and
                width values for each column.
        """
        style = ttk.Style()
        style.theme_use("clam")

        # Configure the style of Heading in Treeview widget
        style.configure("Treeview.Heading", background="#ad73ac")

        # Using treeview widget
        tree_view = ttk.Treeview(self, selectmode="browse")

        # Defining number of columns
        tree_view["columns"] = tuple(column_dictionary)

        # Defining heading
        tree_view["show"] = "headings"

        for column_count, (column, width) in enumerate(
            column_dictionary.items()
        ):
            string_column = str(column_count)
            tree_view.column(string_column, width=width, anchor="se")
            tree_view.heading(string_column, text=column)
        return tree_view

    def create_map_gui(self, physical_map: MapData) -> None:
        """Create a GUI for every map that the overlord has.

        Arguments:
            physical_map (Map) : A map that will be loaded into the
            object.
        """
        new_map = MapWindow(self, "Mining Map", physical_map)
        new_map.prepare_MapWindow()
        self.map_dict[new_map] = physical_map

    def update_maps(
        self, drone_positions: Iterable[Mapping[str, Any]]
    ) -> None:
        """Update the GUI Map with what it's physical map contains.

        Args:
            drone_positions (List[Tuple[int, Coordinate]]): The positions.
        """
        for idx, gui_map in enumerate(self.map_dict):
            zerg_on_map = [
                drone_info
                for drone_info in drone_positions
                if drone_info["map_id"] == idx
            ]
            gui_map.update(zerg_on_map)

    def insert_action(self, action: str, tick: str) -> None:
        """Insert action and tick info into the action table.

        Arguments:
            action (str): String that represents the action happening.

            tick (str): String that represents the tick in which the
                action is taking place.
        """
        self.turn_tree.insert(
            "",
            "end",
            text="Listbox",
            values=(tick, action),
        )

    def legend_insertion(self) -> None:
        """Prepare the legend in the dashboard."""
        for item_counter, (key, unicode) in enumerate(
            Icon.unicode_mappings().items(), start=2
        ):
            self.legend_tree.insert(
                "",
                "end",
                text="Listbox",
                values=(unicode, key),
            )

    def _prep_dashboard_trees(self) -> None:
        """Prepare the three tree views in the dashboard."""
        # https://www.geeksforgeeks.org/python-tkinter-treeview-scrollbar/
        legend_labels = {"Map Symbol": 180, "Meaning": 180}

        action_labels = {"Action": 180, "Tick": 180}

        drone_labels = {
            "Drone ID": 180,
            "Drone Type": 120,
            "State": 120,
            "Health": 90,
            "Capacity": 90,
            "Moves": 90,
        }
        padding = (20, 20)
        self.legend_tree = self._make_tree(legend_labels)
        self.legend_tree.grid(row=0, column=0, padx=padding, pady=padding)
        self.turn_tree = self._make_tree(action_labels)
        self.turn_tree.grid(row=0, column=1, padx=padding, pady=padding)
        self.drone_tree = self._make_tree(drone_labels)
        self.drone_tree.grid(
            row=1, column=0, columnspan=2, padx=padding, pady=padding
        )

    def add_drone_to_tree(self, new_drone: Drone) -> None:
        """Add a drone to the drone tree in the gui.

        Arguments:
            new_drone (Drone) : this is the drone we are adding to the tree in
                the dashboard.
        """
        type_of_drone = type(new_drone).__name__
        status_of_drone = new_drone.state.name
        self.drone_tree.insert(
            "",
            "end",
            text="Listbox",
            values=(
                id(new_drone),
                type_of_drone,
                status_of_drone,
                new_drone.health,
                new_drone.capacity,
                new_drone.moves,
            ),
        )

    def _clear_table(self, tree: ttk.Treeview) -> None:
        """Clear any of the tables in the GUI.

        Arguments:
            tree (ttk.Treeview): This is the tree we will be clearing.
        """
        for entry in tree.get_children():
            tree.delete(entry)

    def update_drone_table(self, drone_dict: Iterable["Drone"]) -> None:
        """Clear drone table and adds a new dictionary of drones to the table.

        Arguments:
            drone_dict (dict) : This dictionary should contain all the drones
                that will be added to the drone table.
        """
        self._clear_table(self.drone_tree)
        for entry in drone_dict:
            self.add_drone_to_tree(entry)
