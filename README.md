# VirtualSMS Python SDK

Python SDK for the VirtualSMS Consumer API — SMS verification, phone number rental, and activation management.

[![PyPI](https://img.shields.io/pypi/v/virtualsmslabs-python-sdk)](https://pypi.org/project/virtualsmslabs-python-sdk/)
[![License](https://img.shields.io/github/license/VirtualSMSLabs/python-sdk)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/virtualsms)](https://www.python.org/)

## Requirements

- Python 3.9 or higher
- No external dependencies (uses standard library only)

## Installation

```bash
pip install virtualsmslabs-python-sdk
```

## Quick Start

```python
from virtualsms import VirtualSMSClient, ActivationStatus

client = VirtualSMSClient("YOUR_API_KEY", "https://api.virtualsms.de")

# Check balance
balance = client.get_balance()
print(f"Balance: ${balance.balance:.2f}")

# Order a WhatsApp number in Brazil
number = client.get_number("wa", 73, max_price=2.00)
print(f"Number: {number.phone_number} (ID: {number.activation_id})")

# Set status to ready (SMS sent)
client.set_status(number.activation_id, ActivationStatus.READY)

# Poll for SMS code
status = client.get_status(number.activation_id)
if status.code is not None:
    print(f"SMS code: {status.code}")
    # Complete the activation
    client.set_status(number.activation_id, ActivationStatus.COMPLETE)
```

## API Reference

### Client Constructor

```python
client = VirtualSMSClient(
    api_key="YOUR_API_KEY",           # Your API key (required)
    base_url="https://api.virtualsms.de",  # API base URL (optional)
    transport=None,                    # Optional custom transport
)
```

### Methods

#### Account

##### `get_balance() -> BalanceResponse`

Returns the current account balance.

```python
balance = client.get_balance()
print(balance.balance)  # 10.50
```

#### Information & Pricing

##### `get_countries(pool_provider=None) -> dict`

Returns all available countries.

##### `get_services_list(country=None, lang=None) -> dict`

Returns available services for a country.

##### `get_operators(country, pool_provider=None) -> list`

Returns available mobile operators for a country.

##### `get_prices(service=None, country=None, pool_provider=None) -> dict`

Returns pricing data organized by country and service.

##### `get_prices_extended(service=None, country=None, free_price=None, pool_provider=None) -> dict`

Returns extended pricing with price tiers.

##### `get_prices_verification(service=None, pool_provider=None) -> dict`

Returns pricing in inverted format (service → country).

##### `get_numbers_status(country, operator=None, pool_provider=None) -> dict`

Returns available phone quantity per service.

##### `get_top_countries_by_service(service) -> list`

Returns top 10 countries for a service, ranked by purchase share and success rate.

#### Ordering Numbers

##### `get_number(service, country, **options) -> NumberResponse`

Orders a phone number. Returns text format response.

```python
number = client.get_number(
    service="wa",
    country=73,
    max_price=2.00,
    operator="claro",
    forward=True,
)
print(number.activation_id)   # 123
print(number.phone_number)    # 447777777777
```

**Options:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `max_price` | `float` | Maximum price willing to pay |
| `operator` | `str` | Mobile operator filter |
| `phone_exception` | `str` | Phone prefixes to exclude (comma-separated) |
| `forward` | `bool` | Enable call forwarding |
| `activation_type` | `int` | Activation type: 0=SMS, 1=number, 2=voice |
| `language` | `str` | Language for voice activation |
| `use_cashback` | `bool` | Use cashback balance first |
| `user_id` | `str` | End-user ID for tracking |
| `ref` | `str` | Referral ID |
| `pool_provider` | `str` | Pool provider: alpha, prime, gamma, zeta |

##### `get_number_v2(service, country, **options) -> dict`

Same as `get_number` but returns JSON with additional fields. Supports `order_id` for idempotency.

#### Activation Management

##### `set_status(id, status) -> str`

Changes activation status.

```python
from virtualsms import ActivationStatus

client.set_status(activation_id, ActivationStatus.READY)     # 1 - SMS sent
client.set_status(activation_id, ActivationStatus.RETRY)     # 3 - Request another SMS
client.set_status(activation_id, ActivationStatus.COMPLETE)  # 6 - Finish
client.set_status(activation_id, ActivationStatus.CANCEL)    # 8 - Cancel
```

##### `get_status(id) -> StatusResponse`

Returns activation status in text format.

```python
status = client.get_status(activation_id)
print(status.status)   # STATUS_OK, STATUS_WAIT_CODE, STATUS_CANCEL
print(status.code)     # 123456 (None if not yet received)
```

##### `get_status_v2(id) -> dict`

Returns activation status in JSON format with SMS/call details.

##### `get_active_activations() -> list`

Returns all currently active activations.

##### `check_extra_activation(id) -> dict`

Checks if a number is available for reactivation.

##### `get_extra_activation(id) -> NumberResponse`

Creates an extra activation on a previously used number.

#### Notifications

##### `get_notifications() -> dict`

Returns user notifications including penalties, low balance alerts, and admin messages.

### Constants

#### ActivationStatus

```python
ActivationStatus.READY     # 1 - SMS has been sent to the number
ActivationStatus.RETRY     # 3 - Request another SMS code
ActivationStatus.COMPLETE  # 6 - Finish activation
ActivationStatus.CANCEL    # 8 - Cancel activation
```

#### PoolProvider

```python
PoolProvider.ALPHA  # 'alpha'
PoolProvider.PRIME  # 'prime'
PoolProvider.GAMMA  # 'gamma'
PoolProvider.ZETA   # 'zeta'
```

## Error Handling

The SDK raises typed exceptions for all API errors. Each error code maps to a specific exception class:

```python
from virtualsms import (
    VirtualSMSClient,
    VirtualSMSException,
    AuthenticationException,
    InsufficientBalanceException,
    NoNumbersException,
    ValidationException,
    ActivationException,
    RateLimitException,
    ServerException,
)

try:
    number = client.get_number("wa", 73)
except AuthenticationException:
    # BAD_KEY, BANNED, PURCHASE_RESTRICTED, SERVICE_RESTRICTED
    pass
except InsufficientBalanceException:
    # NO_BALANCE
    pass
except NoNumbersException:
    # NO_NUMBERS
    pass
except ValidationException:
    # WRONG_SERVICE, WRONG_COUNTRY, BAD_ACTION, BAD_STATUS, NO_PRICES, INVALID_PROVIDER
    pass
except ActivationException:
    # NO_ACTIVATION, WRONG_ACTIVATION_ID, EARLY_CANCEL_DENIED, RENEW_ACTIVATION_NOT_AVAILABLE
    pass
except RateLimitException as e:
    # CONCURRENT_LIMIT — check e.retry_after
    pass
except ServerException:
    # ERROR_SQL, unknown errors
    pass
```

### Error Code Reference

| Error Code | Exception | Description |
|-----------|-----------|-------------|
| `BAD_KEY` | `AuthenticationException` | Invalid API key |
| `BANNED` | `AuthenticationException` | Account banned or IP blocked |
| `PURCHASE_RESTRICTED` | `AuthenticationException` | User restricted from purchasing |
| `SERVICE_RESTRICTED` | `AuthenticationException` | Service restricted for account |
| `NO_BALANCE` | `InsufficientBalanceException` | Insufficient balance |
| `NO_NUMBERS` | `NoNumbersException` | No numbers available |
| `WRONG_SERVICE` | `ValidationException` | Invalid service code |
| `WRONG_COUNTRY` | `ValidationException` | Invalid country ID |
| `BAD_ACTION` | `ValidationException` | Invalid action |
| `BAD_STATUS` | `ValidationException` | Invalid status code |
| `NO_PRICES` | `ValidationException` | No pricing data available |
| `INVALID_PROVIDER` | `ValidationException` | Invalid pool provider |
| `NO_ACTIVATION` | `ActivationException` | Activation not found |
| `WRONG_ACTIVATION_ID` | `ActivationException` | Invalid activation ID |
| `EARLY_CANCEL_DENIED` | `ActivationException` | Cannot cancel within 5 minutes |
| `RENEW_ACTIVATION_NOT_AVAILABLE` | `ActivationException` | Number not available for reactivation |
| `CONCURRENT_LIMIT` | `RateLimitException` | Too many concurrent activations |
| `ERROR_SQL` | `ServerException` | Internal server error |

## Tracking Headers

The SDK sends anonymous tracking headers with every request for analytics and debugging:

| Header | Value | Privacy |
|--------|-------|---------|
| `X-SDK-Version` | `1.0.0` | SDK version string |
| `X-SDK-Language` | `python` | SDK language |
| `X-SDK-Machine-Id` | SHA-256 hash of `platform.platform()` + `sys.implementation.name` (truncated to 32 chars) | Irreversible hash — no hostname or IP exposed |
| `X-SDK-Timestamp` | ISO 8601 UTC timestamp | Request time |

No personally identifiable information is transmitted. The machine ID is a one-way hash and cannot be reversed to identify the source machine.

## Custom Transport

By default, the SDK uses `urllib.request` for HTTP requests. You can provide your own transport implementation:

```python
from virtualsms import VirtualSMSClient, Transport, Response

class MyTransport(Transport):
    def send(self, url: str, headers: dict) -> Response:
        # Your HTTP implementation
        return Response(status_code=200, body="ACCESS_BALANCE:10.50")

client = VirtualSMSClient("API_KEY", "https://api.example.com", transport=MyTransport())
```

## Examples

See the `examples/` directory:

- [`balance.py`](examples/balance.py) — Check account balance
- [`order_number.py`](examples/order_number.py) — Order a phone number
- [`full_workflow.py`](examples/full_workflow.py) — Complete SMS verification workflow

## Testing

```bash
pip install pytest
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Links

- [PyPI](https://pypi.org/project/virtualsmslabs-python-sdk/)
- [GitHub](https://github.com/VirtualSMSLabs/python-sdk)
- [API Documentation](https://virtualsms.de/docs)
- [MCP Integration](https://virtualsms.de/docs/mcp)
