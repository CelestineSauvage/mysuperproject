import requests


class HttpCaller:
    # Class for calling HTTP APIs with OAth2 authentication

    def __init__(self):
        pass

    @staticmethod
    def get(url: str, headers: dict = {}, params: dict = {}, cookies: dict = {}) -> requests.Response:
        # Static function to execute a GET query with OAuth2 authentication

        # Get the results
        response = requests.get(
            url,
            headers=headers,
            params=params,
            cookies=cookies
        )

        HttpCaller.__print_status_code(url, "GET", response)
        return response

    @staticmethod
    def post(url: str, headers: dict = {}, params: dict = {}, body: dict = {}) -> requests.Response:
        # Static function to execute a POST query with OAuth2 authentication

        # Get the access token
        response = requests.post(
            url,
            data=body,
            headers=headers,
            params=params,
        )

        HttpCaller.__print_status_code(url, "POST", response)
        return response

    @classmethod
    def __print_status_code(self, url: str, verb: str, response: requests.Response):
        print("Status Code for HTTP", verb, "on",
              url, ':', response.status_code)


class UnauthorizedException(Exception):
    pass
