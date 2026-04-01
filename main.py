#!/usr/bin/env python3
"""ObjectBox Database Browser - Main Entry Point.

A modern GUI application for browsing and managing ObjectBox databases.

Usage:
    python main.py [database_path]

If database_path is provided, it will be loaded automatically on startup.
If no path is provided, the application will look for 'data.mdb' in the current directory.
"""

from __future__ import annotations

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import customtkinter as ctk
from src.gui.main_window import ObjectBoxBrowser


def main():
    """Main entry point for the ObjectBox Browser application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')

    # Create application instance
    app = ObjectBoxBrowser()

    # Load database from command line argument if provided
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        if os.path.exists(db_path):
            app.file_entry.delete(0, 'end')
            app.file_entry.insert(0, db_path)
            app._load_db()

    # Start the application
    app.mainloop()


if __name__ == '__main__':
    main()
