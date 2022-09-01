import configparser
import time
import typing as t

from os import PathLike
from urllib.parse import urljoin

from vendor.httpx import Auth, Request, Response


class HubstaffAuth(Auth):
    requires_response_body = True

    base_url: t.ClassVar[str] = "https://account.hubstaff.com"
    token_endpoint: t.ClassVar[str] = "/access_tokens"

    def __init__(self, token_mgr: "AbcTokenManager"):
        self.token_mgr = token_mgr

    def auth_flow(self, request: Request):
        if self.token_mgr.should_refresh_token:
            yield from self.perform_auth_request()

        response = yield self.authenticate_request(request)
        if response.status_code == 401:
            yield from self.perform_auth_request()

        yield self.authenticate_request(request)

    def authenticate_request(self, request: Request) -> Request:
        assert self.token_mgr.access_token, "Access token should be set"
        request.headers["Authorization"] = f"Bearer {self.token_mgr.access_token}"
        return request

    def perform_auth_request(self):
        with self.token_mgr:
            response = yield self.build_token_request()
            self.record_refresh_token(response)

    def build_token_request(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        credentials = {
            "grant_type": "refresh_token",
            "refresh_token": self.token_mgr.refresh_token,
        }
        url = urljoin(self.base_url, self.token_endpoint)
        return Request("POST", url, data=credentials, headers=headers)

    def record_refresh_token(self, response: Response):
        data = response.json()
        self.token_mgr.access_token = data["access_token"]
        self.token_mgr.refresh_token = data["refresh_token"]
        self.token_mgr.expires_in(data["expires_in"])


class AbcTokenManager(t.ContextManager):
    access_token: str = ""
    refresh_token: str = ""
    expire_eta: int = 0

    @property
    def should_refresh_token(self):
        return not self.access_token or self.expire_eta <= time.time()

    def __enter__(self):
        self.expire_eta = int(time.time())

    def expires_in(self, inc: int):
        self.expire_eta += inc


class ConfigTokenManager(AbcTokenManager):
    namespace: t.ClassVar[str] = "HUBSTAFF_API"

    def __init__(self, cfg: configparser.ConfigParser, config_path: t.Union[str, PathLike, None] = None):
        self.config = cfg
        self.config_path = config_path

        self.refresh_token = cfg.get(self.namespace, "refresh_token", fallback=cfg.get("DEFAULT", "personal_token"))
        self.access_token = cfg.get(self.namespace, "access_token", fallback=self.access_token)
        self.expire_eta = cfg.getint(self.namespace, "expire_eta", fallback=self.expire_eta)

    def __exit__(self, exc_type, *exc_info):
        if exc_type is None:
            self._update_config()

            if self.config_path is not None:
                self._write_config_to_file()

    def _update_config(self):
        if not self.config.has_section(self.namespace):
            self.config.add_section(self.namespace)

        self.config.set(self.namespace, "access_token", self.access_token)
        self.config.set(self.namespace, "refresh_token", self.refresh_token)
        self.config.set(self.namespace, "expire_eta", str(self.expire_eta))

    def _write_config_to_file(self):
        assert self.config_path is not None

        with open(self.config_path, "w") as cfg_file:
            self.config.write(cfg_file)
