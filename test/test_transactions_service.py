import mock
import pytest
import requests_mock
import requests
from models.block import Block

from src.transactions_service import TransactionsService
from data.data import Database


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@mock.patch("data.data.Database.__init__", return_value=None)
@pytest.fixture
def mock_transactions_service():
    ts = TransactionsService("filepath")
    ts.endpoint = "http://test-endpoint/"
    return ts


@pytest.fixture
def mock_api():
    with requests_mock.Mocker() as m:
        yield m


def test_save_transactions_by_block_range():
    pass


def test_fetch_block_data_success(mock_transactions_service, mock_api):
    endpoint = "http://test-endpoint/"
    mock_result = 2
    mock_data = {"result": mock_result}
    mock_api.post(endpoint, json=mock_data)
    res = mock_transactions_service.fetch_block_data("123")
    assert res == mock_result


def test_fetch_block_data_http_error():
    pass


def test__parse_block(mock_transactions_service):
    hash = "ahash"
    number = "201"
    timestamp = "2022:2012"
    transactions = ["134134", "123120398"]
    mock_response = {
        "hash": hash,
        "number": number,
        "timestamp": timestamp,
        "transactions": transactions,
    }
    res = mock_transactions_service._parse_block(mock_response)
    assert type(res) == Block
    assert res.hash == hash
    assert res.number == number
    assert res.timestamp == timestamp
    assert res.transactions == transactions


def test__parse_transaction():
    pass


def test__parse_block_range(mock_transactions_service):
    range_start = "105"
    range_end = "422"
    assert mock_transactions_service._parse_block_range(
        f"{range_start}-{range_end}"
    ) == [range_start, range_end]


def test__string_to_hex(mock_transactions_service):
    string_hex = [("255", "0xff")]
    for s, h in string_hex:
        assert mock_transactions_service._string_to_hex(s) == h


def test__convert_to_ether(mock_transactions_service):
    wei_ether = [(1, 1 * 10**-18)]
    for w, e in wei_ether:
        assert mock_transactions_service._convert_to_ether(w) == e


def test__hex_to_int(mock_transactions_service):
    hex_int = [("0xff", 255)]
    for h, i in hex_int:
        assert mock_transactions_service._hex_to_int(h) == i
