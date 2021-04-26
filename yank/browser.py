# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import os

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SELENIUM IMPORTS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.exceptions import UnsupportedBrowserError


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ BROWSER                                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Browser:
    """ A utility class used to represent a web browser """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Browsers
    CHROME = _c.CHROME
    CHROMIUM = _c.CHROMIUM
    FIREFOX = _c.FIREFOX

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CLASS ATTRIBUTES                                                               │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Define supported browsers
    supported_browsers = {CHROME: "Chrome", CHROMIUM: "Chromium", FIREFOX: "Firefox"}

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, slug, headless=False):
        """ Init Method """

        # Get supported browsers
        supported_browsers = self.supported_browsers

        # Check if slug not in supported browsers
        if slug not in supported_browsers:

            # Raise UnsupportedBrowserError
            raise UnsupportedBrowserError(
                f"Browser '{slug}' not supported. Please use one of the "
                f"following: {', '.join(list(supported_browsers))}"
            )

        # Set name
        self.name = self.supported_browsers[slug]

        # Set slug
        self.slug = slug

        # Set headless boolean
        self.headless = headless

        # Initialize and set driver
        self.driver = self.initialize_driver(slug, headless)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INITIALIZE DRIVER                                                              │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def initialize_driver(self, slug, headless):
        """ Initializes a Selenium webdriver instance based on the browser slug """

        # Set log level to 0
        # Silences webdriver manager log output
        os.environ["WDM_LOG_LEVEL"] = "0"

        # Check if browser is Firefox
        if slug == _c.FIREFOX:

            # Initialize options
            options = FirefoxOptions()

            # Add headless option
            options.headless = headless

            # Initialize a Firefox driver
            driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install(),
                options=options,
            )

        # Otherwise handle default case
        else:

            # Initialize options
            options = ChromeOptions()

            # Add headless option
            options.headless = headless

            # Define Chrome driver kwargs
            driver_kwargs = {}

            # Check if browser is Chromium
            if slug == _c.CHROMIUM:

                # Add Chrome type to kwargs
                driver_kwargs["chrome_type"] = ChromeType.CHROMIUM

            # Initialize a Chrome driver
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=options,
                **driver_kwargs,
            )

        # Return driver
        return driver
