"""
Presentation Layer - Sidebar Component
======================================

Navigation sidebar with menu options.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing


class Sidebar(ttk.Frame):
    """
    Sidebar navigation component.
    
    Features:
    - Navigation buttons for different views
    - Active view indicator
    - Application title/logo
    - Consistent styling
    """
    
    def __init__(self, parent, width=200, on_navigate: Optional[Callable[[str], None]] = None):
        """
        Initialize sidebar.
        
        Args:
            parent: Parent widget
            width: Width of sidebar in pixels
            on_navigate: Callback function called when navigation button is clicked.
                        Receives view name as parameter.
        """
        super().__init__(parent, style='Sidebar.TFrame', width=width)
        
        self.width = width
        self.on_navigate = on_navigate
        self.current_view = 'home'
        self.nav_buttons = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # App title/logo section
        header = ttk.Frame(self, style='Sidebar.TFrame')
        header.pack(fill=tk.X, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_LARGE)
        
        title = ttk.Label(
            header,
            text="🦟 Mosquitoes\nSimulation",
            style='SidebarTitle.TLabel',
            justify=tk.CENTER
        )
        title.pack()
        
        # Separator
        sep = ttk.Separator(self, orient='horizontal')
        sep.pack(fill=tk.X, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self, style='Sidebar.TFrame')
        nav_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_SMALL)
        
        # Navigation options
        nav_options = [
            ('home', '🏠 Inicio', 'Vista de inicio'),
            ('simulation', '▶️ Simulación', 'Ejecutar simulaciones'),
            ('compare', '📊 Comparar', 'Comparar escenarios'),
            ('checkpoints', '💾 Checkpoints', 'Gestionar checkpoints'),
            ('species', '🦟 Especies', 'Información de especies'),
            ('export', '📁 Exportar', 'Exportar resultados'),
        ]
        
        for view_name, button_text, tooltip in nav_options:
            btn = self._create_nav_button(nav_frame, view_name, button_text, tooltip)
            btn.pack(fill=tk.X, pady=Spacing.PADDING_SMALL)
            self.nav_buttons[view_name] = btn
            
        # Set initial active button
        self._update_active_button('home')
        
        # Footer with version/info
        footer = ttk.Frame(self, style='Sidebar.TFrame')
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)
        
        version_label = ttk.Label(
            footer,
            text="v1.0.0",
            style='SidebarFooter.TLabel',
            justify=tk.CENTER
        )
        version_label.pack()
        
    def _create_nav_button(self, parent, view_name: str, text: str, tooltip: str) -> ttk.Button:
        """
        Create navigation button.
        
        Args:
            parent: Parent widget
            view_name: Internal view name
            text: Button text
            tooltip: Tooltip text
            
        Returns:
            Created button widget
        """
        btn = ttk.Button(
            parent,
            text=text,
            style='Sidebar.TButton',
            command=lambda: self._on_button_click(view_name)
        )
        
        # Add tooltip (simple implementation)
        # In production, use a proper tooltip library
        btn.bind('<Enter>', lambda e: self._show_tooltip(btn, tooltip))
        btn.bind('<Leave>', lambda e: self._hide_tooltip())
        
        return btn
        
    def _on_button_click(self, view_name: str):
        """Handle navigation button click."""
        if view_name != self.current_view:
            self.current_view = view_name
            self._update_active_button(view_name)
            
            if self.on_navigate:
                self.on_navigate(view_name)
                
    def _update_active_button(self, active_view: str):
        """Update button styles to show active view."""
        for view_name, btn in self.nav_buttons.items():
            if view_name == active_view:
                btn.configure(style='SidebarActive.TButton')
            else:
                btn.configure(style='Sidebar.TButton')
                
    def _show_tooltip(self, widget, text: str):
        """Show tooltip (placeholder implementation)."""
        # TODO: Implement proper tooltip
        pass
        
    def _hide_tooltip(self):
        """Hide tooltip."""
        # TODO: Implement proper tooltip
        pass
        
    def set_active_view(self, view_name: str):
        """
        Programmatically set active view.
        
        Args:
            view_name: Name of view to activate
        """
        if view_name in self.nav_buttons:
            self.current_view = view_name
            self._update_active_button(view_name)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Test the sidebar
    from presentation.styles.theme import configure_styles
    
    root = tk.Tk()
    root.title("Test Sidebar")
    root.geometry("800x600")
    root.configure(bg=Colors.BACKGROUND)
    
    configure_styles()
    
    # Content area to show navigation
    content = ttk.Label(
        root,
        text="Selecciona una opción del menú",
        style='TLabel',
        font=Fonts.HEADING
    )
    content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def on_nav(view_name):
        content.config(text=f"Vista activa: {view_name}")
        print(f"Navegando a: {view_name}")
    
    sidebar = Sidebar(root, width=200, on_navigate=on_nav)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    
    root.mainloop()
