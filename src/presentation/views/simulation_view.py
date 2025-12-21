"""
Presentation Layer - Simulation View
=====================================

View for configuring and running simulations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing
from presentation.controllers.simulation_controller import SimulationController
from application.dtos import SimulationConfig


class SimulationView(ttk.Frame):
    """
    View for simulation configuration and execution.
    
    Features:
    - Species selection
    - Parameter configuration
    - Simulation type selection (population/agent/hybrid)
    - Run button with progress
    - Results callback
    """
    
    def __init__(
        self,
        parent,
        controller: SimulationController,
        on_results: Optional[Callable] = None,
        on_log: Optional[Callable[[str, str], None]] = None
    ):
        """
        Initialize simulation view.
        
        Args:
            parent: Parent widget
            controller: Simulation controller instance
            on_results: Callback when simulation completes (result)
            on_log: Callback for logging (message, level)
        """
        super().__init__(parent, style='TFrame')
        
        self.controller = controller
        self.on_results = on_results
        self.on_log = on_log
        
        # Form variables
        self.species_var = tk.StringVar(value='aedes_aegypti')
        self.sim_type_var = tk.StringVar(value='population')  # Fixed to population only
        self.duration_var = tk.StringVar(value='90')
        self.eggs_var = tk.StringVar(value='1000')
        self.larvae_var = tk.StringVar(value='500')
        self.pupae_var = tk.StringVar(value='100')
        self.adults_var = tk.StringVar(value='50')
        self.temp_var = tk.StringVar(value='25.0')
        self.humidity_var = tk.StringVar(value='70.0')
        self.water_var = tk.StringVar(value='1.0')
        
        # Option maps for dropdowns
        self.species_map = {}
        self.sim_type_map = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_XLARGE, pady=Spacing.PADDING_XLARGE)
        
        # Header
        self._create_header(container)
        
        # Configuration form
        self._create_form(container)
        
        # Action buttons
        self._create_actions(container)
        
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="▶️ Configuración de Simulación",
            style='Title.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Description
        desc = ttk.Label(
            header,
            text="Configure los parámetros de la simulación poblacional",
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY
        )
        desc.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.PADDING_MEDIUM)
        
    def _create_form(self, parent):
        """Create configuration form."""
        form = ttk.Frame(parent, style='TFrame')
        form.pack(fill=tk.BOTH, expand=True)
        
        # Two-column layout
        left_col = ttk.Frame(form, style='TFrame')
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, Spacing.PADDING_MEDIUM))
        
        right_col = ttk.Frame(form, style='TFrame')
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(Spacing.PADDING_MEDIUM, 0))
        
        # LEFT COLUMN
        # Species and simulation type section
        basic_section = self._create_section(left_col, "Configuración Básica")
        
        # Species dropdown
        species_options = [
            ('Aedes aegypti (Vector)', 'aedes_aegypti'),
            ('Toxorhynchites (Depredador)', 'toxorhynchites')
        ]
        self.species_map = {opt[0]: opt[1] for opt in species_options}
        self._create_dropdown(basic_section, "Especie:", self.species_var, 
                             species_options, self._on_species_changed, 'species')
        
        # Simulation type is now fixed to 'population' (not shown in GUI)
        # Agent and hybrid simulations are kept in code but not accessible from interface
        self.sim_type_map = {'Poblacional': 'population'}
        
        self._create_input(basic_section, "Duración (días):", self.duration_var, "int")
        
        # Initial population section
        pop_section = self._create_section(left_col, "Población Inicial")
        
        self._create_input(pop_section, "Huevos:", self.eggs_var, "int")
        self._create_input(pop_section, "Larvas:", self.larvae_var, "int")
        self._create_input(pop_section, "Pupas:", self.pupae_var, "int")
        self._create_input(pop_section, "Adultos:", self.adults_var, "int")
        
        # RIGHT COLUMN
        # Environmental conditions section
        env_section = self._create_section(right_col, "Condiciones Ambientales")
        
        self._create_input(env_section, "Temperatura (°C):", self.temp_var, "float")
        self._create_input(env_section, "Humedad (%):", self.humidity_var, "float")
        self._create_input(env_section, "Disponibilidad Agua (0-1):", self.water_var, "float")
        
        # Info box
        info_section = self._create_section(right_col, "Información")
        self._create_info_box(info_section)
        
    def _create_section(self, parent, title: str) -> ttk.Frame:
        """Create a form section with title."""
        section = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        section.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        section.configure(padding=Spacing.PADDING_LARGE)
        
        # Section title
        title_label = ttk.Label(
            section,
            text=title,
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title_label.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        return section
        
    def _create_dropdown(
        self,
        parent,
        label: str,
        variable: tk.StringVar,
        options: list,
        command: Optional[Callable] = None,
        dropdown_type: str = ''
    ):
        """Create a labeled dropdown."""
        row = ttk.Frame(parent, style='TFrame')
        row.pack(fill=tk.X, pady=(0, Spacing.PADDING_SMALL))
        
        # Label
        lbl = ttk.Label(row, text=label, style='TLabel', width=20)
        lbl.pack(side=tk.LEFT)
        
        # Dropdown
        combo = ttk.Combobox(
            row,
            textvariable=variable,
            values=[opt[0] for opt in options],
            state='readonly',
            font=Fonts.BODY
        )
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if command:
            combo.bind('<<ComboboxSelected>>', lambda e: command())
            
    def _create_input(self, parent, label: str, variable: tk.StringVar, input_type: str):
        """Create a labeled input field."""
        row = ttk.Frame(parent, style='TFrame')
        row.pack(fill=tk.X, pady=(0, Spacing.PADDING_SMALL))
        
        # Label
        lbl = ttk.Label(row, text=label, style='TLabel', width=20)
        lbl.pack(side=tk.LEFT)
        
        # Entry with validation
        entry = ttk.Entry(row, textvariable=variable, font=Fonts.BODY)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add validation indicator
        if input_type == 'int':
            vcmd = (self.register(self._validate_int), '%P')
            entry.configure(validate='key', validatecommand=vcmd)
        elif input_type == 'float':
            vcmd = (self.register(self._validate_float), '%P')
            entry.configure(validate='key', validatecommand=vcmd)
            
    def _create_info_box(self, parent):
        """Create information box."""
        info_frame = ttk.Frame(parent, style='TFrame')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        info_text = """
ℹ️ Consejos:

• Poblacional: Rápido, ideal para 
  análisis de largo plazo

• Agentes: Detallado, captura 
  comportamientos individuales

• Híbrida: Compara ambos enfoques

• Duración típica: 60-180 días

• Temperatura óptima: 20-30°C
        """.strip()
        
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY,
            justify=tk.LEFT,
            font=Fonts.SMALL
        )
        info_label.pack(anchor=tk.W)
        
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
        
        # Load defaults button
        load_btn = ttk.Button(
            btn_frame,
            text="Cargar Valores por Defecto",
            style='TButton',
            command=self._load_defaults
        )
        load_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_MEDIUM))
        
        # Run button
        run_btn = ttk.Button(
            btn_frame,
            text="▶️ Ejecutar Simulación",
            style='Primary.TButton',
            command=self._run_simulation
        )
        run_btn.pack(side=tk.LEFT)
        
    def _validate_int(self, value: str) -> bool:
        """Validate integer input."""
        if value == "" or value == "-":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
            
    def _validate_float(self, value: str) -> bool:
        """Validate float input."""
        if value == "" or value == "-" or value == ".":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False
            
    def _on_species_changed(self):
        """Handle species selection change."""
        self._load_defaults()
        
    def _load_defaults(self):
        """Load default values for selected species."""
        species_display = self.species_var.get()
        species_id = self.species_map.get(species_display, 'aedes_aegypti')
        
        # Get default config
        config = self.controller.get_default_config(species_id)
        
        # Update form values
        self.duration_var.set(str(config.duration_days))
        self.eggs_var.set(str(config.initial_eggs))
        self.larvae_var.set(str(config.initial_larvae))
        self.pupae_var.set(str(config.initial_pupae))
        self.adults_var.set(str(config.initial_adults))
        self.temp_var.set(str(config.temperature))
        self.humidity_var.set(str(config.humidity))
        self.water_var.set(str(config.water_availability))
        
        if self.on_log:
            self.on_log(f"Valores por defecto cargados para {species_id}", "info")
            
    def _run_simulation(self):
        """Execute simulation with current configuration."""
        try:
            # Get species ID
            species_display = self.species_var.get()
            species_id = self.species_map.get(species_display, 'aedes_aegypti')
            
            # Build config from form
            config = SimulationConfig(
                species_id=species_id,
                duration_days=int(self.duration_var.get()),
                initial_eggs=int(self.eggs_var.get()),
                initial_larvae=int(self.larvae_var.get()),
                initial_pupae=int(self.pupae_var.get()),
                initial_adults=int(self.adults_var.get()),
                temperature=float(self.temp_var.get()),
                humidity=float(self.humidity_var.get()),
                water_availability=float(self.water_var.get())
            )
            
            # Validate
            is_valid, errors = config.validate()
            if not is_valid:
                messagebox.showerror(
                    "Configuración Inválida",
                    "Errores de validación:\n\n" + "\n".join(f"• {e}" for e in errors)
                )
                return
            
            # Simulation type is fixed to 'population'
            sim_type = 'population'
            
            # Log start
            if self.on_log:
                self.on_log("Iniciando simulación poblacional...", "info")
            
            # Execute population simulation
            result = self.controller.run_population_simulation(config)
            if self.on_log:
                self.on_log("Simulación poblacional completada", "success")
            
            # Show success message
            messagebox.showinfo(
                "Simulación Completa",
                f"La simulación se completó exitosamente.\n\n"
                f"Duración: {config.duration_days} días\n"
                f"Especie: {species_id}"
            )
            
            # Callback with results
            if self.on_results:
                self.on_results(result, config)
                
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            if self.on_log:
                self.on_log(f"Error: {str(e)}", "error")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error ejecutando simulación:\n{str(e)}")
            if self.on_log:
                self.on_log(f"Error: {str(e)}", "error")
