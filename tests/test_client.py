import pytest

from virtualsms.client import VirtualSMSClient
from virtualsms.transport import Transport, Response
from virtualsms.constants import ActivationStatus
from virtualsms.exceptions import (
    AuthenticationException,
    InsufficientBalanceException,
    NoNumbersException,
    VirtualSMSException,
)
from virtualsms.response import BalanceResponse, NumberResponse


class MockTransport(Transport):
    def __init__(self):
        self.last_url = None
        self.last_headers = {}
        self._response = None

    def set_response(self, response: Response):
        self._response = response

    def send(self, url: str, headers: dict) -> Response:
        self.last_url = url
        self.last_headers = {}
        for key, value in headers.items():
            self.last_headers[key] = value
        return self._response


@pytest.fixture
def transport():
    return MockTransport()


@pytest.fixture
def client(transport):
    return VirtualSMSClient(
        api_key="test-api-key",
        base_url="https://api.example.com",
        transport=transport,
    )


class TestGetBalance:
    def test_returns_balance_response(self, client, transport):
        transport.set_response(Response(200, "ACCESS_BALANCE:10.50"))
        result = client.get_balance()
        assert isinstance(result, BalanceResponse)
        assert result.balance == 10.50

    def test_sends_correct_url(self, client, transport):
        transport.set_response(Response(200, "ACCESS_BALANCE:10.50"))
        client.get_balance()
        assert "action=getBalance" in transport.last_url
        assert "api_key=test-api-key" in transport.last_url
        assert "/stubs/handler_api" in transport.last_url

    def test_throws_auth_exception_on_bad_key(self, client, transport):
        transport.set_response(Response(401, "BAD_KEY"))
        with pytest.raises(AuthenticationException):
            client.get_balance()


class TestGetNumber:
    def test_returns_number_response(self, client, transport):
        transport.set_response(Response(200, "ACCESS_NUMBER:123:447777777777"))
        result = client.get_number("wa", 73)
        assert isinstance(result, NumberResponse)
        assert result.activation_id == 123
        assert result.phone_number == "447777777777"

    def test_sends_required_params(self, client, transport):
        transport.set_response(Response(200, "ACCESS_NUMBER:123:447777777777"))
        client.get_number("wa", 73, max_price=2.00)
        assert "action=getNumber" in transport.last_url
        assert "service=wa" in transport.last_url
        assert "country=73" in transport.last_url
        assert "maxPrice=2.0" in transport.last_url or "maxPrice=2" in transport.last_url

    def test_throws_no_balance_exception(self, client, transport):
        transport.set_response(Response(402, "NO_BALANCE"))
        with pytest.raises(InsufficientBalanceException):
            client.get_number("wa", 73)

    def test_throws_no_numbers_exception(self, client, transport):
        transport.set_response(Response(404, "NO_NUMBERS"))
        with pytest.raises(NoNumbersException):
            client.get_number("wa", 73)

    def test_optional_params_not_sent_when_none(self, client, transport):
        transport.set_response(Response(200, "ACCESS_NUMBER:123:447777777777"))
        client.get_number("wa", 73)
        assert "maxPrice" not in transport.last_url
        assert "operator" not in transport.last_url


class TestGetNumberV2:
    def test_returns_dict(self, client, transport):
        transport.set_response(
            Response(200, '{"activationId":123,"phoneNumber":"447777777777","activationCost":1.50}')
        )
        result = client.get_number_v2("wa", 73)
        assert isinstance(result, dict)
        assert result["activationId"] == 123
        assert result["phoneNumber"] == "447777777777"


class TestSetStatus:
    def test_sends_id_and_status(self, client, transport):
        transport.set_response(Response(200, "ACCESS_READY"))
        client.set_status(123, ActivationStatus.READY)
        assert "action=setStatus" in transport.last_url
        assert "id=123" in transport.last_url
        assert "status=1" in transport.last_url

    def test_complete_returns_activation(self, client, transport):
        transport.set_response(Response(200, "ACCESS_ACTIVATION"))
        result = client.set_status(123, ActivationStatus.COMPLETE)
        assert result == "ACCESS_ACTIVATION"


class TestGetStatus:
    def test_returns_status_with_code(self, client, transport):
        transport.set_response(Response(200, "STATUS_OK:123456"))
        result = client.get_status(123)
        assert result.status == "STATUS_OK"
        assert result.code == "123456"

    def test_wait_code(self, client, transport):
        transport.set_response(Response(200, "STATUS_WAIT_CODE"))
        result = client.get_status(123)
        assert result.status == "STATUS_WAIT_CODE"
        assert result.code is None


class TestGetStatusV2:
    def test_returns_dict(self, client, transport):
        transport.set_response(
            Response(200, '{"verificationType":0,"sms":{"code":"123456","text":"Your code"}}')
        )
        result = client.get_status_v2(123)
        assert isinstance(result, dict)
        assert result["verificationType"] == 0
        assert result["sms"]["code"] == "123456"


class TestGetCountries:
    def test_returns_dict(self, client, transport):
        transport.set_response(Response(200, '{"Brazil":{"id":73,"eng":"Brazil","visible":1}}'))
        result = client.get_countries()
        assert isinstance(result, dict)
        assert "Brazil" in result
        assert result["Brazil"]["id"] == 73


class TestGetServicesList:
    def test_sends_country_param(self, client, transport):
        transport.set_response(Response(200, '{"status":"success","services":[]}'))
        client.get_services_list(country=73)
        assert "action=getServicesList" in transport.last_url
        assert "country=73" in transport.last_url


class TestGetOperators:
    def test_returns_country_operators(self, client, transport):
        transport.set_response(
            Response(200, '{"status":"success","countryOperators":["any","claro","vivo"]}')
        )
        result = client.get_operators(73)
        assert "action=getOperators" in transport.last_url
        assert result == ["any", "claro", "vivo"]


class TestGetPrices:
    def test_returns_dict(self, client, transport):
        transport.set_response(Response(200, '{"73":{"wa":{"cost":"1.50","count":"100"}}}'))
        result = client.get_prices("wa", 73)
        assert "action=getPrices" in transport.last_url
        assert result["73"]["wa"]["cost"] == "1.50"


class TestGetPricesExtended:
    def test_sends_correct_action(self, client, transport):
        transport.set_response(Response(200, '{"73":{"wa":{"cnt":100,"cost":1.5}}}'))
        client.get_prices_extended("wa", 73)
        assert "action=getPricesExtended" in transport.last_url


class TestGetPricesVerification:
    def test_sends_correct_action(self, client, transport):
        transport.set_response(Response(200, '{"wa":{"73":{"count":100,"price":"1.50"}}}'))
        client.get_prices_verification("wa")
        assert "action=getPricesVerification" in transport.last_url


class TestGetNumbersStatus:
    def test_returns_dict(self, client, transport):
        transport.set_response(Response(200, '{"tg_73":150,"wa_73":50}'))
        result = client.get_numbers_status(73)
        assert "action=getNumbersStatus" in transport.last_url
        assert result["tg_73"] == 150


class TestGetTopCountriesByService:
    def test_returns_list(self, client, transport):
        transport.set_response(Response(200, '[{"country":"6","share":"29.74","rate":"61.73"}]'))
        result = client.get_top_countries_by_service("wa")
        assert "action=getListOfTopCountriesByService" in transport.last_url
        assert len(result) == 1


class TestGetActiveActivations:
    def test_returns_list(self, client, transport):
        transport.set_response(
            Response(200, '{"status":"success","activeActivations":[{"activationId":123}]}')
        )
        result = client.get_active_activations()
        assert "action=getActiveActivations" in transport.last_url
        assert len(result) == 1


class TestCheckExtraActivation:
    def test_returns_dict(self, client, transport):
        transport.set_response(
            Response(200, '{"status":"success","cost":200,"service":"tw","phone":777777777}')
        )
        result = client.check_extra_activation(123)
        assert "action=checkExtraActivation" in transport.last_url
        assert result["cost"] == 200


class TestGetExtraActivation:
    def test_returns_number_response(self, client, transport):
        transport.set_response(Response(200, "ACCESS_NUMBER:456:447777777777"))
        result = client.get_extra_activation(123)
        assert isinstance(result, NumberResponse)
        assert result.activation_id == 456


class TestGetNotifications:
    def test_returns_dict(self, client, transport):
        transport.set_response(Response(200, '{"status":"success","notifications":[],"unreadCount":0}'))
        result = client.get_notifications()
        assert "action=getNotifications" in transport.last_url
        assert result["unreadCount"] == 0


class TestTrackingHeaders:
    def test_headers_are_sent(self, client, transport):
        transport.set_response(Response(200, "ACCESS_BALANCE:10.50"))
        client.get_balance()
        assert transport.last_headers.get("X-SDK-Version") is not None
        assert transport.last_headers.get("X-SDK-Language") == "python"
        assert transport.last_headers.get("X-SDK-Machine-Id") is not None
        assert transport.last_headers.get("X-SDK-Timestamp") is not None

    def test_machine_id_is_stable(self, client, transport):
        transport.set_response(Response(200, "ACCESS_BALANCE:10.50"))
        client.get_balance()
        first_id = transport.last_headers["X-SDK-Machine-Id"]
        client.get_balance()
        second_id = transport.last_headers["X-SDK-Machine-Id"]
        assert first_id == second_id
        assert len(first_id) == 32

    def test_version_is_set(self, client, transport):
        transport.set_response(Response(200, "ACCESS_BALANCE:10.50"))
        client.get_balance()
        assert transport.last_headers["X-SDK-Version"] == "1.0.0"
