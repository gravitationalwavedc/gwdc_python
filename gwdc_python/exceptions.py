import functools


class GWDCRequestException(Exception):
    def __init__(self, gwdc, msg):
        self.gwdc = gwdc
        self.msg = msg
        super().__init__(self.msg)


class GWDCUnknownException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class GWDCAuthenticationError(Exception):
    raise_msg = 'APIToken matching query does not exist.'

    def __init__(self):
        super().__init__(self.__class__.raise_msg)


def handle_request_errors(func):
    @functools.wraps(func)
    def wrapper_handle_exceptions(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GWDCRequestException as exc:
            if exc.msg == 'Signature has expired':
                exc.gwdc._refresh_access_token()
                return func(*args, **kwargs)

            for exception in (GWDCAuthenticationError,):
                if exc.msg == exception.raise_msg:
                    raise exception
            else:
                raise GWDCUnknownException(exc.msg)
    return wrapper_handle_exceptions
