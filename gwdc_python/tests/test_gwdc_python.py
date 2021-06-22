import pytest
import json
from gwdc_python.gwdc import GWDC
from gwdc_python.exceptions import AuthenticationError


# Set up possible data responses from auth server
def access_token_response():
    data = {
        "jwtToken": {
            "jwtToken": "mock_jwt_token",
            "refreshToken": "mock_refresh_token"
        }
    }
    return {"text": json.dumps({"data": data})}


def refresh_token_response():
    data = {
        "refreshToken": {
            "token": "mock_jwt_token_new",
            "refreshToken": "mock_refresh_token_new"
        }
    }
    return {"text": json.dumps({"data": data})}


# Set up possible error responses from auth server
def api_token_incorrect():
    errors = [{"message": "APIToken matching query does not exist."}]
    return {"text": json.dumps({"errors": errors})}


# Set up possible data responses from Bilby server
def request_test_response():
    data = {
        "testResponse": "mock_response"
    }
    return {"text": json.dumps({"data": data})}


# Set up possible error responses from Bilby server
def access_token_expired():
    errors = [{"message": 'Signature has expired'}]
    return {"text": json.dumps({"errors": errors})}


# Set up GWDC class with specified responses
@pytest.fixture
def setup_gwdc(requests_mock):
    def _setup_gwdc(auth_responses=[], responses=[]):
        auth_response_list = [response() for response in auth_responses]
        response_list = [response() for response in responses]
        requests_mock.post('https://gwcloud.org.au/auth/graphql', auth_response_list)
        requests_mock.post('https://gwcloud.org.au/bilby/graphql', response_list)
        return GWDC(token='mock_token', endpoint='https://gwcloud.org.au/bilby/graphql')
    return _setup_gwdc


# Test that GWDC will raise an AuthenticationError if the API Token cannot be found in the auth database
def test_gwdc_api_token(setup_gwdc):
    with pytest.raises(AuthenticationError):
        setup_gwdc(
            auth_responses=[api_token_incorrect]
        )


# Test GWDC setup, obtaining initial access token
def test_gwdc_init(setup_gwdc):
    gwdc = setup_gwdc(
        auth_responses=[access_token_response]
    )
    assert gwdc.jwt_token == "mock_jwt_token"
    assert gwdc.refresh_token == "mock_refresh_token"


# Test that refreshing token works
def test_gwdc_refresh(setup_gwdc):
    gwdc = setup_gwdc(
        auth_responses=[access_token_response, refresh_token_response]
    )
    gwdc._refresh_access_token()
    assert gwdc.jwt_token == "mock_jwt_token_new"
    assert gwdc.refresh_token == "mock_refresh_token_new"


# Test that a token will be automatically refreshed if it has expired
def test_gwdc_request(setup_gwdc):
    gwdc = setup_gwdc(
        auth_responses=[access_token_response, refresh_token_response],
        responses=[access_token_expired, request_test_response]
    )
    assert gwdc.jwt_token == "mock_jwt_token"
    assert gwdc.refresh_token == "mock_refresh_token"
    response = gwdc.request(
        query="""
            query {
                testResponse
            }
        """
    )
    assert gwdc.jwt_token == "mock_jwt_token_new"
    assert gwdc.refresh_token == "mock_refresh_token_new"
    assert response["testResponse"] == "mock_response"
