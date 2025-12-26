"""
Presentation Layer - Simulation View
=====================================

View for configuring and running simulations with:
- Parameter validation and range checking
- Informative tooltips for all parameters
- Preset scenarios for common use cases
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing
from presentation.controllers.simulation_controller import SimulationController
from presentation.widgets.tooltip import create_tooltip
from presentation.data.scenario_presets import (
    SCENARIO_PRESETS,
    PARAMETER_RANGES,
    PARAMETER_TOOLTIPS,
    SCENARIO_CATEGORIES,
    get_presets_by_category,
    get_preset_by_name,
    validate_parameter
)
from application.dtos import SimulationConfig


class SimulationView(ttk.Frame):
    """
    View for simulation configuration and execution.
    
    Features:
    - Species selection
    - Parameter configuration with validation
    - Informative tooltips for all parameters
    - Scenario presets for quick configuration
    - Real-time validation feedback
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
        
        # Validation status tracking
        self.validation_labels: Dict[str, ttk.Label] = {}
        
        # Option maps for dropdowns
        self.species_map = {}
        self.sim_type_map = {}
        
        # Trace variables for real-time validation
        self.duration_var.trace_add('write', lambda *args: self._validate_field('duration'))
        self.eggs_var.trace_add('write', lambda *args: self._validate_field('initial_eggs'))
        self.larvae_var.trace_add('write', lambda *args: self._validate_field('initial_larvae'))
        self.pupae_var.trace_add('write', lambda *args: self._validate_field('initial_pupae'))
        self.adults_var.trace_add('write', lambda *args: self._validate_field('initial_adults'))
        self.temp_var.trace_add('write', lambda *args: self._validate_field('temperature'))
        self.humidity_var.trace_add('write', lambda *args: self._validate_field('humidity'))
        self.water_var.trace_add('write', lambda *args: self._validate_field('water_availability'))
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_XLARGE, pady=Spacing.PADDING_XLARGE)
        
        # Header
        self._create_header(container)
        
        # Scenario presets section
        self._create_presets_section(container)
        
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
    
    def _create_presets_section(self, parent):
        """Create scenario presets section."""
        presets_frame = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        presets_frame.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        presets_frame.configure(padding=Spacing.PADDING_LARGE)
        
        # Section title
        title_row = ttk.Frame(presets_frame, style='TFrame')
        title_row.pack(fill=tk.X, pady=(0, Spacing.PADDING_MEDIUM))
        
        title_label = ttk.Label(
            title_row,
            text="📋 Escenarios Predefinidos",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title_label.pack(side=tk.LEFT)
        
        # Add tooltip for presets
        create_tooltip(
            title_label,
            "Escenarios de simulación predefinidos para casos comunes.\n"
            "Seleccione una categoría y un escenario para cargar automáticamente todos los parámetros."
        )
        
        # Category and preset selection row
        selection_row = ttk.Frame(presets_frame, style='TFrame')
        selection_row.pack(fill=tk.X)
        
        # Category dropdown
        category_label = ttk.Label(selection_row, text="Categoría:", style='TLabel', width=15)
        category_label.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        self.category_var = tk.StringVar(value='baseline')
        category_names = [(SCENARIO_CATEGORIES[cat]['name'], cat) for cat in SCENARIO_CATEGORIES]
        category_combo = ttk.Combobox(
            selection_row,
            textvariable=self.category_var,
            values=[name for name, _ in category_names],
            state='readonly',
            width=25,
            font=Fonts.BODY
        )
        category_combo.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_MEDIUM))
        category_combo.bind('<<ComboboxSelected>>', self._on_category_changed)
        
        # Add category tooltip
        create_tooltip(
            category_combo,
            "Categorías de escenarios:\n\n" +
            "\n".join(f"• {cat['name']}: {cat['description']}" 
                     for cat in SCENARIO_CATEGORIES.values()),
            delay=300
        )
        
        # Preset dropdown
        preset_label = ttk.Label(selection_row, text="Escenario:", style='TLabel', width=15)
        preset_label.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            selection_row,
            textvariable=self.preset_var,
            state='readonly',
            width=30,
            font=Fonts.BODY
        )
        self.preset_combo.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_MEDIUM))
        self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_selected)
        
        # Load preset button
        load_preset_btn = ttk.Button(
            selection_row,
            text="⬇️ Cargar",
            style='TButton',
            command=self._load_preset
        )
        load_preset_btn.pack(side=tk.LEFT)
        
        # Description label (shows when preset is selected) - must be created BEFORE _update_preset_list
        self.preset_desc_label = ttk.Label(
            presets_frame,
            text="",
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY,
            wraplength=800
        )
        self.preset_desc_label.pack(fill=tk.X, pady=(Spacing.PADDING_MEDIUM, 0))
        
        # Initialize category presets
        self._update_preset_list()

        
    def _on_category_changed(self, event=None):
        """Handle category selection change."""
        self._update_preset_list()
        
    def _update_preset_list(self):
        """Update preset list based on selected category."""
        # Get selected category ID
        category_display = self.category_var.get()
        category_id = None
        for name, cat_id in [(SCENARIO_CATEGORIES[c]['name'], c) for c in SCENARIO_CATEGORIES]:
            if name == category_display:
                category_id = cat_id
                break
        
        if not category_id:
            category_id = 'baseline'
        
        # Get presets for category
        presets = get_presets_by_category(category_id)
        if isinstance(presets, dict):
            # If returned dict, get the list for this category
            presets = presets.get(category_id, [])
        
        # Update combo values
        preset_names = [p.name for p in presets]
        self.preset_combo['values'] = preset_names
        if preset_names:
            self.preset_combo.set(preset_names[0])
            self._on_preset_selected()
        
    def _on_preset_selected(self, event=None):
        """Handle preset selection to show description."""
        preset_name = self.preset_var.get()
        if not preset_name:
            return
        
        preset = get_preset_by_name(preset_name)
        if preset:
            self.preset_desc_label.config(
                text=f"📝 {preset.description} | Especie: {preset.species} | "
                     f"Duración: {preset.duration} días | Temp: {preset.temperature}°C"
            )
        
    def _load_preset(self):
        """Load selected preset into form."""
        preset_name = self.preset_var.get()
        if not preset_name:
            messagebox.showwarning("Seleccionar Escenario", "Por favor seleccione un escenario primero.")
            return
        
        preset = get_preset_by_name(preset_name)
        if not preset:
            messagebox.showerror("Error", f"Escenario '{preset_name}' no encontrado.")
            return
        
        # Update form with preset values
        self.species_var.set(preset.species)
        self.duration_var.set(str(preset.duration))
        self.eggs_var.set(str(preset.initial_eggs))
        self.larvae_var.set(str(preset.initial_larvae))
        self.pupae_var.set(str(preset.initial_pupae))
        self.adults_var.set(str(preset.initial_adults))
        self.temp_var.set(str(preset.temperature))
        self.humidity_var.set(str(preset.humidity))
        self.water_var.set(str(preset.water_availability))
        
        if self.on_log:
            self.on_log(f"Escenario '{preset.name}' cargado correctamente", "success")
        
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
        
        self._create_input(basic_section, "Duración (días):", self.duration_var, "int", "duration")
        
        # Initial population section
        pop_section = self._create_section(left_col, "Población Inicial")
        
        self._create_input(pop_section, "Huevos:", self.eggs_var, "int", "initial_eggs")
        self._create_input(pop_section, "Larvas:", self.larvae_var, "int", "initial_larvae")
        self._create_input(pop_section, "Pupas:", self.pupae_var, "int", "initial_pupae")
        self._create_input(pop_section, "Adultos:", self.adults_var, "int", "initial_adults")
        
        # RIGHT COLUMN
        # Environmental conditions section
        env_section = self._create_section(right_col, "Condiciones Ambientales")
        
        self._create_input(env_section, "Temperatura (°C):", self.temp_var, "float", "temperature")
        self._create_input(env_section, "Humedad (%):", self.humidity_var, "float", "humidity")
        self._create_input(env_section, "Disponibilidad Agua (0-1):", self.water_var, "float", "water_availability")
        
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
        """Create a labeled dropdown with optional tooltip."""
        row = ttk.Frame(parent, style='TFrame')
        row.pack(fill=tk.X, pady=(0, Spacing.PADDING_SMALL))
        
        # Label
        lbl = ttk.Label(row, text=label, style='TLabel', width=20)
        lbl.pack(side=tk.LEFT)
        
        # Add tooltip to label if available
        if dropdown_type in PARAMETER_TOOLTIPS:
            create_tooltip(lbl, PARAMETER_TOOLTIPS[dropdown_type], delay=300)
        
        # Dropdown
        combo = ttk.Combobox(
            row,
            textvariable=variable,
            values=[opt[0] for opt in options],
            state='readonly',
            font=Fonts.BODY
        )
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add tooltip to combo as well
        if dropdown_type in PARAMETER_TOOLTIPS:
            create_tooltip(combo, PARAMETER_TOOLTIPS[dropdown_type], delay=300)
        
        if command:
            combo.bind('<<ComboboxSelected>>', lambda e: command())
            
    def _create_input(self, parent, label: str, variable: tk.StringVar, input_type: str, param_name: str = ''):
        """Create a labeled input field with validation and tooltip."""
        row = ttk.Frame(parent, style='TFrame')
        row.pack(fill=tk.X, pady=(0, Spacing.PADDING_SMALL))
        
        # Label
        lbl = ttk.Label(row, text=label, style='TLabel', width=20)
        lbl.pack(side=tk.LEFT)
        
        # Add tooltip to label if parameter info available
        if param_name and param_name in PARAMETER_TOOLTIPS:
            create_tooltip(lbl, PARAMETER_TOOLTIPS[param_name], delay=300)
        
        # Entry with validation
        entry = ttk.Entry(row, textvariable=variable, font=Fonts.BODY)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Spacing.PADDING_SMALL))
        
        # Add tooltip to entry as well
        if param_name and param_name in PARAMETER_TOOLTIPS:
            create_tooltip(entry, PARAMETER_TOOLTIPS[param_name], delay=300)
        
        # Validation indicator label
        validation_label = ttk.Label(row, text="", style='TLabel', width=3)
        validation_label.pack(side=tk.LEFT)
        
        # Store reference for validation updates
        if param_name:
            self.validation_labels[param_name] = validation_label
        
        # Add keystroke validation
        if input_type == 'int':
            vcmd = (self.register(self._validate_int), '%P')
            entry.configure(validate='key', validatecommand=vcmd)
        elif input_type == 'float':
            vcmd = (self.register(self._validate_float), '%P')
            entry.configure(validate='key', validatecommand=vcmd)
    
    def _validate_field(self, param_name: str):
        """Validate field value and update visual indicator."""
        if param_name not in self.validation_labels:
            return
        
        # Map param_name to variable
        var_map = {
            'duration': self.duration_var,
            'initial_eggs': self.eggs_var,
            'initial_larvae': self.larvae_var,
            'initial_pupae': self.pupae_var,
            'initial_adults': self.adults_var,
            'temperature': self.temp_var,
            'humidity': self.humidity_var,
            'water_availability': self.water_var
        }
        
        variable = var_map.get(param_name)
        if not variable:
            return
        
        value_str = variable.get()
        if not value_str or value_str == "" or value_str == "-" or value_str == ".":
            # Empty or partial input - neutral
            self.validation_labels[param_name].config(text="", foreground=Colors.TEXT_SECONDARY)
            return
        
        try:
            value = float(value_str)
            is_valid, error_msg = validate_parameter(param_name, value)
            
            if is_valid:
                # Valid - show checkmark
                self.validation_labels[param_name].config(text="✓", foreground=Colors.SUCCESS)
                self.validation_labels[param_name].pack_configure()
            else:
                # Invalid - show warning
                self.validation_labels[param_name].config(text="⚠", foreground=Colors.WARNING)
                # Add tooltip with error message
                create_tooltip(self.validation_labels[param_name], error_msg, delay=100)
                
        except ValueError:
            # Parse error - show error
            self.validation_labels[param_name].config(text="✗", foreground=Colors.ERROR)
            
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
        """Handle species selection change.
        
        Note: Preserves all parameter values when switching species.
        Parameters are now species-independent.
        """
        # Simply log the species change without resetting parameters
        # To reset parameters use: self._load_defaults()
        species_display = self.species_var.get()
        if self.on_log:
            self.on_log(f"Especie cambiada a: {species_display}", "info")
        
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
