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
from yank.tools import initialize_driver


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ YANKER                                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Yanker:
    """ A base class for custom Yanker classes """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Modes
    SESSION = _c.SESSION
    TRANSIENT = _c.TRANSIENT

    # Browsers
    CHROME = _c.CHROME
    CHROMIUM = _c.CHROMIUM
    FIREFOX = _c.FIREFOX

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Define supported browsers
    supported_browsers = (CHROME, CHROMIUM, FIREFOX)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CUSTOMIZABLE CLASS ATTRIBUTES                                                  │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Initialize mode to transient
    mode = TRANSIENT

    # Initialize start URLs to None
    start_urls = None

    # Initialize auto headers to False
    auto_headers = False

    # Initialize default headers to None
    default_headers = None

    # Initialize browser
    browser = CHROME

    # Initialize headless to True
    headless = True

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(
        self,
        start_urls=None,
        mode="",
        auto_headers=None,
        default_headers=None,
        browser="",
        headless=None,
    ):
        """ Init Method """

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ MODE                                                                       │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set mode
        self.mode = mode if mode else self.mode

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ START URLS                                                                 │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Initialize start URLs from class attribute
        self.start_urls = start_urls or self.start_urls or []

        # Check if start URLs is a string
        if type(self.start_urls) is str:

            # Convert to list
            self.start_urls = [self.start_urls]

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ HEADERS                                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Set auto headers
        self.auto_headers = (
            auto_headers if auto_headers is not None else self.auto_headers
        )

        # Get default headers
        default_headers = self.default_headers

        # Initialize default headers
        self.default_headers = copy.deepcopy(default_headers) if default_headers else {}

        # Check if additional default headers were passed in
        if default_headers:

            # Update the instance's default headers
            self.default_headers.update(default_headers)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ BROWSER AND DRIVER                                                         │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Determine if Selenium driver is required
        driver_is_required = auto_headers

        # Check if driver is required
        if driver_is_required:

            # Get browser and supported browsers
            browser = browser or self.browser
            supported_browsers = self.supported_browsers

            # Check if browser not in supported browsers
            if self.browser not in supported_browsers:

                # Raise UnsupportedBrowserError
                raise UnsupportedBrowserError(
                    f"Browser '{browser}' not supported. Please use one of the "
                    f"following: {', '.join(list(supported_browsers))}"
                )

            # Get headless
            headless = headless if headless is not None else self.headless

            # Initialize Selenium webdriver
            driver = initialize_driver(browser, headless)

        # Otherwise handle case of no browser
        else:

            # Set browser to empty string
            browser = ""

            # Initialize driver to None
            driver = None

        # Set browser
        self.browser = browser

        # Set driver
        self.driver = driver

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

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ ITERATE OVER START URLS                                                    │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Iterate over start URLs
        for start_url in self.start_urls:

            target = self.pliers.get(start_url)
            print(target.response)

            # Call yank start method on start URL
            # self.yank_start(start_url)

        # ┌────────────────────────────────────────────────────────────────────────────┐
        # │ CLOSE DRIVER                                                               │
        # └────────────────────────────────────────────────────────────────────────────┘

        # Get driver
        driver = self.driver

        # Check if driver is not nulle
        if driver:

            # Close driver
            driver.close()

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ YANK START                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def yank_start(self, target):
        """ The action performed on each of the Yanker's start URLs """

        # Raise NotImplementedError
        raise NotImplementedError
