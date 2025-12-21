"""
Presentation Layer - Species Info View
=======================================

View for displaying species information and parameters.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing


class SpeciesView(ttk.Frame):
    """
    View for species information.
    
    Features:
    - Species selector
    - Biological parameters display
    - Life cycle information
    - References and sources
    """
    
    def __init__(
        self,
        parent,
        on_log: Optional[Callable[[str, str], None]] = None
    ):
        """
        Initialize species view.
        
        Args:
            parent: Parent widget
            on_log: Callback for logging (message, level)
        """
        super().__init__(parent, style='TFrame')
        
        self.on_log = on_log
        self.current_species = 'aedes_aegypti'
        
        self._setup_ui()
        self._load_species_info(self.current_species)
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_XLARGE, pady=Spacing.PADDING_XLARGE)
        
        # Header
        self._create_header(container)
        
        # Species selector
        self._create_species_selector(container)
        
        # Content area (two columns)
        content = ttk.Frame(container, style='TFrame')
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left column - General info and life cycle
        left_col = ttk.Frame(content, style='TFrame')
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, Spacing.PADDING_MEDIUM))
        
        self._create_general_info(left_col)
        self._create_life_cycle_info(left_col)
        
        # Right column - Parameters
        right_col = ttk.Frame(content, style='TFrame')
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(Spacing.PADDING_MEDIUM, 0))
        
        self._create_parameters_info(right_col)
        self._create_references_info(right_col)
        
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="🦟 Información de Especies",
            style='Title.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Description
        desc = ttk.Label(
            header,
            text="Consulte parámetros biológicos y características de las especies modeladas",
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY
        )
        desc.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.PADDING_MEDIUM)
        
    def _create_species_selector(self, parent):
        """Create species selector."""
        selector_frame = ttk.Frame(parent, style='TFrame')
        selector_frame.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Label
        label = ttk.Label(
            selector_frame,
            text="Seleccione una especie:",
            style='TLabel',
            font=Fonts.DEFAULT
        )
        label.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_MEDIUM))
        
        # Dropdown
        self.species_var = tk.StringVar(value='Aedes aegypti (Vector)')
        species_options = [
            'Aedes aegypti (Vector)',
            'Toxorhynchites (Depredador)'
        ]
        
        dropdown = ttk.Combobox(
            selector_frame,
            textvariable=self.species_var,
            values=species_options,
            state='readonly',
            width=30,
            font=Fonts.DEFAULT
        )
        dropdown.pack(side=tk.LEFT)
        dropdown.bind('<<ComboboxSelected>>', self._on_species_changed)
        
    def _create_general_info(self, parent):
        """Create general information panel."""
        panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        panel.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Title
        title = ttk.Label(
            panel,
            text="Información General",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Info text
        self.general_text = tk.Text(
            panel,
            height=10,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='disabled'
        )
        self.general_text.pack(fill=tk.BOTH, expand=True)
        
    def _create_life_cycle_info(self, parent):
        """Create life cycle information panel."""
        panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        panel.pack(fill=tk.BOTH, expand=True)
        panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Title
        title = ttk.Label(
            panel,
            text="Ciclo de Vida",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Life cycle text
        self.lifecycle_text = tk.Text(
            panel,
            height=12,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='disabled'
        )
        self.lifecycle_text.pack(fill=tk.BOTH, expand=True)
        
    def _create_parameters_info(self, parent):
        """Create parameters information panel."""
        panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        panel.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.PADDING_LARGE))
        panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Title
        title = ttk.Label(
            panel,
            text="Parámetros del Modelo",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Parameters text with scrollbar
        text_frame = ttk.Frame(panel, style='TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical')
        
        self.parameters_text = tk.Text(
            text_frame,
            height=15,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='disabled',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.parameters_text.yview)
        
        self.parameters_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_references_info(self, parent):
        """Create references panel."""
        panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        panel.pack(fill=tk.X)
        panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Title
        title = ttk.Label(
            panel,
            text="Referencias",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # References text
        self.references_text = tk.Text(
            panel,
            height=8,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='disabled'
        )
        self.references_text.pack(fill=tk.BOTH, expand=True)
        
    def _on_species_changed(self, event):
        """Handle species selection change."""
        species_display = self.species_var.get()
        
        if 'Aedes' in species_display:
            species_id = 'aedes_aegypti'
        else:
            species_id = 'toxorhynchites'
        
        self.current_species = species_id
        self._load_species_info(species_id)
        
        if self.on_log:
            self.on_log(f"Información cargada: {species_display}", "info")
        
    def _load_species_info(self, species_id: str):
        """Load species information."""
        if species_id == 'aedes_aegypti':
            self._load_aedes_info()
        else:
            self._load_toxorhynchites_info()
    
    def _load_aedes_info(self):
        """Load Aedes aegypti information."""
        # General info
        general = """Nombre Científico: Aedes aegypti (Linnaeus, 1762)
Nombre Común: Mosquito del dengue, mosquito de la fiebre amarilla
Familia: Culicidae
Orden: Diptera

Distribución: Zonas tropicales y subtropicales de todo el mundo
Hábitat: Áreas urbanas, criaderos artificiales (contenedores con agua estancada)

Importancia Médica:
Vector principal de dengue, zika, chikungunya y fiebre amarilla. Responsable de millones de infecciones anuales a nivel mundial.

Comportamiento:
- Actividad diurna (picos matutinos y vespertinos)
- Alimentación antropofílica (preferencia por sangre humana)
- Vuelo de corto alcance (50-100 metros típicamente)"""
        
        self._update_text_widget(self.general_text, general)
        
        # Life cycle
        lifecycle = """Metamorfosis Completa (Holometábolo):

1. HUEVO (2-7 días)
   - Oviposición en paredes de contenedores
   - Resistentes a desecación (hasta 1 año)
   - Eclosión al contacto con agua
   - Supervivencia: ~80%

2. LARVA (6-10 días total)
   - L1 (1-2 días): 1-2 mm, filtrador activo
   - L2 (1-2 días): 2-4 mm, desarrollo acelerado
   - L3 (2-3 días): 4-6 mm, vulnerable a depredación
   - L4 (2-4 días): 6-8 mm, fase pre-pupal
   - Supervivencia por estadio: 80-85%

3. PUPA (1-3 días)
   - No se alimenta, metamorfosis activa
   - Móvil, responde a estímulos
   - Supervivencia: ~90%

4. ADULTO (14-30 días)
   - Hembras: 5-7 mm, hematófagas
   - Machos: más pequeños, nectarívoros
   - Supervivencia diaria: ~95%
   - Capacidad reproductiva: 50-200 huevos/ciclo gonotrófico"""
        
        self._update_text_widget(self.lifecycle_text, lifecycle)
        
        # Parameters
        parameters = """TASAS DE DESARROLLO (25°C):
• Duración huevo: 2-4 días
• Duración L1-L4: 6-10 días (2.5 días promedio c/u)
• Duración pupa: 1-3 días
• Tiempo generacional: 10-17 días

SUPERVIVENCIA:
• Huevo → Larva: 80%
• Larva → Pupa: 80-85% por estadio
• Pupa → Adulto: 90%
• Adulto (diaria): 95%
• Huevo → Adulto: ~40-50%

REPRODUCCIÓN:
• Huevos por hembra: 50-200 por ciclo
• Ciclos gonotróficos: 3-5 en vida adulta
• Días entre oviposiciones: 2-4 días
• Proporción sexual: 1:1

EFECTOS AMBIENTALES:
• Temperatura óptima: 25-30°C
• Rango térmico: 15-40°C (desarrollo)
• Humedad mínima: >60% (supervivencia adulta)
• Disponibilidad de agua: Crítica para oviposición

DENSIDAD-DEPENDENCIA:
• Capacidad de carga: ~10,000 ind/criadero
• Competencia larval: Alta en L3-L4
• Mortalidad DD: Aumenta exponencialmente"""
        
        self._update_text_widget(self.parameters_text, parameters)
        
        # References
        references = """Fuentes Científicas:

[1] Yang, H.M., et al. (2009). "Assessing the effects of temperature on dengue transmission." Epidemiology & Infection, 137(8), 1179-1187.

[2] Focks, D.A., et al. (1993). "Dynamic life table model for Aedes aegypti." Journal of Medical Entomology, 30(6), 1003-1017.

[3] Brady, O.J., et al. (2013). "Global temperature constraints on Aedes aegypti and Ae. albopictus persistence." Parasites & Vectors, 6, 338.

[4] WHO (2020). "Dengue and severe dengue - Fact sheet." World Health Organization.

Datos de configuración basados en literatura científica revisada por pares y recomendaciones de la OMS."""
        
        self._update_text_widget(self.references_text, references)
    
    def _load_toxorhynchites_info(self):
        """Load Toxorhynchites information."""
        # General info
        general = """Nombre Científico: Toxorhynchites spp.
Nombre Común: Mosquito elefante, mosquito depredador
Familia: Culicidae
Orden: Diptera

Distribución: Regiones tropicales y subtropicales
Hábitat: Cavidades de árboles, contenedores grandes con agua

Importancia en Control Biológico:
Agente de control biológico natural de larvas de mosquitos vectores. Larvas depredadoras consumen hasta 20 larvas de Aedes por día.

Comportamiento:
- Adultos no hematófagos (no pican)
- Alimentación nectarívora
- Larvas depredadoras especializadas
- Mayor tamaño que vectores (10-18 mm adulto)"""
        
        self._update_text_widget(self.general_text, general)
        
        # Life cycle
        lifecycle = """Metamorfosis Completa (Holometábolo):

1. HUEVO (3-7 días)
   - Oviposición individual en criaderos
   - No resistentes a desecación
   - Supervivencia: ~85%

2. LARVA (15-25 días total)
   - L1 (2-4 días): 2-3 mm, aún no depredadora
   - L2 (3-5 días): 4-6 mm, inicio depredación
   - L3 (5-8 días): 8-12 mm, depredación activa (5-10 presas/día)
   - L4 (5-8 días): 12-18 mm, depredación máxima (10-20 presas/día)
   - Supervivencia: 90-95% con alimentación adecuada

3. PUPA (2-4 días)
   - Mayor tamaño que vectores
   - No se alimenta
   - Supervivencia: ~95%

4. ADULTO (20-40 días)
   - No hematófagos (machos y hembras)
   - Alimentación nectarívora
   - Mayor longevidad que vectores
   - Supervivencia diaria: ~98%
   - Capacidad reproductiva: 50-100 huevos/ciclo"""
        
        self._update_text_widget(self.lifecycle_text, lifecycle)
        
        # Parameters
        parameters = """TASAS DE DESARROLLO (25°C):
• Duración huevo: 3-7 días
• Duración L1-L4: 15-25 días (variable por alimentación)
• Duración pupa: 2-4 días
• Tiempo generacional: 25-40 días

SUPERVIVENCIA:
• Huevo → Larva: 85%
• Larva → Pupa: 90-95%
• Pupa → Adulto: 95%
• Adulto (diaria): 98%
• Huevo → Adulto: ~75%

DEPREDACIÓN:
• L3: 5-10 larvas de Aedes/día
• L4: 10-20 larvas de Aedes/día
• Preferencia: Larvas L1-L3 de vectores
• Canibalismo: Posible en alta densidad

REPRODUCCIÓN:
• Huevos por hembra: 50-100 por ciclo
• Ciclos reproductivos: 2-4 en vida adulta
• Días entre oviposiciones: 5-7 días
• Proporción sexual: 1:1

EFECTOS AMBIENTALES:
• Temperatura óptima: 25-28°C
• Rango térmico: 18-35°C
• Humedad mínima: >70%
• Disponibilidad de presas: Crítica"""
        
        self._update_text_widget(self.parameters_text, parameters)
        
        # References
        references = """Fuentes Científicas:

[1] Steffan, W.A., & Evenhuis, N.L. (1981). "Biology of Toxorhynchites." Annual Review of Entomology, 26, 159-181.

[2] Collins, L.E., & Blackwell, A. (2000). "The biology of Toxorhynchites mosquitoes and their potential as biocontrol agents." Biocontrol News and Information, 21(4), 105N-116N.

[3] Trpis, M. (1973). "Interaction between the predator Toxorhynchites and its prey Aedes aegypti." Bulletin of the World Health Organization, 49(4), 359.

[4] Focks, D.A., & Sackett, S.R. (1985). "Field experiments on the effect of Toxorhynchites amboinensis on Aedes aegypti." Medical and Veterinary Entomology, 1(2), 221-228.

Parámetros ajustados para simulación realista de control biológico."""
        
        self._update_text_widget(self.references_text, references)
    
    def _update_text_widget(self, widget: tk.Text, content: str):
        """Update text widget content."""
        widget.config(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert('1.0', content)
        widget.config(state='disabled')
