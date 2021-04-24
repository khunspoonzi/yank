# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import copy

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.exceptions import UnsupportedBrowserError
from yank.pliers import Pliers


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Yanker:
    """ A base class for custom Yanker classes """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    CHROME = _c.CHROME
    SESSION = _c.SESSION
    TRANSIENT = _c.TRANSIENT

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize mode to transient
    mode = TRANSIENT

    # Initialize start URLs to None
    start_urls = None

    # Initialize default headers to None
    default_headers = None

    # Initialize default browser
    default_browser = CHROME

    # Define supported browsers
    supported_browsers = (CHROME,)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(
        self,
        start_urls=None,
        auto_headers=True,
        default_headers=None,
        default_browser=CHROME,
    ):
        """ Init Method """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ BROWSER                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get default and supported browsers
        default_browser = default_browser or self.default_browser
        supported_browsers = self.supported_browsers

        # Check if default browser not in supported browsers
        if self.default_browser not in supported_browsers:

            # Raise UnsupportedBrowserError
            raise UnsupportedBrowserError(
                f"Browser '{default_browser}' not supported. Please use one of the "
                f"following: {', '.join(list(supported_browsers))}"
            )

        # Set default browser
        self.default_browser = default_browser

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ START URLS                                                                 │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize start URLs from class attribute
        self.start_urls = self.start_urls or []

        # Check if start URLs is a string
        if type(self.start_urls) is str:

            # Convert to list
            self.start_urls = [self.start_urls]

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

        # Iterate over start URLs
        for start_url in self.start_urls:

            target = self.pliers.get(start_url)
            print(target.response)

            # Call yank start method on start URL
            # self.yank_start(start_url)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ YANK START                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def yank_start(self, target):
        """ The action performed on each of the Yanker's start URLs """

        # Raise NotImplementedError
        raise NotImplementedError


if __name__ == "__main__":

    yanker = Yanker()
