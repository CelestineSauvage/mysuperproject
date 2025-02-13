import json
import sys
import logging
from helpers.HttpCaller import HttpCaller, UnauthorizedException

logger = logging.getLogger(__name__)


class Oauth2Helper:
    # Class for OAuth2 authentication

    def __init__(self):
        pass

    @staticmethod
    def get_access_token_by_client_credential(access_token_url: str, scope: str, client_id: str, client_secret: str, params: dict = {}) -> str:
        # Function to get an access token via the 'client_credentials' OAuth2 Grant Type
        # - https://www.oauth.com/oauth2-servers/access-tokens/client-credentials/

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        body = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

        response = HttpCaller.post(
            url=access_token_url, headers=headers, params=params, body=body)

        if response.status_code == 401:
            raise UnauthorizedException("Wrong client_id or client_secret")
            sys.exit(1)

        # Convert response to a JSON object
        jsonResponse = json.loads(response.text)
        access_token = jsonResponse["access_token"]
        expire = int(jsonResponse["expires_in"])
        logger.info(f"Obtained access_token {access_token}"
                    f"that will expires in {expire / 60} minutes.")

        return access_token
