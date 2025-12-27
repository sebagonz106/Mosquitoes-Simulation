"""
Presentation Layer - Predator-Prey Simulation View
===================================================

View for configuring and running predator-prey simulations with:
- Dual species parameter configuration (prey and predator)
- Shared environmental parameters
- Preset scenarios for predator-prey interactions
- Comparison with/without predators
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing
from presentation.controllers.predator_prey_controller import PredatorPreyController
from presentation.data.scenario_presets import (
    ENVIRONMENTAL_PRESETS,
    PREDATOR_PREY_PRESETS,
    get_environmental_preset_by_name,
    get_predator_prey_preset_by_name,
    get_all_environmental_preset_names,
    get_all_predator_prey_preset_names,
    validate_parameter
)
from application.dtos import PredatorPreyConfig


class PredatorPreyView(ttk.Frame):
    """
    View for predator-prey simulation configuration and execution.
    
    Features:
    - Dual species selection (prey and predator)
    - Shared environmental parameters with presets
    - Predator-prey population presets
    - Comparison with/without predators
    - Real-time parameter validation
    - Results visualization and export
    """
    
    def __init__(
        self,
        parent,
        controller: PredatorPreyController,
        on_results: Optional[Callable] = None,
        on_log: Optional[Callable[[str, str], None]] = None
    ):
        """
        Initialize predator-prey view.
        
        Args:
            parent: Parent widget
            controller: PredatorPreyController instance
            on_results: Callback when simulation completes (result)
            on_log: Callback for logging (message, level)
        """
        super().__init__(parent, style='TFrame')
        
        self.controller = controller
        self.on_results = on_results
        self.on_log = on_log
        
        # Form variables - Environmental (SHARED)
        self.duration_var = tk.StringVar(value='90')
        self.temp_var = tk.StringVar(value='28.0')
        self.humidity_var = tk.StringVar(value='80.0')
        self.water_var = tk.StringVar(value='1.0')
        
        # Form variables - Prey
        self.prey_species_var = tk.StringVar(value='aedes_aegypti')
        self.prey_eggs_var = tk.StringVar(value='1000')
        self.prey_larvae_var = tk.StringVar(value='500')
        self.prey_pupae_var = tk.StringVar(value='100')
        self.prey_adults_var = tk.StringVar(value='100')
        
        # Form variables - Predator
        self.predator_species_var = tk.StringVar(value='toxorhynchites')
        self.predator_larvae_var = tk.StringVar(value='20')
        self.predator_pupae_var = tk.StringVar(value='5')
        self.predator_adults_var = tk.StringVar(value='10')
        
        # Preset variables
        self.env_preset_var = tk.StringVar(value='(Personalizado)')
        self.pp_preset_var = tk.StringVar(value='(Personalizado)')
        
        # Validation status tracking
        self.validation_labels: Dict[str, ttk.Label] = {}
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=Spacing.LARGE, pady=Spacing.LARGE)
        
        # ====== PRESETS SECTION ======
        self._create_presets_section(main_frame)
        
        # ====== ENVIRONMENTAL PARAMETERS SECTION (SHARED) ======
        self._create_environmental_section(main_frame)
        
        # ====== SPECIES & POPULATIONS SECTION (DUAL) ======
        self._create_species_populations_section(main_frame)
        
        # ====== BUTTONS SECTION ======
        self._create_buttons_section(main_frame)
    
    def _create_presets_section(self, parent):
        """Create presets selection section."""
        frame = ttk.LabelFrame(parent, text='Presets', style='TLabelframe')
        frame.pack(fill='x', pady=(0, Spacing.LARGE))
        
        # Environmental presets
        ttk.Label(frame, text='Parámetros Ambientales:').pack(anchor='w', padx=Spacing.MEDIUM, pady=(Spacing.MEDIUM, 0))
        env_combo = ttk.Combobox(
            frame,
            textvariable=self.env_preset_var,
            values=['(Personalizado)'] + get_all_environmental_preset_names(),
            state='readonly',
            width=40
        )
        env_combo.pack(padx=Spacing.MEDIUM, pady=Spacing.SMALL, fill='x')
        env_combo.bind('<<ComboboxSelected>>', self._on_env_preset_selected)
        
        # Predator-prey presets
        ttk.Label(frame, text='Población Presa-Depredador:').pack(anchor='w', padx=Spacing.MEDIUM, pady=(Spacing.MEDIUM, 0))
        pp_combo = ttk.Combobox(
            frame,
            textvariable=self.pp_preset_var,
            values=['(Personalizado)'] + get_all_predator_prey_preset_names(),
            state='readonly',
            width=40
        )
        pp_combo.pack(padx=Spacing.MEDIUM, pady=Spacing.SMALL, fill='x')
        pp_combo.bind('<<ComboboxSelected>>', self._on_pp_preset_selected)
    
    def _create_environmental_section(self, parent):
        """Create environmental parameters section (SHARED)."""
        frame = ttk.LabelFrame(parent, text='Parámetros Ambientales (Compartidos)', style='TLabelframe')
        frame.pack(fill='x', pady=(0, Spacing.LARGE))
        
        # Create grid
        inner_frame = ttk.Frame(frame)
        inner_frame.pack(fill='x', padx=Spacing.MEDIUM, pady=Spacing.MEDIUM)
        
        # Duration
        ttk.Label(inner_frame, text='Duración (días):').grid(row=0, column=0, sticky='w', padx=(0, Spacing.MEDIUM))
        duration_entry = ttk.Entry(inner_frame, textvariable=self.duration_var, width=10)
        duration_entry.grid(row=0, column=1, sticky='w')
        duration_entry.bind('<KeyRelease>', lambda e: self._validate_field('duration'))
        self.validation_labels['duration'] = ttk.Label(inner_frame, text='', foreground=Colors.ERROR)
        self.validation_labels['duration'].grid(row=0, column=2, padx=Spacing.SMALL)
        
        # Temperature
        ttk.Label(inner_frame, text='Temperatura (°C):').grid(row=1, column=0, sticky='w', padx=(0, Spacing.MEDIUM), pady=(Spacing.MEDIUM, 0))
        temp_entry = ttk.Entry(inner_frame, textvariable=self.temp_var, width=10)
        temp_entry.grid(row=1, column=1, sticky='w', pady=(Spacing.MEDIUM, 0))
        temp_entry.bind('<KeyRelease>', lambda e: self._validate_field('temperature'))
        self.validation_labels['temperature'] = ttk.Label(inner_frame, text='', foreground=Colors.ERROR)
        self.validation_labels['temperature'].grid(row=1, column=2, padx=Spacing.SMALL, pady=(Spacing.MEDIUM, 0))
        
        # Humidity
        ttk.Label(inner_frame, text='Humedad (%):').grid(row=2, column=0, sticky='w', padx=(0, Spacing.MEDIUM), pady=(Spacing.MEDIUM, 0))
        humidity_entry = ttk.Entry(inner_frame, textvariable=self.humidity_var, width=10)
        humidity_entry.grid(row=2, column=1, sticky='w', pady=(Spacing.MEDIUM, 0))
        humidity_entry.bind('<KeyRelease>', lambda e: self._validate_field('humidity'))
        self.validation_labels['humidity'] = ttk.Label(inner_frame, text='', foreground=Colors.ERROR)
        self.validation_labels['humidity'].grid(row=2, column=2, padx=Spacing.SMALL, pady=(Spacing.MEDIUM, 0))
        
        # Water availability
        ttk.Label(inner_frame, text='Disponibilidad de agua:').grid(row=3, column=0, sticky='w', padx=(0, Spacing.MEDIUM), pady=(Spacing.MEDIUM, 0))
        water_entry = ttk.Entry(inner_frame, textvariable=self.water_var, width=10)
        water_entry.grid(row=3, column=1, sticky='w', pady=(Spacing.MEDIUM, 0))
        water_entry.bind('<KeyRelease>', lambda e: self._validate_field('water_availability'))
        self.validation_labels['water_availability'] = ttk.Label(inner_frame, text='', foreground=Colors.ERROR)
        self.validation_labels['water_availability'].grid(row=3, column=2, padx=Spacing.SMALL, pady=(Spacing.MEDIUM, 0))
    
    def _create_species_populations_section(self, parent):
        """Create dual species and populations section."""
        frame = ttk.LabelFrame(parent, text='Especies y Poblaciones Iniciales', style='TLabelframe')
        frame.pack(fill='both', expand=True, pady=(0, Spacing.LARGE))
        
        # Create two columns: Prey (left) and Predator (right)
        left_frame = ttk.LabelFrame(frame, text='PRESA (Aedes aegypti)', style='TLabelframe')
        left_frame.pack(side='left', fill='both', expand=True, padx=(Spacing.MEDIUM, Spacing.SMALL), pady=Spacing.MEDIUM)
        
        right_frame = ttk.LabelFrame(frame, text='DEPREDADOR (Toxorhynchites)', style='TLabelframe')
        right_frame.pack(side='right', fill='both', expand=True, padx=(Spacing.SMALL, Spacing.MEDIUM), pady=Spacing.MEDIUM)
        
        # LEFT COLUMN: PREY
        self._create_prey_section(left_frame)
        
        # RIGHT COLUMN: PREDATOR
        self._create_predator_section(right_frame)
    
    def _create_prey_section(self, parent):
        """Create prey species configuration."""
        # Species selection (read-only for now, only Aedes)
        ttk.Label(parent, text='Especie:').pack(anchor='w', padx=Spacing.MEDIUM, pady=(Spacing.MEDIUM, 0))
        ttk.Label(parent, text='Aedes aegypti', foreground=Colors.INFO).pack(anchor='w', padx=Spacing.MEDIUM + 10, pady=(0, Spacing.MEDIUM))
        
        # Populations
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill='x', padx=Spacing.MEDIUM, pady=(0, Spacing.MEDIUM))
        
        fields = [
            ('Huevos:', self.prey_eggs_var, 'initial_eggs'),
            ('Larvas:', self.prey_larvae_var, 'initial_larvae'),
            ('Pupas:', self.prey_pupae_var, 'initial_pupae'),
            ('Adultos:', self.prey_adults_var, 'initial_adults'),
        ]
        
        for i, (label, var, field) in enumerate(fields):
            ttk.Label(grid_frame, text=label).grid(row=i, column=0, sticky='w', pady=(0, Spacing.SMALL))
            entry = ttk.Entry(grid_frame, textvariable=var, width=12)
            entry.grid(row=i, column=1, sticky='w', padx=(Spacing.SMALL, 0), pady=(0, Spacing.SMALL))
            entry.bind('<KeyRelease>', lambda e, f=field: self._validate_field(f'prey_{f}' if f != 'species' else f))
            self.validation_labels[f'prey_{field}'] = ttk.Label(grid_frame, text='', foreground=Colors.ERROR)
            self.validation_labels[f'prey_{field}'].grid(row=i, column=2, padx=Spacing.SMALL, pady=(0, Spacing.SMALL))
    
    def _create_predator_section(self, parent):
        """Create predator species configuration."""
        # Species selection (read-only for now, only Toxorhynchites)
        ttk.Label(parent, text='Especie:').pack(anchor='w', padx=Spacing.MEDIUM, pady=(Spacing.MEDIUM, 0))
        ttk.Label(parent, text='Toxorhynchites spp.', foreground=Colors.SUCCESS).pack(anchor='w', padx=Spacing.MEDIUM + 10, pady=(0, Spacing.MEDIUM))
        
        # Populations
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill='x', padx=Spacing.MEDIUM, pady=(0, Spacing.MEDIUM))
        
        fields = [
            ('Larvas:', self.predator_larvae_var, 'larvae'),
            ('Pupas:', self.predator_pupae_var, 'pupae'),
            ('Adultos:', self.predator_adults_var, 'adults'),
        ]
        
        for i, (label, var, field) in enumerate(fields):
            ttk.Label(grid_frame, text=label).grid(row=i, column=0, sticky='w', pady=(0, Spacing.SMALL))
            entry = ttk.Entry(grid_frame, textvariable=var, width=12)
            entry.grid(row=i, column=1, sticky='w', padx=(Spacing.SMALL, 0), pady=(0, Spacing.SMALL))
            entry.bind('<KeyRelease>', lambda e, f=field: self._validate_field(f'predator_{f}'))
            self.validation_labels[f'predator_{field}'] = ttk.Label(grid_frame, text='', foreground=Colors.ERROR)
            self.validation_labels[f'predator_{field}'].grid(row=i, column=2, padx=Spacing.SMALL, pady=(0, Spacing.SMALL))
    
    def _create_buttons_section(self, parent):
        """Create buttons section."""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=(Spacing.LARGE, 0))
        
        # Run button
        self.run_button = ttk.Button(frame, text='Ejecutar Simulación', command=self._on_run_clicked)
        self.run_button.pack(side='left', padx=(0, Spacing.MEDIUM))
    
    def _on_env_preset_selected(self, event):
        """Handle environmental preset selection."""
        preset_name = self.env_preset_var.get()
        if preset_name == '(Personalizado)':
            return
        
        preset = get_environmental_preset_by_name(preset_name)
        if preset:
            self.temp_var.set(str(preset['temperature']))
            self.humidity_var.set(str(preset['humidity']))
            self.water_var.set(str(preset['water_availability']))
    
    def _on_pp_preset_selected(self, event):
        """Handle predator-prey preset selection."""
        preset_name = self.pp_preset_var.get()
        if preset_name == '(Personalizado)':
            return
        
        preset = get_predator_prey_preset_by_name(preset_name)
        if preset:
            self.duration_var.set(str(preset.duration))
            self.prey_eggs_var.set(str(preset.prey_initial_eggs))
            self.prey_larvae_var.set(str(preset.prey_initial_larvae))
            self.prey_pupae_var.set(str(preset.prey_initial_pupae))
            self.prey_adults_var.set(str(preset.prey_initial_adults))
            self.predator_larvae_var.set(str(preset.predator_initial_larvae))
            self.predator_pupae_var.set(str(preset.predator_initial_pupae))
            self.predator_adults_var.set(str(preset.predator_initial_adults))
            self.temp_var.set(str(preset.temperature))
            self.humidity_var.set(str(preset.humidity))
            self.water_var.set(str(preset.water_availability))
    
    def _validate_field(self, field_name: str):
        """Validate a single field."""
        # Map field names to variables and validation keys
        field_map = {
            'duration': (self.duration_var, 'duration'),
            'temperature': (self.temp_var, 'temperature'),
            'humidity': (self.humidity_var, 'humidity'),
            'water_availability': (self.water_var, 'water_availability'),
            'prey_initial_eggs': (self.prey_eggs_var, 'initial_eggs'),
            'prey_initial_larvae': (self.prey_larvae_var, 'initial_larvae'),
            'prey_initial_pupae': (self.prey_pupae_var, 'initial_pupae'),
            'prey_initial_adults': (self.prey_adults_var, 'initial_adults'),
            'predator_larvae': (self.predator_larvae_var, 'initial_larvae'),
            'predator_pupae': (self.predator_pupae_var, 'initial_pupae'),
            'predator_adults': (self.predator_adults_var, 'initial_adults'),
        }
        
        if field_name not in field_map:
            return
        
        var, val_key = field_map[field_name]
        try:
            value = float(var.get())
            is_valid, error_msg = validate_parameter(val_key, value)
            
            if is_valid:
                self.validation_labels[field_name].config(text='✓')
            else:
                self.validation_labels[field_name].config(text=f'✗ {error_msg}')
        except ValueError:
            self.validation_labels[field_name].config(text='✗ Número inválido')
    
    def _on_run_clicked(self):
        """Handle run button click."""
        try:
            # Build configuration
            config = PredatorPreyConfig(
                species_id=self.prey_species_var.get(),
                predator_species_id=self.predator_species_var.get(),
                duration_days=int(self.duration_var.get()),
                initial_eggs=int(self.prey_eggs_var.get()),
                initial_larvae=int(self.prey_larvae_var.get()),
                initial_pupae=int(self.prey_pupae_var.get()),
                initial_adults=int(self.prey_adults_var.get()),
                temperature=float(self.temp_var.get()),
                humidity=float(self.humidity_var.get()),
                water_availability=float(self.water_var.get()),
                predator_initial_larvae=int(self.predator_larvae_var.get()),
                predator_initial_pupae=int(self.predator_pupae_var.get()),
                predator_initial_adults=int(self.predator_adults_var.get()),
            )
            
            # Validate
            is_valid, errors = config.validate()
            if not is_valid:
                messagebox.showerror('Validación Fallida', '\n'.join(errors))
                return
            
            # Run simulation
            self.run_button.config(state='disabled')
            self.update()  # Force UI update
            
            try:
                # Always run comparison (with and without predators)
                result = self.controller.run_predator_prey_comparison(config)
                if self.on_log:
                    self.on_log('Comparación completada: con y sin depredadores', 'info')
                
                # Callback with results (will trigger results view in main.py)
                if self.on_results:
                    self.on_results(result)
                    
            except Exception as e:
                # Only re-enable button if there was an error
                if self.winfo_exists():
                    self.run_button.config(state='normal')
                raise
                
        except Exception as e:
            messagebox.showerror('Error en Simulación', str(e))
            if self.on_log:
                self.on_log(f'Error: {str(e)}', 'error')
