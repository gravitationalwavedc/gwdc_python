import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm
from humps import camelize, decamelize

from .exceptions import GWDCRequestException, handle_request_errors
from .utils import split_variables_dict
from .logger import create_logger

AUTH_ENDPOINT = 'https://gwcloud.org.au/auth/graphql'

logger = create_logger(__name__)


class GWDC:
    def __init__(self, token, endpoint):
        self.api_token = token
        self.endpoint = endpoint
        self._obtain_access_token()

    def _request(self, endpoint, query, variables=None, headers={}, method="POST"):
        variables = camelize(variables)
        variables, files, files_map = split_variables_dict(variables)

        if files:
            operations = {
                "query": query,
                "variables": variables,
                "operationName": query.replace('(', ' ').split()[1]  # Hack for getting mutation name from query string
            }

            e = MultipartEncoder({
                "operations": json.dumps(operations),
                "map": json.dumps(files_map),
                **files
            })

            encoder_len = e.len
            bar = tqdm(total=encoder_len, leave=True, unit='B', unit_scale=True)

            def update_progress(mon):
                update_bytes = mon.bytes_read - bar.n
                bar.update(update_bytes)

                if not update_bytes:
                    bar.close()
                    logger.info("Files are being processed remotely, please be patient. This may take a while...")

            m = MultipartEncoderMonitor(e, update_progress)

            request_params = {
                "data": m
            }

            headers['Content-Type'] = m.content_type
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
            return decamelize(content.get('data', None))
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
        self.jwt_token = data["jwt_token"]["jwt_token"]
        self.refresh_token = data["jwt_token"]["refresh_token"]

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
            variables={"refresh_token": self.refresh_token}
        )
        self.jwt_token = data["refresh_token"]["token"]
        self.refresh_token = data["refresh_token"]["refresh_token"]

    @handle_request_errors
    def request(self, query, variables=None, headers=None, authorize=True):

        all_headers = {'Authorization': 'JWT ' + self.jwt_token} if authorize else {}
        if headers is not None:
            all_headers = {**all_headers, **headers}

        return self._request(endpoint=self.endpoint, query=query, variables=variables, headers=all_headers)
