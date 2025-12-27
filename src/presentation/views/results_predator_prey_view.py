"""
Presentation Layer - Predator-Prey Results View
================================================

View for displaying predator-prey simulation results with charts and statistics.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing
from application.dtos import PredatorPreyResult
from application import visualization

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PredatorPreyResultsView(ttk.Frame):
    """
    View for displaying predator-prey simulation results.
    
    Features:
    - Predator-prey interaction visualization
    - Statistics summary
    - Comparison charts (with/without predators if available)
    - Export options (CSV + PNG images)
    """
    
    def __init__(
        self,
        parent,
        result: PredatorPreyResult,
        comparison_result: Optional[Dict[str, PredatorPreyResult]] = None,
        on_log: Optional[Callable] = None
    ):
        """
        Initialize predator-prey results view.
        
        Args:
            parent: Parent widget
            result: PredatorPreyResult to display
            comparison_result: Optional comparison dict with 'with_predators' and 'without_predators'
            on_log: Optional callback for logging (message, level)
        """
        super().__init__(parent, style='TFrame')
        
        self.result = result
        self.comparison_result = comparison_result
        self.on_log = on_log
        self.current_figure = None
        self.current_canvas = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.LARGE, pady=Spacing.LARGE)
        
        # Header
        self._create_header(container)
        
        # Statistics section
        self._create_statistics(container)
        
        # Chart area
        self._create_charts_area(container)
        
        # Action buttons
        self._create_action_buttons(container)
    
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.LARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="📊 Resultados: Simulación Presa-Depredador",
            font=(Fonts.DEFAULT, 16, 'bold'),
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Description
        desc = ttk.Label(
            header,
            text=f"Presa: {self.result.prey_species_id} | Depredador: {self.result.predator_species_id} | Duración: {self.result.duration_days} días",
            foreground=Colors.TEXT_SECONDARY
        )
        desc.pack(anchor=tk.W, pady=(Spacing.SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.MEDIUM)
    
    def _create_statistics(self, parent):
        """Create statistics section."""
        frame = ttk.LabelFrame(parent, text='Estadísticas', style='TLabelframe')
        frame.pack(fill=tk.X, pady=(0, Spacing.LARGE))
        
        stats = self.result.statistics
        
        # Create two columns
        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Spacing.MEDIUM, pady=Spacing.MEDIUM)
        
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=Spacing.MEDIUM, pady=Spacing.MEDIUM)
        
        # LEFT: Prey statistics
        ttk.Label(left_frame, text='PRESA (Aedes aegypti)', font=(Fonts.DEFAULT, 11, 'bold')).pack(anchor=tk.W, pady=(0, Spacing.SMALL))
        
        prey_stats = [
            (f"Inicial: {stats['prey_initial']:.0f}", Colors.INFO),
            (f"Final: {stats['prey_final']:.0f}", Colors.INFO),
            (f"Pico: {stats['prey_peak']:.0f} (día {self.result.peak_day})", Colors.SUCCESS),
            (f"Promedio: {stats['prey_mean']:.1f} ± {stats['prey_std']:.1f}", Colors.INFO),
            (f"Reducción: {stats['predation_reduction_percent']:.1f}%", Colors.ERROR),
        ]
        
        for text, color in prey_stats:
            lbl = ttk.Label(left_frame, text=text, foreground=color)
            lbl.pack(anchor=tk.W, pady=Spacing.SMALL)
        
        # RIGHT: Predator statistics
        ttk.Label(right_frame, text='DEPREDADOR (Toxorhynchites)', font=(Fonts.DEFAULT, 11, 'bold')).pack(anchor=tk.W, pady=(0, Spacing.SMALL))
        
        pred_stats = [
            (f"Inicial: {stats['predator_initial']:.0f}", Colors.INFO),
            (f"Final: {stats['predator_final']:.0f}", Colors.INFO),
            (f"Pico: {stats['predator_peak']:.0f}", Colors.SUCCESS),
            (f"Promedio: {stats['predator_mean']:.1f} ± {stats['predator_std']:.1f}", Colors.INFO),
        ]
        
        for text, color in pred_stats:
            lbl = ttk.Label(right_frame, text=text, foreground=color)
            lbl.pack(anchor=tk.W, pady=Spacing.SMALL)
    
    def _create_charts_area(self, parent):
        """Create charts visualization area."""
        frame = ttk.LabelFrame(parent, text='Visualizaciones', style='TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.LARGE))
        
        # Create button frame for chart selection
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=Spacing.MEDIUM, pady=(Spacing.MEDIUM, 0))
        
        ttk.Button(
            button_frame,
            text='Ver Dinámicas Completas',
            command=self._show_interaction_chart
        ).pack(side=tk.LEFT, padx=Spacing.SMALL)
        
        if self.comparison_result:
            ttk.Button(
                button_frame,
                text='Ver Comparación (con/sin depredadores)',
                command=self._show_comparison_chart
            ).pack(side=tk.LEFT, padx=Spacing.SMALL)
        
        # Canvas frame for matplotlib
        self.canvas_frame = ttk.Frame(frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.MEDIUM, pady=Spacing.MEDIUM)
        
        # Show default chart
        self._show_interaction_chart()
    
    def _show_interaction_chart(self):
        """Display predator-prey interaction chart."""
        # Clear previous canvas
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            self.current_canvas = None
        
        if self.current_figure:
            plt.close(self.current_figure)
            self.current_figure = None
        
        # Create figure
        self.current_figure = visualization.plot_predator_prey_interaction(
            self.result,
            show=False
        )
        
        # Embed in tkinter
        self.current_canvas = FigureCanvasTkAgg(self.current_figure, self.canvas_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_comparison_chart(self):
        """Display comparison chart (with/without predators)."""
        if not self.comparison_result:
            messagebox.showwarning('Sin Comparación', 'No hay datos de comparación disponibles')
            return
        
        # Clear previous canvas
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            self.current_canvas = None
        
        if self.current_figure:
            plt.close(self.current_figure)
            self.current_figure = None
        
        # Extract results
        with_pred = self.comparison_result.get('with_predators')
        without_pred = self.comparison_result.get('without_predators')
        
        if not (with_pred and without_pred):
            messagebox.showerror('Error', 'No se pueden mostrar los datos de comparación')
            return
        
        # Create figure
        self.current_figure = visualization.plot_predation_impact_comparison(
            with_pred, without_pred,
            show=False
        )
        
        # Embed in tkinter
        self.current_canvas = FigureCanvasTkAgg(self.current_figure, self.canvas_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_action_buttons(self, parent):
        """Create action buttons section."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(Spacing.LARGE, 0))
        
        ttk.Button(
            frame,
            text='📥 Exportar Resultados (CSV)',
            command=self._export_csv
        ).pack(side=tk.LEFT, padx=Spacing.SMALL)
        
        ttk.Button(
            frame,
            text='🖼️ Exportar Gráficas (PNG)',
            command=self._export_graphs
        ).pack(side=tk.LEFT, padx=Spacing.SMALL)
    
    def _export_csv(self):
        """Export trajectory data as CSV."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
            )
            
            if not file_path:
                return
            
            import csv
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Day', 'Prey_Eggs', 'Prey_Larvae', 'Prey_Pupae', 'Prey_Adults',
                    'Prey_Total', 'Predator_Total', 'Temperature', 'Humidity'
                ])
                
                # Data
                for i, prey_state in enumerate(self.result.prey_trajectory):
                    pred_total = sum(self.result.predator_trajectory[i]) if self.result.predator_trajectory else 0
                    writer.writerow([
                        prey_state['day'],
                        prey_state['eggs'],
                        prey_state['larvae'],
                        prey_state['pupae'],
                        prey_state['adults'],
                        prey_state['total'],
                        int(pred_total),
                        prey_state['temperature'],
                        prey_state['humidity']
                    ])
            
            messagebox.showinfo('Éxito', f'Resultados exportados a:\n{file_path}')
            if self.on_log:
                self.on_log(f'CSV exportado: {file_path}', 'info')
                
        except Exception as e:
            messagebox.showerror('Error en Exportación', str(e))
            if self.on_log:
                self.on_log(f'Error exportando CSV: {str(e)}', 'error')
    
    def _export_graphs(self):
        """Export graphs as PNG images."""
        try:
            dir_path = filedialog.askdirectory(title='Selecciona carpeta para guardar gráficas')
            if not dir_path:
                return
            
            dir_path = Path(dir_path)
            
            # Export main interaction chart
            fig1 = visualization.plot_predator_prey_interaction(
                self.result,
                show=False,
                save_path=str(dir_path / 'predator_prey_dynamics.png')
            )
            plt.close(fig1)
            
            # Export comparison if available
            if self.comparison_result:
                with_pred = self.comparison_result.get('with_predators', self.comparison_result.get('result_with'))
                without_pred = self.comparison_result.get('without_predators', self.comparison_result.get('result_without'))
                
                if with_pred and without_pred:
                    fig2 = visualization.plot_predation_impact_comparison(
                        with_pred, without_pred,
                        show=False,
                        save_path=str(dir_path / 'predation_impact_comparison.png')
                    )
                    plt.close(fig2)
            
            messagebox.showinfo('Éxito', f'Gráficas exportadas a:\n{dir_path}')
            if self.on_log:
                self.on_log(f'Gráficas exportadas a: {dir_path}', 'info')
                
        except Exception as e:
            messagebox.showerror('Error en Exportación', str(e))
            if self.on_log:
                self.on_log(f'Error exportando gráficas: {str(e)}', 'error')
