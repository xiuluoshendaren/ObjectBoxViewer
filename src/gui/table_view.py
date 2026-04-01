"""Table view component for displaying entity records."""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

import customtkinter as ctk

from .styles import COLORS, FONTS, get_button_style


class TableView(ctk.CTkFrame):
    """
    A table view for displaying entity records with dynamic columns.

    Features:
    - Dynamic column generation based on data structure
    - Virtual scrolling for large datasets
    - Row selection and double-click handling
    - Sortable columns with sort field selector
    """

    def __init__(
        self,
        master: tk.Widget,
        on_row_select: Callable[[int, dict], None] | None = None,
        on_row_double_click: Callable[[int, dict], None] | None = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.on_row_select = on_row_select
        self.on_row_double_click = on_row_double_click

        self._data: list[tuple[int, dict | None, bytes]] = []
        self._filtered_data: list[tuple[int, dict | None, bytes]] = []
        self._columns: list[str] = []
        self._sort_column: str = 'ID'
        self._sort_reverse: bool = False
        self._search_query: str = ''

        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components."""
        # Control panel (sort + search)
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Sort controls
        self.sort_frame = ctk.CTkFrame(self.control_frame, fg_color='transparent')
        self.sort_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Sort label
        sort_label = ctk.CTkLabel(
            self.sort_frame,
            text="Sort by:",
            font=FONTS['body'],
            text_color=COLORS['fg_light']
        )
        sort_label.pack(side=tk.LEFT, padx=5)

        # Sort column selector
        self.sort_var = tk.StringVar(value='ID')
        self.sort_combo = ttk.Combobox(
            self.sort_frame,
            textvariable=self.sort_var,
            state='readonly',
            width=25,
            font=FONTS['body']
        )
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_combo.bind('<<ComboboxSelected>>', self._on_sort_change)

        # Sort order button
        self.sort_order_btn = ctk.CTkButton(
            self.sort_frame,
            text="↑ Ascending",
            command=self._toggle_sort_order,
            width=120,
            **get_button_style('primary')
        )
        self.sort_order_btn.pack(side=tk.LEFT, padx=5)

        # Search controls
        self.search_frame = ctk.CTkFrame(self.control_frame, fg_color='transparent')
        self.search_frame.pack(side=tk.RIGHT, fill=tk.X, padx=10)

        # Search label
        search_label = ctk.CTkLabel(
            self.search_frame,
            text="Search:",
            font=FONTS['body'],
            text_color=COLORS['fg_light']
        )
        search_label.pack(side=tk.LEFT, padx=5)

        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            textvariable=self.search_var,
            placeholder_text="Search in all fields...",
            width=250,
            font=FONTS['body']
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self._on_search_change)

        # Clear search button
        self.clear_search_btn = ctk.CTkButton(
            self.search_frame,
            text="✕",
            command=self._clear_search,
            width=30,
            **get_button_style('warning')
        )
        self.clear_search_btn.pack(side=tk.LEFT, padx=5)

        # Create Treeview with scrollbar
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Vertical scrollbar
        self.v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)

        # Horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL)

        # Treeview
        self.tree = ttk.Treeview(
            self.tree_frame,
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set,
            show='tree headings',
            selectmode='browse',
            height=20
        )

        self.v_scrollbar.config(command=self.tree.yview)
        self.h_scrollbar.config(command=self.tree.xview)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.h_scrollbar.grid(row=1, column=0, sticky='ew')

        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        # Configure tags for alternating row colors
        self.tree.tag_configure('oddrow', background=COLORS['row_odd'])
        self.tree.tag_configure('evenrow', background=COLORS['row_even'])

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-1>', self._on_header_click)

        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def set_data(self, data: list[tuple[int, dict | None, bytes]]):
        """
        Set the data to display.

        Args:
            data: List of (record_id, parsed_dict_or_None, raw_bytes) tuples
        """
        # Clear existing data
        self.clear()

        self._data = data

        if not data:
            return

        # Determine columns from the first few records
        self._infer_columns()

        # Configure tree columns
        self._setup_columns()

        # Insert data
        self._insert_data()

    def _infer_columns(self):
        """Infer column names from data structure."""
        # Always include ID column
        columns = ['ID']

        # Collect all unique keys from parsed records
        all_keys = set()

        for record_id, parsed, _ in self._data:
            if parsed and isinstance(parsed, dict):
                all_keys.update(parsed.keys())

        # Sort keys and add to columns
        columns.extend(sorted(all_keys))

        self._columns = columns

    def _setup_columns(self):
        """Configure tree columns."""
        # Set column identifiers
        self.tree['columns'] = self._columns

        # Configure each column
        for col in self._columns:
            self.tree.heading(col, text=col, anchor=tk.W)

            # Set column width based on content
            if col == 'ID':
                width = 100
            else:
                width = 180

            self.tree.column(
                col,
                width=width,
                minwidth=50,
                anchor=tk.W,
                stretch=True
            )

        # Update sort combo box with available columns
        self.sort_combo['values'] = self._columns
        if self._sort_column in self._columns:
            self.sort_var.set(self._sort_column)

    def _insert_data(self):
        """Insert data into the tree (with sorting applied)."""
        # Sort data before inserting
        sorted_data = self._sort_data()

        for idx, (record_id, parsed, raw) in enumerate(sorted_data):
            # Build values list
            values = [str(record_id)]

            if parsed and isinstance(parsed, dict):
                # Add values for each column (in order)
                for col in self._columns[1:]:  # Skip ID column
                    value = parsed.get(col, '')

                    # Format value for display
                    if isinstance(value, (dict, list)):
                        value_str = json.dumps(value, ensure_ascii=False)[:100]
                    else:
                        value_str = str(value) if value is not None else ''

                    values.append(value_str)
            else:
                # No parsed data, fill with placeholder
                values.extend(['<binary data>'] * (len(self._columns) - 1))

            # Determine row tag
            tag = 'oddrow' if idx % 2 == 0 else 'evenrow'

            # Insert row
            self.tree.insert(
                '',
                tk.END,
                iid=str(record_id),
                values=values,
                tags=(tag,)
            )

    def clear(self):
        """Clear all data from the table."""
        # Clear tree items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Clear columns
        self.tree['columns'] = ()

        # Reset state
        self._data = []
        self._columns = []

    def get_selected_record(self) -> tuple[int, dict | None] | None:
        """
        Get the currently selected record.

        Returns:
            Tuple of (record_id, parsed_dict_or_None), or None if no selection
        """
        selection = self.tree.selection()
        if not selection:
            return None

        record_id = int(selection[0])

        # Find the record in data
        for rid, parsed, _ in self._data:
            if rid == record_id:
                return (rid, parsed)

        return None

    def _on_select(self, event):
        """Handle row selection."""
        if self.on_row_select:
            result = self.get_selected_record()
            if result:
                self.on_row_select(result[0], result[1])

    def _on_double_click(self, event):
        """Handle row double-click."""
        if self.on_row_double_click:
            result = self.get_selected_record()
            if result:
                self.on_row_double_click(result[0], result[1])

    def get_record_count(self) -> int:
        """Get the number of records currently displayed."""
        return len(self._data)

    def _sort_data(self) -> list[tuple[int, dict | None, bytes]]:
        """Sort data by the current sort column and order."""
        if not self._data or not self._sort_column:
            return self._data

        def get_sort_key(item):
            record_id, parsed, _ = item

            if self._sort_column == 'ID':
                return record_id

            if parsed and isinstance(parsed, dict):
                value = parsed.get(self._sort_column, '')

                # Handle different types
                if value is None:
                    return ('', 0)  # Sort None values first
                elif isinstance(value, (int, float)):
                    return ('', value)
                elif isinstance(value, str):
                    return (value.lower(), 0)
                else:
                    return (str(value).lower(), 0)

            return ('', 0)

        return sorted(self._data, key=get_sort_key, reverse=self._sort_reverse)

    def _on_sort_change(self, event):
        """Handle sort column change."""
        self._sort_column = self.sort_var.get()
        self._refresh_display()

    def _toggle_sort_order(self):
        """Toggle between ascending and descending sort."""
        self._sort_reverse = not self._sort_reverse

        if self._sort_reverse:
            self.sort_order_btn.configure(text="↓ Descending")
        else:
            self.sort_order_btn.configure(text="↑ Ascending")

        self._refresh_display()

    def _on_header_click(self, event):
        """Handle column header click for sorting."""
        region = self.tree.identify('region', event.x, event.y)

        if region == 'heading':
            column = self.tree.identify_column(event.x)
            if column:
                col_name = self.tree.heading(column)['text']
                if col_name in self._columns:
                    # Update sort column
                    self._sort_column = col_name
                    self.sort_var.set(col_name)

                    # Toggle sort order if clicking the same column
                    self._toggle_sort_order()

    def _refresh_display(self):
        """Refresh the table display with current sort settings."""
        if not self._data:
            return

        # Remember current selection
        selection = self.tree.selection()

        # Clear and re-insert data
        for item in self.tree.get_children():
            self.tree.delete(item)

        self._insert_data()

        # Restore selection if possible
        if selection:
            try:
                self.tree.selection_set(selection)
            except Exception:
                pass

    def _on_search_change(self, event):
        """Handle search input change."""
        self._search_query = self.search_var.get().lower().strip()
        self._apply_search_filter()

    def _clear_search(self):
        """Clear search and show all records."""
        self.search_var.set('')
        self._search_query = ''
        self._apply_search_filter()

    def _apply_search_filter(self):
        """Apply search filter to data."""
        if not self._search_query:
            # No search, show all data
            self._filtered_data = self._data.copy()
        else:
            # Filter data based on search query
            self._filtered_data = []

            for record_id, parsed, raw in self._data:
                # Search in record ID
                if self._search_query in str(record_id).lower():
                    self._filtered_data.append((record_id, parsed, raw))
                    continue

                # Search in all parsed fields
                if parsed and isinstance(parsed, dict):
                    found = False
                    for key, value in parsed.items():
                        # Convert value to string and search
                        value_str = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
                        if self._search_query in value_str.lower():
                            found = True
                            break

                    if found:
                        self._filtered_data.append((record_id, parsed, raw))

        # Refresh display with filtered data
        self._refresh_display()

        # Update status to show filtered count
        if hasattr(self.master, 'update_search_status'):
            self.master.update_search_status(len(self._filtered_data), len(self._data))

