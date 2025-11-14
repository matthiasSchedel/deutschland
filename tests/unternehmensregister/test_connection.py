import pytest
from deutschland.unternehmensregister import Unternehmensregister


def test_exception_on_invalid_http_code():
    ur = Unternehmensregister()
    with pytest.raises(ConnectionError):
        ur._Unternehmensregister__get_response("https://mock.httpstatus.io/500")
        ur._Unternehmensregister__get_response("https://mock.httpstatus.io/503")
        ur._Unternehmensregister__get_response("https://mock.httpstatus.io/404")


def test_get_response():
    ur = Unternehmensregister()
    assert (
        ur._Unternehmensregister__get_response("https://mock.httpstatus.io/200").status_code
        == 200
    )
