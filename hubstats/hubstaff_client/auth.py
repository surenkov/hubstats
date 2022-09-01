import time
import typing as t

from urllib.parse import urljoin
from vendor.httpx import Auth, Request, Response


class HubstaffAuth(Auth):
    requires_response_body = True

    base_url: t.ClassVar[str] = "https://account.hubstaff.com/"
    token_endpoint: t.ClassVar[str] = "/access_tokens"

    def __init__(self, personal_token: str):
        self.personal_token = personal_token
        self.access_token: t.Optional[str] = None
        self._expire_eta: float = time.monotonic()

    def auth_flow(self, request: Request):
        if self.access_token is None:
            yield from self.perform_auth_request()

        response = yield self.authenticate_request(request)
        if response.status_code == 401:
            yield from self.perform_auth_request()

        yield self.authenticate_request(request)

    @property
    def should_refresh_token(self):
        return self.access_token is None or self._expire_eta <= time.monotonic()

    def authenticate_request(self, request: Request) -> Request:
        assert self.access_token is not None, "Access token should be set"
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        return request

    def perform_auth_request(self):
        response = yield self.build_token_request()
        self.record_refresh_token(response)

    def build_token_request(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        credentials = {
            "grant_type": "refresh_token",
            "refresh_token": self.personal_token,
        }
        url = urljoin(self.base_url, self.token_endpoint)
        self._expire_eta = time.monotonic()
        return Request("POST", url, data=credentials, headers=headers)

    def record_refresh_token(self, response: Response):
        data = response.json()
        self.access_token = data["access_token"]
        self._expire_eta += data["expires_in"]
