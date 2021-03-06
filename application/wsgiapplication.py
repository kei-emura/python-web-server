import traceback
from typing import Iterable, List, Callable

from application.http.request import Request
from application.http.response import Response, ResponseNotFound, ResponseServerError
from application.views.parameters import ParametersView
from application.views.headers import HeadersView
from application.views.now import NowView
from application.views.index import IndexView
from application.views.static import StaticView
from application.views.cookie import SetCookieView
from application.views.user import UserView
from application.views.errors import page_not_found, server_error
from application.views.base import BaseView
from application.utils import add_slash

URL_VIEW = {
    "/": IndexView(),
    "/now/": NowView(),
    "/headers/": HeadersView(),
    "/parameters/": ParametersView(),
    "/set_cookie/": SetCookieView(),
    "/user/": UserView(),
}


class WSGIApplication:
    env: dict
    start_response: Callable[[str, List[tuple]], None]

    @staticmethod
    def create_response(request: Request) -> Response:
        try:
            path = add_slash(request.path)
            if path.startswith("/static/"):
                return StaticView().get_response(request)

            elif path in URL_VIEW:
                view: BaseView = URL_VIEW[path]
                return view.get_response(request)

            else:
                raise FileNotFoundError

        except FileNotFoundError:
            return page_not_found()

        except Exception:
            print("WsgiApplication 500 Error: " + traceback.format_exc())
            return server_error()

    def set_response_to_start_response(self, response: Response) -> None:
        headers = [(k, v) for k, v in response.headers.items()]
        if response.cookies:
            cookies = [("Set-Cookie", f"{k}={v}") for k, v in response.cookies.items()]
            headers = headers + cookies
        self.start_response(response.status, headers)

    def application(self, env: dict, start_response: Callable[[str, Iterable[tuple]], None]) -> Iterable[bytes]:
        self.env = env
        self.start_response = start_response

        request = Request(env)
        response: Response = self.create_response(request)
        self.set_response_to_start_response(response)

        return [response.body]
