# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from datetime import datetime

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQLALCHEMY IMPORTS                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import Column, DateTime, exists, Float, func, Integer, String

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RICH IMPORTS                                                                       │
# └────────────────────────────────────────────────────────────────────────────────────┘

from rich.console import Console
from rich.table import Table

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INTERFACE                                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Interface:
    """ A utility class for managing the schema of yanked data """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Interface
    NULL = _c.NULL
    TYPE = _c.TYPE
    UNIQUE = _c.UNIQUE

    # Fields
    ID = _c.ID
    URL = _c.URL
    YANKED_AT = _c.YANKED_AT

    # Type Map
    TYPE_MAP = {
        str: String,
        int: Integer,
        float: Float,
        datetime: DateTime,
    }

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize name to empty string
    name = ""

    # Initialize database session
    db_session = None

    # Initialize skip by URL to False
    skip_by_url = False

    # Initialize session limit to None
    session_limit = None

    # Initialize session count to 0
    session_count = 0

    # Initialize display list by to None
    display_list_by = None

    # Initialize cached console to None
    _console = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, DBBase, db_table_name, **kwargs):
        """ Init Method """

        # Get common constants
        TYPE = self.TYPE
        UNIQUE = self.UNIQUE

        # Set table name
        self.db_table_name = db_table_name

        # Get attributes
        attributes = {k: v for k, v in kwargs.items() if k.startswith("__")}

        # Iterate over attributes
        for k, v in attributes.items():

            # Set attribute
            setattr(self, k.replace("__", "", 1).strip(), v)

        # Initialize field map from kwargs
        field_map = {k: v for k, v in kwargs.items() if k not in attributes}

        # Add yanked at and URL to field map
        field_map[self.URL] = str
        field_map[self.YANKED_AT] = datetime

        # Normalize the structure of the field map
        self.field_map = {
            k: (v if type(v) is dict else {TYPE: v}) for k, v in field_map.items()
        }

        # Define columns decorator
        def columns(cls):
            """ Dynamically sets SQLAlchemy columns on a target ORM class """

            # Iterate over field map
            for field, info in self.field_map.items():

                # Get column type
                ColType = self.TYPE_MAP[info[TYPE]]

                # Get unique
                unique = info.get(UNIQUE, False)

                # Set class attribute
                setattr(cls, field, Column(ColType, unique=unique))

            # Return the ORM class
            return cls

        # Define Item ORM class
        @columns
        class Item(DBBase):
            """ The ORM class that will house the user-defined columns """

            # Set table name
            __tablename__ = self.db_table_name

            # Set ID as primary key
            id = Column(Integer, primary_key=True)

            # NOTE: URL and yanked at are set above in the field map

        # Set Item class on interface object
        self.Item = Item

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ NEW                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def new(self, **kwargs):
        """ A creates a new Item using the SQLAlchemy ORM Item class """

        # Cast the item fields spplied as kawrgs and return an initialized Item object
        return self.Item(**self.cast_fields(kwargs))

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ COUNT                                                                          │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def count(self):
        """ Returns a count of items in the database """

        # Return count
        return self.db_session.query(func.count(self.Item.id)).scalar()

        """
        For more info on counting with SQL Alchemy:

        https://stackoverflow.com/questions/10822635/get-the-number-of-rows-in-table-
        using-sqlalchemy

        https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower
        -than-the-raw-query
        """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ EXISTS                                                                         │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def exists(self, **kwargs):
        """
        Returns a boolean of whether an item by the filter kwargs exists in the database
        """

        # Get Item
        Item = self.Item

        # Convert field names to field objects
        kwargs = {getattr(Item, field, None): value for field, value in kwargs.items()}

        # Remove null fields
        kwargs = {k: v for k, v in kwargs.items() if k}

        # Return boolean of whether or not the object exists
        return self.db_session.query(
            exists().where(*[k == v for k, v in kwargs.items()])
        ).scalar()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ ALL                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def all(self):
        """ Returns a queryset of all items in the database """

        # Return a queryset of all items
        return self.db_session.query(self.Item).all()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ FILTER                                                                         │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def filter(self, **kwargs):
        """
        Returns a filtered queryset of items in the database by the provided kwargs
        """

        # Return filtered queryset
        return self.db_session.query(self.Item).filter_by(**kwargs)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CAST FIELDS                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def cast_fields(self, item_dict):
        """ Casts a dict of item fields according to a the interface's field map """

        # Cast item dict
        item_dict = {
            field: self.cast_field(field, value) for field, value in item_dict.items()
        }

        # Return the item dict
        return item_dict

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CAST FIELD                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def cast_field(self, field, value):
        """ Casts a value according to a field in the interface's field map """

        # Get field map
        field_map = self.field_map

        # Check if value is None
        if value is None:

            # Get null boolean
            null = field_map[field].get(self.NULL, False)

            # Check if null is permitted
            if null:

                # Return the value
                return value

        # Get value type
        value_type = type(value)

        # Check if value is a list
        if value_type is list:

            # Return a comma separated list
            # Currently no support for array structures in database
            return "; ".join([str(i).replace(";", ",") for i in value])

        # Get to type
        to_type = field_map[field][self.TYPE]

        # Check if to type is int
        if to_type is int:

            # Check if value is str
            if value_type is str:

                # Remove common unwanted characters
                value = value.replace(",", "")

        # Handle case of datetime
        elif to_type is datetime:

            # Assert value is datetime
            assert value_type is datetime, f"{field} is not a valid datetime"

        # Handle normal case
        else:

            # Cast value to appropriate type
            value = to_type(value)

        # Return value
        return value

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
    # │ DISPLAY LIST                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def display_list(self):
        """ Displays a list of items using a Rich Table """

        # Get row count
        row_count = self.count()

        # Initialize Rich Table
        table = Table(title=f"{self.name}: {self.db_table_name} ({row_count} rows)")

        # Get display fields
        display_fields = self.display_list_by

        # Check if display fields is None
        if not display_fields:

            # Define display list by as the first n fields in the field map
            display_fields = list(self.field_map.keys())[:5]

        # Add ID to display fields
        display_fields = ["id"] + list(display_fields)

        # Initialize fields
        fields = []

        # Iterate over display fields
        for display_field in display_fields:

            # Get field and display
            field, display = (
                display_field
                if type(display_field) in [list, tuple]
                else (display_field, display_field.replace("_", " "))
            )

            # Create column
            table.add_column(display)

            # Add field to fields
            fields.append(field)

        # Get items
        items = self.db_session.query(self.Item).all()

        # Iterate over items
        for item in items:

            # Add row
            table.add_row(*[str(getattr(item, field)) for field in fields])

        # Display table of tables
        self.console.print(table, justify="center")
