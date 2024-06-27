"""Display information on the drones and actions in the game."""

from __future__ import annotations

import tkinter
from tkinter import ttk
from typing import TYPE_CHECKING

from utils.icon import Icon

from .label_counter import LabeledCounter
from .map_window import MapWindow

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from units.ally import Atron, Player
    from units.ally.drones import Drone
    from utils import MapData


class Dashboard(tkinter.Toplevel):
    """Display information on the drones and actions in the game."""

    def __init__(self, parent: tkinter.Tk, player: Player) -> None:
        """Serve as the constructor for the Dashboard object.

        Args:
            parent (tkinter.Tk): Takes in a tkinter top level window
        """
        super().__init__(parent)
        self.photo = tkinter.PhotoImage(file="icon.png")
        self.configure(bg="#2C292C")

        self._map_window = MapWindow(self, "Mining Map")

        # Configure the style of Heading in Treeview widget
        self.wm_iconphoto(False, self.photo)
        self._prep_dashboard_trees()
        self.legend_insertion()
        self._player = player
        self._player_health = LabeledCounter(
            self,
            "Player Health:",
            counter=player.health,
        )
        self._player_health.grid(row=0, column=0, columnspan=2)
        self.title("Overlord's Dashboard")

    def set_map(self, map_data: MapData) -> MapWindow:
        """Set the mining map.

        Args:
            map_file (MapData): The map data.
        """
        self._map_window.map_data = map_data
        self._player.deploy(self._map_window)
        self._player_health.counter.reset()
        return self._map_window

    def unset_map(self) -> None:
        """Unset the mining map."""
        if self._map_window:
            self._map_window.unbind("<<PlayerMoved>>")

    def _make_tree(self, labels: Mapping[str, int]) -> ttk.Treeview:
        """Build trees for the dashboard to use.

        Dashboards typically serve as spreadsheets in the gui.
        https://www.geeksforgeeks.org/python-tkinter-treeview-scrollbar/
        Args:
            labels (Mapping[str, int]): Contains dictionaries and
                width values for each column.
        """
        style = ttk.Style()
        style.theme_use("clam")

        # Configure the style of Heading in Treeview widget
        style.configure("Treeview.Heading", background="#ad73ac")

        # Using treeview widget
        tree_view = ttk.Treeview(self, selectmode="browse")

        # Defining number of columns
        tree_view["columns"] = tuple(labels)

        # Defining heading
        tree_view["show"] = "headings"

        for column_count, (column, width) in enumerate(labels.items()):
            string_column = str(column_count)
            tree_view.column(string_column, width=width, anchor="se")
            tree_view.heading(string_column, text=column)
        return tree_view

    def legend_insertion(self) -> None:
        """Prepare the legend in the dashboard."""
        for key, unicode in Icon.unicode_mappings().items():
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

        drone_labels = {
            "Drone ID": 180,
            "Drone Type": 120,
            "Health": 90,
            "Capacity": 90,
        }
        padding = (20, 20)
        self.legend_tree = self._make_tree(legend_labels)
        self.legend_tree.grid(row=1, column=0, padx=padding, pady=padding)
        self.drone_tree = self._make_tree(drone_labels)
        self.drone_tree.grid(row=1, column=1, padx=padding, pady=padding)

    def add_atron_to_tree(self, new_drone: Atron) -> None:
        """Add a drone to the drone tree in the gui.

        Args:
            new_drone (Atron) : This is the atron we are adding to the tree in
                the dashboard.
        """
        type_of_drone = type(new_drone).__name__
        self.drone_tree.insert(
            "",
            "end",
            text="Listbox",
            values=(
                id(new_drone),
                type_of_drone,
                new_drone.health,
                new_drone.payload.get(),
            ),
        )

    def update_drone_table(self, drones: Iterable[Drone]) -> None:
        """Clear drone table and adds a new list of drones to the table.

        Args:
            drones (Iterable[Drone]) : The list of drones.
        """
        for entry in self.drone_tree.get_children():
            self.drone_tree.delete(entry)
        for drone in drones:
            self.add_atron_to_tree(drone)
