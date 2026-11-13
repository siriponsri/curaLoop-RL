"""Decode the upstream (success, log_info) interface without changing its rule."""


def decode_native_result(value):
    if not isinstance(value, tuple) or len(value) != 2:
        raise ValueError("Native eval() must return (success, log_info)")
    success, detail = value
    if type(success).__module__.startswith("numpy") and getattr(success, "ndim", None) == 0:
        success = success.item()
    if not isinstance(success, (bool, int, float)) or success not in (0, 1):
        raise ValueError("Native success flag must be zero or one")
    return {"success": bool(success == 1), "native_log_info": str(detail)}
