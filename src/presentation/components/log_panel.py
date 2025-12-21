"""
Presentation Layer - Log Panel Component
=========================================

Scrollable log panel for displaying activity and errors.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Literal
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing


LogLevel = Literal['INFO', 'WARNING', 'ERROR', 'SUCCESS']


class LogPanel(ttk.Frame):
    """
    Log panel component for displaying activity messages.
    
    Features:
    - Scrollable text area
    - Color-coded messages by level
    - Timestamps
    - Auto-scroll to bottom
    - Clear log button
    """
    
    def __init__(self, parent, height=150):
        """
        Initialize log panel.
        
        Args:
            parent: Parent widget
            height: Height of log panel in pixels
        """
        super().__init__(parent, style='TFrame')
        
        self.height = height
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Header with title and clear button
        header = ttk.Frame(self, style='TFrame')
        header.pack(fill=tk.X, padx=Spacing.PADDING_MEDIUM, pady=(Spacing.PADDING_SMALL, 0))
        
        title = ttk.Label(
            header,
            text="Log de Actividad",
            style='Heading.TLabel'
        )
        title.pack(side=tk.LEFT)
        
        clear_btn = ttk.Button(
            header,
            text="Limpiar",
            command=self.clear_log,
            width=10
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # Separator
        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill=tk.X, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(self, style='TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.text_widget = tk.Text(
            text_frame,
            height=self.height // 20,  # Approximate line height
            wrap=tk.WORD,
            font=Fonts.MONO,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            yscrollcommand=scrollbar.set,
            relief='solid',
            borderwidth=1,
            padx=Spacing.PADDING_SMALL,
            pady=Spacing.PADDING_SMALL,
            state='disabled'  # Read-only
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.text_widget.yview)
        
        # Configure text tags for colored messages
        self.text_widget.tag_config('INFO', foreground=Colors.INFO)
        self.text_widget.tag_config('SUCCESS', foreground=Colors.SUCCESS)
        self.text_widget.tag_config('WARNING', foreground=Colors.WARNING)
        self.text_widget.tag_config('ERROR', foreground=Colors.ERROR)
        self.text_widget.tag_config('TIMESTAMP', foreground=Colors.TEXT_SECONDARY)
        
        # Add welcome message
        self.log("Sistema iniciado", level='SUCCESS')
        
    def log(self, message: str, level: LogLevel = 'INFO'):
        """
        Add a log message.
        
        Args:
            message: Message text
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        # Get current timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Format message
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        # Enable editing temporarily
        self.text_widget.config(state='normal')
        
        # Insert timestamp
        self.text_widget.insert(tk.END, f"[{timestamp}] ", 'TIMESTAMP')
        
        # Insert level and message
        self.text_widget.insert(tk.END, f"[{level}] {message}\n", level)
        
        # Disable editing
        self.text_widget.config(state='disabled')
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
        
    def clear_log(self):
        """Clear all log messages."""
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.config(state='disabled')
        self.log("Log limpiado", level='INFO')
        
    def log_info(self, message: str):
        """Log info message."""
        self.log(message, level='INFO')
        
    def log_success(self, message: str):
        """Log success message."""
        self.log(message, level='SUCCESS')
        
    def log_warning(self, message: str):
        """Log warning message."""
        self.log(message, level='WARNING')
        
    def log_error(self, message: str):
        """Log error message."""
        self.log(message, level='ERROR')


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Test the log panel
    from presentation.styles.theme import configure_styles
    
    root = tk.Tk()
    root.title("Test Log Panel")
    root.geometry("600x300")
    root.configure(bg=Colors.BACKGROUND)
    
    configure_styles()
    
    log_panel = LogPanel(root, height=250)
    log_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add test messages
    log_panel.log_info("Cargando configuración...")
    log_panel.log_success("Configuración cargada correctamente")
    log_panel.log_warning("Advertencia: Temperatura fuera del rango óptimo")
    log_panel.log_error("Error: No se pudo cargar checkpoint")
    log_panel.log_info("Iniciando simulación...")
    
    root.mainloop()
