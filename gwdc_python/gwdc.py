import json
import logging
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm

from .exceptions import GWDCRequestException, handle_request_errors
from .utils import split_variables_dict

AUTH_ENDPOINT = 'https://gwcloud.org.au/auth/graphql'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class GWDC:
    def __init__(self, token, endpoint):
        self.api_token = token
        self.endpoint = endpoint
        self._obtain_access_token()

    def _request(self, endpoint, query, variables=None, headers={}, method="POST"):
        variables, files, files_map = split_variables_dict(variables)
        bar = None
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

            last_progress = 0

            def update_progress(mon):
                nonlocal last_progress
                s = mon.bytes_read - last_progress
                last_progress = mon.bytes_read
                bar.update(s)

                if mon.bytes_read == encoder_len:
                    logger.info("Job upload is being processed remotely, please be patient. This may take a while...")

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

        if bar:
            bar.close()

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
    def request(self, query, variables=None, headers=None, authorize=True):

        all_headers = {'Authorization': 'JWT ' + self.jwt_token} if authorize else {}
        if headers is not None:
            all_headers = {**all_headers, **headers}

        return self._request(endpoint=self.endpoint, query=query, variables=variables, headers=all_headers)
