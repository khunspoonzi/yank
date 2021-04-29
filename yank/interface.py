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

        # Get to type
        to_type = self.field_map[field][self.TYPE]

        # Cast value to appropriate type
        value = to_type(value)

        # Return value
        return value
