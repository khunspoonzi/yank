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

        # Initialize response to None
        self.response = None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ SET RESPONSE                                                                   │
    # └────────────────────────────────────────────────────────────────────────────────┘

    def set_response(self, response):
        """ Sets a response to the current request object """

        # Set response
        self.response = response

        print(response)

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ IS LOADING                                                                     │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def is_loading(self):
        """
        Returns a boolean of whether the request is loading based on presence of a
        response
        """
        return self.response is None

    # ┌────────────────────────────────────────────────────────────────────────────────┐
    # │ STATUS CODE                                                                    │
    # └────────────────────────────────────────────────────────────────────────────────┘

    @property
    def status_code(self):
        """ Returns the status code of the request's response object """

        # Return response status code
        return self.response.status_code if self.response else None
