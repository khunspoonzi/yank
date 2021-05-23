# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import math
import re

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RICH IMPORTS                                                                       │
# └────────────────────────────────────────────────────────────────────────────────────┘

from rich.columns import Columns
from rich.console import Console, render_group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.tools import display_commands


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INTERFACE DISPLAY MIXIN                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


class InterfaceDisplayMixin:
    """ Interface Display Mixin """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize cached console to None
    _console = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSOLE                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def console(self):
        """ Returns a cached or newly initialized Rich console object """

        # Check if console is cached
        if self._console:

            # Return cached console
            return self._console

        # Initialize a new Rich console
        console = Console()

        # Cache console
        self._console = console

        # Return console
        return console

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET LIST RENDERABLE                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get_list_renderable(
        self, interactive=False, limit=None, offset=0, sort_by=None, filter_by=None
    ):
        """ Returns a Rich table renderable for the interface list view """

        # Define max limit
        limit_max = 1000

        # Initialize limie
        limit = limit or limit_max

        # Get limit where max is 1000
        limit = min(limit, limit_max)

        # Get display map
        display_map = self.list_display_map

        # Get items
        items = self.db_session.query(self.Item)

        # Check if filter by is not null
        if filter_by:

            # Apply filters
            items = self.filter(**filter_by, queryset=items, display_map=display_map)

        # Check if sort by is not null
        if sort_by:

            # Apply sort fields
            items = self.sort(*sort_by, queryset=items, display_map=display_map)

        # Get row count
        row_count = items.count()

        # Get page count
        page_count = math.ceil(row_count / limit)

        # Define title
        title = (
            f"{self.name}: {self.db_table_name}\n"
            f"Page {int(offset / limit) + 1} of {page_count} "
            f"({row_count} {self.inflector.plural('row', row_count)})"
        )

        # Limit items
        items = items.offset(offset).limit(limit)

        # Initialize Rich Table as renderable
        renderable = Table(title=title)

        # Get display fields
        display_fields = self.display_list_by

        # Initialize fields
        fields = []

        # Iterate over display fields
        for field, display in display_fields.items():

            # Create column
            renderable.add_column(display)

            # Add field to fields
            fields.append(field)

        # Iterate over items
        for item in items:

            # Add row
            renderable.add_row(*[str(getattr(item, field)) for field in fields])

        # Check if interactive
        if interactive:

            # Initialize caption
            caption = "c\[ommands]: Show available commands"  # noqa

            # Initialize sub-caption
            sub_caption = ""

            # Check if sort by is not null
            if sort_by:

                # Add sort sub-caption
                sub_caption += f"sort {','.join(sort_by)}\n"

            # Check if filter by is not null
            if filter_by:

                # Get filter strings
                filter_strings = [f"{f}={v}" for f, v in filter_by.items()]

                # Add filter sub-caption
                sub_caption += f"filter {','.join(filter_strings)}\n"

            # Check if sub-caption
            if sub_caption:

                # Combine caption and sub-caption
                caption = sub_caption + "\n" + caption

            # Set caption
            renderable.caption = caption.strip("\n")

        # Pad renderable
        renderable = Padding(renderable, (1, 1))

        # Return renderable and row count
        return renderable, row_count

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY LIST                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_list(
        self,
        interactive=False,
        limit=20,
        offset=0,
        sort_by=None,
        filter_by=None,
    ):
        """ Displays a list of items using a Rich Table """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ STATIC                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get renderable
        renderable, row_count = self.get_list_renderable(
            interactive=interactive,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            filter_by=filter_by,
        )

        # Get console
        console = self.console

        # Clear console
        console.clear()

        # Print renderable list view and return
        console.print(renderable, justify="center")

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ INTERACTIVE                                                                │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Return if not interactive
        if not interactive:
            return

        # Initialize while loop
        while True:

            # Get command
            command = console.input(_c.INPUT_TAG)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ BASIC COMMANDS                                                         │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle case of reset
            if command in ["r", "reset"]:

                # Reset sort fields
                sort_by = None

                # Reset filters
                filter_by = None

            # Otherwise handle case of quit
            elif command in ["q", "quit"]:
                break

            # Otherwise handle case of command
            elif command in ["c", "command", "commands"]:

                # Display commands
                display_commands(
                    "List View Commands",
                    console,
                    ("'", "<int> = 1", "Go to next nth page", "' 5"),
                    (";", "<int> = 1", "Go to previous nth page", "; 3"),
                    ("l[imit]", "<int>", "Set max number of rows per page", "l 10"),
                    (
                        "s[ort]",
                        "<field>[,<field>]",
                        "Sort rows by field(s)",
                        "s name,-age",
                    ),
                    (
                        "f[ilter]",
                        "<field>=<value>[,<field>=<value>]",
                        "Filter rows by field(s)",
                        "f name=Bob,age=24",
                    ),
                    ("d[etail]", "<id>", "Display a row in detail view", "d 5"),
                    ("r[eset]", "", "Reset sort and filter parameters", "r"),
                )

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ ARGUMENT COMMANDS                                                      │
            # └────────────────────────────────────────────────────────────────────────┘

            # Otherwise handle more complex commands
            else:

                # Get command and index
                match = re.search(r"([a-zA-Z';]+) *(.*)", command)

                # Separate args from command
                command, args = (
                    (match.group(1).strip(), match.group(2)) if match else (None, None)
                )

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ NEXT PAGE                                                          │
                # └────────────────────────────────────────────────────────────────────┘

                # Handle case of next page
                if command == "'":

                    # Define multiplier
                    multiplier = int(args) if args.isdigit() else 1

                    # Get new offset
                    new_offset = offset + (limit * multiplier)

                    # Increment offset by limit
                    offset = offset if new_offset >= row_count else new_offset

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ PREVIOUS PAGE                                                      │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of previous page
                elif command == ";":

                    # Define multiplier
                    multiplier = int(args) if args.isdigit() else 1

                    # Get new offset
                    new_offset = offset - (limit * multiplier)

                    # Decrement offset by limit
                    offset = max(new_offset, 0)

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ LIMIT                                                              │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of limit
                elif command in ["l", "limit"]:

                    # Set new limit
                    limit = max(int(args), 0) if args.isdigit() else None

                    # Reset offset to 0
                    offset = 0

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ SORT                                                               │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of sort
                elif command in ["s", "sort"]:

                    # Set sort by argument
                    sort_by = [f.strip() for f in args.split(",")]

                    # Remove null items
                    sort_by = [s for s in sort_by if s]

                    # Set to None if null
                    sort_by = sort_by or None

                    # Reset offset to zero
                    offset = 0

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ FILTER                                                             │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of filter
                elif command in ["f", "filter"]:

                    # Set filter by argument
                    filter_by = [f.strip() for f in args.split(",")]

                    # Convert filter by to kwargs
                    filter_by = (
                        {
                            f: v
                            for f, v in [
                                arg.split("=") for arg in filter_by if "=" in arg
                            ]
                        }
                        if filter_by
                        else None
                    )

                    # Cast values
                    filter_by = self.cast_fields(
                        filter_by, display_map=self.list_display_map
                    )

                    # Reset offset to zero
                    offset = 0

                # ┌────────────────────────────────────────────────────────────────────┐
                # │ DETAIL                                                             │
                # └────────────────────────────────────────────────────────────────────┘

                # Otherwise handle case of detail
                elif command in ["d", "detail"]:

                    # Get item ID
                    item_id = int(args)

                    # Display interface detail view
                    self.display_detail(item_id=item_id, interactive=interactive)

            # ┌────────────────────────────────────────────────────────────────────────┐
            # │ RE-RENDER                                                              │
            # └────────────────────────────────────────────────────────────────────────┘

            # Get renderable and row count
            renderable, row_count = self.get_list_renderable(
                interactive=interactive,
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                filter_by=filter_by,
            )

            # Clear console
            console.clear()

            # Print renderable list view and return
            console.print(renderable, justify="center")

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET DETAIL RENDERABLE                                                          │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @render_group()
    def get_detail_renderable(self, item_id):

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ GET ITEM                                                                   │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get item by ID
        item = self.get(id=int(item_id))

        # Yield heading
        # yield Panel(Text("BACKTEST", style="bold", justify="center"))

        # Define panel kwargs
        panel_kwargs = {"title_align": "right"}

        # Get display detail by
        display_detail_by = self.display_detail_by

        # Iterate over rows in display detail by
        for row in display_detail_by:

            # Initialize columns
            cols = []

            # Iterate over columns in row
            for field, display in row.items():

                # Get value
                value = getattr(item, field, "N/A")

                # Stringify value
                value = str(value)

                # Add Panel to columns
                cols.append(Panel(value, title=display, **panel_kwargs))

            # Yield row of columns
            yield Columns(cols, expand=True)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DISPLAY DETAIL                                                                 │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_detail(self, item_id, interactive=False):
        """ Displays an item detail view using Rich Panels """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ STATIC                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get detail renderable
        renderable = self.get_detail_renderable(item_id=item_id)

        # Get console
        console = self.console

        # Clear console
        console.clear()

        # Print renderable list view and return
        console.print(renderable, justify="center")

        input("temp")
