# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SELENIUM IMPORTS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ INITIALIZE DRIVER                                                                  │
# └────────────────────────────────────────────────────────────────────────────────────┘


def initialize_driver(browser, headless):
    """ Initializes a Selenium webdriver instance based on the supplied browser """

    # Check if browser is Firefox
    if browser == _c.FIREFOX:

        # Initialize options
        options = FirefoxOptions()

        # Add headless option
        options.headless = headless

        # Initialize a Firefox driver
        driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(), options=options
        )

    # Otherwise handle default case
    else:

        # Initialize options
        options = ChromeOptions()

        # Add headless option
        options.headless = headless

        # Define Chrome driver manager kwargs
        kwargs = {}

        # Check if browser is Chromium
        if browser == _c.CHROMIUM:

            # Add Chrome type to kwargs
            kwargs["chrome_type"] = ChromeType.CHROMIUM

        # Initialize a Chrome driver
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options, **kwargs
        )

    # Return driver
    return driver
