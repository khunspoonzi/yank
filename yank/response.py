# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ GENERAL IMPORTS                                                                    │
# └────────────────────────────────────────────────────────────────────────────────────┘

from json.decoder import JSONDecodeError

# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ BEAUTIFUL SOUP IMPORTS                                                             │
# └────────────────────────────────────────────────────────────────────────────────────┘

from bs4 import BeautifulSoup


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ RESPONSE                                                                           │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Response:
    """ A utility class used to represent a single HTTP response """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, request, response):
        """ Init Method """

        # Set request
        self.request = request

        # Set response
        self._response = response

        # Initialize cached JSON
        self._json = None

        # Initialize cached soup
        self._soup = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ STATUS CODE                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def status_code(self):
        """ Returns the status code of the request's response object """

        # Return response status code
        return self._response.status_code

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ HTML                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def html(self):
        """ Returns the HTML source of the response depending driver and response """

        # Return driver source if driver is defined otherwise response content
        return (
            self.request.driver.page_source
            if self.request.driver
            else self._response.content
        )

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ JSON                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def json(self):
        """ Returns a JSON dict of the response object """

        # Check if JSON is cached
        if self._json is not None:

            # Return cached JSON
            return self._json

        try:

            # Get JSON
            _json = self._response.json()

            # Cache JSON
            self._json = _json

            # Return JSON data
            return _json

        except (AttributeError, JSONDecodeError):

            # Return None
            return None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SOUP                                                                           │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def soup(self):
        """ Returns a HTML BeautifulSoup of the response object """

        # Check if soup is cached
        if self._soup is not None:

            # Return cached soup
            return self._soup

        # Get soup
        _soup = BeautifulSoup(self.html, "lxml")

        # Cache soup
        self._soup = _soup

        # Return soup data
        return _soup
