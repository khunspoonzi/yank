# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import copy

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.pliers import Pliers


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Yanker:
    """ A base class for custom Yanker classes """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    SESSION = _c.SESSION
    TRANSIENT = _c.TRANSIENT

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize mode to transient
    mode = _c.TRANSIENT

    # Initialize start URLs to None
    start_urls = None

    # Initialize default headers to None
    default_headers = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, start_urls=None):
        """ Init Method """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ START URLS                                                                 │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize start URLs from class attribute
        self.start_urls = self.start_urls or []

        # Check if additional start URLs were passed in
        if start_urls:

            # Extend the instance's start URLs
            self.start_urls.extend(start_urls)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ DEFAULT HEADERS                                                            │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get default headers
        default_headers = self.default_headers

        # Initialize default headers
        self.default_headers = copy.deepcopy(default_headers) if default_headers else {}

        # Check if additional default headers were passed in
        if default_headers:

            # Update the instance's default headers
            self.default_headers.update(default_headers)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ PLIERS                                                                     │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize pliers
        self.pliers = Pliers(yanker=self)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ YANK                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def yank(self):
        """ Runs the yanker on its start URLs """

        # Call authenticate method
        self.authenticate()

        # Iterate over start URLs
        for start_url in self.start_urls:

            # Call yank start method on start URL
            self.yank_start(start_url)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ AUTHENTICATE                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def authenticate(self):
        """ Performs a one-time global action to authenticate the user or session """

        # Return None by default
        return None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ YANK START                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def yank_start(self):
        """ """

        # Raise NotImplementedError
        raise NotImplementedError()


if __name__ == "__main__":

    yanker = Yanker()
