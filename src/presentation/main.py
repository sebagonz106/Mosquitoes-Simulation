"""
Presentation Layer - Main Application Window
============================================

Main window with navigation and content area.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from presentation.styles.theme import Colors, Fonts, Spacing, configure_styles
from presentation.components import Sidebar, LogPanel
from presentation.views import HomeView, SimulationView, ResultsView, CompareView, CheckpointsView, SpeciesView
from presentation.controllers import SimulationController


class Application(tk.Tk):
    """
    Main application window.
    
    Features:
    - Sidebar navigation
    - Content area for views
    - Log panel at bottom
    - Resizable window
    - Proper styling
    """
    
    def __init__(self):
        """Initialize application window."""
        super().__init__()
        
        # Window configuration
        self.title("Mosquitoes Simulation - Sistema de Simulación Multi-Enfoque")
        self.geometry("1200x800")
        self.minsize(900, 600)
        self.configure(bg=Colors.BACKGROUND)
        
        # Apply theme styles
        configure_styles()
        
        # Current view tracking
        self.current_view_name = 'home'
        self.current_view_widget = None
        self.current_config = None  # Store current simulation config
        
        # Initialize controller
        self.simulation_controller = SimulationController()
        
        # Setup UI
        self._setup_ui()
        
        # Load initial view
        self._load_view('home')
        
    def _setup_ui(self):
        """Setup main UI structure."""
        # Main vertical paned window (top area | log panel)
        main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Top horizontal paned window (sidebar | content)
        top_paned = ttk.PanedWindow(main_paned, orient=tk.HORIZONTAL)
        main_paned.add(top_paned, weight=1)
        
        # Sidebar (resizable)
        self.sidebar = Sidebar(top_paned, width=220, on_navigate=self._on_navigate)
        top_paned.add(self.sidebar, weight=0)
        
        # Content area with scrollbar
        content_container = ttk.Frame(top_paned, style='TFrame')
        top_paned.add(content_container, weight=1)
        
        # Create canvas and scrollbar
        self.content_canvas = tk.Canvas(
            content_container,
            bg=Colors.BACKGROUND,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            content_container,
            orient='vertical',
            command=self.content_canvas.yview
        )
        
        # Content frame inside canvas
        self.content_frame = ttk.Frame(self.content_canvas, style='TFrame')
        
        # Configure canvas
        self.content_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create window in canvas
        self.canvas_window = self.content_canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor='nw'
        )
        
        # Bind canvas resize
        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.content_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Enable mousewheel scrolling
        self.content_canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        
        # Log panel (resizable at bottom)
        self.log_panel = LogPanel(main_paned, height=180)
        main_paned.add(self.log_panel, weight=0)
        
        # Log welcome message
        self.log_panel.log_success("Aplicación iniciada correctamente")
        self.log_panel.log_info("Navegue usando el menú lateral")
        
    def _on_navigate(self, view_name: str):
        """
        Handle navigation to a different view.
        
        Args:
            view_name: Name of view to navigate to
        """
        self.log_panel.log_info(f"Navegando a: {view_name}")
        self._load_view(view_name)
        
        # Update sidebar selection
        self.sidebar.set_active_view(view_name)
        
    def _load_view(self, view_name: str):
        """
        Load a view into the content area.
        
        Args:
            view_name: Name of view to load
        """
        # Remove current view if exists
        if self.current_view_widget:
            self.current_view_widget.destroy()
            self.current_view_widget = None
            
        # Create new view based on name
        if view_name == 'home':
            self.current_view_widget = HomeView(self.content_frame, on_navigate=self._on_navigate)
            
        elif view_name == 'simulation':
            # Simulation configuration view
            self.current_view_widget = SimulationView(
                self.content_frame,
                controller=self.simulation_controller,
                on_results=self._on_simulation_results,
                on_log=self._on_log_message
            )
            
        elif view_name == 'compare':
            # Compare scenarios view
            self.current_view_widget = CompareView(
                self.content_frame,
                on_log=self._on_log_message
            )
            
        elif view_name == 'checkpoints':
            # Checkpoints management view
            self.current_view_widget = CheckpointsView(
                self.content_frame,
                controller=self.simulation_controller,
                on_log=self._on_log_message,
                on_load_checkpoint=self._on_load_checkpoint
            )
            
        elif view_name == 'species':
            # Species information view
            self.current_view_widget = SpeciesView(
                self.content_frame,
                on_log=self._on_log_message
            )
            
        elif view_name == 'export':
            # Placeholder for export view
            self.current_view_widget = self._create_placeholder_view(
                "Exportar Resultados",
                "Vista de exportación de datos y gráficos.\n\n(En desarrollo)"
            )
            
        else:
            # Unknown view
            self.current_view_widget = self._create_placeholder_view(
                "Vista no encontrada",
                f"La vista '{view_name}' no está implementada."
            )
            self.log_panel.log_error(f"Vista desconocida: {view_name}")
            
        # Pack the new view
        if self.current_view_widget:
            self.current_view_widget.pack(fill=tk.BOTH, expand=True)
            
        # Update current view tracking
        self.current_view_name = view_name
        
        # Reset scroll position to top
        self.content_canvas.yview_moveto(0)
        
        # Log success
        self.log_panel.log_success(f"Vista cargada: {view_name}")
        
    def _create_placeholder_view(self, title: str, message: str) -> ttk.Frame:
        """
        Create a placeholder view for unimplemented sections.
        
        Args:
            title: View title
            message: Placeholder message
            
        Returns:
            Placeholder frame widget
        """
        # Main frame that fills the content area
        frame = ttk.Frame(self.content_frame, style='TFrame')
        
        # Add minimum height to ensure content is visible
        frame.configure(height=600)
        
        # Outer container with padding
        outer = ttk.Frame(frame, style='TFrame')
        outer.pack(fill=tk.BOTH, expand=True, padx=50, pady=100)
        
        # Center container
        container = ttk.Frame(outer, style='TFrame')
        container.pack(expand=True)
        
        # Icon
        icon = ttk.Label(
            container,
            text="🚧",
            font=('Segoe UI', 48),
            style='TLabel'
        )
        icon.pack(pady=(0, Spacing.PADDING_LARGE))
        
        # Title
        title_label = ttk.Label(
            container,
            text=title,
            font=('Segoe UI', 18, 'bold'),
            foreground=Colors.PRIMARY,
            style='TLabel'
        )
        title_label.pack()
        
        # Message
        message_label = ttk.Label(
            container,
            text=message,
            font=Fonts.DEFAULT,
            foreground=Colors.TEXT_SECONDARY,
            justify=tk.CENTER,
            style='TLabel'
        )
        message_label.pack(pady=(Spacing.PADDING_MEDIUM, 0))
        
        return frame
    
    def _on_simulation_results(self, result, config=None):
        """
        Handle simulation results.
        
        Args:
            result: Simulation result (PopulationResult, AgentResult, or HybridResult)
            config: SimulationConfig used for the simulation
        """
        # Store config for checkpoint saving
        self.current_config = config
        
        # Remove current view
        if self.current_view_widget:
            self.current_view_widget.destroy()
            self.current_view_widget = None
        
        # Create results view with controller and config
        self.current_view_widget = ResultsView(
            self.content_frame,
            result,
            controller=self.simulation_controller,
            config=config
        )
        self.current_view_widget.pack(fill=tk.BOTH, expand=True)
        
        # Reset scroll
        self.content_canvas.yview_moveto(0)
        
        # Log
        self.log_panel.log_success("Resultados cargados - use los botones para exportar")
        
    def _on_log_message(self, message: str, level: str):
        """
        Handle log messages from views.
        
        Args:
            message: Log message
            level: Log level ('info', 'success', 'error', 'warning')
        """
        if level == 'info':
            self.log_panel.log_info(message)
        elif level == 'success':
            self.log_panel.log_success(message)
        elif level == 'error':
            self.log_panel.log_error(message)
        elif level == 'warning':
            self.log_panel.log_warning(message)
    
    def _on_load_checkpoint(self, checkpoint_path: str):
        """
        Handle checkpoint loading.
        
        Args:
            checkpoint_path: Path to checkpoint file
        """
        try:
            # Load checkpoint
            config, result, sim_type = self.simulation_controller.service.load_checkpoint(checkpoint_path)
            
            # Show results
            self._on_simulation_results(result, config)
            
            self.log_panel.log_success(f"Checkpoint cargado correctamente")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error cargando checkpoint:\n{str(e)}")
            self.log_panel.log_error(f"Error cargando checkpoint: {str(e)}")
    
    def _on_frame_configure(self, event=None):
        """Reset scroll region when frame size changes."""
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox('all'))
        
    def _on_canvas_configure(self, event):
        """Resize content frame when canvas size changes."""
        # Make content frame same width as canvas
        canvas_width = event.width
        self.content_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        # Only scroll if content is larger than visible area
        if self.content_canvas.bbox('all'):
            self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the application."""
    app = Application()
    app.mainloop()


if __name__ == '__main__':
    main()
