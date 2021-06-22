import requests
import json
from .utils import split_variables_dict
from .exceptions import GWDCRequestException, handle_request_errors

AUTH_ENDPOINT = 'https://gwcloud.org.au/auth/graphql'


class GWDC:
    def __init__(self, token, endpoint):
        self.api_token = token
        self.endpoint = endpoint
        self._obtain_access_token()

    def _request(self, endpoint, query, variables=None, headers=None, method="POST"):
        variables, files, files_map = split_variables_dict(variables)
        if files:
            operations = {
                "query": query,
                "variables": variables,
                "operationName": query.replace('(', ' ').split()[1]  # Hack for getting mutation name from query string
            }

            request_params = {
                "data": {
                    "operations": json.dumps(operations),
                    "map": json.dumps(files_map),
                    **files
                },
                "files": files
            }
        else:
            request_params = {
                "json": {
                    "query": query,
                    "variables": variables
                }
            }

        request = requests.request(
            method=method,
            url=endpoint,
            headers=headers,
            **request_params
        )

        content = json.loads(request.content)
        errors = content.get('errors', None)
        if not errors:
            return content.get('data', None)
        else:
            raise GWDCRequestException(gwdc=self, msg=errors[0].get('message'))

    @handle_request_errors
    def _obtain_access_token(self):
        data = self._request(
            endpoint=AUTH_ENDPOINT,
            query="""
                query ($token: String!){
                    jwtToken (token: $token) {
                        jwtToken
                        refreshToken
                    }
                }
            """,
            variables={"token": self.api_token}
        )
        self.jwt_token = data["jwtToken"]["jwtToken"]
        self.refresh_token = data["jwtToken"]["refreshToken"]

    @handle_request_errors
    def _refresh_access_token(self):
        data = self._request(
            endpoint=AUTH_ENDPOINT,
            query="""
                mutation RefreshToken ($refreshToken: String!){
                    refreshToken (refreshToken: $refreshToken) {
                        token
                        refreshToken
                    }
                }
            """,
            variables={"refreshToken": self.refresh_token}
        )

        self.jwt_token = data["refreshToken"]["token"]
        self.refresh_token = data["refreshToken"]["refreshToken"]

    @handle_request_errors
    def request(self, query, variables=None, headers=None):

        all_headers = {'Authorization': 'JWT ' + self.jwt_token}
        if headers is not None:
            all_headers = {**all_headers, **headers} 

        return self._request(endpoint=self.endpoint, query=query, variables=variables, headers=all_headers)
