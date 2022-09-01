import typing as t
from vendor import httpx

__all__ = (
    "HubstaffError",
    "InvalidParameters",
    "Unauthorized",
    "InactiveOrganization",
    "NotFound",
    "RateLimitExceeded",
)


class HubstaffError(Exception):
    status_code: t.ClassVar[int]

    def __init__(self, response_data: t.Any):
        self.response_data = response_data


class InvalidParameters(HubstaffError):
    status_code = 400


class Unauthorized(HubstaffError):
    status_code = 401


class InactiveOrganization(HubstaffError):
    status_code = 403


class NotFound(HubstaffError):
    status_code = 404


class RateLimitExceeded(HubstaffError):
    status_code = 429


def response_error(response: httpx.Response):
    for cls in HubstaffError.__subclasses__():
        if cls.status_code == response.status_code:
             return cls(response.content)

    raise LookupError(response.status_code)
