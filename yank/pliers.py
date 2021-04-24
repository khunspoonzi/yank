# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import requests

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.target import Target


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PLIERS                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Pliers:
    """ A utility class used for yanking webpages and API data """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Define requester
    requester = requests

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, yanker):
        """ Init Method """

        # Set yanker
        self.yanker = yanker

        # Set mode
        self.mode = yanker.mode

        # Check if mode is session
        if self.mode == _c.SESSION:

            # Set requester to a new requests session
            self.requester = requests.Session()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ REQUEST                                                                        │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def request(self, url, method):
        """ Performs an HTTP request on a Target object using the pliers' requester """

        # Initialize target object from URL
        target = Target(url=url, pliers=self)

        # Handle case of GET
        if method == _c.GET:

            # Call GET method on target
            target.get()

        # Return target
        return target

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ GET                                                                            │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def get(self, url):
        """ Performs an HTTP GET request using the pliers' requester """

        # Make GET request and return target
        return self.request(url, method=_c.GET)
