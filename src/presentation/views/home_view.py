"""
Presentation Layer - Home View
==============================

Welcome screen with quick access buttons.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing


class HomeView(ttk.Frame):
    """
    Home/welcome view.
    
    Features:
    - Welcome message
    - Quick access buttons
    - Project description
    - Statistics cards (placeholder)
    """
    
    def __init__(self, parent, on_navigate: Optional[Callable[[str], None]] = None):
        """
        Initialize home view.
        
        Args:
            parent: Parent widget
            on_navigate: Callback for navigation
        """
        super().__init__(parent, style='TFrame')
        
        self.on_navigate = on_navigate
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_XLARGE, pady=Spacing.PADDING_XLARGE)
        
        # Welcome header
        self._create_header(container)
        
        # Quick access section
        self._create_quick_access(container)
        
        # Information section
        self._create_info_section(container)
        
    def _create_header(self, parent):
        """Create welcome header."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.PADDING_XLARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="🦟 Simulador de Mosquitos",
            style='Title.TLabel',
            font=('Segoe UI', 24, 'bold'),
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Subtitle
        subtitle = ttk.Label(
            header,
            text="Sistema de simulación multi-enfoque para poblaciones de mosquitos",
            style='TLabel',
            font=Fonts.DEFAULT,
            foreground=Colors.TEXT_SECONDARY
        )
        subtitle.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.PADDING_LARGE)
        
    def _create_quick_access(self, parent):
        """Create quick access buttons section."""
        section = ttk.Frame(parent, style='TFrame')
        section.pack(fill=tk.X, pady=(0, Spacing.PADDING_XLARGE))
        
        # Section title
        title = ttk.Label(
            section,
            text="Acceso Rápido",
            style='Heading.TLabel'
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Button grid
        button_frame = ttk.Frame(section, style='TFrame')
        button_frame.pack(fill=tk.X)
        
        # Quick access options
        quick_actions = [
            {
                'view': 'simulation',
                'icon': '▶️',
                'title': 'Nueva Simulación',
                'description': 'Ejecutar simulación con parámetros personalizados'
            },
            {
                'view': 'compare',
                'icon': '📊',
                'title': 'Comparar Escenarios',
                'description': 'Analizar y comparar múltiples simulaciones'
            },
            {
                'view': 'checkpoints',
                'icon': '💾',
                'title': 'Checkpoints',
                'description': 'Gestionar puntos de guardado de simulaciones'
            }
        ]
        
        for i, action in enumerate(quick_actions):
            card = self._create_action_card(button_frame, action)
            card.grid(row=0, column=i, padx=Spacing.PADDING_MEDIUM, sticky='nsew')
            
        # Configure grid weights for equal distribution
        for i in range(len(quick_actions)):
            button_frame.columnconfigure(i, weight=1)
            
    def _create_action_card(self, parent, action_data: dict) -> ttk.Frame:
        """
        Create action card widget.
        
        Args:
            parent: Parent widget
            action_data: Dictionary with 'view', 'icon', 'title', 'description'
            
        Returns:
            Card frame widget
        """
        # Card frame
        card = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        card.configure(padding=Spacing.PADDING_LARGE)
        
        # Icon
        icon_label = ttk.Label(
            card,
            text=action_data['icon'],
            font=('Segoe UI', 32),
            style='TLabel'
        )
        icon_label.pack(pady=(0, Spacing.PADDING_MEDIUM))
        
        # Title
        title_label = ttk.Label(
            card,
            text=action_data['title'],
            style='Heading.TLabel',
            justify=tk.CENTER
        )
        title_label.pack()
        
        # Description
        desc_label = ttk.Label(
            card,
            text=action_data['description'],
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY,
            wraplength=200,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(Spacing.PADDING_SMALL, Spacing.PADDING_MEDIUM))
        
        # Button
        btn = ttk.Button(
            card,
            text="Abrir",
            style='Primary.TButton',
            command=lambda: self._on_navigate_click(action_data['view'])
        )
        btn.pack()
        
        # Hover effect
        card.bind('<Enter>', lambda e: card.configure(relief='raised'))
        card.bind('<Leave>', lambda e: card.configure(relief='solid'))
        
        return card
        
    def _create_info_section(self, parent):
        """Create information section."""
        section = ttk.Frame(parent, style='TFrame')
        section.pack(fill=tk.BOTH, expand=True)
        
        # Section title
        title = ttk.Label(
            section,
            text="Sobre el Proyecto",
            style='Heading.TLabel'
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Info grid
        info_frame = ttk.Frame(section, style='TFrame')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info cards
        info_items = [
            {
                'title': '3 Tipos de Simulación',
                'description': 'Basada en agentes (ABM), parámetros poblacionales, e híbrida'
            },
            {
                'title': '2 Especies Modeladas',
                'description': 'Aedes aegypti (vector) y Toxorhynchites (depredador)'
            },
            {
                'title': 'Control Biológico',
                'description': 'Análisis de estrategias de depredación y competencia'
            },
            {
                'title': 'Visualización Avanzada',
                'description': 'Gráficos, tablas y métricas detalladas de resultados'
            }
        ]
        
        for i, info in enumerate(info_items):
            row = i // 2
            col = i % 2
            
            card = self._create_info_card(info_frame, info)
            card.grid(row=row, column=col, padx=Spacing.PADDING_MEDIUM, 
                     pady=Spacing.PADDING_MEDIUM, sticky='nsew')
                     
        # Configure grid
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        info_frame.rowconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)
        
    def _create_info_card(self, parent, info_data: dict) -> ttk.Frame:
        """
        Create info card widget.
        
        Args:
            parent: Parent widget
            info_data: Dictionary with 'title' and 'description'
            
        Returns:
            Card frame widget
        """
        card = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        card.configure(padding=Spacing.PADDING_LARGE)
        
        # Title
        title = ttk.Label(
            card,
            text=info_data['title'],
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Description
        desc = ttk.Label(
            card,
            text=info_data['description'],
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY,
            wraplength=280,
            justify=tk.LEFT
        )
        desc.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        return card
        
    def _on_navigate_click(self, view_name: str):
        """Handle navigation button click."""
        if self.on_navigate:
            self.on_navigate(view_name)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Test the home view
    from presentation.styles.theme import configure_styles
    
    root = tk.Tk()
    root.title("Test Home View")
    root.geometry("900x700")
    root.configure(bg=Colors.BACKGROUND)
    
    configure_styles()
    
    def on_nav(view_name):
        print(f"Navegando a: {view_name}")
    
    home = HomeView(root, on_navigate=on_nav)
    home.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
