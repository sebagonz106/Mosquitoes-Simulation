"""
Presentation Layer - Visual Theme
==================================

Color palette, fonts, and styling constants for the application.
Theme: Light, clean, scientific/professional.
"""

import tkinter as tk
from tkinter import ttk
from typing import Literal
# ============================================================================
# COLOR PALETTE (Light Theme)
# ============================================================================

class Colors:
    """Application color scheme - Light theme."""
    
    # Primary colors
    PRIMARY = "#2E7D32"          # Green - main accent
    PRIMARY_DARK = "#1B5E20"     # Darker green
    PRIMARY_LIGHT = "#4CAF50"    # Lighter green
    
    # Secondary colors
    SECONDARY = "#1976D2"        # Blue - secondary accent
    SECONDARY_DARK = "#0D47A1"   # Darker blue
    SECONDARY_LIGHT = "#42A5F5"  # Lighter blue
    
    # Neutral colors
    BACKGROUND = "#FAFAFA"       # Very light gray - main background
    SURFACE = "#FFFFFF"          # White - cards, panels
    SURFACE_VARIANT = "#F5F5F5"  # Light gray - alternate surfaces
    
    # Text colors
    TEXT_PRIMARY = "#212121"     # Almost black - main text
    TEXT_SECONDARY = "#757575"   # Gray - secondary text
    TEXT_DISABLED = "#BDBDBD"    # Light gray - disabled text
    
    # Border colors
    BORDER = "#E0E0E0"           # Light gray border
    BORDER_DARK = "#BDBDBD"      # Darker border for emphasis
    
    # Status colors
    SUCCESS = "#4CAF50"          # Green - success messages
    WARNING = "#FF9800"          # Orange - warnings
    ERROR = "#F44336"            # Red - errors
    INFO = "#2196F3"             # Blue - information
    
    # Sidebar
    SIDEBAR_BG = "#EEEEEE"       # Light gray sidebar
    SIDEBAR_SELECTED = "#E8F5E9" # Very light green - selected item
    SIDEBAR_HOVER = "#F5F5F5"    # Lighter gray - hover state


# ============================================================================
# TYPOGRAPHY
# ============================================================================

class Fonts:
    """Font definitions for the application."""
    
    # Font families
    FAMILY = "Segoe UI"          # Windows default
    FAMILY_MONO = "Consolas"     # Monospace for code/logs
    
    # Font sizes
    SIZE_TITLE = 18              # Main titles
    SIZE_HEADING = 14            # Section headings
    SIZE_BODY = 11               # Normal text
    SIZE_SMALL = 9               # Small text (labels, hints)
    SIZE_BUTTON = 10             # Button text
    
    # Font weights
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"
    
    # Prebuilt font tuples
    TITLE = (FAMILY, SIZE_TITLE, WEIGHT_BOLD)
    HEADING = (FAMILY, SIZE_HEADING, WEIGHT_BOLD)
    DEFAULT = (FAMILY, SIZE_BODY, WEIGHT_NORMAL)  # Default font
    BODY = (FAMILY, SIZE_BODY, WEIGHT_NORMAL)
    BODY_BOLD = (FAMILY, SIZE_BODY, WEIGHT_BOLD)
    SMALL = (FAMILY, SIZE_SMALL, WEIGHT_NORMAL)
    BUTTON = (FAMILY, SIZE_BUTTON, WEIGHT_NORMAL)
    MONO = (FAMILY_MONO, SIZE_BODY, WEIGHT_NORMAL)


# ============================================================================
# SPACING & DIMENSIONS
# ============================================================================

class Spacing:
    """Spacing constants for consistent layout."""
    
    # Padding
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    PADDING_XLARGE = 30
    
    # Margins
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 10
    MARGIN_LARGE = 15
    
    # Widget dimensions
    SIDEBAR_WIDTH = 180
    LOG_HEIGHT = 150
    BUTTON_HEIGHT = 35
    INPUT_HEIGHT = 30
    
    # Border radius (for rounded corners)
    RADIUS = 5


# ============================================================================
# WIDGET STYLES
# ============================================================================

def configure_styles():
    """
    Configure ttk styles for themed widgets.
    
    Call this once at application startup.
    """
    style = ttk.Style()
    
    # Use 'clam' theme as base (clean and customizable)
    style.theme_use('clam')
    
    # ========================================
    # Button Styles
    # ========================================
    
    # Primary button (green accent)
    style.configure(
        'Primary.TButton',
        background=Colors.PRIMARY,
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        font=Fonts.BUTTON,
        padding=(15, 8)
    )
    style.map(
        'Primary.TButton',
        background=[('active', Colors.PRIMARY_DARK), ('pressed', Colors.PRIMARY_DARK)]
    )
    
    # Secondary button (blue accent)
    style.configure(
        'Secondary.TButton',
        background=Colors.SECONDARY,
        foreground='white',
        borderwidth=0,
        focuscolor='none',
        font=Fonts.BUTTON,
        padding=(15, 8)
    )
    style.map(
        'Secondary.TButton',
        background=[('active', Colors.SECONDARY_DARK), ('pressed', Colors.SECONDARY_DARK)]
    )
    
    # Default button (neutral)
    style.configure(
        'TButton',
        background=Colors.SURFACE,
        foreground=Colors.TEXT_PRIMARY,
        borderwidth=1,
        focuscolor='none',
        font=Fonts.BUTTON,
        padding=(12, 8)
    )
    style.map(
        'TButton',
        background=[('active', Colors.SURFACE_VARIANT), ('pressed', Colors.SURFACE_VARIANT)]
    )
    
    # Sidebar button (navigation)
    style.configure(
        'Sidebar.TButton',
        background=Colors.SIDEBAR_BG,
        foreground=Colors.TEXT_PRIMARY,
        borderwidth=0,
        focuscolor='none',
        font=Fonts.BUTTON,
        padding=(15, 10),
        anchor='w'
    )
    style.map(
        'Sidebar.TButton',
        background=[('active', Colors.SIDEBAR_HOVER)]
    )
    
    # Active sidebar button
    style.configure(
        'SidebarActive.TButton',
        background=Colors.SIDEBAR_SELECTED,
        foreground=Colors.PRIMARY,
        borderwidth=0,
        focuscolor='none',
        font=Fonts.BODY_BOLD,
        padding=(15, 10),
        anchor='w'
    )
    style.map(
        'SidebarActive.TButton',
        background=[('active', Colors.SIDEBAR_SELECTED)]
    )
    
    # ========================================
    # Frame Styles
    # ========================================
    
    style.configure('TFrame', background=Colors.BACKGROUND)
    style.configure('Card.TFrame', background=Colors.SURFACE, relief='flat')
    style.configure('Sidebar.TFrame', background=Colors.SIDEBAR_BG)
    
    # ========================================
    # Label Styles
    # ========================================
    
    style.configure(
        'TLabel',
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.BODY
    )
    
    style.configure(
        'Title.TLabel',
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.TITLE
    )
    
    style.configure(
        'Heading.TLabel',
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT_PRIMARY,
        font=Fonts.HEADING
    )
    
    style.configure(
        'Secondary.TLabel',
        background=Colors.BACKGROUND,
        foreground=Colors.TEXT_SECONDARY,
        font=Fonts.SMALL
    )
    
    # Sidebar labels
    style.configure(
        'SidebarTitle.TLabel',
        background=Colors.SIDEBAR_BG,
        foreground=Colors.PRIMARY,
        font=Fonts.HEADING
    )
    
    style.configure(
        'SidebarFooter.TLabel',
        background=Colors.SIDEBAR_BG,
        foreground=Colors.TEXT_SECONDARY,
        font=Fonts.SMALL
    )
    
    # ========================================
    # Entry/Input Styles
    # ========================================
    
    style.configure(
        'TEntry',
        fieldbackground=Colors.SURFACE,
        foreground=Colors.TEXT_PRIMARY,
        borderwidth=1,
        relief='solid',
        font=Fonts.BODY
    )
    
    # ========================================
    # Combobox Styles
    # ========================================
    
    style.configure(
        'TCombobox',
        fieldbackground=Colors.SURFACE,
        foreground=Colors.TEXT_PRIMARY,
        background=Colors.SURFACE,
        borderwidth=1,
        font=Fonts.BODY
    )
    
    # ========================================
    # Treeview (Table) Styles
    # ========================================
    
    style.configure(
        'Treeview',
        background=Colors.SURFACE,
        foreground=Colors.TEXT_PRIMARY,
        fieldbackground=Colors.SURFACE,
        borderwidth=1,
        relief='solid',
        font=Fonts.BODY
    )
    
    style.configure(
        'Treeview.Heading',
        background=Colors.SURFACE_VARIANT,
        foreground=Colors.TEXT_PRIMARY,
        borderwidth=1,
        relief='flat',
        font=Fonts.BODY_BOLD
    )
    
    style.map(
        'Treeview',
        background=[('selected', Colors.PRIMARY_LIGHT)],
        foreground=[('selected', 'white')]
    )
    
    # ========================================
    # Separator Styles
    # ========================================
    
    style.configure('TSeparator', background=Colors.BORDER)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card_style(parent, title, value, unit=""):
    """
    Create a styled metric card frame.
    
    Args:
        parent: Parent widget
        title: Metric title
        value: Metric value
        unit: Optional unit string
        
    Returns:
        Frame containing the styled metric
    """
    frame = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
    frame.configure(padding=Spacing.PADDING_MEDIUM)
    
    # Title label
    title_label = ttk.Label(
        frame,
        text=title,
        style='Secondary.TLabel',
        background=Colors.SURFACE
    )
    title_label.pack(pady=(0, Spacing.PADDING_SMALL))
    
    # Value label
    value_text = f"{value} {unit}".strip()
    value_label = ttk.Label(
        frame,
        text=value_text,
        font=(Fonts.FAMILY, 20, Fonts.WEIGHT_BOLD),
        foreground=Colors.PRIMARY,
        background=Colors.SURFACE
    )
    value_label.pack()
    
    return frame


def apply_hover_effect(widget, enter_color, leave_color):
    """
    Apply hover effect to a widget.
    
    Args:
        widget: Widget to apply effect to
        enter_color: Color when mouse enters
        leave_color: Color when mouse leaves
    """
    def on_enter(e):
        widget['background'] = enter_color
    
    def on_leave(e):
        widget['background'] = leave_color
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


def create_separator(parent, orient: Literal['horizontal', 'vertical'] = 'horizontal'):
    """
    Create a visual separator line.
    
    Args:
        parent: Parent widget
        orient: 'horizontal' or 'vertical'
        
    Returns:
        Separator widget
    """
    return ttk.Separator(parent, orient=orient)


# ============================================================================
# ICONS (Unicode characters as placeholders)
# ============================================================================

class Icons:
    """Unicode icons for UI elements."""
    
    HOME = "🏠"
    PLAY = "▶"
    CHART = "📊"
    SAVE = "💾"
    EXPORT = "📤"
    INFO = "ℹ️"
    SETTINGS = "⚙️"
    FOLDER = "📁"
    DELETE = "🗑"
    REFRESH = "🔄"
    CHECK = "✓"
    CROSS = "✗"
    WARNING = "⚠️"
    MOSQUITO = "🦟"
