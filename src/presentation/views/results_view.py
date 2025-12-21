"""
Presentation Layer - Results View
==================================

View for displaying simulation results with charts and statistics.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Union
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing
from application.dtos import PopulationResult, AgentResult, HybridResult
from application import visualization

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure


class ResultsView(ttk.Frame):
    """
    View for displaying simulation results.
    
    Features:
    - Population trajectory charts
    - Statistics summary cards
    - Data table
    - Export options
    """
    
    def __init__(
        self,
        parent,
        result: Union[PopulationResult, AgentResult, HybridResult],
        controller=None,
        config=None
    ):
        """
        Initialize results view.
        
        Args:
            parent: Parent widget
            result: Simulation result to display
            controller: SimulationController for saving checkpoints
            config: SimulationConfig used for the simulation
        """
        super().__init__(parent, style='TFrame')
        
        self.result = result
        self.controller = controller
        self.config = config
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_LARGE)
        
        # Header
        self._create_header(container)
        
        # Statistics cards
        self._create_statistics(container)
        
        # Charts
        self._create_charts(container)
        
        # Actions
        self._create_actions(container)
        
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="📊 Resultados de la Simulación",
            style='Title.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Determine result type
        result_type = self._get_result_type()
        
        # Get species ID safely
        species_id = "N/A"
        if isinstance(self.result, PopulationResult):
            species_id = self.result.species_id
        elif isinstance(self.result, HybridResult):
            species_id = self.result.population_result.species_id
        
        # Description
        desc = ttk.Label(
            header,
            text=f"Tipo: {result_type} | Especie: {species_id}",
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY
        )
        desc.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.PADDING_MEDIUM)
        
    def _get_result_type(self) -> str:
        """Determine result type."""
        if isinstance(self.result, PopulationResult):
            return "Simulación Poblacional"
        elif isinstance(self.result, AgentResult):
            return "Simulación Basada en Agentes"
        elif isinstance(self.result, HybridResult):
            return "Simulación Híbrida"
        else:
            return "Desconocido"
            
    def _create_statistics(self, parent):
        """Create statistics summary cards."""
        stats_frame = ttk.Frame(parent, style='TFrame')
        stats_frame.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Get statistics from result
        stats = self._extract_statistics()
        
        # Create metric cards
        cards = ttk.Frame(stats_frame, style='TFrame')
        cards.pack(fill=tk.X)
        
        for i, (label, value) in enumerate(stats.items()):
            card = self._create_metric_card(cards, label, value)
            card.grid(row=0, column=i, padx=Spacing.PADDING_SMALL, sticky='nsew')
            
        # Configure grid
        for i in range(len(stats)):
            cards.columnconfigure(i, weight=1)
            
    def _extract_statistics(self) -> dict:
        """Extract key statistics from result."""
        stats = {}
        
        if isinstance(self.result, PopulationResult):
            # Population result statistics
            if hasattr(self.result, 'statistics') and self.result.statistics:
                s = self.result.statistics
                stats['Duración'] = f"{len(self.result.days)} días"
                stats['Población Final'] = f"{int(self.result.total_population[-1]):,}"
                stats['Población Pico'] = f"{int(s.get('peak_population', 0)):,}"
                stats['Día Pico'] = f"Día {s.get('peak_day', 0)}"
            else:
                stats['Duración'] = f"{len(self.result.days)} días"
                stats['Población Final'] = f"{int(self.result.total_population[-1]):,}"
                
        elif isinstance(self.result, AgentResult):
            # Agent result statistics - get from daily_stats
            stats['Duración'] = f"{len(self.result.daily_stats)} días"
            
            # Extract vector counts from daily_stats
            if self.result.daily_stats:
                vector_counts = [stat['num_vectors_alive'] for stat in self.result.daily_stats]
                stats['Vectores Iniciales'] = f"{self.result.num_vectors_initial:,}"
                stats['Vectores Finales'] = f"{self.result.num_vectors_final:,}"
                stats['Depredadores Finales'] = f"{self.result.num_predators_final:,}"
                stats['Huevos Totales'] = f"{self.result.total_eggs_laid:,}"
            
        elif isinstance(self.result, HybridResult):
            # Hybrid result - show both
            pop = self.result.population_result
            agent = self.result.agent_result
            
            stats['Duración'] = f"{len(pop.days)} días"
            stats['Población Final'] = f"{int(pop.total_population[-1]):,}"
            stats['Agentes Finales'] = f"{agent.num_vectors_final:,}"
            
        return stats
        
    def _create_metric_card(self, parent, label: str, value: str) -> ttk.Frame:
        """Create a metric card."""
        card = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        card.configure(padding=Spacing.PADDING_MEDIUM)
        
        # Label
        lbl = ttk.Label(
            card,
            text=label,
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY,
            font=Fonts.SMALL
        )
        lbl.pack()
        
        # Value
        val = ttk.Label(
            card,
            text=value,
            style='TLabel',
            foreground=Colors.PRIMARY,
            font=(Fonts.FAMILY, 16, Fonts.WEIGHT_BOLD)
        )
        val.pack(pady=(Spacing.PADDING_SMALL, 0))
        
        return card
        
    def _create_charts(self, parent):
        """Create matplotlib charts."""
        chart_frame = ttk.Frame(parent, style='TFrame')
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create figure
        if isinstance(self.result, PopulationResult):
            self._create_population_chart(chart_frame)
        elif isinstance(self.result, AgentResult):
            self._create_agent_chart(chart_frame)
        elif isinstance(self.result, HybridResult):
            self._create_hybrid_chart(chart_frame)
            
    def _create_population_chart(self, parent):
        """Create chart for population results."""
        # Use existing visualization function
        fig = visualization.plot_population_total(
            self.result,
            show=False,
            figsize=(10, 6)
        )
        
        # Style adjustments for integration
        ax = fig.gca()
        ax.set_facecolor(Colors.BACKGROUND)
        fig.patch.set_facecolor(Colors.SURFACE)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        
    def _create_agent_chart(self, parent):
        """Create chart for agent results."""
        # Use existing visualization function
        fig = visualization.plot_agent_survival(
            self.result,
            show=False,
            figsize=(10, 6)
        )
        
        # Style adjustments
        ax = fig.gca()
        ax.set_facecolor(Colors.BACKGROUND)
        fig.patch.set_facecolor(Colors.SURFACE)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        
    def _create_hybrid_chart(self, parent):
        """Create comparison chart for hybrid results."""
        # Create figure with 2 subplots manually since we need custom styling
        fig = Figure(figsize=(10, 8), facecolor=Colors.SURFACE)
        
        # Population subplot
        ax1 = fig.add_subplot(211)
        pop = self.result.population_result
        ax1.plot(pop.days, pop.total_population, label='Modelo Poblacional', 
                color=Colors.PRIMARY, linewidth=2)
        ax1.set_ylabel('Población Total', fontsize=10, color=Colors.TEXT_PRIMARY)
        ax1.set_title('Comparación: Modelo Poblacional vs Basado en Agentes', 
                     fontsize=12, fontweight='bold', color=Colors.PRIMARY)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_facecolor(Colors.BACKGROUND)
        
        # Agent subplot
        ax2 = fig.add_subplot(212)
        agent = self.result.agent_result
        
        # Extract vector counts from daily_stats
        vector_counts = [stat['num_vectors_alive'] for stat in agent.daily_stats]
        days_agent = list(range(len(vector_counts)))
        
        ax2.plot(days_agent, vector_counts, label='Modelo Basado en Agentes', 
                color=Colors.SECONDARY, linewidth=2)
        ax2.set_xlabel('Días', fontsize=10, color=Colors.TEXT_PRIMARY)
        ax2.set_ylabel('Número de Vectores', fontsize=10, color=Colors.TEXT_PRIMARY)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_facecolor(Colors.BACKGROUND)
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        
    def _create_actions(self, parent):
        """Create action buttons."""
        actions = ttk.Frame(parent, style='TFrame')
        actions.pack(fill=tk.X, pady=(Spacing.PADDING_LARGE, 0))
        
        # Separator
        sep = ttk.Separator(actions, orient='horizontal')
        sep.pack(fill=tk.X, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Button frame
        btn_frame = ttk.Frame(actions, style='TFrame')
        btn_frame.pack(anchor=tk.E)
        
        # Export data button
        export_data_btn = ttk.Button(
            btn_frame,
            text="📁 Exportar Datos",
            style='TButton',
            command=self._export_data
        )
        export_data_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        # Export chart button
        export_chart_btn = ttk.Button(
            btn_frame,
            text="📊 Exportar Gráfico",
            style='TButton',
            command=self._export_chart
        )
        export_chart_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        # Save checkpoint button
        save_checkpoint_btn = ttk.Button(
            btn_frame,
            text="💾 Guardar Checkpoint",
            style='Secondary.TButton',
            command=self._save_checkpoint
        )
        save_checkpoint_btn.pack(side=tk.LEFT)
        
    def _export_data(self):
        """Export result data to CSV."""
        from tkinter import filedialog
        import csv
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if isinstance(self.result, PopulationResult):
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Día', 'Huevos', 'Larvas', 'Pupas', 'Adultos', 'Total'])
                        for i in range(len(self.result.days)):
                            writer.writerow([
                                self.result.days[i],
                                self.result.eggs[i],
                                self.result.larvae[i],
                                self.result.pupae[i],
                                self.result.adults[i],
                                self.result.total_population[i]
                            ])
                
                from tkinter import messagebox
                messagebox.showinfo("Éxito", f"Datos exportados a:\n{filename}")
                
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Error exportando datos:\n{str(e)}")
                
    def _export_chart(self):
        """Export chart to PNG."""
        from tkinter import filedialog, messagebox
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Create figure again and save
                fig = Figure(figsize=(10, 6))
                ax = fig.add_subplot(111)
                
                if isinstance(self.result, PopulationResult):
                    ax.plot(self.result.days, self.result.total_population, 
                           label='Población Total', color=Colors.PRIMARY, linewidth=2)
                    ax.set_ylabel('Población')
                    ax.set_title('Evolución Temporal de la Población')
                    
                ax.set_xlabel('Días')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico exportado a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando gráfico:\n{str(e)}")
                
    def _save_checkpoint(self):
        """Save result as checkpoint."""
        from tkinter import simpledialog, messagebox
        
        if not self.controller or not self.config:
            messagebox.showwarning(
                "No Disponible",
                "No se puede guardar checkpoint: información de configuración no disponible."
            )
            return
        
        # Get species ID safely
        species_id = "result"
        if isinstance(self.result, PopulationResult):
            species_id = self.result.species_id
        elif isinstance(self.result, HybridResult):
            species_id = self.result.population_result.species_id
        
        name = simpledialog.askstring(
            "Guardar Checkpoint",
            "Nombre del checkpoint:",
            initialvalue=f"sim_{species_id}"
        )
        
        if name:
            try:
                # Determine simulation type
                if isinstance(self.result, PopulationResult):
                    sim_type = 'population'
                elif isinstance(self.result, AgentResult):
                    sim_type = 'agent'
                else:
                    sim_type = 'hybrid'
                
                # Ensure name has .json extension
                if not name.endswith('.json'):
                    checkpoint_filename = f"{name}.json"
                else:
                    checkpoint_filename = name
                
                # Save checkpoint directly via service with the result we have
                checkpoint_path = self.controller.service.save_checkpoint(
                    result=self.result,  # Use the result we already have
                    config=self.config,
                    simulation_type=sim_type,
                    checkpoint_name=checkpoint_filename
                )
                
                messagebox.showinfo(
                    "Éxito",
                    f"Checkpoint guardado correctamente:\n{checkpoint_path.name}"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando checkpoint:\n{str(e)}")
