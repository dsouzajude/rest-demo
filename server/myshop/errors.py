class ApiException(Exception):
    code = 400

    def __init__(self, message='', **kwargs):
        super(ApiException, self).__init__(message)
        self.extra_data = kwargs


class UserExists(ApiException):
    code = 409


class BadRequest(ApiException):
    pass


class SessionExpired(ApiException):
    code = 401


class Unauthorized(ApiException):
    code = 401


class InvalidLogin(ApiException):
    code = 401
