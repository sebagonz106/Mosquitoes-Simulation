"""
Presentation Layer - Checkpoints View
======================================

View for managing simulation checkpoints.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, TYPE_CHECKING
import sys
import os
from datetime import datetime
from pathlib import Path

if TYPE_CHECKING:
    from presentation.controllers.simulation_controller import SimulationController

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from presentation.styles.theme import Colors, Fonts, Spacing


class CheckpointsView(ttk.Frame):
    """
    View for checkpoint management.
    
    Features:
    - List saved checkpoints
    - Load checkpoint to continue simulation
    - Delete old checkpoints
    - Checkpoint metadata display
    """
    
    def __init__(
        self,
        parent,
        controller: Optional['SimulationController'] = None,
        on_log: Optional[Callable[[str, str], None]] = None,
        on_load_checkpoint: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize checkpoints view.
        
        Args:
            parent: Parent widget
            on_log: Callback for logging (message, level)
            on_load_checkpoint: Callback when checkpoint is loaded
        """
        super().__init__(parent, style='TFrame')
        
        self.on_log = on_log
        self.on_load_checkpoint = on_load_checkpoint
        self.controller = controller
        self.checkpoints = []  # List of checkpoint metadata
        
        self._setup_ui()
        self._load_checkpoints()
        
    def _setup_ui(self):
        """Setup UI components."""
        # Main container with padding
        container = ttk.Frame(self, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PADDING_XLARGE, pady=Spacing.PADDING_XLARGE)
        
        # Header
        self._create_header(container)
        
        # Checkpoint list
        self._create_checkpoint_list(container)
        
        # Checkpoint details
        self._create_details_panel(container)
        
    def _create_header(self, parent):
        """Create header section."""
        header = ttk.Frame(parent, style='TFrame')
        header.pack(fill=tk.X, pady=(0, Spacing.PADDING_LARGE))
        
        # Title
        title = ttk.Label(
            header,
            text="💾 Puntos de Guardado",
            style='Title.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W)
        
        # Description
        desc = ttk.Label(
            header,
            text="Gestione checkpoints de simulaciones para reanudar o comparar resultados",
            style='TLabel',
            foreground=Colors.TEXT_SECONDARY
        )
        desc.pack(anchor=tk.W, pady=(Spacing.PADDING_SMALL, 0))
        
        # Separator
        sep = ttk.Separator(header, orient='horizontal')
        sep.pack(fill=tk.X, pady=Spacing.PADDING_MEDIUM)
        
    def _create_checkpoint_list(self, parent):
        """Create checkpoint list panel."""
        list_panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        list_panel.pack(fill=tk.BOTH, expand=True, pady=(0, Spacing.PADDING_LARGE))
        list_panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Panel title
        title = ttk.Label(
            list_panel,
            text="Checkpoints Guardados",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Tree frame
        tree_frame = ttk.Frame(list_panel, style='TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient='vertical')
        hsb = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        # Treeview for checkpoints
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('name', 'date', 'species', 'duration', 'size'),
            show='tree headings',
            height=10,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Column configuration
        self.tree.heading('#0', text='ID')
        self.tree.heading('name', text='Nombre')
        self.tree.heading('date', text='Fecha')
        self.tree.heading('species', text='Especie')
        self.tree.heading('duration', text='Duración')
        self.tree.heading('size', text='Tamaño')
        
        self.tree.column('#0', width=50, stretch=False)
        self.tree.column('name', width=200)
        self.tree.column('date', width=150)
        self.tree.column('species', width=150)
        self.tree.column('duration', width=100)
        self.tree.column('size', width=100)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self._on_checkpoint_selected)
        
        # Button frame
        btn_frame = ttk.Frame(list_panel, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=(Spacing.PADDING_MEDIUM, 0))
        
        # Refresh button
        refresh_btn = ttk.Button(
            btn_frame,
            text="🔄 Actualizar",
            style='Secondary.TButton',
            command=self._load_checkpoints
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        # Load button
        self.load_btn = ttk.Button(
            btn_frame,
            text="📂 Cargar",
            style='TButton',
            command=self._load_selected_checkpoint,
            state='disabled'
        )
        self.load_btn.pack(side=tk.LEFT, padx=(0, Spacing.PADDING_SMALL))
        
        # Delete button
        self.delete_btn = ttk.Button(
            btn_frame,
            text="🗑️ Eliminar",
            style='Secondary.TButton',
            command=self._delete_selected_checkpoint,
            state='disabled'
        )
        self.delete_btn.pack(side=tk.LEFT)
        
    def _create_details_panel(self, parent):
        """Create checkpoint details panel."""
        details_panel = ttk.Frame(parent, style='Card.TFrame', relief='solid', borderwidth=1)
        details_panel.pack(fill=tk.X)
        details_panel.configure(padding=Spacing.PADDING_LARGE)
        
        # Panel title
        title = ttk.Label(
            details_panel,
            text="Detalles del Checkpoint",
            style='Heading.TLabel',
            foreground=Colors.PRIMARY
        )
        title.pack(anchor=tk.W, pady=(0, Spacing.PADDING_MEDIUM))
        
        # Details text
        self.details_text = tk.Text(
            details_panel,
            height=8,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_PRIMARY,
            relief='flat',
            borderwidth=0,
            wrap=tk.WORD,
            state='disabled'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self._update_details_text("Seleccione un checkpoint para ver los detalles")
        
    def _load_checkpoints(self):
        """Load list of available checkpoints."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.controller:
            if self.on_log:
                self.on_log("No se puede cargar checkpoints: controller no disponible", "error")
            return
        
        try:
            # Load real checkpoints from service
            checkpoints_data = self.controller.list_checkpoints()
            
            if not checkpoints_data:
                if self.on_log:
                    self.on_log("No hay checkpoints guardados", "info")
                return
            
            # Store checkpoints
            self.checkpoints = checkpoints_data
            
            # Add to tree
            for i, cp in enumerate(checkpoints_data):
                # Format size
                file_path = Path(cp['path'])
                size_bytes = file_path.stat().st_size if file_path.exists() else 0
                size_mb = size_bytes / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
                
                # Format date
                timestamp = cp.get('timestamp', '')
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp)
                        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        date_str = timestamp
                else:
                    date_str = "N/A"
                
                # Format duration
                duration = cp.get('duration', 0)
                duration_str = f"{duration} días"
                
                # Format species
                species = cp.get('species', 'N/A')
                if species == 'aedes_aegypti':
                    species_display = 'Aedes aegypti'
                elif species == 'toxorhynchites':
                    species_display = 'Toxorhynchites'
                else:
                    species_display = species
                
                self.tree.insert(
                    '',
                    'end',
                    text=str(i + 1),
                    values=(cp['filename'], date_str, species_display, duration_str, size_str),
                    tags=(str(i),)
                )
            
            if self.on_log:
                self.on_log(f"{len(checkpoints_data)} checkpoints encontrados", "info")
                
        except Exception as e:
            if self.on_log:
                self.on_log(f"Error cargando checkpoints: {str(e)}", "error")
        
    def _on_checkpoint_selected(self, event):
        """Handle checkpoint selection."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            checkpoint_index = int(item['text']) - 1  # Convert to 0-based index
            
            # Find checkpoint details
            if 0 <= checkpoint_index < len(self.checkpoints):
                checkpoint = self.checkpoints[checkpoint_index]
                
                details = f"Archivo: {checkpoint['filename']}\n"
                details += f"Fecha: {checkpoint.get('timestamp', 'N/A')}\n"
                details += f"Especie: {checkpoint.get('species', 'N/A')}\n"
                details += f"Duración: {checkpoint.get('duration', 0)} días\n"
                details += f"Tipo: {checkpoint.get('simulation_type', 'N/A')}\n"
                details += f"Ruta: {checkpoint['path']}"
                
                self._update_details_text(details)
                
                # Enable buttons
                self.load_btn.config(state='normal')
                self.delete_btn.config(state='normal')
        else:
            self._update_details_text("Seleccione un checkpoint para ver los detalles")
            self.load_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
    
    def _update_details_text(self, text: str):
        """Update details text widget."""
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', text)
        self.details_text.config(state='disabled')
        
    def _load_selected_checkpoint(self):
        """Load the selected checkpoint."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        checkpoint_index = int(item['text']) - 1
        
        if 0 <= checkpoint_index < len(self.checkpoints):
            checkpoint = self.checkpoints[checkpoint_index]
            checkpoint_name = checkpoint['filename']
            checkpoint_path = checkpoint['path']
            
            if messagebox.askyesno(
                "Cargar Checkpoint",
                f"¿Desea cargar el checkpoint '{checkpoint_name}'?"
            ):
                try:
                    if self.on_log:
                        self.on_log(f"Cargando checkpoint '{checkpoint_name}'...", "info")
                    
                    if self.on_load_checkpoint:
                        self.on_load_checkpoint(checkpoint_path)
                    
                    if self.on_log:
                        self.on_log(f"Checkpoint '{checkpoint_name}' cargado correctamente", "success")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error cargando checkpoint:\n{str(e)}")
                    if self.on_log:
                        self.on_log(f"Error cargando checkpoint: {str(e)}", "error")
    
    def _delete_selected_checkpoint(self):
        """Delete the selected checkpoint."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        checkpoint_index = int(item['text']) - 1
        
        if 0 <= checkpoint_index < len(self.checkpoints):
            checkpoint = self.checkpoints[checkpoint_index]
            checkpoint_name = checkpoint['filename']
            checkpoint_path = Path(checkpoint['path'])
            
            if messagebox.askyesno(
                "Eliminar Checkpoint",
                f"¿Está seguro que desea eliminar el checkpoint '{checkpoint_name}'?\n\n"
                "Esta acción no se puede deshacer."
            ):
                try:
                    # Delete file
                    if checkpoint_path.exists():
                        checkpoint_path.unlink()
                        
                        if self.on_log:
                            self.on_log(f"Checkpoint '{checkpoint_name}' eliminado", "success")
                        
                        # Reload list
                        self._load_checkpoints()
                    else:
                        messagebox.showwarning("Advertencia", "El archivo no existe")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error eliminando checkpoint:\n{str(e)}")
                    if self.on_log:
                        self.on_log(f"Error eliminando checkpoint: {str(e)}", "error")
