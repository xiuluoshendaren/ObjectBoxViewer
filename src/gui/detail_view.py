"""Detail view component for displaying record details."""

from __future__ import annotations

import json
import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from typing import Any

import customtkinter as ctk

from .styles import COLORS, FONTS, get_button_style, get_label_style


class JSONSyntaxHighlighter:
    """JSON syntax highlighter for Text widget."""

    # Color scheme for JSON syntax
    TAG_COLORS = {
        'key': '#FF6B6B',      # Red for keys
        'string': '#4ECDC4',   # Teal for strings
        'number': '#95E1D3',   # Light green for numbers
        'boolean': '#F38181',  # Coral for booleans
        'null': '#AA96DA',     # Purple for null
        'bracket': '#FCBAD3',  # Pink for brackets
    }

    @staticmethod
    def highlight(text_widget: ctk.CTkTextbox, json_text: str):
        """Apply syntax highlighting to JSON text."""
        # Use the underlying tkinter Text widget
        text = text_widget._textbox if hasattr(text_widget, '_textbox') else text_widget

        # Configure tags with colors
        for tag_name, color in JSONSyntaxHighlighter.TAG_COLORS.items():
            text.tag_configure(tag_name, foreground=color)

        # Clear existing tags
        for tag in JSONSyntaxHighlighter.TAG_COLORS.keys():
            text.tag_remove(tag, '1.0', tk.END)

        try:
            # Parse JSON to validate and get structure
            data = json.loads(json_text)

            # Highlight line by line
            lines = json_text.split('\n')
            line_num = 1

            for line in lines:
                # Highlight keys (strings followed by colon)
                key_pattern = r'"([^"]+)":\s*'
                for match in re.finditer(key_pattern, line):
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end() - 1}"  # Exclude colon
                    text.tag_add('key', start, end)

                # Highlight string values
                string_pattern = r':\s*"([^"]*)"'
                for match in re.finditer(string_pattern, line):
                    start = f"{line_num}.{match.start() + 2}"  # Skip colon and space
                    end = f"{line_num}.{match.end()}"
                    text.tag_add('string', start, end)

                # Highlight numbers
                number_pattern = r':\s*(-?\d+\.?\d*)'
                for match in re.finditer(number_pattern, line):
                    start = f"{line_num}.{match.start() + 2}"
                    end = f"{line_num}.{match.end()}"
                    text.tag_add('number', start, end)

                # Highlight booleans
                bool_pattern = r':\s*(true|false)'
                for match in re.finditer(bool_pattern, line, re.IGNORECASE):
                    start = f"{line_num}.{match.start() + 2}"
                    end = f"{line_num}.{match.end()}"
                    text.tag_add('boolean', start, end)

                # Highlight null
                null_pattern = r':\s*(null)'
                for match in re.finditer(null_pattern, line, re.IGNORECASE):
                    start = f"{line_num}.{match.start() + 2}"
                    end = f"{line_num}.{match.end()}"
                    text.tag_add('null', start, end)

                # Highlight brackets and braces
                for i, char in enumerate(line):
                    if char in '{}[]':
                        pos = f"{line_num}.{i}"
                        text.tag_add('bracket', pos, f"{line_num}.{i+1}")

                line_num += 1

        except json.JSONDecodeError:
            # If JSON is invalid, don't highlight
            pass


class DetailView(ctk.CTkToplevel):
    """
    A popup window for displaying detailed record information.

    Features:
    - JSON formatting and syntax highlighting
    - Read-only view mode
    - Copy to clipboard
    - Export to JSON file
    """

    def __init__(
        self,
        master: tk.Widget,
        record_id: int,
        data: dict[str, Any] | None,
        raw_bytes: bytes | None = None,
        on_delete: callable = None,
        entity_id: int | None = None
    ):
        super().__init__(master)

        self.record_id = record_id
        self.data = data
        self.raw_bytes = raw_bytes
        self.on_delete = on_delete  # Callback for delete operation
        self.entity_id = entity_id  # Entity ID for deletion

        self._setup_window()
        self._setup_ui()
        self._load_data()

    def _setup_window(self):
        """Configure window properties."""
        self.title(f"Record #{self.record_id}")

        # Window size and position
        self.geometry("900x700")
        self.minsize(700, 500)

        # Center on parent
        self.transient(self.master)
        self.grab_set()

        # Make window resizable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _setup_ui(self):
        """Initialize UI components."""
        # Main container
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self._setup_header()

        # Content area
        self._setup_content()

        # Footer with buttons
        self._setup_footer()

    def _setup_header(self):
        """Setup header with title."""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Record Details - ID: {self.record_id}",
            **get_label_style('title')
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=5)

        # Record info
        if self.data:
            info_text = f"Type: {type(self.data).__name__}"
            info_label = ctk.CTkLabel(
                header_frame,
                text=info_text,
                **get_label_style('normal')
            )
            info_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def _setup_content(self):
        """Setup content area with text widget."""
        # Text frame
        text_frame = ctk.CTkFrame(self.main_frame)
        text_frame.grid(row=1, column=0, sticky='nsew')
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Text widget with scrollbar
        self.text = ctk.CTkTextbox(
            text_frame,
            font=FONTS['code_large'],  # Use larger font for better readability
            wrap=tk.WORD
        )
        self.text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(text_frame, command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.text.configure(yscrollcommand=scrollbar.set)

    def _setup_footer(self):
        """Setup footer with action buttons."""
        footer_frame = ctk.CTkFrame(self.main_frame)
        footer_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))

        # Left side buttons
        left_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        left_frame.pack(side=tk.LEFT)

        # Format button
        self.format_btn = ctk.CTkButton(
            left_frame,
            text="📋 Format",
            command=self._format_json,
            **get_button_style('primary')
        )
        self.format_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Copy button
        self.copy_btn = ctk.CTkButton(
            left_frame,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard,
            **get_button_style('primary')
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Export button
        self.export_btn = ctk.CTkButton(
            left_frame,
            text="Export to JSON",
            command=self._export_to_json,
            **get_button_style('success')
        )
        self.export_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Delete button (if callback provided)
        if self.on_delete and self.entity_id is not None:
            self.delete_btn = ctk.CTkButton(
                left_frame,
                text="🗑️ Delete Record",
                command=self._delete_record,
                **get_button_style('danger')
            )
            self.delete_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Right side - Close button
        right_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        right_frame.pack(side=tk.RIGHT)

        # Close button
        self.close_btn = ctk.CTkButton(
            right_frame,
            text="Close",
            command=self.destroy,
            **get_button_style('warning')
        )
        self.close_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    def _load_data(self):
        """Load and display data."""
        self.text.delete('1.0', tk.END)

        if self.data:
            # Format JSON with indentation
            try:
                formatted = json.dumps(
                    self.data,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
                self.text.insert('1.0', formatted)

                # Apply syntax highlighting
                self._apply_syntax_highlighting()
            except Exception as e:
                self.text.insert('1.0', f"Error formatting data: {e}\n\nRaw data:\n{self.data}")
        elif self.raw_bytes:
            # Display raw bytes
            self.text.insert(
                '1.0',
                f"Binary data ({len(self.raw_bytes)} bytes)\n\n"
                f"Hex:\n{self.raw_bytes[:500].hex()}\n\n"
                f"UTF-8 (may be incomplete):\n{self.raw_bytes[:500].decode('utf-8', errors='replace')}"
            )
        else:
            self.text.insert('1.0', "No data available")

        # Make text read-only
        self.text.configure(state=tk.DISABLED)

    def _apply_syntax_highlighting(self):
        """Apply JSON syntax highlighting."""
        json_text = self.text.get('1.0', tk.END).strip()
        if json_text:
            JSONSyntaxHighlighter.highlight(self.text, json_text)

    def _format_json(self):
        """Format JSON with proper indentation."""
        try:
            # Get current JSON text
            json_text = self.text.get('1.0', tk.END).strip()
            data = json.loads(json_text)

            # Re-format with proper indentation
            formatted = json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                default=str
            )

            # Update text (temporarily enable editing)
            self.text.configure(state=tk.NORMAL)
            self.text.delete('1.0', tk.END)
            self.text.insert('1.0', formatted)
            self.text.configure(state=tk.DISABLED)

            # Re-apply syntax highlighting
            self._apply_syntax_highlighting()

        except json.JSONDecodeError as e:
            messagebox.showerror(
                "Format Error",
                f"Cannot format invalid JSON:\n{e.msg}",
                parent=self
            )
        except Exception as e:
            messagebox.showerror(
                "Format Error",
                f"Failed to format JSON:\n{str(e)}",
                parent=self
            )

    def _copy_to_clipboard(self):
        """Copy data to clipboard."""
        if not self.data:
            return

        try:
            formatted = json.dumps(
                self.data,
                indent=2,
                ensure_ascii=False,
                default=str
            )

            self.clipboard_clear()
            self.clipboard_append(formatted)
            self.update()  # Keep clipboard after window closes

            # Show success message
            self._show_message("Copied to clipboard!")
        except Exception as e:
            self._show_message(f"Error copying: {e}", error=True)

    def _export_to_json(self):
        """Export data to JSON file."""
        if not self.data:
            return

        # Ask for file location
        from tkinter import filedialog

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"record_{self.record_id}_{timestamp}.json"

        filepath = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            initialfile=default_filename,
            title='Export Record to JSON'
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    self.data,
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )

            self._show_message(f"Exported to: {filepath}")
        except Exception as e:
            self._show_message(f"Error exporting: {e}", error=True)

    def _delete_record(self):
        """Delete this record from the database."""
        # Show confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete record #{self.record_id}?\n\n"
            "This action cannot be undone!",
            icon='warning',
            parent=self
        )

        if not confirm:
            return

        # Call delete callback
        if self.on_delete and self.entity_id is not None:
            try:
                success = self.on_delete(self.entity_id, self.record_id)

                if success:
                    self._show_message("Record deleted successfully!")
                    # Close the detail window after a short delay
                    self.after(1000, self.destroy)
                else:
                    self._show_message("Failed to delete record.\n\n"
                                     "The database may be opened in read-only mode.",
                                     error=True)
            except Exception as e:
                self._show_message(f"Error deleting record: {e}", error=True)

    def _show_message(self, message: str, error: bool = False):
        """Show a temporary message popup centered on parent window."""
        # Create a small popup
        popup = ctk.CTkToplevel(self)
        popup.title("Message" if not error else "Error")

        # Set as transient to ensure it stays on top of parent
        popup.transient(self)

        # Calculate center position
        popup_width = 320
        popup_height = 120

        # Get parent window position and size
        self.update_idletasks()  # Ensure geometry is up to date
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        # Calculate centered position
        x = parent_x + (parent_width - popup_width) // 2
        y = parent_y + (parent_height - popup_height) // 2

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        # Prevent resizing
        popup.resizable(False, False)

        # Message label
        label = ctk.CTkLabel(
            popup,
            text=message,
            wraplength=280,
            text_color=COLORS['danger'] if error else COLORS['success'],
            font=FONTS['body']
        )
        label.pack(pady=20)

        # OK button
        ok_btn = ctk.CTkButton(
            popup,
            text="OK",
            command=popup.destroy,
            **get_button_style('primary')
        )
        ok_btn.pack()
        ok_btn.focus_set()  # Set focus to OK button

        # Grab focus to make it modal
        popup.grab_set()

        # Auto-close after 3 seconds
        popup.after(3000, lambda: popup.destroy() if popup.winfo_exists() else None)

