import pytest
import json
from gwdc_python.gwdc import GWDC
from gwdc_python.exceptions import GWDCAuthenticationError, GWDCUnknownException


def api_token_request(is_authenticated):
    def _api_token_request():
        data = {"sessionUser": {"isAuthenticated": is_authenticated}}
        return {"text": json.dumps({"data": data})}

    return _api_token_request


# Set up possible data responses from Bilby server
def request_test_response():
    data = {"testResponse": "mock_response"}
    return {"text": json.dumps({"data": data})}


# Set up GWDC class with specified responses
@pytest.fixture
def setup_gwdc(requests_mock):
    def _setup_gwdc(responses=None, error_handler=None, token="mock_token"):
        if responses is None:
            responses = []

        response_list = [response() for response in responses]
        requests_mock.post("https://gwcloud.org.au/graphql", response_list)
        return GWDC(
            token=token,
            endpoint="https://gwcloud.org.au/graphql",
            custom_error_handler=error_handler,
        )

    return _setup_gwdc


# Test GWDC setup, obtaining initial access token
def test_gwdc_init(setup_gwdc, requests_mock):
    gwdc = setup_gwdc(responses=[api_token_request(True)])
    assert gwdc.api_token == "mock_token"
    assert requests_mock.call_count == 1
    assert "Authorization" in requests_mock.request_history[0].headers
    assert requests_mock.request_history[0].headers["Authorization"] == "mock_token"


# Test that GWDC will raise an GWDCAuthenticationError if the API Token cannot be found in the auth database
def test_gwdc_api_token(setup_gwdc):
    with pytest.raises(GWDCAuthenticationError):
        setup_gwdc(responses=[api_token_request(False)])


# Test that GWDC will allow the custom error handler to intercept raised errors
def test_gwdc_custom_error_handling_token(setup_gwdc):
    class TestException(Exception):
        pass

    def custom_error_handler(f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except GWDCAuthenticationError:
                raise TestException

        return wrapper

    with pytest.raises(TestException):
        setup_gwdc(
            responses=[api_token_request(False)], error_handler=custom_error_handler
        )


# Test that creating an instance without a token works
def test_gwdc_no_token(setup_gwdc, requests_mock):
    try:
        setup_gwdc(responses=[], token="")
    except json.decoder.JSONDecodeError:
        pytest.fail("Unexpected error when creating GWDC without a token")

    assert requests_mock.call_count == 0


# Test that requests still work correctly without providing a token
def test_gwdc_request_no_token(setup_gwdc, requests_mock):
    gwdc = setup_gwdc(responses=[request_test_response], token="")

    response = gwdc.request(query="""
            query {
                testResponse
            }
        """)

    assert response["test_response"] == "mock_response"

    # Authorization should not have been provided in the headers
    assert "Authorization" not in requests_mock.request_history[0].headers
    assert "X-Correlation-ID" in requests_mock.request_history[0].headers


# Test that requests can accept arbitrary variables
def test_gwdc_request_variables(setup_gwdc, requests_mock):
    gwdc = setup_gwdc(responses=[request_test_response], token="")

    response = gwdc.request(query="""
            query { 
                testResponse
            }
        """)

    assert response["test_response"] == "mock_response"

    response = gwdc.request(
        query="""
            query { 
                testResponse
            }
        """,
        variables=None,
    )
    assert response["test_response"] == "mock_response"

    response = gwdc.request(
        query="""
            query { 
                testResponse
            }
        """,
        variables={},
    )
    assert response["test_response"] == "mock_response"

    response = gwdc.request(
        query="""
            query { 
                testResponse
            }
        """,
        variables={"the hat": "the cat"},
    )
    assert response["test_response"] == "mock_response"


# Set up a GraphQL error response, optionally with extensions on the first error
def error_response(message="m", extensions=None):
    def _error_response():
        error = {"message": message}
        if extensions is not None:
            error["extensions"] = extensions
        return {"text": json.dumps({"errors": [error]})}

    return _error_response


# Test that extensions passed to GWDCUnknownException are stored and retrievable
def test_exception_extensions_round_trip():
    extensions = {"missing_files": ["/a"]}
    exception = GWDCUnknownException("m", extensions=extensions)

    assert exception.extensions == {"missing_files": ["/a"]}


# Test that extensions defaults to None when not provided
def test_exception_extensions_default_none():
    exception = GWDCUnknownException("m")

    assert exception.extensions is None


# Test that positional construction is unchanged for backwards compatibility
def test_exception_backwards_compat():
    exception = GWDCUnknownException("m")

    assert str(exception) == "m"
    assert exception.msg == "m"


# Test that non-dict extensions values are stored as-is
def test_exception_extensions_non_dict_stored_as_is():
    exception = GWDCUnknownException("m", extensions="boom")

    assert exception.extensions == "boom"


# Test that _request raises GWDCUnknownException carrying extensions from the error payload
def test_request_raises_with_extensions(setup_gwdc):
    gwdc = setup_gwdc(
        responses=[error_response(extensions={"missing_files": ["/a", "/b"]})],
        token="",
    )

    with pytest.raises(GWDCUnknownException) as excinfo:
        gwdc.request(query="""
                query {
                    testResponse
                }
            """)

    assert excinfo.value.extensions["missing_files"] == ["/a", "/b"]


# Test that _request raises with extensions=None when the error has none
def test_request_raises_without_extensions(setup_gwdc):
    gwdc = setup_gwdc(responses=[error_response()], token="")

    with pytest.raises(GWDCUnknownException) as excinfo:
        gwdc.request(query="""
                query {
                    testResponse
                }
            """)

    assert excinfo.value.extensions is None
