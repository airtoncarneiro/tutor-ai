"""Optional capability check for the official Gemini SDK.

The compatibility client remains the V1 default. This module deliberately does
not make a network call or require an additional dependency.
"""


def native_sdk_available() -> bool:
    try:
        import google.genai  # type: ignore[import-not-found]
    except ImportError:
        return False
    return True

