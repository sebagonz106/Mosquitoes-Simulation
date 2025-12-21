"""
Presentation Layer - Compare View
==================================

View for comparing multiple simulation scenarios.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, Dict
import sys
import os
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing
from presentation.controllers.simulation_controller import SimulationController
from application import visualization
from application.dtos import ComparisonResult

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk


class CompareView(ttk.Frame):
    """
    View for comparing simulation scenarios.
    
    Features:
    - Load multiple simulation results
    - Side-by-side comparison
    - Comparative charts
    - Difference analysis
    """
    
    def __init__(
        self,
        parent,
        on_log: Optional[Callable[[str, str], None]] = None
    ):
        """
        Initialize compare view.
        
        Args:
            parent: Parent widget
            on_log: Callback for logging (message, level)
        """
        super().__init__(parent, style='TFrame')
        
        self.on_log = on_log
        self.controller = SimulationController()
        self.scenarios = {}  # Dict[scenario_name, SimulationConfig]
        self.scenario_results = {}  # Dict[scenario_name, result]
        self.comparison_canvas = None  # Current matplotlib canvas
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_XLARGE, pady=Spacing.PADDING_XLARGE)
        
        # Header
        self._create_header(container)
        
        # Scenario management
        self._create_scenario_panel(container)
        
        # Comparison area (placeholder)
        self._create_comparison_area(container)
        
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="⚖️ Comparación de Escenarios",
            style='Title.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Description
        desc = ttk.Label(
            header,
            text="Compare múltiples simulaciones para analizar diferentes estrategias de control",
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY
        )
        desc.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.PADDING_MEDIUM)
        
    def _create_scenario_panel(self, parent):
        """Create scenario management panel."""
        panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        panel.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Panel title
        title = ttk.Label(
            panel,
            text="Escenarios Cargados",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Scenario list frame
        list_frame = ttk.Frame(panel, style='TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
        self.scenario_listbox = tk.Listbox(
            list_frame,
            height=6,
            font=Fonts.DEFAULT,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY,
            selectforeground=Colors.SURFACE,
            yscrollcommand=scrollbar.set,
            relief='flat',
            borderwidth=0
        )
        scrollbar.config(command=self.scenario_listbox.yview)
        
        self.scenario_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.scenario_listbox.bind('<<ListboxSelect>>', self._on_scenario_selected)
        
        # Button frame
        btn_frame = ttk.Frame(panel, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=(Spacing.PADDING_MEDIUM, 0))
        
        # Load scenario button
        self.load_btn = ttk.Button(
            btn_frame,
            text="➕ Cargar Escenario",
            style='TButton',
            command=self._load_scenario
        )
        self.load_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        # Remove scenario button
        self.remove_btn = ttk.Button(
            btn_frame,
            text="➖ Eliminar Seleccionado",
            style='Secondary.TButton',
            command=self._remove_scenario,
            state='disabled'
        )
        self.remove_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        # Compare button
        self.compare_btn = ttk.Button(
            btn_frame,
            text="📊 Comparar",
            style='TButton',
            command=self._compare_scenarios,
            state='disabled'
        )
        self.compare_btn.pack(side=tk.RIGHT)
        
    def _create_comparison_area(self, parent):
        """Create comparison visualization area."""
        self.comparison_area = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        self.comparison_area.pack(fill=tk.BOTH, expand=True)
        self.comparison_area.configure(padding=Spacing.PADDING_LARGE)
        area = self.comparison_area
        
        # Area title
        title = ttk.Label(
            area,
            text="Resultados de Comparación",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Placeholder content
        placeholder = ttk.Frame(area, style='TFrame')
        placeholder.pack(fill=tk.BOTH, expand=True)
        
        # Center container
        center = ttk.Frame(placeholder, style='TFrame')
        center.pack(expand=True)
        
        # Icon
        icon = ttk.Label(
            center,
            text="📊",
            font=('Segoe UI', 64),
            style='TLabel'
        )
        icon.pack(pady=(0, Spacing.PADDING_LARGE))
        
        # Message
        message = ttk.Label(
            center,
            text="Cargue al menos dos escenarios para comenzar la comparación\n\n"
                 "Funcionalidades próximamente:\n"
                 "• Comparación de trayectorias poblacionales\n"
                 "• Análisis de diferencias estadísticas\n"
                 "• Gráficos comparativos lado a lado\n"
                 "• Métricas de efectividad de control\n"
                 "• Exportación de reportes comparativos",
            font=Fonts.DEFAULT,
            foreground=Colors.TEXT_SECONDARY,
            justify=tk.CENTER,
            style='TLabel'
        )
        message.pack()
        
    def _on_scenario_selected(self, event):
        """Handle scenario selection in listbox."""
        selection = self.scenario_listbox.curselection()
        if selection:
            self.remove_btn.config(state='normal')
        else:
            self.remove_btn.config(state='disabled')
    
    def _load_scenario(self):
        """Load a scenario from checkpoint file."""
        file_path = filedialog.askopenfilename(
            title="Seleccione un checkpoint de simulación",
            initialdir=str(self.controller.service.checkpoint_dir),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Load checkpoint
            config, result, sim_type = self.controller.service.load_checkpoint(file_path)
            
            # Generate scenario name from filename
            scenario_name = Path(file_path).stem
            
            # Check if already loaded
            if scenario_name in self.scenarios:
                if not messagebox.askyesno(
                    "Escenario Existente",
                    f"El escenario '{scenario_name}' ya está cargado.\n¿Desea reemplazarlo?"
                ):
                    return
            
            # Store scenario
            self.scenarios[scenario_name] = config
            self.scenario_results[scenario_name] = result
            
            # Update UI
            self._update_scenario_list()
            
            # Enable compare button if we have at least 2 scenarios
            if len(self.scenarios) >= 2:
                self.compare_btn.config(state='normal')
            
            if self.on_log:
                self.on_log(f"Escenario cargado: {scenario_name}", "success")
                
        except FileNotFoundError:
            messagebox.showerror("Error", f"Archivo no encontrado:\n{file_path}")
            if self.on_log:
                self.on_log("Error: Archivo no encontrado", "error")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando checkpoint:\n{str(e)}")
            if self.on_log:
                self.on_log(f"Error cargando checkpoint: {str(e)}", "error")
    
    def _update_scenario_list(self):
        """Update the scenario listbox."""
        # Clear listbox
        self.scenario_listbox.delete(0, tk.END)
        
        # Add all scenarios
        for scenario_name in self.scenarios.keys():
            self.scenario_listbox.insert(tk.END, scenario_name)
        
        # Show placeholder if empty
        if not self.scenarios:
            self.scenario_listbox.insert(tk.END, "No hay escenarios cargados")
            self.scenario_listbox.config(state='disabled')
        else:
            self.scenario_listbox.config(state='normal')
    
    def _remove_scenario(self):
        """Remove selected scenario."""
        selection = self.scenario_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        scenario_name = self.scenario_listbox.get(index)
        
        if messagebox.askyesno(
            "Eliminar Escenario",
            f"¿Está seguro que desea eliminar el escenario '{scenario_name}'?"
        ):
            # Remove from data
            if scenario_name in self.scenarios:
                del self.scenarios[scenario_name]
                del self.scenario_results[scenario_name]
            
            # Update UI
            self._update_scenario_list()
            
            # Disable compare button if less than 2 scenarios
            if len(self.scenarios) < 2:
                self.compare_btn.config(state='disabled')
            
            # Clear comparison area if any
            if self.comparison_canvas:
                self._clear_comparison_area()
            
            if self.on_log:
                self.on_log(f"Escenario eliminado: {scenario_name}", "info")
    
    def _compare_scenarios(self):
        """Execute comparison of loaded scenarios."""
        if len(self.scenarios) < 2:
            messagebox.showwarning(
                "Escenarios Insuficientes",
                "Debe cargar al menos 2 escenarios para realizar una comparación."
            )
            return
        
        try:
            if self.on_log:
                self.on_log(f"Comparando {len(self.scenarios)} escenarios...", "info")
            
            # Execute comparison using the service
            comparison = self.controller.service.compare_scenarios(
                self.scenarios,
                simulation_type='population'
            )
            
            # Show results
            self._show_comparison(comparison)
            
            if self.on_log:
                best = comparison.get_best_scenario('peak_population')
                worst = comparison.get_worst_scenario('peak_population')
                self.on_log(
                    f"Comparación completa. Mejor control: {best}, Peor control: {worst}",
                    "success"
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando comparación:\n{str(e)}")
            if self.on_log:
                self.on_log(f"Error en comparación: {str(e)}", "error")
    
    def _show_comparison(self, comparison: ComparisonResult):
        """Show comparison results with matplotlib charts."""
        # Clear previous comparison
        self._clear_comparison_area()
        
        # Create matplotlib figure
        try:
            fig = visualization.plot_scenario_comparison(
                comparison,
                metric='total_population',
                show=False,
                figsize=(12, 7)
            )
            
            # Embed in tkinter
            self.comparison_canvas = FigureCanvasTkAgg(fig, self.comparison_area)
            self.comparison_canvas.draw()
            self.comparison_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add navigation toolbar
            toolbar = NavigationToolbar2Tk(self.comparison_canvas, self.comparison_area)
            toolbar.update()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando gráficos:\n{str(e)}")
            if self.on_log:
                self.on_log(f"Error mostrando gráficos: {str(e)}", "error")
    
    def _clear_comparison_area(self):
        """Clear the comparison area."""
        for widget in self.comparison_area.winfo_children():
            widget.destroy()
        
        self.comparison_canvas = None
        
        # Restore placeholder
        placeholder = ttk.Frame(self.comparison_area, style='TFrame')
        placeholder.pack(fill=tk.BOTH, expand=True)
        
        center = ttk.Frame(placeholder, style='TFrame')
        center.pack(expand=True)
        
        icon = ttk.Label(
            center,
            text="📊",
            font=('Segoe UI', 64),
            style='TLabel'
        )
        icon.pack(pady=(0, Spacing.PADDING_LARGE))
        
        message = ttk.Label(
            center,
            text="Cargue al menos dos escenarios y haga clic en 'Comparar'\n\n"
                 "para ver las trayectorias poblacionales y análisis comparativo",
            font=Fonts.DEFAULT,
            foreground=Colors.TEXT_SECONDARY,
            justify=tk.CENTER,
            style='TLabel'
        )
        message.pack()
