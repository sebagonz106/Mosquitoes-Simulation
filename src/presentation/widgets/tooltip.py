"""
Tooltip Widget Module
=====================

Custom tooltip implementation for tkinter widgets.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class ToolTip:
    """
    Custom tooltip widget that displays help text on hover.
    
    Features:
    - Shows on mouse hover
    - Hides on mouse leave
    - Configurable delay
    - Multiline text support
    - Styled background
    """
    
    def __init__(
        self,
        widget: tk.Widget,
        text: str,
        delay: int = 500,
        wrap_length: int = 300
    ):
        """
        Initialize tooltip.
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text (supports newlines)
            delay: Delay in milliseconds before showing
            wrap_length: Maximum width before wrapping text
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window: Optional[tk.Toplevel] = None
        self.schedule_id: Optional[str] = None
        
        # Bind hover events
        self.widget.bind('<Enter>', self._on_enter)
        self.widget.bind('<Leave>', self._on_leave)
        self.widget.bind('<Button>', self._on_leave)  # Hide on click
        
    def _on_enter(self, event=None):
        """Handle mouse enter event."""
        self._cancel_schedule()
        self.schedule_id = self.widget.after(self.delay, self._show)
        
    def _on_leave(self, event=None):
        """Handle mouse leave event."""
        self._cancel_schedule()
        self._hide()
        
    def _cancel_schedule(self):
        """Cancel scheduled tooltip display."""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None
            
    def _show(self):
        """Display tooltip window."""
        if self.tooltip_window:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Make window stay on top
        self.tooltip_window.attributes('-topmost', True)
        
        # Configure tooltip appearance
        frame = ttk.Frame(
            self.tooltip_window,
            relief='solid',
            borderwidth=1,
            style='Tooltip.TFrame'
        )
        frame.pack()
        
        # Add text label
        label = ttk.Label(
            frame,
            text=self.text,
            justify=tk.LEFT,
            wraplength=self.wrap_length,
            style='Tooltip.TLabel',
            padding=(8, 6)
        )
        label.pack()
        
    def _hide(self):
        """Hide tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
    def update_text(self, text: str):
        """
        Update tooltip text.
        
        Args:
            text: New tooltip text
        """
        self.text = text
        if self.tooltip_window:
            # If tooltip is currently shown, refresh it
            self._hide()
            self._show()


def create_tooltip(widget: tk.Widget, text: str, **kwargs) -> ToolTip:
    """
    Convenience function to create and attach tooltip to widget.
    
    Args:
        widget: Widget to attach tooltip to
        text: Tooltip text
        **kwargs: Additional arguments for ToolTip constructor
    
    Returns:
        ToolTip instance
    
    Example:
        >>> entry = ttk.Entry(parent)
        >>> create_tooltip(entry, "Enter a value between 0 and 100")
    """
    return ToolTip(widget, text, **kwargs)
