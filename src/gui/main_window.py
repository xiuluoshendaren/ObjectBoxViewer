"""Main window for ObjectBox Browser."""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any

import customtkinter as ctk

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db import ReqableDB
from src.schema import EntityInfo
from .styles import (
    COLORS, FONTS, configure_theme, configure_treeview_style,
    get_button_style, get_label_style, get_entry_style
)
from .table_view import TableView
from .detail_view import DetailView


class ObjectBoxBrowser(ctk.CTk):
    """Main application window for browsing ObjectBox databases."""

    def __init__(self):
        super().__init__()

        # Database connection
        self.db: ReqableDB | None = None
        self.db_path: str = ''

        # Current selection
        self.current_entity_id: int | None = None
        self.entities: dict[int, EntityInfo] = {}
        self.total_records: int = 0  # Track total records for status

        # Setup window
        self._setup_window()
        self._setup_ui()

        # Load default database if exists
        self._load_default_db()

    def _setup_window(self):
        """Configure main window properties."""
        self.title("ObjectBox Browser")

        # Window size
        self.geometry("1400x900")
        self.minsize(1000, 700)

        # Configure theme
        configure_theme()
        configure_treeview_style()  # Apply Treeview styles

        # Make window responsive
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        """Initialize UI components."""
        # Header with file selector
        self._setup_header()

        # Main content area
        self._setup_content()

        # Status bar
        self._setup_status_bar()

    def _setup_header(self):
        """Setup header with file selector."""
        header_frame = ctk.CTkFrame(self, height=60)
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)

        # File selector label
        label = ctk.CTkLabel(
            header_frame,
            text="Database File:",
            **get_label_style('heading')
        )
        label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # File path entry
        self.file_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Select a .mdb file...",
            **get_entry_style()
        )
        self.file_entry.grid(row=0, column=1, padx=5, pady=10, sticky='ew')

        # Browse button
        self.browse_btn = ctk.CTkButton(
            header_frame,
            text="Browse",
            command=self._browse_file,
            **get_button_style('primary')
        )
        self.browse_btn.grid(row=0, column=2, padx=5, pady=10)

        # Load button
        self.load_btn = ctk.CTkButton(
            header_frame,
            text="Load",
            command=self._load_db,
            **get_button_style('success')
        )
        self.load_btn.grid(row=0, column=3, padx=5, pady=10)

        # Close DB button
        self.close_btn = ctk.CTkButton(
            header_frame,
            text="Close DB",
            command=self._close_db,
            **get_button_style('warning')
        )
        self.close_btn.grid(row=0, column=4, padx=5, pady=10)

    def _setup_content(self):
        """Setup main content area with entity list and table."""
        # Main container
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Left panel: Entity list
        self._setup_entity_list(content_frame)

        # Right panel: Table view
        self._setup_table_view(content_frame)

    def _setup_entity_list(self, parent: tk.Widget):
        """Setup entity list panel."""
        left_panel = ctk.CTkFrame(parent, width=300)
        left_panel.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_propagate(False)

        # Label
        label = ctk.CTkLabel(
            left_panel,
            text="Entities",
            **get_label_style('heading')
        )
        label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        # Entity list (Treeview)
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Create Treeview for entities
        self.entity_tree = ttk.Treeview(
            list_frame,
            columns=['name', 'count'],
            show='headings',
            selectmode='browse',
            height=20
        )

        self.entity_tree.heading('name', text='Entity Name')
        self.entity_tree.heading('count', text='Records')

        self.entity_tree.column('name', width=180, anchor='w')
        self.entity_tree.column('count', width=80, anchor='e')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.entity_tree.yview)
        self.entity_tree.configure(yscrollcommand=scrollbar.set)

        self.entity_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind selection event
        self.entity_tree.bind('<<TreeviewSelect>>', self._on_entity_select)

    def _setup_table_view(self, parent: tk.Widget):
        """Setup table view panel."""
        right_panel = ctk.CTkFrame(parent)
        right_panel.grid(row=0, column=1, sticky='nsew')
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Table view component
        self.table_view = TableView(
            right_panel,
            on_row_select=self._on_row_select,
            on_row_double_click=self._on_row_double_click,
            main_window=self  # Pass reference to main window
        )
        self.table_view.grid(row=0, column=0, sticky='nsew')

    def _setup_status_bar(self):
        """Setup status bar."""
        status_frame = ctk.CTkFrame(self, height=30)
        status_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

        # Status label
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="No database loaded",
            **get_label_style('normal')
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Record count
        self.record_count_label = ctk.CTkLabel(
            status_frame,
            text="Records: 0",
            **get_label_style('normal')
        )
        self.record_count_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def _load_default_db(self):
        """Load the default database if it exists."""
        # Check for data.mdb in current directory
        default_path = os.path.join(os.getcwd(), 'data.mdb')

        if os.path.exists(default_path):
            self.file_entry.insert(0, default_path)
            self._load_db()

    def _browse_file(self):
        """Open file browser to select database file."""
        filepath = filedialog.askopenfilename(
            title="Select ObjectBox Database",
            filetypes=[
                ("ObjectBox Database", "*.mdb"),
                ("All Files", "*.*")
            ]
        )

        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)

    def _load_db(self):
        """Load the selected database file."""
        db_path = self.file_entry.get()

        if not db_path:
            messagebox.showwarning("Warning", "Please select a database file first.")
            return

        if not os.path.exists(db_path):
            messagebox.showerror("Error", f"File not found: {db_path}")
            return

        try:
            # Close existing connection
            if self.db:
                self.db.close()

            # Open new connection
            self.db = ReqableDB(db_path=db_path)
            self.db.open()

            self.db_path = db_path

            # Load entities
            self._load_entities()

            # Update status
            self.status_label.configure(text=f"Loaded: {os.path.basename(db_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database:\n{str(e)}")
            self.db = None

    def _close_db(self):
        """Close the current database connection."""
        if self.db:
            self.db.close()
            self.db = None

        # Clear UI
        self._clear_entity_list()
        self.table_view.clear()

        # Update status
        self.status_label.configure(text="No database loaded")
        self.record_count_label.configure(text="Records: 0")

    def _load_entities(self):
        """Load and display all entities from the database."""
        if not self.db:
            return

        # Clear existing list
        self._clear_entity_list()

        # Get entity stats
        stats = self.db.get_entity_stats()

        # Populate entity list
        for entity_id, stat in stats.items():
            self.entity_tree.insert(
                '',
                tk.END,
                iid=str(entity_id),
                values=(stat['name'], stat['count'])
            )

        self.entities = self.db.list_entities()

        # Update status
        total_records = sum(stat['count'] for stat in stats.values())
        self.record_count_label.configure(text=f"Total Records: {total_records}")

    def _clear_entity_list(self):
        """Clear the entity list."""
        for item in self.entity_tree.get_children():
            self.entity_tree.delete(item)

    def _on_entity_select(self, event):
        """Handle entity selection."""
        selection = self.entity_tree.selection()
        if not selection:
            return

        entity_id = int(selection[0])
        self.current_entity_id = entity_id

        # Load records for this entity
        self._load_entity_records(entity_id)

    def _load_entity_records(self, entity_id: int):
        """Load records for a specific entity."""
        if not self.db:
            return

        # Show loading indicator
        self.status_label.configure(text="Loading records...")
        self.update()

        try:
            # Load all records for this entity
            data = list(self.db.iter_entity(entity_id))

            # Store total count
            self.total_records = len(data)

            # Display in table
            self.table_view.set_data(data)

            # Update status
            entity_info = self.entities.get(entity_id)
            entity_name = entity_info.name if entity_info else f"Entity {entity_id}"

            self.status_label.configure(text=f"Entity: {entity_name}")
            self.record_count_label.configure(text=f"Records: {self.total_records}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records:\n{str(e)}")
            self.status_label.configure(text="Error loading records")

    def update_search_status(self, filtered_count: int, total_count: int):
        """Update status bar with search results count."""
        if filtered_count == total_count:
            self.record_count_label.configure(text=f"Records: {total_count}")
        else:
            self.record_count_label.configure(text=f"Records: {filtered_count} / {total_count} (filtered)")

    def _on_row_select(self, record_id: int, data: dict | None):
        """Handle row selection in table."""
        # Update status with selected record ID
        self.status_label.configure(
            text=f"Selected Record ID: {record_id}"
        )

    def _on_row_double_click(self, record_id: int, data: dict | None):
        """Handle row double-click to show details."""
        # Get raw bytes if available
        raw_bytes = None
        if self.db and self.current_entity_id:
            for rid, _, raw in self.db.iter_entity(self.current_entity_id):
                if rid == record_id:
                    raw_bytes = raw
                    break

        # Open detail view
        DetailView(self, record_id, data, raw_bytes)

    def _on_close(self):
        """Handle window close event."""
        if self.db:
            self.db.close()

        self.destroy()


if __name__ == '__main__':
    app = ObjectBoxBrowser()
    app.mainloop()
