import pytest

from virtualsms.exceptions import (
    ActivationException,
    AuthenticationException,
    InsufficientBalanceException,
    NoNumbersException,
    RateLimitException,
    ServerException,
    ValidationException,
    VirtualSMSException,
)


class TestExceptionMapping:
    def test_bad_key_throws_authentication_exception(self):
        exc = VirtualSMSException.from_error_code("BAD_KEY", 401)
        assert isinstance(exc, AuthenticationException)
        assert exc.error_code == "BAD_KEY"
        assert exc.http_status == 401

    def test_banned_throws_authentication_exception(self):
        exc = VirtualSMSException.from_error_code("BANNED", 403)
        assert isinstance(exc, AuthenticationException)

    def test_banned_on_429_throws_rate_limit_exception(self):
        exc = VirtualSMSException.from_error_code("BANNED", 429)
        assert isinstance(exc, RateLimitException)

    def test_banned_on_429_has_rate_limit_fields(self):
        exc = VirtualSMSException.from_error_code(
            "BANNED", 429, retry_after=60,
            rate_limit_limit=100, rate_limit_remaining=0,
        )
        assert isinstance(exc, RateLimitException)
        assert exc.rate_limit_limit == 100
        assert exc.rate_limit_remaining == 0
        assert exc.retry_after == 60

    def test_no_balance_throws_insufficient_balance_exception(self):
        exc = VirtualSMSException.from_error_code("NO_BALANCE", 402)
        assert isinstance(exc, InsufficientBalanceException)
        assert exc.error_code == "NO_BALANCE"

    def test_no_numbers_throws_no_numbers_exception(self):
        exc = VirtualSMSException.from_error_code("NO_NUMBERS", 404)
        assert isinstance(exc, NoNumbersException)

    def test_wrong_service_throws_validation_exception(self):
        exc = VirtualSMSException.from_error_code("WRONG_SERVICE", 400)
        assert isinstance(exc, ValidationException)

    def test_wrong_country_throws_validation_exception(self):
        exc = VirtualSMSException.from_error_code("WRONG_COUNTRY", 400)
        assert isinstance(exc, ValidationException)

    def test_bad_action_throws_validation_exception(self):
        exc = VirtualSMSException.from_error_code("BAD_ACTION", 400)
        assert isinstance(exc, ValidationException)

    def test_bad_status_throws_validation_exception(self):
        exc = VirtualSMSException.from_error_code("BAD_STATUS", 400)
        assert isinstance(exc, ValidationException)

    def test_no_activation_throws_activation_exception(self):
        exc = VirtualSMSException.from_error_code("NO_ACTIVATION", 404)
        assert isinstance(exc, ActivationException)

    def test_wrong_activation_id_throws_activation_exception(self):
        exc = VirtualSMSException.from_error_code("WRONG_ACTIVATION_ID", 404)
        assert isinstance(exc, ActivationException)

    def test_early_cancel_denied_throws_activation_exception(self):
        exc = VirtualSMSException.from_error_code("EARLY_CANCEL_DENIED", 400)
        assert isinstance(exc, ActivationException)

    def test_renew_activation_not_available_throws_activation_exception(self):
        exc = VirtualSMSException.from_error_code("RENEW_ACTIVATION_NOT_AVAILABLE", 400)
        assert isinstance(exc, ActivationException)

    def test_concurrent_limit_throws_rate_limit_exception(self):
        exc = VirtualSMSException.from_error_code("CONCURRENT_LIMIT", 429)
        assert isinstance(exc, RateLimitException)

    def test_purchase_restricted_throws_authentication_exception(self):
        exc = VirtualSMSException.from_error_code("PURCHASE_RESTRICTED", 403)
        assert isinstance(exc, AuthenticationException)

    def test_service_restricted_throws_authentication_exception(self):
        exc = VirtualSMSException.from_error_code("SERVICE_RESTRICTED", 403)
        assert isinstance(exc, AuthenticationException)

    def test_error_sql_throws_server_exception(self):
        exc = VirtualSMSException.from_error_code("ERROR_SQL", 500)
        assert isinstance(exc, ServerException)

    def test_no_prices_throws_validation_exception(self):
        exc = VirtualSMSException.from_error_code("NO_PRICES", 400)
        assert isinstance(exc, ValidationException)

    def test_invalid_provider_throws_validation_exception(self):
        exc = VirtualSMSException.from_error_code("INVALID_PROVIDER", 400)
        assert isinstance(exc, ValidationException)

    def test_unknown_error_throws_server_exception(self):
        exc = VirtualSMSException.from_error_code("SOME_UNKNOWN_CODE", 500)
        assert isinstance(exc, ServerException)
        assert exc.error_code == "SOME_UNKNOWN_CODE"

    def test_concurrent_limit_exception_stores_retry_after(self):
        exc = VirtualSMSException.from_error_code("CONCURRENT_LIMIT", 429, retry_after=30)
        assert isinstance(exc, RateLimitException)
        assert exc.retry_after == 30

    def test_all_exceptions_extend_base(self):
        exceptions = [
            AuthenticationException("test", "TEST", 400),
            InsufficientBalanceException("test", "TEST", 400),
            NoNumbersException("test", "TEST", 400),
            ValidationException("test", "TEST", 400),
            ActivationException("test", "TEST", 400),
            RateLimitException("test", "TEST", 400),
            ServerException("test", "TEST", 400),
        ]
        for exc in exceptions:
            assert isinstance(exc, VirtualSMSException)
