"""LMDB read layer for Reqable's ObjectBox database."""

from __future__ import annotations

import base64
import gzip
import json
import os
import re
import struct
from typing import Any, Generator

import lmdb

from .schema import discover_entities, get_entity_count, EntityInfo
from .decoder import decode_value, format_bytes_for_display

# ObjectBox key prefixes (first 4 bytes of 8-byte keys)
PREFIX_CAPTURE = b"\x18\x00\x00\x2c"   # Proxy capture records
PREFIX_API_TEST = b"\x18\x00\x00\x3c"  # API test records
PREFIX_COOKIE = b"\x18\x00\x00\x40"    # Cookie storage
PREFIX_API_COLLECTION = b"\x18\x00\x00\x7c"  # API collection

_GZIP_B64_RE = re.compile(r"H4sI[A-Za-z0-9+/=]{20,}")


def _default_db_path() -> str:
    # Windows: %APPDATA%\Reqable\box
    # macOS: ~/Library/Application Support/Reqable/box
    appdata = os.environ.get("APPDATA")
    if appdata:
        # Windows
        return os.path.join(appdata, "Reqable", "box")
    else:
        # macOS/Linux
        home = os.path.expanduser("~")
        # '/Users/xiuluo/Library/Application Support/com.reqable.macosx/box'
        return os.path.join(home, "Library", "Application Support", "com.reqable.macosx", "box")


def _default_capture_dir() -> str:
    # Windows: %APPDATA%\Reqable\capture
    # macOS: ~/Library/Application Support/Reqable/capture
    appdata = os.environ.get("APPDATA")
    if appdata:
        # Windows
        return os.path.join(appdata, "Reqable", "capture")
    else:
        # macOS/Linux
        home = os.path.expanduser("~")
        return os.path.join(home, "Library", "Application Support", "Reqable", "capture")


class ReqableDB:
    """Read-only accessor for Reqable's ObjectBox LMDB database."""

    def __init__(
        self,
        db_path: str | None = None,
        capture_dir: str | None = None,
        readonly: bool = True,
    ) -> None:
        # Handle .mdb file paths - LMDB expects directory path
        if db_path and db_path.endswith('.mdb'):
            db_path = os.path.dirname(db_path)

        self.db_path = db_path or _default_db_path()
        self.capture_dir = capture_dir or _default_capture_dir()
        self.readonly = readonly  # Store read/write mode
        self._env: lmdb.Environment | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self) -> None:
        if self._env is not None:
            return
        self._env = lmdb.open(
            self.db_path,
            readonly=self.readonly,  # Use instance variable
            lock=False,
            max_dbs=128,
            map_size=2 * 1024 * 1024 * 1024,  # 2 GB map
        )

    def close(self) -> None:
        if self._env is not None:
            self._env.close()
            self._env = None

    @property
    def env(self) -> lmdb.Environment:
        if self._env is None:
            self.open()
        assert self._env is not None
        return self._env

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _decode_gzip_b64(raw: bytes) -> dict[str, Any] | None:
        """Extract gzip+base64 JSON embedded in a FlatBuffers value."""
        text = raw.decode("utf-8", errors="replace")
        for match in _GZIP_B64_RE.finditer(text):
            try:
                decoded = base64.b64decode(match.group())
                decompressed = gzip.decompress(decoded)
                return json.loads(decompressed)
            except Exception:
                continue
        return None

    @staticmethod
    def _extract_json_objects(raw: bytes) -> list[dict[str, Any]]:
        """Extract top-level JSON objects embedded in binary data."""
        results: list[dict[str, Any]] = []
        i = 0
        length = len(raw)
        while i < length:
            if raw[i : i + 1] != b"{":
                i += 1
                continue
            depth = 0
            start = i
            for j in range(i, length):
                if raw[j : j + 1] == b"{":
                    depth += 1
                elif raw[j : j + 1] == b"}":
                    depth -= 1
                    if depth == 0:
                        try:
                            obj = json.loads(raw[start : j + 1])
                            results.append(obj)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass
                        i = j + 1
                        break
            else:
                break
        return results

    @staticmethod
    def _entity_id(key: bytes) -> int:
        """Extract the entity ID (last 4 bytes, big-endian) from an 8-byte key."""
        return struct.unpack(">I", key[4:8])[0]

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def _iter_prefix(self, prefix: bytes) -> Generator[tuple[int, bytes], None, None]:
        """Yield (entity_id, raw_value) for all records matching *prefix*."""
        with self.env.begin() as txn:
            cursor = txn.cursor()
            for key, value in cursor:
                if key[:4] == prefix:
                    yield self._entity_id(key), value

    def iter_captures(self) -> Generator[tuple[int, dict[str, Any]], None, None]:
        """Yield (entity_id, parsed_dict) for proxy capture records."""
        for eid, raw in self._iter_prefix(PREFIX_CAPTURE):
            parsed = self._decode_gzip_b64(raw)
            if parsed is not None:
                yield eid, parsed

    def iter_api_tests(self) -> Generator[tuple[int, dict[str, Any]], None, None]:
        """Yield (entity_id, parsed_dict) for API test records."""
        for eid, raw in self._iter_prefix(PREFIX_API_TEST):
            objects = self._extract_json_objects(raw)
            for obj in objects:
                if "request" in obj or "api" in obj:
                    yield eid, obj
                    break

    # ------------------------------------------------------------------
    # Single-record lookups
    # ------------------------------------------------------------------

    def get_capture(self, record_id: int) -> dict[str, Any] | None:
        """Return parsed capture record by its ``id`` field, or *None*."""
        for _, parsed in self.iter_captures():
            if parsed.get("id") == record_id:
                return parsed
        return None

    def get_api_test(self, entity_id: int) -> dict[str, Any] | None:
        """Return parsed API test record by entity ID, or *None*."""
        for eid, parsed in self.iter_api_tests():
            if eid == entity_id:
                return parsed
        return None

    # ------------------------------------------------------------------
    # Generic entity operations
    # ------------------------------------------------------------------

    def list_entities(self) -> dict[int, EntityInfo]:
        """
        List all entity types in the database.

        Returns:
            Dictionary mapping entity_id to EntityInfo
        """
        return discover_entities(self.env)

    def iter_entity(self, entity_id: int) -> Generator[tuple[int, dict[str, Any] | None, bytes], None, None]:
        """
        Iterate over all records of a specific entity type.

        Args:
            entity_id: Entity type ID

        Yields:
            Tuples of (record_id, parsed_dict_or_None, raw_bytes)
        """
        # Get entity info
        entities = self.list_entities()
        if entity_id not in entities:
            return

        entity_info = entities[entity_id]

        # Iterate over all records with this prefix
        with self.env.begin() as txn:
            cursor = txn.cursor()

            for key, value in cursor:
                if key[:4] == entity_info.data_prefix:
                    record_id = self._entity_id(key)
                    parsed = decode_value(value)
                    yield record_id, parsed, value

    def get_record(self, entity_id: int, record_id: int) -> dict[str, Any] | None:
        """
        Get a specific record by entity type and record ID.

        Args:
            entity_id: Entity type ID
            record_id: Record ID within the entity

        Returns:
            Parsed dictionary, or None if not found
        """
        for rid, parsed, _ in self.iter_entity(entity_id):
            if rid == record_id:
                return parsed

        return None

    def delete_record(self, entity_id: int, record_id: int) -> bool:
        """
        Delete a specific record from the database.

        WARNING: This modifies the database. The database must be opened
        in read-write mode (readonly=False).

        Args:
            entity_id: Entity type ID
            record_id: Record ID within the entity

        Returns:
            True if deleted, False if not found
        """
        # Get entity info
        entities = self.list_entities()
        if entity_id not in entities:
            return False

        entity_info = entities[entity_id]

        # Construct the key
        key_prefix = entity_info.data_prefix
        key = key_prefix + struct.pack('>I', record_id)

        # Delete the record
        try:
            with self.env.begin(write=True) as txn:
                deleted = txn.delete(key)
                return deleted
        except Exception:
            # Database is read-only or other error
            return False

    def get_entity_stats(self) -> dict[int, dict[str, Any]]:
        """
        Get statistics for all entities.

        Returns:
            Dictionary mapping entity_id to stats (name, count, prefix)
        """
        entities = self.list_entities()
        stats = {}

        for entity_id, entity_info in entities.items():
            count = get_entity_count(self.env, entity_info.data_prefix)
            stats[entity_id] = {
                'name': entity_info.name,
                'count': count,
                'prefix': entity_info.data_prefix.hex()
            }

        return stats
