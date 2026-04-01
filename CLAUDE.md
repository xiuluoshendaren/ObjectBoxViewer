# ObjectBox Database Viewer

A modern GUI application for browsing and managing ObjectBox databases. This tool provides a universal browser that automatically discovers all entity types in any ObjectBox database, with features for data exploration, JSON detail viewing, export, and record deletion.

## Project Overview

- **Technology Stack**: Python 3.9+, CustomTkinter, LMDB, FlatBuffers
- **Purpose**: GUI tool for viewing and managing ObjectBox database files
- **Key Features**:
  - Universal entity discovery
  - Modern UI with CustomTkinter
  - Dynamic data table generation
  - JSON detail view with syntax highlighting
  - Export to JSON
  - Record deletion with confirmation

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

## Development Guidelines

### Workflow
1. Always create a plan before making code changes
2. Save plans to `.claude/plans/` directory
3. Commit all changes to git with clear commit messages

### Memory System
- **Memory Location**: `.claude/memory/`
  - Contains project-specific memories and context
  - Stores user preferences, feedback, and project knowledge

### Planning
- **Plans Directory**: `.claude/plans/`
  - Save implementation plans before making changes
  - Include objectives, steps, and impact analysis

## Build & Deployment

- Supports multi-platform builds (macOS ARM64/Intel, Windows)
- Uses PyInstaller for creating standalone executables
- GitHub Actions for automated multi-platform builds
- See README.md for detailed build instructions

## Key Technical Details

- ObjectBox uses LMDB storage with 8-byte keys
- Entity discovery via schema prefix scanning
- Multiple data decoding strategies (gzip, base64, JSON, FlatBuffers)
- Modern UI built with CustomTkinter