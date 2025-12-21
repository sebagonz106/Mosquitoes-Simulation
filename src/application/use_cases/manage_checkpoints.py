"""
Use Cases para gestión de checkpoints de simulaciones.

Este módulo implementa los casos de uso relacionados con guardar, cargar,
listar y eliminar checkpoints de simulaciones.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple
import os
import json

from application.use_cases.base import UseCase
from application.services.simulation_service import SimulationService
from application.dtos import PopulationResult, AgentResult, HybridResult, SimulationConfig


# ============================================================================
# DTOs para SaveCheckpoint
# ============================================================================

@dataclass
class SaveCheckpointRequest:
    """Request para guardar un checkpoint de simulación."""
    
    result: Union[PopulationResult, AgentResult, HybridResult]
    config: SimulationConfig
    simulation_type: str  # 'population', 'agent', 'hybrid'
    checkpoint_name: Optional[str] = None


@dataclass
class SaveCheckpointResponse:
    """Response del guardado de checkpoint."""
    
    success: bool
    checkpoint_path: Optional[Path] = None
    timestamp: Optional[str] = None
    error_message: Optional[str] = None


# ============================================================================
# DTOs para LoadCheckpoint
# ============================================================================

@dataclass
class LoadCheckpointRequest:
    """Request para cargar un checkpoint."""
    
    checkpoint_path: Path


@dataclass
class LoadCheckpointResponse:
    """Response de carga de checkpoint."""
    
    success: bool
    config: Optional[SimulationConfig] = None
    result: Optional[Union[PopulationResult, AgentResult, HybridResult]] = None
    simulation_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# ============================================================================
# DTOs para ListCheckpoints
# ============================================================================

@dataclass
class CheckpointInfo:
    """Información resumida de un checkpoint."""
    
    path: Path
    timestamp: str
    species_id: str
    simulation_type: str
    duration_days: int


@dataclass
class ListCheckpointsRequest:
    """Request para listar checkpoints."""
    
    species_id: Optional[str] = None
    simulation_type: Optional[str] = None


@dataclass
class ListCheckpointsResponse:
    """Response con lista de checkpoints."""
    
    success: bool
    checkpoints: List[CheckpointInfo]
    count: int
    error_message: Optional[str] = None


# ============================================================================
# DTOs para DeleteCheckpoint
# ============================================================================

@dataclass
class DeleteCheckpointRequest:
    """Request para eliminar un checkpoint."""
    
    checkpoint_path: Path


@dataclass
class DeleteCheckpointResponse:
    """Response de eliminación de checkpoint."""
    
    success: bool
    deleted_path: Optional[Path] = None
    error_message: Optional[str] = None


# ============================================================================
# Use Case: SaveCheckpoint
# ============================================================================

class SaveCheckpoint(UseCase[SaveCheckpointRequest, SaveCheckpointResponse]):
    """
    Caso de uso para guardar checkpoints de simulaciones.
    
    Valida los parámetros y delega el guardado al SimulationService.
    """
    
    VALID_SIMULATION_TYPES = {'population', 'agent', 'hybrid'}
    
    def __init__(self, simulation_service: SimulationService):
        """
        Inicializa el caso de uso.
        
        Args:
            simulation_service: Servicio de simulación con capacidad de checkpointing
        """
        self.simulation_service = simulation_service
    
    def validate_request(self, request: SaveCheckpointRequest) -> None:
        """
        Valida el request de guardado.
        
        Args:
            request: Request a validar
            
        Raises:
            ValueError: Si la validación falla
        """
        # Validar result no es None
        if request.result is None:
            raise ValueError("El resultado de simulación no puede ser None")
        
        # Validar config no es None
        if request.config is None:
            raise ValueError("La configuración de simulación no puede ser None")
        
        # Validar simulation_type
        if request.simulation_type not in self.VALID_SIMULATION_TYPES:
            raise ValueError(
                f"Tipo de simulación inválido: {request.simulation_type}. "
                f"Debe ser uno de: {', '.join(self.VALID_SIMULATION_TYPES)}"
            )
        
        # Validar checkpoint_name si está presente
        if request.checkpoint_name is not None:
            if not isinstance(request.checkpoint_name, str):
                raise ValueError("El nombre del checkpoint debe ser un string")
            
            if not request.checkpoint_name.strip():
                raise ValueError("El nombre del checkpoint no puede estar vacío")
            
            # Validar caracteres permitidos (alfanuméricos, guiones, underscores, punto)
            import re
            if not re.match(r'^[\w\-\.]+$', request.checkpoint_name):
                raise ValueError(
                    "El nombre del checkpoint solo puede contener letras, números, "
                    "guiones, underscores y puntos"
                )
    
    def _execute(self, request: SaveCheckpointRequest) -> SaveCheckpointResponse:
        """
        Ejecuta el guardado del checkpoint.
        
        Args:
            request: Datos para guardar
            
        Returns:
            Response con información del checkpoint guardado
        """
        try:
            # Guardar checkpoint usando el servicio
            checkpoint_path = self.simulation_service.save_checkpoint(
                result=request.result,
                config=request.config,
                simulation_type=request.simulation_type,
                checkpoint_name=request.checkpoint_name
            )
            
            # Extraer timestamp del nombre del archivo
            # Formato: species_timestamp_counter.json
            filename = checkpoint_path.stem  # sin extensión
            parts = filename.split('_')
            
            # El timestamp está después del species_id
            # Ejemplo: aedes_aegypti_20260111_103045_123456_1.json
            # Buscar el patrón de fecha/hora
            timestamp_str = None
            for i in range(len(parts) - 3):
                # Intentar reconstruir timestamp
                potential_timestamp = f"{parts[i]}_{parts[i+1]}_{parts[i+2]}"
                if len(parts[i]) == 8 and len(parts[i+1]) == 6:  # YYYYMMDD_HHMMSS
                    timestamp_str = potential_timestamp
                    break
            
            return SaveCheckpointResponse(
                success=True,
                checkpoint_path=checkpoint_path,
                timestamp=timestamp_str or "unknown"
            )
        
        except Exception as e:
            return SaveCheckpointResponse(
                success=False,
                error_message=f"Error al guardar checkpoint: {str(e)}"
            )


# ============================================================================
# Use Case: LoadCheckpoint
# ============================================================================

class LoadCheckpoint(UseCase[LoadCheckpointRequest, LoadCheckpointResponse]):
    """
    Caso de uso para cargar checkpoints guardados.
    
    Valida la existencia del archivo y delega la carga al SimulationService.
    """
    
    def __init__(self, simulation_service: SimulationService):
        """
        Inicializa el caso de uso.
        
        Args:
            simulation_service: Servicio de simulación con capacidad de checkpointing
        """
        self.simulation_service = simulation_service
    
    def validate_request(self, request: LoadCheckpointRequest) -> None:
        """
        Valida el request de carga.
        
        Args:
            request: Request a validar
            
        Raises:
            ValueError: Si la validación falla
        """
        # Validar que checkpoint_path no es None
        if request.checkpoint_path is None:
            raise ValueError("La ruta del checkpoint no puede ser None")
        
        # Convertir a Path si es string
        if isinstance(request.checkpoint_path, str):
            request.checkpoint_path = Path(request.checkpoint_path)
        
        # Validar que el archivo existe
        if not request.checkpoint_path.exists():
            raise ValueError(
                f"El archivo de checkpoint no existe: {request.checkpoint_path}"
            )
        
        # Validar que es un archivo (no directorio)
        if not request.checkpoint_path.is_file():
            raise ValueError(
                f"La ruta no es un archivo: {request.checkpoint_path}"
            )
        
        # Validar extensión .json
        if request.checkpoint_path.suffix.lower() != '.json':
            raise ValueError(
                f"El checkpoint debe ser un archivo JSON: {request.checkpoint_path}"
            )
    
    def _execute(self, request: LoadCheckpointRequest) -> LoadCheckpointResponse:
        """
        Ejecuta la carga del checkpoint.
        
        Args:
            request: Datos de carga
            
        Returns:
            Response con datos del checkpoint cargado
        """
        try:
            # Cargar checkpoint usando el servicio
            config, result, simulation_type = self.simulation_service.load_checkpoint(
                request.checkpoint_path
            )
            
            # Extraer metadata básica del checkpoint
            with open(request.checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            metadata = {
                'timestamp': checkpoint_data.get('timestamp', 'unknown'),
                'simulation_type': checkpoint_data.get('simulation_type', simulation_type),
                'species_id': config.species_id,
                'duration_days': config.duration_days
            }
            
            return LoadCheckpointResponse(
                success=True,
                config=config,
                result=result,
                simulation_type=simulation_type,
                metadata=metadata
            )
        
        except json.JSONDecodeError as e:
            return LoadCheckpointResponse(
                success=False,
                error_message=f"Error al decodificar JSON: {str(e)}"
            )
        
        except Exception as e:
            return LoadCheckpointResponse(
                success=False,
                error_message=f"Error al cargar checkpoint: {str(e)}"
            )


# ============================================================================
# Use Case: ListCheckpoints
# ============================================================================

class ListCheckpoints(UseCase[ListCheckpointsRequest, ListCheckpointsResponse]):
    """
    Caso de uso para listar checkpoints guardados.
    
    Permite filtrar por especie y tipo de simulación.
    """
    
    VALID_SIMULATION_TYPES = {'population', 'agent', 'hybrid'}
    
    def __init__(self, simulation_service: SimulationService):
        """
        Inicializa el caso de uso.
        
        Args:
            simulation_service: Servicio de simulación con capacidad de checkpointing
        """
        self.simulation_service = simulation_service
    
    def validate_request(self, request: ListCheckpointsRequest) -> None:
        """
        Valida el request de listado.
        
        Args:
            request: Request a validar
            
        Raises:
            ValueError: Si la validación falla
        """
        # Validar simulation_type si está presente
        if request.simulation_type is not None:
            if request.simulation_type not in self.VALID_SIMULATION_TYPES:
                raise ValueError(
                    f"Tipo de simulación inválido: {request.simulation_type}. "
                    f"Debe ser uno de: {', '.join(self.VALID_SIMULATION_TYPES)}"
                )
        
        # Validar species_id si está presente
        if request.species_id is not None:
            if not isinstance(request.species_id, str):
                raise ValueError("El species_id debe ser un string")
            
            if not request.species_id.strip():
                raise ValueError("El species_id no puede estar vacío")
    
    def _execute(self, request: ListCheckpointsRequest) -> ListCheckpointsResponse:
        """
        Ejecuta el listado de checkpoints.
        
        Args:
            request: Parámetros de filtrado
            
        Returns:
            Response con lista de checkpoints
        """
        try:
            # Listar checkpoints usando el servicio
            checkpoints_data = self.simulation_service.list_checkpoints(
                species=request.species_id,
                simulation_type=request.simulation_type
            )
            
            # Convertir a CheckpointInfo
            checkpoints = []
            for cp_data in checkpoints_data:
                info = CheckpointInfo(
                    path=cp_data['path'],
                    timestamp=cp_data['timestamp'],
                    species_id=cp_data['species'],
                    simulation_type=cp_data['simulation_type'],
                    duration_days=cp_data['duration_days']
                )
                checkpoints.append(info)
            
            return ListCheckpointsResponse(
                success=True,
                checkpoints=checkpoints,
                count=len(checkpoints)
            )
        
        except Exception as e:
            return ListCheckpointsResponse(
                success=False,
                checkpoints=[],
                count=0,
                error_message=f"Error al listar checkpoints: {str(e)}"
            )


# ============================================================================
# Use Case: DeleteCheckpoint
# ============================================================================

class DeleteCheckpoint(UseCase[DeleteCheckpointRequest, DeleteCheckpointResponse]):
    """
    Caso de uso para eliminar checkpoints.
    
    Valida que el archivo existe y está dentro del directorio de checkpoints
    para seguridad.
    """
    
    def __init__(self, simulation_service: SimulationService):
        """
        Inicializa el caso de uso.
        
        Args:
            simulation_service: Servicio de simulación con capacidad de checkpointing
        """
        self.simulation_service = simulation_service
    
    def validate_request(self, request: DeleteCheckpointRequest) -> None:
        """
        Valida el request de eliminación.
        
        Args:
            request: Request a validar
            
        Raises:
            ValueError: Si la validación falla
        """
        # Validar que checkpoint_path no es None
        if request.checkpoint_path is None:
            raise ValueError("La ruta del checkpoint no puede ser None")
        
        # Convertir a Path si es string
        if isinstance(request.checkpoint_path, str):
            request.checkpoint_path = Path(request.checkpoint_path)
        
        # Validar que el archivo existe
        if not request.checkpoint_path.exists():
            raise ValueError(
                f"El archivo de checkpoint no existe: {request.checkpoint_path}"
            )
        
        # Validar que es un archivo (no directorio)
        if not request.checkpoint_path.is_file():
            raise ValueError(
                f"La ruta no es un archivo: {request.checkpoint_path}"
            )
        
        # Validar que está dentro del directorio de checkpoints (seguridad)
        checkpoint_dir = self.simulation_service.checkpoint_dir
        try:
            # Resolver rutas absolutas para comparación
            checkpoint_abs = request.checkpoint_path.resolve()
            checkpoint_dir_abs = checkpoint_dir.resolve()
            
            # Verificar que el checkpoint está dentro del directorio permitido
            if not str(checkpoint_abs).startswith(str(checkpoint_dir_abs)):
                raise ValueError(
                    f"El checkpoint debe estar dentro del directorio de checkpoints: "
                    f"{checkpoint_dir}"
                )
        except Exception as e:
            raise ValueError(f"Error al validar la ruta del checkpoint: {str(e)}")
    
    def _execute(self, request: DeleteCheckpointRequest) -> DeleteCheckpointResponse:
        """
        Ejecuta la eliminación del checkpoint.
        
        Args:
            request: Datos de eliminación
            
        Returns:
            Response con resultado de la eliminación
        """
        try:
            # Eliminar el archivo
            request.checkpoint_path.unlink()
            
            return DeleteCheckpointResponse(
                success=True,
                deleted_path=request.checkpoint_path
            )
        
        except PermissionError:
            return DeleteCheckpointResponse(
                success=False,
                error_message=f"Permiso denegado para eliminar: {request.checkpoint_path}"
            )
        
        except Exception as e:
            return DeleteCheckpointResponse(
                success=False,
                error_message=f"Error al eliminar checkpoint: {str(e)}"
            )
