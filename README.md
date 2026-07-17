# PayFlow Demo

A minimal Python payments library used as a testbed for CodePilot.

## Modules

### `app.models`

Defines the core data models used throughout the library.

| Class | Description |
|-------|-------------|
| `Customer` | Represents a customer with a stored payment card. |
| `Card` | Represents a payment card (number, expiry, CVC). |

### `app.payments`

Handles charge processing against the payment gateway.

| Symbol | Description |
|--------|-------------|
| `charge_customer(customer, amount)` | Charge a customer's stored card. Returns a result dict on success. |
| `ChargeError` | Raised when a charge cannot be completed. |

**Example**

```python
from app.models import Card, Customer
from app.payments import charge_customer

card = Card("4242424242424242", 12, 2025, "123")
customer = Customer("cus_1", "alice@example.com", card)
result = charge_customer(customer, 1000)
print(result)  # {"status": "success", "charge_id": "ch_test_001"}
```

### `app.webhooks`

Provides utilities to securely receive and dispatch webhook payloads sent
by the payment gateway.

| Symbol | Description |
|--------|-------------|
| `verify_signature(payload, signature, secret)` | Verify the HMAC-SHA256 signature of an incoming webhook payload. |
| `parse_event(payload)` | Deserialise a raw JSON payload into a Python dict. |
| `route_event(event)` | Dispatch a parsed event to the appropriate internal handler. |

**Example**

```python
from app.webhooks import verify_signature, parse_event, route_event

raw_body = b'{"type": "charge.succeeded", "id": "evt_1", "data": {}}'
secret = "whsec_test"

import hmac, hashlib
sig = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

if verify_signature(raw_body, sig, secret=secret):
    event = parse_event(raw_body)
    route_event(event)
```
