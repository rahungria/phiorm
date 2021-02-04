import philog


class ORMException(Exception):
    pass


class ORMFatal(ORMException):
    def __init__(self, msg):
        self.msg = msg
        philog.fatal(
            f'Exception Caught: {msg}.'
        )
        super().__init__(msg)

    def __str__(self):
        return self.msg


class ORMError(ORMException):
    def __init__(self, msg):
        self.msg = msg
        philog.error(
            f'Exception Caught: {msg}.'
        )
        super().__init__(msg)

    def __str__(self):
        return self.msg


class ConnectionError(ORMError):
    pass


class ConfigurationError(ORMError):
    pass


class FieldError(ORMError):
    '''
    Logged error exception

    fields -- stores info on which fields caused the error
    '''
    def __init__(self, msg, fields):
        self.fields = fields
        super().__init__(msg)


class ValidationError(ORMError):
    pass
