# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ SESSION LIMIT REACHED                                                              │
# └────────────────────────────────────────────────────────────────────────────────────┘


class SessionLimitReached(Exception):
    """ Session Limit Reached """


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ UNSUPPORTED BROWSER ERROR                                                          │
# └────────────────────────────────────────────────────────────────────────────────────┘


class UnsupportedBrowserError(Exception):
    """ Unsupported Browser Error """


# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ UNSUPPORTED DRIVER MODE ERROR                                                      │
# └────────────────────────────────────────────────────────────────────────────────────┘


class UnsupportedDriverModeError(Exception):
    """ Unsupported Driver Mode Error """
