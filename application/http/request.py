from dataclasses import dataclass
from typing import Optional


@dataclass
class Request:
    env: dict
    method: str = ""
    path: str = ""
    body: bytes = b""
    headers: dict = None
    cookies: dict = None
    GET: Optional[dict] = None
    POST: Optional[dict] = None

    def __post_init__(self):
        self.method = self.env["REQUEST_METHOD"]
        self.path = self.env["PATH_INFO"]
        self.body = self.env["wsgi.input"].read()

        if self.headers is None:
            self.headers = {}
        self.headers["CONTENT_TYPE"] = self.env["CONTENT_TYPE"]
        self.headers["CONTENT_LENGTH"] = self.env["CONTENT_LENGTH"]

        if self.cookies is None:
            self.cookies = {}

        if "HTTP_COOKIE" in self.env:
            cookies_list = self.env["HTTP_COOKIE"].split("; ")
            for cookie in cookies_list:
                key, value = cookie.split("=")
                self.cookies[key] = value

        if self.GET is None:
            self.GET = {}

        if self.method == "GET" and self.env["QUERY_STRING"]:
            for pair in self.env["QUERY_STRING"].split("&"):
                key, value = pair.split("=")
                self.GET[key] = value

        if self.POST is None:
            self.POST = {}

        if self.method == "POST" and self.headers["CONTENT_TYPE"] == "application/x-www-form-urlencoded":
            for pair in self.body.decode().split("&"):
                key, value = pair.split("=")
                self.POST[key] = value
