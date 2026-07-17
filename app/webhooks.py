"""Webhook processing for incoming payment gateway events.

This module provides utilities to securely receive and dispatch webhook
payloads sent by the payment gateway.  It covers three concerns:

1. **Signature verification** — ensuring the payload was sent by the gateway.
2. **Event parsing** — deserialising the raw payload into a structured dict.
3. **Event routing** — dispatching parsed events to the appropriate handler.

Typical usage::

    from app.webhooks import verify_signature, parse_event, route_event

    raw_body = request.get_data()
    sig_header = request.headers.get("X-Signature")

    if not verify_signature(raw_body, sig_header, secret="whsec_..."):
        abort(400)

    event = parse_event(raw_body)
    route_event(event)
"""

import hashlib
import hmac
import json


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify that a webhook payload was signed by the payment gateway.

    The gateway signs each payload with HMAC-SHA256 using the webhook
    secret configured in your dashboard.  This function computes the
    expected signature and compares it to the one supplied in the
    ``X-Signature`` header using a timing-safe comparison.

    Args:
        payload: The raw request body as bytes.
        signature: The hex-encoded HMAC-SHA256 digest from the
            ``X-Signature`` header.
        secret: Your webhook signing secret (e.g. ``"whsec_..."``).

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.

    Example::

        raw_body = b'{"type": "charge.succeeded", "id": "evt_1"}'
        sig = hmac.new(b"mysecret", raw_body, hashlib.sha256).hexdigest()

        assert verify_signature(raw_body, sig, secret="mysecret") is True
        assert verify_signature(raw_body, "badsig", secret="mysecret") is False
    """
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_event(payload: bytes) -> dict:
    """Deserialise a raw webhook payload into a Python dict.

    The gateway sends JSON-encoded payloads.  This function decodes the
    bytes and returns a dictionary that callers can inspect to determine
    the event type and associated data.

    Args:
        payload: The raw request body as bytes (UTF-8 encoded JSON).

    Returns:
        A dict representing the event.  At minimum the dict contains a
        ``"type"`` key (e.g. ``"charge.succeeded"``) and an ``"id"`` key.

    Raises:
        ValueError: If *payload* is not valid JSON.

    Example::

        raw = b'{"type": "charge.succeeded", "id": "evt_1", "data": {}}'
        event = parse_event(raw)
        print(event["type"])  # "charge.succeeded"
    """
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid webhook payload: {exc}") from exc


def route_event(event: dict) -> None:
    """Dispatch a parsed webhook event to the appropriate handler.

    Reads ``event["type"]`` and calls the matching internal handler.
    Unknown event types are silently ignored so that new gateway events
    do not break existing deployments.

    Supported event types:

    +---------------------------+----------------------------------+
    | Event type                | Action                           |
    +===========================+==================================+
    | ``charge.succeeded``      | Logs the successful charge.      |
    +---------------------------+----------------------------------+
    | ``charge.failed``         | Logs the failed charge.          |
    +---------------------------+----------------------------------+

    Args:
        event: A parsed event dict as returned by :func:`parse_event`.

    Returns:
        ``None``

    Example::

        event = {"type": "charge.succeeded", "id": "evt_1", "data": {}}
        route_event(event)  # logs: "Charge succeeded: evt_1"
    """
    handlers = {
        "charge.succeeded": _handle_charge_succeeded,
        "charge.failed": _handle_charge_failed,
    }
    handler = handlers.get(event.get("type"))
    if handler:
        handler(event)


def _handle_charge_succeeded(event: dict) -> None:
    """Handle a successful charge event."""
    print(f"Charge succeeded: {event.get('id')}")


def _handle_charge_failed(event: dict) -> None:
    """Handle a failed charge event."""
    print(f"Charge failed: {event.get('id')}")
