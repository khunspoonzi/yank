# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import os

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SELENIUM IMPORTS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ PROJECT IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

import yank.constants as _c

from yank.exceptions import UnsupportedBrowserError, UnsupportedDriverModeError


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ BROWSER                                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Browser:
    """ A utility class used to represent a web browser """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ CONSTANTS                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    # Driver modes
    EAGER = _c.EAGER
    NORMAL = _c.NORMAL
    QUICK = _c.QUICK

    # Define driver modes
    DRIVER_MODES = [EAGER, QUICK, NORMAL]

    # Browsers
    CHROME = _c.CHROME
    CHROMIUM = _c.CHROMIUM
    FIREFOX = _c.FIREFOX

    # Define supported browsers
    SUPPORTED_BROWSERS = {CHROME: "Chrome", CHROMIUM: "Chromium", FIREFOX: "Firefox"}

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, slug, driver_mode=NORMAL, driver_headless=False):
        """ Init Method """

        # Get driver modes
        driver_modes = self.DRIVER_MODES

        # Check if driver mode not in driver modes
        if driver_mode not in driver_modes:

            # Raise UnsupportedDriverModeError
            raise UnsupportedDriverModeError(
                f"Driver mode '{driver_mode}' not supported. Please use one of the "
                f"following: {', '.join(driver_modes)}"
            )

        # Get supported browsers
        supported_browsers = self.SUPPORTED_BROWSERS

        # Check if slug not in supported browsers
        if slug not in supported_browsers:

            # Raise UnsupportedBrowserError
            raise UnsupportedBrowserError(
                f"Browser '{slug}' not supported. Please use one of the "
                f"following: {', '.join(list(supported_browsers))}"
            )

        # Set name
        self.name = supported_browsers[slug]

        # Set slug
        self.slug = slug

        # Set driver mode
        self.driver_mode = driver_mode

        # Set driver headless boolean
        self.driver_headless = driver_headless

        # Initialize and set driver
        self.driver = self.initialize_driver(slug, driver_mode, driver_headless)

        # Initialize quick driver cache
        self._driver_quick = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ DRIVER QUICK                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def driver_quick(self):
        """
        Returns an initialized Selenium webdriver instance with no page load strategy
        """

        # Get constants
        QUICK = self.QUICK

        # Check if driver mode is quick
        if self.driver_mode == QUICK:

            # Return the driver
            return self.driver

        # Check if the quick driver is cached
        if self._driver_quick:

            # Return the cached driver
            return self._driver_quick

        # Initialize a new quick driver
        driver_quick = self.initialize_driver(self.slug, _c.NONE, self.driver_headless)

        # Set quick driver
        self._driver_quick = driver_quick

        # Return quick driver
        return driver_quick

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INITIALIZE DRIVER                                                              │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def initialize_driver(self, slug, driver_mode, driver_headless):
        """ Initializes a Selenium webdriver instance based on the browser slug """

        # Set log level to 0
        # Silences webdriver manager log output
        os.environ["WDM_LOG_LEVEL"] = "0"

        # Define desired capability args
        desired_capability_args = {"pageLoadStrategy": driver_mode}

        # Check if browser is Firefox
        if slug == _c.FIREFOX:

            # Initialize options
            options = FirefoxOptions()

            # Add headless option
            options.headless = driver_headless

            # Initialize desired capabilities
            desired_capabilities = DesiredCapabilities.FIREFOX

            # Set page load strategy to None
            desired_capabilities.update(desired_capability_args)

            # Initialize a Firefox driver
            driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install(),
                options=options,
                desired_capabilities=desired_capabilities,
            )

        # Otherwise handle default case
        else:

            # Initialize options
            options = ChromeOptions()

            # Add headless option
            options.headless = driver_headless

            # Disable blink features
            # Helps to evade CloudFlare asking you to prove you are human with captcha
            options.add_argument("--disable-blink-features=AutomationControlled")

            # See https://stackoverflow.com/questions/64165726/
            # selenium-stuck-on-checking-your-browser-before-accessing-url

            # Initialize desired capabilities
            desired_capabilities = DesiredCapabilities.CHROME

            # Set page load strategy to None
            desired_capabilities.update(desired_capability_args)

            # Define Chrome driver kwargs
            driver_kwargs = {}

            # Check if browser is Chromium
            if slug == _c.CHROMIUM:

                # Add Chrome type to kwargs
                driver_kwargs["chrome_type"] = ChromeType.CHROMIUM

            # Initialize a Chrome driver
            driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(),
                options=options,
                desired_capabilities=desired_capabilities,
                **driver_kwargs,
            )

            # Check if headless is True
            if driver_headless:

                # Get default user agent
                user_agent = driver.execute_script("return navigator.userAgent;")

                # Remove indication that user agent is a headless browser
                user_agent = user_agent.replace("HeadlessChrome", "Chrome")

                # Replace driver user agent
                driver.execute_cdp_cmd(
                    "Network.setUserAgentOverride", {"userAgent": user_agent}
                )

        # Return driver
        return driver

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ STOP WHEN                                                                      │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @staticmethod
    def stop_when(condition, timeout=10):
        """ Stops a driver from loading further when a certain condition is met """

        # Define decorator
        def decorator(method):

            # Define wrapper
            def wrapper(instance, driver):

                # Wait for listing nav links to appear
                WebDriverWait(driver, timeout).until(condition)

                # Stop further loading
                driver.execute_script("window.stop();")

                # Execute original method
                return method(instance, driver)

            # Set has stop when attribute on wrapped method
            wrapper.has_stop_when = True

            # Return wrapper
            return wrapper

        # Return the decorator
        return decorator
