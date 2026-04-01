"""GUI styles and theme configuration."""

import customtkinter as ctk
from tkinter import ttk, font as tkfont


# Color scheme - Modern gray-blue theme with better contrast
COLORS = {
    'bg_dark': '#3a3f4b',      # Main background - gray-blue
    'bg_light': '#4a505c',     # Lighter background
    'bg_lighter': '#5a616d',   # Even lighter for headers
    'fg_dark': '#ffffff',      # Primary text - pure white
    'fg_light': '#e8eaed',     # Secondary text - off-white
    'fg_medium': '#b8bbbf',    # Tertiary text - light gray
    'accent': '#5dade2',       # Accent - bright blue
    'accent_hover': '#6fc3f5', # Accent hover - lighter blue
    'success': '#4ade80',      # Success - bright green
    'warning': '#fbbf24',      # Warning - amber
    'danger': '#f87171',       # Danger - coral red
    'border': '#6b7280',       # Border - medium gray
    'row_odd': '#404650',      # Odd row - medium gray-blue
    'row_even': '#363c48',     # Even row - darker gray-blue
    'selection': '#5dade2'     # Selection - bright blue
}


# Font configuration - increased sizes for better readability
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'heading': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 12),
    'code': ('Consolas', 11),
    'code_large': ('Consolas', 14),  # Larger font for detail views
    'small': ('Segoe UI', 10)
}


def configure_theme():
    """Configure CustomTkinter theme and appearance."""
    # Set appearance mode (dark/light)
    ctk.set_appearance_mode('dark')

    # Set default color theme
    ctk.set_default_color_theme('dark-blue')


def get_treeview_style() -> dict:
    """Get styling options for ttk.Treeview widgets."""
    return {
        'show': 'tree headings',
        'selectmode': 'browse',
    }


def configure_treeview_style():
    """Configure ttk.Treeview style for better visibility."""
    style = ttk.Style()

    # Configure Treeview widget
    style.theme_use('clam')  # Use clam theme for better customization

    # Treeview background and foreground
    style.configure(
        'Treeview',
        background=COLORS['row_odd'],
        foreground=COLORS['fg_dark'],
        fieldbackground=COLORS['row_odd'],
        font=FONTS['body'],
        rowheight=28  # Increase row height for better readability
    )

    # Treeview heading
    style.configure(
        'Treeview.Heading',
        background=COLORS['bg_lighter'],
        foreground=COLORS['fg_dark'],
        font=FONTS['heading'],
        relief='flat'
    )

    # Heading hover effect
    style.map(
        'Treeview.Heading',
        background=[('active', COLORS['accent'])],
        foreground=[('active', COLORS['fg_dark'])]
    )

    # Selected row
    style.map(
        'Treeview',
        background=[('selected', COLORS['selection'])],
        foreground=[('selected', COLORS['fg_dark'])]
    )

    # Scrollbar style
    style.configure(
        'Vertical.TScrollbar',
        background=COLORS['bg_light'],
        troughcolor=COLORS['bg_dark'],
        arrowcolor=COLORS['fg_light']
    )

    style.configure(
        'Horizontal.TScrollbar',
        background=COLORS['bg_light'],
        troughcolor=COLORS['bg_dark'],
        arrowcolor=COLORS['fg_light']
    )

    # Combobox style
    style.configure(
        'TCombobox',
        background=COLORS['bg_light'],
        foreground=COLORS['fg_dark'],
        fieldbackground=COLORS['bg_light'],
        font=FONTS['body'],
        arrowcolor=COLORS['fg_light']
    )

    style.map(
        'TCombobox',
        background=[('active', COLORS['accent'])],
        foreground=[('active', COLORS['fg_dark'])]
    )


def get_table_columns_style() -> dict:
    """Get styling for table columns."""
    return {
        'anchor': 'w',
        'stretch': True
    }


def apply_window_icon(window):
    """Apply window icon if available."""
    try:
        # Try to set window icon (placeholder for now)
        pass
    except Exception:
        pass


def get_button_style(style_type: str = 'primary') -> dict:
    """
    Get button styling based on type.

    Args:
        style_type: 'primary', 'danger', 'success', or 'warning'

    Returns:
        Dictionary of button styling options
    """
    styles = {
        'primary': {
            'fg_color': COLORS['accent'],
            'hover_color': COLORS['accent_hover'],
            'text_color': COLORS['fg_dark']
        },
        'danger': {
            'fg_color': COLORS['danger'],
            'hover_color': '#c0392b',
            'text_color': COLORS['fg_dark']
        },
        'success': {
            'fg_color': COLORS['success'],
            'hover_color': '#27ae60',
            'text_color': COLORS['fg_dark']
        },
        'warning': {
            'fg_color': COLORS['warning'],
            'hover_color': '#e67e22',
            'text_color': COLORS['fg_dark']
        }
    }

    return styles.get(style_type, styles['primary'])


def get_label_style(style_type: str = 'normal') -> dict:
    """
    Get label styling based on type.

    Args:
        style_type: 'title', 'heading', or 'normal'

    Returns:
        Dictionary of label styling options
    """
    styles = {
        'title': {
            'font': FONTS['title'],
            'text_color': COLORS['fg_dark']
        },
        'heading': {
            'font': FONTS['heading'],
            'text_color': COLORS['fg_dark']
        },
        'normal': {
            'font': FONTS['body'],
            'text_color': COLORS['fg_light']
        }
    }

    return styles.get(style_type, styles['normal'])


def get_entry_style() -> dict:
    """Get entry widget styling."""
    return {
        'placeholder_text_color': COLORS['fg_light'],
        'text_color': COLORS['fg_dark'],
        'fg_color': COLORS['bg_light'],
        'border_color': COLORS['border']
    }
