# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from datetime import datetime

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

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Set database meta
    db_meta = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, **kwargs):
        """ Init Method """

        # Initialize field map from kwargs
        field_map = kwargs

        # Normalize the structure of the field map
        self.field_map = {
            k: (v if type(v) is dict else {self.TYPE: v}) for k, v in field_map.items()
        }

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CAST                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def cast(self, field, value):
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

        # Get to type
        to_type = field_map[field][self.TYPE]

        # Check if to type is int
        if to_type is int:

            # Check if value is str
            if type(value) is str:

                # Remove common unwanted characters
                value = value.replace(",", "")

        # Handle case of datetime
        if to_type is datetime:

            # Assert value is datetime
            assert type(value) is datetime, f"{field} is not a valid datetime"

        # Handle normal case
        else:

            # Cast value to appropriate type
            value = to_type(value)

        # Return value
        return value
