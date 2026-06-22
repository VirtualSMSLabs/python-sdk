import json

import pytest

from virtualsms.parser import TextResponseParser, ParsedResponse


@pytest.fixture
def parser():
    return TextResponseParser()


class TestParseAccessBalance:
    def test_parses_access_balance_response(self, parser):
        result = parser.parse("ACCESS_BALANCE:10.50")
        assert result.is_success is True
        assert result.type == "balance"
        assert result.data["balance"] == 10.50

    def test_parses_access_balance_with_zero(self, parser):
        result = parser.parse("ACCESS_BALANCE:0.00")
        assert result.is_success is True
        assert result.type == "balance"
        assert result.data["balance"] == 0.00

    def test_parses_access_balance_large_number(self, parser):
        result = parser.parse("ACCESS_BALANCE:9999.99")
        assert result.is_success is True
        assert result.data["balance"] == 9999.99


class TestParseAccessNumber:
    def test_parses_access_number_response(self, parser):
        result = parser.parse("ACCESS_NUMBER:123:447777777777")
        assert result.is_success is True
        assert result.type == "number"
        assert result.data["activation_id"] == 123
        assert result.data["phone_number"] == "447777777777"

    def test_parses_access_number_with_large_id(self, parser):
        result = parser.parse("ACCESS_NUMBER:999999:5551234")
        assert result.is_success is True
        assert result.data["activation_id"] == 999999
        assert result.data["phone_number"] == "5551234"


class TestParseStatus:
    def test_parses_status_wait_code(self, parser):
        result = parser.parse("STATUS_WAIT_CODE")
        assert result.is_success is True
        assert result.type == "status"
        assert result.data["status"] == "STATUS_WAIT_CODE"
        assert result.data["code"] is None

    def test_parses_status_wait_retry(self, parser):
        result = parser.parse("STATUS_WAIT_RETRY")
        assert result.is_success is True
        assert result.type == "status"
        assert result.data["status"] == "STATUS_WAIT_RETRY"

    def test_parses_status_ok_with_code(self, parser):
        result = parser.parse("STATUS_OK:123456")
        assert result.is_success is True
        assert result.type == "status"
        assert result.data["status"] == "STATUS_OK"
        assert result.data["code"] == "123456"

    def test_parses_status_ok_without_code(self, parser):
        result = parser.parse("STATUS_OK")
        assert result.is_success is True
        assert result.type == "status"
        assert result.data["status"] == "STATUS_OK"
        assert result.data["code"] is None

    def test_parses_status_cancel(self, parser):
        result = parser.parse("STATUS_CANCEL")
        assert result.is_success is True
        assert result.type == "status"
        assert result.data["status"] == "STATUS_CANCEL"


class TestParseFullSms:
    def test_parses_full_sms_response(self, parser):
        result = parser.parse("FULL_SMS:Your verification code is 123456")
        assert result.is_success is True
        assert result.type == "status"
        assert result.data["status"] == "FULL_SMS"
        assert result.data["sms_text"] == "Your verification code is 123456"

    def test_parses_full_sms_empty_text(self, parser):
        result = parser.parse("FULL_SMS:")
        assert result.is_success is True
        assert result.data["status"] == "FULL_SMS"
        assert result.data["sms_text"] == ""


class TestParseSetStatus:
    def test_parses_access_ready(self, parser):
        result = parser.parse("ACCESS_READY")
        assert result.is_success is True
        assert result.type == "set_status"
        assert result.data["status"] == "ACCESS_READY"

    def test_parses_access_retry_get(self, parser):
        result = parser.parse("ACCESS_RETRY_GET")
        assert result.is_success is True
        assert result.type == "set_status"
        assert result.data["status"] == "ACCESS_RETRY_GET"

    def test_parses_access_activation(self, parser):
        result = parser.parse("ACCESS_ACTIVATION")
        assert result.is_success is True
        assert result.type == "set_status"
        assert result.data["status"] == "ACCESS_ACTIVATION"

    def test_parses_access_cancel(self, parser):
        result = parser.parse("ACCESS_CANCEL")
        assert result.is_success is True
        assert result.type == "set_status"
        assert result.data["status"] == "ACCESS_CANCEL"


class TestParseErrorCodes:
    def test_detects_error_bad_key(self, parser):
        result = parser.parse("BAD_KEY")
        assert result.is_success is False
        assert result.error_code == "BAD_KEY"

    def test_detects_error_banned(self, parser):
        result = parser.parse("BANNED")
        assert result.is_success is False
        assert result.error_code == "BANNED"

    def test_detects_error_no_balance(self, parser):
        result = parser.parse("NO_BALANCE")
        assert result.is_success is False
        assert result.error_code == "NO_BALANCE"

    def test_detects_error_no_numbers(self, parser):
        result = parser.parse("NO_NUMBERS")
        assert result.is_success is False
        assert result.error_code == "NO_NUMBERS"

    def test_detects_error_wrong_service(self, parser):
        result = parser.parse("WRONG_SERVICE")
        assert result.is_success is False
        assert result.error_code == "WRONG_SERVICE"

    def test_detects_error_wrong_country(self, parser):
        result = parser.parse("WRONG_COUNTRY")
        assert result.is_success is False
        assert result.error_code == "WRONG_COUNTRY"

    def test_detects_error_no_activation(self, parser):
        result = parser.parse("NO_ACTIVATION")
        assert result.is_success is False
        assert result.error_code == "NO_ACTIVATION"

    def test_detects_error_bad_action(self, parser):
        result = parser.parse("BAD_ACTION")
        assert result.is_success is False
        assert result.error_code == "BAD_ACTION"

    def test_detects_error_bad_status(self, parser):
        result = parser.parse("BAD_STATUS")
        assert result.is_success is False
        assert result.error_code == "BAD_STATUS"

    def test_detects_error_early_cancel_denied(self, parser):
        result = parser.parse("EARLY_CANCEL_DENIED")
        assert result.is_success is False
        assert result.error_code == "EARLY_CANCEL_DENIED"

    def test_detects_error_wrong_activation_id(self, parser):
        result = parser.parse("WRONG_ACTIVATION_ID")
        assert result.is_success is False
        assert result.error_code == "WRONG_ACTIVATION_ID"

    def test_detects_error_renew_activation_not_available(self, parser):
        result = parser.parse("RENEW_ACTIVATION_NOT_AVAILABLE")
        assert result.is_success is False
        assert result.error_code == "RENEW_ACTIVATION_NOT_AVAILABLE"

    def test_detects_error_purchase_restricted(self, parser):
        result = parser.parse("PURCHASE_RESTRICTED")
        assert result.is_success is False
        assert result.error_code == "PURCHASE_RESTRICTED"

    def test_detects_error_concurrent_limit(self, parser):
        result = parser.parse("CONCURRENT_LIMIT")
        assert result.is_success is False
        assert result.error_code == "CONCURRENT_LIMIT"

    def test_detects_error_no_prices(self, parser):
        result = parser.parse("NO_PRICES")
        assert result.is_success is False
        assert result.error_code == "NO_PRICES"

    def test_detects_error_invalid_provider(self, parser):
        result = parser.parse("INVALID_PROVIDER")
        assert result.is_success is False
        assert result.error_code == "INVALID_PROVIDER"

    def test_detects_error_sql(self, parser):
        result = parser.parse("ERROR_SQL")
        assert result.is_success is False
        assert result.error_code == "ERROR_SQL"

    def test_detects_unknown_error_as_unknown(self, parser):
        result = parser.parse("SOME_UNKNOWN_ERROR")
        assert result.is_success is False
        assert result.error_code == "UNKNOWN"


class TestParseJson:
    def test_detects_json_response(self, parser):
        body = '{"status":"success","services":[]}'
        result = parser.parse(body)
        assert result.is_success is True
        assert result.type == "json"
        assert result.data["raw"] == body
        assert result.data["decoded"] == {"status": "success", "services": []}

    def test_detects_json_error_response(self, parser):
        body = '{"status":"error","error":"Something failed"}'
        result = parser.parse(body)
        assert result.is_success is False
        assert result.error_code == "UNKNOWN"
        assert result.error_message == "Something failed"

    def test_detects_json_error_with_error_code(self, parser):
        body = '{"status":"error","errorCode":"NO_NUMBERS","error":"No numbers"}'
        result = parser.parse(body)
        assert result.is_success is False
        assert result.error_code == "NO_NUMBERS"
        assert result.error_message == "No numbers"

    def test_detects_json_array(self, parser):
        body = '[{"country":"6","share":"29.74"}]'
        result = parser.parse(body)
        assert result.is_success is True
        assert result.type == "json"
        assert isinstance(result.data["decoded"], list)


class TestParseEdgeCases:
    def test_empty_body_returns_unknown_error(self, parser):
        result = parser.parse("")
        assert result.is_success is False
        assert result.error_code == "UNKNOWN"

    def test_whitespace_only_body_returns_unknown_error(self, parser):
        result = parser.parse("   ")
        assert result.is_success is False
        assert result.error_code == "UNKNOWN"
