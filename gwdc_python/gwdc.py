import requests
import json
import jwt
from .utils import split_variables_dict

AUTH_ENDPOINT = 'https://gwcloud.org.au/auth/graphql'

class GWDC:
    def __init__(self, token, endpoint):
        self.api_token = token
        self.endpoint = endpoint
        self._obtain_access_token()

    def _request(self, endpoint, query, variables=None, headers=None, method="POST"):
        request = requests.request(
            method=method,
            url=endpoint,
            json={
                "query": query,
                "variables": variables
            },
            headers=headers
        )
        content = json.loads(request.content)
        return content.get('data', None), content.get('errors', None)

    def _file_upload_request(self, endpoint, query, variables=None, files=None, files_map=None, headers=None, method="POST"):

        operations = {
            "query": query,
            "variables": variables,
            "operationName": query.replace('(', ' ').split()[1] # Hack for getting mutation name from query string
        }
        
        data = {
            "operations": json.dumps(operations),
            "map": json.dumps(files_map),
            **files
        }

        request = requests.request(
            method=method,
            url=endpoint,
            data=data,
            headers=headers,
            files=files
        )

        content = json.loads(request.content)
        return content.get('data', None), content.get('errors', None)

    def _obtain_access_token(self):
        data, errors = self._request(
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


    def _refresh_access_token(self):
        data, errors = self._request(
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


    def request(self, query, variables=None, headers=None):
        variables, files, files_map = split_variables_dict(variables)

        all_headers = {'Authorization': 'JWT ' + self.jwt_token}
        if headers is not None:
            all_headers = {**all_headers, **headers} 
        
        if files:
            data, errors = self._file_upload_request(endpoint=self.endpoint, query=query, variables=variables, files=files, files_map=files_map, headers=all_headers)
        else:
            data, errors = self._request(endpoint=self.endpoint, query=query, variables=variables, headers=all_headers)

        if not errors:
            return data, errors
        else:
            error = errors[0].get('message')
            if error == 'Signature has expired':
                self._refresh_access_token()
                return self.request(query, variables, headers)
            else:
                raise Exception(error)
