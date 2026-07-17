import hashlib
import hmac
import json


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_event(payload: bytes) -> dict:
    event = json.loads(payload)
    if "type" not in event or "data" not in event:
        raise ValueError("malformed webhook event")
    return event


def route_event(event: dict, handlers: dict) -> bool:
    handler = handlers.get(event["type"])
    if handler is None:
        return False
    handler(event["data"])
    return True
