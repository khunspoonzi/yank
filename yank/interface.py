# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from datetime import datetime

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SQLALCHEMY IMPORTS                                                                 │
# └────────────────────────────────────────────────────────────────────────────────────┘

from sqlalchemy import Column, Integer

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.interface_database_mixin import InterfaceDatabaseMixin
from yank.interface_display_mixin import InterfaceDisplayMixin


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INTERFACE                                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Interface(InterfaceDatabaseMixin, InterfaceDisplayMixin):
    """ A utility class for managing the schema of yanked data """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Interface
    CAST = _c.CAST
    DISPLAY = _c.DISPLAY
    NULL = _c.NULL
    UNIQUE = _c.UNIQUE

    # Fields
    ID = _c.ID
    URL = _c.URL
    YANKED_AT = _c.YANKED_AT

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize name to empty string
    name = ""

    # Initialize skip by URL to False
    skip_by_url = False

    # Initialize session limit to None
    session_limit = None

    # Initialize session count to 0
    session_count = 0

    # Initialize display list by to None
    display_list_by = None

    # Initialize list display map to None
    list_display_map = None

    # Initialize display detail by to None
    display_detail_by = None

    # Initialize detail display map to None
    detail_display_map = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, DBBase, db_table_name, **kwargs):
        """ Init Method """

        # Get common constants
        CAST = self.CAST
        DISPLAY = self.DISPLAY
        UNIQUE = self.UNIQUE

        # Set table name
        self.db_table_name = db_table_name

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ CUSTOM ATTRIBUTES                                                          │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get attributes
        attributes = {k: v for k, v in kwargs.items() if k.startswith("__")}

        # Iterate over attributes
        for k, v in attributes.items():

            # Set attribute
            setattr(self, k.replace("__", "", 1).strip(), v)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ FIELD MAP                                                                  │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize field map from kwargs
        field_map = {k: v for k, v in kwargs.items() if k not in attributes}

        # Add yanked at and URL to field map
        field_map[self.URL] = {CAST: str, DISPLAY: "URL"}
        field_map[self.YANKED_AT] = datetime

        # Normalize the structure of the field map
        self.field_map = {
            k: (v if type(v) is dict else {CAST: v}) for k, v in field_map.items()
        }

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DEFAULT DISPLAY                                                            │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Iterate over field map
        for field, info in self.field_map.items():

            # Define display
            info[DISPLAY] = info.get(DISPLAY) or " ".join(
                [w.title() for w in field.split("_")]
            )

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ COLUMNS                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Define columns decorator
        def columns(cls):
            """ Dynamically sets SQLAlchemy columns on a target ORM class """

            # Iterate over field map
            for field, info in self.field_map.items():

                # Get column type
                ColType = self.TYPE_MAP[info[CAST]]

                # Get unique
                unique = info.get(UNIQUE, False)

                # Set class attribute
                setattr(cls, field, Column(ColType, unique=unique))

            # Return the ORM class
            return cls

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ ITEM                                                                       │
        # └────────────────────────────────────────────────────────────────────────────┘

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

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DISPLAY SETTINGS                                                           │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize list display map
        self.list_display_map = {_c.ID: _c.ID}

        # Check if display list by is defined
        if self.display_list_by:

            # Iterate over display list by
            for item in self.display_list_by:

                # Initialize display
                display = None

                # Check if item is a list or tuple
                if type(item) in (list, tuple):

                    # Unpack field and display
                    field, display = item

                # Otherwise handle string
                else:

                    # Set field
                    field = item

                # Continue if field not in field map
                if field not in self.field_map:
                    continue

                # Set display
                display = display or self.field_map[field][_c.DISPLAY]

                # Add to display map
                self.list_display_map[display] = field

        # Otherwise handle case of undefined display list by
        else:

            # Iterate over the first five items of the field map
            for field in list(self.field_map.keys())[:5]:

                # Add to display map
                self.list_display_map[self.field_map[field][_c.DISPLAY]] = field

        # Convert display list by into a dictionary
        self.display_list_by = {v: k for k, v in self.list_display_map.items()}

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CAST FIELDS                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def cast_fields(self, item_dict, display_map=None):
        """ Casts a dict of item fields according to a the interface's field map """

        # Initialize display map
        display_map = {k.lower(): v for k, v in display_map.items()} or {}

        # Convert fields from display
        item_dict = {
            field
            if field in self.field_map
            else display_map.get(field.lower(), field): value
            for field, value in item_dict.items()
        }

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
        to_type = field_map[field][self.CAST]

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
