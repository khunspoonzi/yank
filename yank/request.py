# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SELENIUM IMPORTS                                                                   │
# └────────────────────────────────────────────────────────────────────────────────────┘

from seleniumwire.request import HTTPHeaders


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ REQUEST                                                                            │
# └────────────────────────────────────────────────────────────────────────────────────┘


class Request:
    """ A utility class used to represent a single HTTP request """

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ INIT METHOD                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def __init__(self, url):
        """ Init Method """

        # Set URL
        self.url = url

        # Initialize headers to None
        self.headers = None

        # Initialize response to None
        self.response = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SET RESPONSE                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def set_response(self, response):
        """ Sets a response to the current request object """

        # Get headers
        headers = response.request.headers

        # Check if headers is a Seleniumwire HTTPHeader object
        if type(headers) is HTTPHeaders:

            # Convert headers to dict
            headers = dict(headers)

        # Set request headers
        self.headers = headers

        # Set response
        self.response = response

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ STATUS CODE                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def status_code(self):
        """ Returns the status code of the request's response object """

        # Return response status code
        return self.response.status_code if self.response is not None else None
