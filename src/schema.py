"""Schema discovery and parsing for ObjectBox databases."""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from typing import Any

import lmdb


@dataclass
class EntityInfo:
    """Information about an ObjectBox entity type."""

    entity_id: int
    name: str
    data_prefix: bytes
    index_prefix: bytes
    last_entity_id: int = 0
    last_index_id: int = 0


def discover_entities(env: lmdb.Environment) -> dict[int, EntityInfo]:
    """
    Discover all entity types from the ObjectBox schema.

    ObjectBox stores schema information under the special prefix 00 00 00 00.
    Each schema record contains the entity name and metadata.

    Args:
        env: LMDB environment opened on an ObjectBox database

    Returns:
        Dictionary mapping entity_id to EntityInfo
    """
    entities = {}

    with env.begin() as txn:
        cursor = txn.cursor()

        for key, value in cursor:
            # Schema records have prefix 00 00 00 00
            if key[:4] == b'\x00\x00\x00\x00' and key[4:8] != b'\x00\x00\x00\x00':
                # Extract entity ID from the key (last 4 bytes, big-endian)
                entity_id = struct.unpack('>I', key[4:8])[0]

                # Extract entity name from FlatBuffers data
                # The name is typically stored as a null-terminated string
                name_match = re.search(rb'(\w+Entity)\x00', value)
                if name_match:
                    entity_name = name_match.group(1).decode('utf-8')

                    # Calculate data and index prefixes
                    # Data prefix: 0x18000000 + (entity_id * 4)
                    # Index prefix: 0x20000000 + (entity_id * 4)
                    data_prefix_int = 0x18000000 + (entity_id * 4)
                    index_prefix_int = 0x20000000 + (entity_id * 4)

                    data_prefix = data_prefix_int.to_bytes(4, 'big')
                    index_prefix = index_prefix_int.to_bytes(4, 'big')

                    # Try to extract last_entity_id and last_index_id from schema
                    last_entity_id = extract_last_ids(value)

                    entities[entity_id] = EntityInfo(
                        entity_id=entity_id,
                        name=entity_name,
                        data_prefix=data_prefix,
                        index_prefix=index_prefix,
                        last_entity_id=last_entity_id,
                        last_index_id=last_entity_id
                    )

    return entities


def extract_last_ids(schema_data: bytes) -> int:
    """
    Extract last entity ID from FlatBuffers schema data.

    This is a best-effort extraction from the binary schema format.
    Returns 0 if extraction fails.
    """
    try:
        # Look for patterns that might indicate last IDs
        # This is heuristic and may need adjustment for different ObjectBox versions
        for i in range(len(schema_data) - 4):
            if schema_data[i:i+2] == b'\x10\x00':  # Common marker
                potential_id = struct.unpack('<I', schema_data[i+2:i+6])[0]
                if 0 < potential_id < 1000:  # Reasonable entity ID range
                    return potential_id
    except Exception:
        pass

    return 0


def get_entity_count(env: lmdb.Environment, prefix: bytes) -> int:
    """
    Count the number of records for a specific entity type.

    Args:
        env: LMDB environment
        prefix: 4-byte prefix for the entity type

    Returns:
        Number of records matching this prefix
    """
    count = 0

    with env.begin() as txn:
        cursor = txn.cursor()

        for key, _ in cursor:
            if key[:4] == prefix:
                count += 1

    return count


def get_all_prefixes(env: lmdb.Environment) -> dict[bytes, int]:
    """
    Get all unique prefixes and their counts from the database.

    This is useful for discovering entities even when schema parsing fails.

    Args:
        env: LMDB environment

    Returns:
        Dictionary mapping 4-byte prefixes to record counts
    """
    prefixes: dict[bytes, int] = {}

    with env.begin() as txn:
        cursor = txn.cursor()

        for key, _ in cursor:
            prefix = key[:4]
            prefixes[prefix] = prefixes.get(prefix, 0) + 1

    return prefixes
