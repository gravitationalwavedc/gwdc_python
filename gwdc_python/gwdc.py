import json
from pathlib import Path
from uuid import uuid4

import requests
from appdirs import user_config_dir
from humps import camelize, decamelize
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm

from .constants import APP_NAME, ORGANISATION
from .exceptions import GWDCRequestException, handle_request_errors
from .logger import create_logger
from .utils import split_variables_dict

logger = create_logger(__name__)


class GWDC:
    def __init__(self, token, auth_endpoint, endpoint, custom_error_handler=None):
        self.api_token = token
        self.auth_endpoint = auth_endpoint
        self.endpoint = endpoint
        if custom_error_handler:
            self._apply_custom_error_handler(custom_error_handler)

        if self.api_token:
            self._obtain_access_token()
        else:
            self.public_id = self._obtain_public_id()
            self.session_id = self._obtain_session_id()

    def _obtain_session_id(self):
        return str(uuid4())

    def _obtain_public_id(self):
        config_file = Path(user_config_dir(APP_NAME, ORGANISATION)) / 'config.json'

        def write_new_config():
            uuid = str(uuid4())

            config = {
                'public_id': uuid
            }

            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text(json.dumps(config))

        if not config_file.exists():
            write_new_config()

        try:
            return json.loads(config_file.read_text())['public_id']
        except Exception:
            write_new_config()
            return json.loads(config_file.read_text())['public_id']

    def _apply_custom_error_handler(self, custom_error_handler):
        self._obtain_access_token = custom_error_handler(self._obtain_access_token)
        self._refresh_access_token = custom_error_handler(self._refresh_access_token)
        self.request = custom_error_handler(self.request)

    def _request(self, endpoint, query, variables=None, headers=None, method="POST"):
        if headers is None:
            headers = {}

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
            endpoint=self.auth_endpoint,
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
            endpoint=self.auth_endpoint,
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

        all_headers = {}
        if authorize:
            if self.api_token:
                all_headers = {'Authorization': 'JWT ' + self.jwt_token}
            elif self.public_id:
                all_headers = {'X-Correlation-ID': f"{self.public_id} {self.session_id}"}

        if headers is not None:
            all_headers = {**all_headers, **headers}

        return self._request(endpoint=self.endpoint, query=query, variables=variables, headers=all_headers)
