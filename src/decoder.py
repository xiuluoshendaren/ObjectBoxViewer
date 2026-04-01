"""Data decoder for ObjectBox values."""

from __future__ import annotations

import base64
import gzip
import json
import re
from typing import Any


# Pattern to detect gzip+base64 encoded data (common in Reqable captures)
_GZIP_B64_PATTERN = re.compile(r'H4sI[A-Za-z0-9+/=]{20,}')


def decode_value(raw: bytes) -> dict[str, Any] | None:
    """
    Decode an ObjectBox value using multiple strategies.

    Strategies (in order of priority):
    1. Try gzip + base64 decode (common in Reqable data)
    2. Extract embedded JSON objects
    3. Return None (indicates FlatBuffers data that needs schema)

    Args:
        raw: Raw bytes from the database

    Returns:
        Decoded dictionary, or None if decoding failed
    """
    # Strategy 1: Try gzip + base64
    result = try_gzip_b64_decode(raw)
    if result is not None:
        return result

    # Strategy 2: Extract embedded JSON
    json_objects = extract_embedded_json(raw)
    if json_objects:
        # Return the first JSON object found
        return json_objects[0]

    # Strategy 3: Return None (FlatBuffers data)
    return None


def try_gzip_b64_decode(raw: bytes) -> dict[str, Any] | None:
    """
    Try to decode gzip + base64 encoded JSON embedded in the data.

    Args:
        raw: Raw bytes potentially containing gzip+base64 data

    Returns:
        Decoded dictionary, or None if not found/failed
    """
    try:
        text = raw.decode('utf-8', errors='replace')

        for match in _GZIP_B64_PATTERN.finditer(text):
            try:
                # Decode base64
                decoded = base64.b64decode(match.group())

                # Decompress gzip
                decompressed = gzip.decompress(decoded)

                # Parse JSON
                return json.loads(decompressed)
            except Exception:
                continue
    except Exception:
        pass

    return None


def extract_embedded_json(raw: bytes) -> list[dict[str, Any]]:
    """
    Extract top-level JSON objects embedded in binary data.

    This scans through the bytes looking for complete JSON objects
    (starting with '{' and ending with '}').

    Args:
        raw: Raw bytes potentially containing JSON

    Returns:
        List of decoded JSON objects
    """
    results: list[dict[str, Any]] = []

    i = 0
    length = len(raw)

    while i < length:
        # Look for opening brace
        if raw[i:i+1] != b'{':
            i += 1
            continue

        # Found opening brace, try to find matching closing brace
        depth = 0
        start = i

        for j in range(i, length):
            if raw[j:j+1] == b'{':
                depth += 1
            elif raw[j:j+1] == b'}':
                depth -= 1

                if depth == 0:
                    # Found complete JSON object
                    try:
                        obj = json.loads(raw[start:j+1])
                        results.append(obj)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass

                    i = j + 1
                    break
        else:
            # No matching closing brace found
            break

    return results


def format_bytes_for_display(raw: bytes, max_length: int = 200) -> str:
    """
    Format raw bytes for display when JSON decoding fails.

    Args:
        raw: Raw bytes
        max_length: Maximum length before truncation

    Returns:
        Formatted string representation
    """
    if len(raw) <= max_length:
        # Try to decode as UTF-8
        try:
            text = raw.decode('utf-8')
            # Check if it's mostly printable
            if all(c.isprintable() or c.isspace() for c in text):
                return text
        except UnicodeDecodeError:
            pass

        # Fall back to hex representation
        return raw.hex()

    # Truncate long data
    truncated = raw[:max_length]
    try:
        text = truncated.decode('utf-8', errors='replace')
        if all(c.isprintable() or c.isspace() for c in text):
            return f"{text}... ({len(raw)} bytes total)"
    except UnicodeDecodeError:
        pass

    return f"{truncated.hex()}... ({len(raw)} bytes total)"
