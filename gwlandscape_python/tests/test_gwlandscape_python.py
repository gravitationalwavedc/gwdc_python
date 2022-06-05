import pytest

from gwlandscape_python import GWLandscape


@pytest.fixture
def mock_gwdc_init(mocker):
    def mock_init(self, token, endpoint):
        pass

    mocker.patch('gwdc_python.gwdc.GWDC.__init__', mock_init)


@pytest.fixture
def setup_mock_gwdc(mocker, mock_gwdc_init):
    def mock_gwdc(request_data):
        mock_request = mocker.Mock(return_value=request_data)
        mocker.patch('gwdc_python.gwdc.GWDC.request', mock_request)

    return mock_gwdc


def test_constructor(mock_gwdc_init):
    gw = GWLandscape(token='test_token')
    assert gw.request == gw.client.request
