# ObjectBox Database Browser

A modern GUI application for browsing and managing ObjectBox databases.

## Features

- **Universal Browser**: Automatically discovers all entity types in any ObjectBox database
- **Modern UI**: Built with CustomTkinter for a sleek, modern interface
- **Data Exploration**: Browse records with dynamic column generation
- **Detail View**: Double-click any record to see formatted JSON details
- **Export**: Export records to JSON files
- **Delete Records**: Remove unwanted records with confirmation

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the Application

```bash
python main.py
```

Or specify a database file to load automatically:

```bash
python main.py /path/to/your/data.mdb
```

### Using the GUI

1. **Open a Database**:
   - Click "Browse" to select a `.mdb` file
   - Or enter the path manually and click "Load"

2. **Browse Entities**:
   - The left panel shows all discovered entity types
   - Click on an entity to load its records

3. **View Records**:
   - The right panel displays records in a table
   - Columns are automatically generated from the data structure

4. **View Details**:
   - Double-click a record to open the detail view
   - See formatted JSON with syntax highlighting

5. **Export Data**:
   - In the detail view, click "Export to JSON" to save the record

6. **Close Database**:
   - Click "Close DB" to close the current database connection

## Architecture

```
ObjectBoxViewer/
├── src/
│   ├── db.py              # Database access layer (LMDB + ObjectBox)
│   ├── schema.py          # Entity discovery and schema parsing
│   ├── decoder.py         # Data decoding (gzip/base64/JSON/FlatBuffers)
│   └── gui/
│       ├── main_window.py # Main application window
│       ├── table_view.py  # Data table component
│       ├── detail_view.py # Record detail popup
│       └── styles.py      # UI styling and themes
├── main.py                # Application entry point
└── requirements.txt       # Python dependencies
```

## How It Works

### ObjectBox Storage

ObjectBox uses LMDB as its underlying storage engine:

- **Keys**: 8-byte format `[4-byte prefix][4-byte entity ID]`
- **Values**: FlatBuffers serialized data or gzip+base64 encoded JSON
- **Prefixes**: Calculated as `0x18000000 + (entity_type_id * 4)`

### Entity Discovery

The browser automatically discovers all entity types by:

1. Scanning the `00 00 00 00` prefix for schema records
2. Parsing entity names from FlatBuffers metadata
3. Calculating data prefixes for each entity type

### Data Decoding

Records are decoded using multiple strategies:

1. **Gzip + Base64**: Decompress and decode (common in Reqable)
2. **Embedded JSON**: Extract JSON objects from binary data
3. **FlatBuffers**: Display raw bytes (requires schema for parsing)

## Limitations

- **Create/Update**: Not supported (requires FlatBuffers schema compilation)
- **Large Datasets**: Performance may degrade with 100,000+ records
- **Binary Data**: Some records may only show raw bytes

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

This project follows PEP 8 guidelines with type hints.

## License

MIT License

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## Troubleshooting

### "Failed to load database" error

- Ensure the file is a valid ObjectBox `.mdb` file
- Check that you have read permissions for the file
- Try closing any applications that might have the database open

### "No entities found"

- The database might be empty
- The database might not be a valid ObjectBox format

### Performance Issues

- For large databases (>50,000 records), loading may take a few seconds
- Consider exporting specific records rather than browsing all data
