import functools


class GWDCUnknownException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class GWDCAuthenticationError(Exception):
    raise_msg = "Invalid API token provided"

    def __init__(self):
        super().__init__(self.__class__.raise_msg)
