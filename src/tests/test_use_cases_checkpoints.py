"""
Tests para los casos de uso de gestión de checkpoints.

Cubre SaveCheckpoint, LoadCheckpoint, ListCheckpoints y DeleteCheckpoint.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import os
from datetime import datetime
import numpy as np

# Configurar path antes de imports
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from application.use_cases.manage_checkpoints import (
    SaveCheckpoint, SaveCheckpointRequest, SaveCheckpointResponse,
    LoadCheckpoint, LoadCheckpointRequest, LoadCheckpointResponse,
    ListCheckpoints, ListCheckpointsRequest, ListCheckpointsResponse,
    DeleteCheckpoint, DeleteCheckpointRequest, DeleteCheckpointResponse,
    CheckpointInfo
)
from application.use_cases.base import ExecutionError
from application.dtos import SimulationConfig, PopulationResult, AgentResult, HybridResult
from application.services.simulation_service import SimulationService
from typing import Tuple, Dict


class TestSaveCheckpoint(unittest.TestCase):
    """Tests para el caso de uso SaveCheckpoint."""
    
    def setUp(self):
        """Configuración común para tests."""
        self.simulation_service = Mock(spec=SimulationService)
        self.use_case = SaveCheckpoint(self.simulation_service)
        
        # Config de ejemplo
        self.config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=100,
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=50,
            temperature=28.0,
            humidity=80.0
        )
        
        # Result de ejemplo
        self.result = PopulationResult(
            species_id='aedes_aegypti',
            days=np.array([0, 1, 2]),
            eggs=np.array([0, 100, 200]),
            larvae=np.array([0, 80, 160]),
            pupae=np.array([0, 20, 40]),
            adults=np.array([50, 60, 70]),
            total_population=np.array([50, 260, 470]),
            statistics={
                'peak_population': 70,
                'peak_day': 2,
                'final_population': 70,
                'mean_total': 60.0
            }
        )
    
    def test_save_checkpoint_success_with_custom_name(self):
        """Test guardado exitoso con nombre personalizado."""
        # Configurar mock
        expected_path = Path('/checkpoints/custom_checkpoint.json')
        self.simulation_service.save_checkpoint.return_value = expected_path
        
        # Crear request
        request = SaveCheckpointRequest(
            result=self.result,
            config=self.config,
            simulation_type='population',
            checkpoint_name='custom_checkpoint.json'
        )
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.checkpoint_path, expected_path)
        self.assertIsNone(response.error_message)
        
        # Verificar llamada al servicio
        self.simulation_service.save_checkpoint.assert_called_once_with(
            result=self.result,
            config=self.config,
            simulation_type='population',
            checkpoint_name='custom_checkpoint.json'
        )
    
    def test_save_checkpoint_success_auto_name(self):
        """Test guardado exitoso con nombre auto-generado."""
        # Configurar mock
        expected_path = Path('/checkpoints/aedes_aegypti_20260111_103045_123456.json')
        self.simulation_service.save_checkpoint.return_value = expected_path
        
        # Crear request sin nombre personalizado
        request = SaveCheckpointRequest(
            result=self.result,
            config=self.config,
            simulation_type='population'
        )
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.checkpoint_path, expected_path)
        
        # Verificar llamada al servicio con checkpoint_name=None
        self.simulation_service.save_checkpoint.assert_called_once_with(
            result=self.result,
            config=self.config,
            simulation_type='population',
            checkpoint_name=None
        )
    
    def test_save_checkpoint_fails_if_result_is_none(self):
        """Test fallo cuando result es None."""
        request = SaveCheckpointRequest(
            result=None,  # type: ignore
            config=self.config,
            simulation_type='population'
        )
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("no puede ser None", str(context.exception))
    
    def test_save_checkpoint_fails_if_config_is_none(self):
        """Test fallo cuando config es None."""
        request = SaveCheckpointRequest(
            result=self.result,
            config=None,  # type: ignore
            simulation_type='population'
        )
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("no puede ser None", str(context.exception))
    
    def test_save_checkpoint_fails_if_invalid_simulation_type(self):
        """Test fallo con tipo de simulación inválido."""
        request = SaveCheckpointRequest(
            result=self.result,
            config=self.config,
            simulation_type='invalid_type'
        )
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("Tipo de simulación inválido", str(context.exception))
    
    def test_save_checkpoint_fails_if_invalid_checkpoint_name(self):
        """Test fallo con nombre de checkpoint inválido."""
        request = SaveCheckpointRequest(
            result=self.result,
            config=self.config,
            simulation_type='population',
            checkpoint_name='invalid/name/with/slashes.json'
        )
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("solo puede contener", str(context.exception))
    
    def test_save_checkpoint_handles_service_exception(self):
        """Test manejo de excepciones del servicio."""
        # Configurar mock para lanzar excepción
        self.simulation_service.save_checkpoint.side_effect = Exception("Disk full")
        
        request = SaveCheckpointRequest(
            result=self.result,
            config=self.config,
            simulation_type='population'
        )
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar que devuelve error en lugar de lanzar excepción
        self.assertFalse(response.success)
        self.assertIsNotNone(response.error_message)
        assert response.error_message is not None  # Type narrowing
        self.assertIn("Disk full", response.error_message)
        self.assertIsNone(response.checkpoint_path)
    
    def test_save_checkpoint_hybrid_success(self):
        """Test guardado exitoso de checkpoint híbrido."""
        # Crear AgentResult
        agent_result = AgentResult(
            num_vectors_initial=50,
            num_predators_initial=5,
            num_vectors_final=35,
            num_predators_final=4,
            total_eggs_laid=250,
            total_prey_consumed=15,
            daily_stats=[]
        )
        
        # Crear HybridResult
        hybrid_result = HybridResult(
            population_result=self.result,
            agent_result=agent_result,
            comparison_data={'metric': 'value', 'difference': 10}
        )
        
        # Configurar mock
        expected_path = Path('/checkpoints/hybrid_checkpoint.json')
        self.simulation_service.save_checkpoint.return_value = expected_path
        
        # Crear request
        request = SaveCheckpointRequest(
            result=hybrid_result,
            config=self.config,
            simulation_type='hybrid',
            checkpoint_name='hybrid_checkpoint.json'
        )
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.checkpoint_path, expected_path)
        self.assertIsNone(response.error_message)
        
        # Verificar llamada al servicio
        self.simulation_service.save_checkpoint.assert_called_once_with(
            result=hybrid_result,
            config=self.config,
            simulation_type='hybrid',
            checkpoint_name='hybrid_checkpoint.json'
        )


class TestLoadCheckpoint(unittest.TestCase):
    """Tests para el caso de uso LoadCheckpoint."""
    
    def setUp(self):
        """Configuración común para tests."""
        self.simulation_service = Mock(spec=SimulationService)
        self.use_case = LoadCheckpoint(self.simulation_service)
        
        # Crear archivo temporal para tests
        self.temp_dir = tempfile.mkdtemp()
        self.checkpoint_path = Path(self.temp_dir) / 'test_checkpoint.json'
        
        # Datos de checkpoint de ejemplo
        self.checkpoint_data = {
            'timestamp': '2026-01-11T10:30:45.123456',
            'simulation_type': 'population',
            'config': {
                'species_id': 'aedes_aegypti',
                'duration_days': 100,
                'initial_adults': 50,
                'temperature': 28.0,
                'humidity': 80.0
            },
            'result': {
                'total_trajectory': [50, 60, 70],
                'eggs_trajectory': [0, 100, 200],
                'larvae_trajectory': [0, 80, 160],
                'pupae_trajectory': [0, 20, 40],
                'adults_trajectory': [50, 60, 70],
                'extinction_day': None,
                'peak_population': 70,
                'peak_day': 2
            }
        }
        
        # Escribir checkpoint
        with open(self.checkpoint_path, 'w') as f:
            json.dump(self.checkpoint_data, f)
    
    def tearDown(self):
        """Limpieza después de tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_load_checkpoint_success(self):
        """Test carga exitosa de checkpoint válido."""
        # Configurar mock
        config = SimulationConfig(
            species_id='aedes_aegypti',
            duration_days=100,
            initial_eggs=0,
            initial_larvae=0,
            initial_pupae=0,
            initial_adults=50,
            temperature=28.0,
            humidity=80.0
        )
        result = PopulationResult(
            species_id='aedes_aegypti',
            days=np.array([0, 1, 2]),
            eggs=np.array([0, 100, 200]),
            larvae=np.array([0, 80, 160]),
            pupae=np.array([0, 20, 40]),
            adults=np.array([50, 60, 70]),
            total_population=np.array([50, 260, 470]),
            statistics={
                'peak_population': 70,
                'peak_day': 2,
                'final_population': 70,
                'mean_total': 60.0
            }
        )
        
        self.simulation_service.load_checkpoint.return_value = (config, result, 'population')
        
        # Crear request
        request = LoadCheckpointRequest(checkpoint_path=self.checkpoint_path)
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertIsNotNone(response.config)
        self.assertIsNotNone(response.result)
        self.assertEqual(response.simulation_type, 'population')
        self.assertIsNotNone(response.metadata)
        self.assertIsNone(response.error_message)
        
        # Verificar metadata
        assert response.metadata is not None  # Type narrowing
        self.assertEqual(response.metadata['species_id'], 'aedes_aegypti')
        self.assertEqual(response.metadata['duration_days'], 100)
    
    def test_load_checkpoint_fails_if_file_not_exists(self):
        """Test fallo cuando archivo no existe."""
        non_existent_path = Path('/non/existent/checkpoint.json')
        request = LoadCheckpointRequest(checkpoint_path=non_existent_path)
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("no existe", str(context.exception))
    
    def test_load_checkpoint_fails_if_not_json_file(self):
        """Test fallo si no es archivo JSON."""
        # Crear archivo temporal sin extensión .json
        txt_path = Path(self.temp_dir) / 'test.txt'
        txt_path.write_text("not a json")
        
        request = LoadCheckpointRequest(checkpoint_path=txt_path)
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("debe ser un archivo JSON", str(context.exception))
    
    def test_load_checkpoint_handles_corrupted_json(self):
        """Test manejo de JSON corrupto."""
        # Crear archivo con JSON inválido
        corrupted_path = Path(self.temp_dir) / 'corrupted.json'
        corrupted_path.write_text("{invalid json content")
        
        # Configurar mock para lanzar excepción
        self.simulation_service.load_checkpoint.side_effect = json.JSONDecodeError(
            "Invalid", "doc", 0
        )
        
        request = LoadCheckpointRequest(checkpoint_path=corrupted_path)
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar que devuelve error
        self.assertFalse(response.success)
        self.assertIsNotNone(response.error_message)
        assert response.error_message is not None  # Type narrowing
        self.assertIn("decodificar JSON", response.error_message)
    
    def test_load_checkpoint_handles_service_exception(self):
        """Test manejo de excepciones del servicio."""
        # Configurar mock para lanzar excepción
        self.simulation_service.load_checkpoint.side_effect = Exception(
            "Missing required key"
        )
        
        request = LoadCheckpointRequest(checkpoint_path=self.checkpoint_path)
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar que devuelve error
        self.assertFalse(response.success)
        self.assertIsNotNone(response.error_message)
        assert response.error_message is not None  # Type narrowing
        self.assertIn("Missing required key", response.error_message)


class TestListCheckpoints(unittest.TestCase):
    """Tests para el caso de uso ListCheckpoints."""
    
    def setUp(self):
        """Configuración común para tests."""
        self.simulation_service = Mock(spec=SimulationService)
        self.use_case = ListCheckpoints(self.simulation_service)
    
    def test_list_all_checkpoints(self):
        """Test listar todos los checkpoints sin filtros."""
        # Configurar mock
        checkpoints_data = [
            {
                'path': Path('/checkpoints/aedes_aegypti_1.json'),
                'timestamp': '2026-01-11T10:30:00',
                'species': 'aedes_aegypti',
                'simulation_type': 'population',
                'duration_days': 100
            },
            {
                'path': Path('/checkpoints/anopheles_gambiae_1.json'),
                'timestamp': '2026-01-11T11:00:00',
                'species': 'anopheles_gambiae',
                'simulation_type': 'agent',
                'duration_days': 200
            }
        ]
        self.simulation_service.list_checkpoints.return_value = checkpoints_data
        
        # Crear request sin filtros
        request = ListCheckpointsRequest()
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.count, 2)
        self.assertEqual(len(response.checkpoints), 2)
        self.assertIsNone(response.error_message)
        
        # Verificar primer checkpoint
        cp1 = response.checkpoints[0]
        self.assertEqual(cp1.species_id, 'aedes_aegypti')
        self.assertEqual(cp1.simulation_type, 'population')
        self.assertEqual(cp1.duration_days, 100)
    
    def test_list_checkpoints_filtered_by_species(self):
        """Test listar checkpoints filtrados por especie."""
        # Configurar mock
        checkpoints_data = [
            {
                'path': Path('/checkpoints/aedes_aegypti_1.json'),
                'timestamp': '2026-01-11T10:30:00',
                'species': 'aedes_aegypti',
                'simulation_type': 'population',
                'duration_days': 100
            }
        ]
        self.simulation_service.list_checkpoints.return_value = checkpoints_data
        
        # Crear request con filtro de especie
        request = ListCheckpointsRequest(species_id='aedes_aegypti')
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.count, 1)
        self.assertEqual(response.checkpoints[0].species_id, 'aedes_aegypti')
        
        # Verificar llamada al servicio con filtro
        self.simulation_service.list_checkpoints.assert_called_once_with(
            species='aedes_aegypti',
            simulation_type=None
        )
    
    def test_list_checkpoints_filtered_by_simulation_type(self):
        """Test listar checkpoints filtrados por tipo de simulación."""
        # Configurar mock
        checkpoints_data = [
            {
                'path': Path('/checkpoints/agent_sim_1.json'),
                'timestamp': '2026-01-11T10:30:00',
                'species': 'aedes_aegypti',
                'simulation_type': 'agent',
                'duration_days': 150
            }
        ]
        self.simulation_service.list_checkpoints.return_value = checkpoints_data
        
        # Crear request con filtro de tipo
        request = ListCheckpointsRequest(simulation_type='agent')
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.count, 1)
        self.assertEqual(response.checkpoints[0].simulation_type, 'agent')
        
        # Verificar llamada al servicio
        self.simulation_service.list_checkpoints.assert_called_once_with(
            species=None,
            simulation_type='agent'
        )
    
    def test_list_checkpoints_empty_result(self):
        """Test lista vacía cuando no hay checkpoints."""
        # Configurar mock para devolver lista vacía
        self.simulation_service.list_checkpoints.return_value = []
        
        # Crear request
        request = ListCheckpointsRequest()
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.count, 0)
        self.assertEqual(len(response.checkpoints), 0)
    
    def test_list_checkpoints_fails_with_invalid_simulation_type(self):
        """Test fallo con tipo de simulación inválido."""
        request = ListCheckpointsRequest(simulation_type='invalid_type')
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("Tipo de simulación inválido", str(context.exception))
    
    def test_list_checkpoints_fails_with_empty_species_id(self):
        """Test fallo con species_id vacío."""
        request = ListCheckpointsRequest(species_id='   ')
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("no puede estar vacío", str(context.exception))
    
    def test_list_checkpoints_handles_service_exception(self):
        """Test manejo de excepciones del servicio."""
        # Configurar mock para lanzar excepción
        self.simulation_service.list_checkpoints.side_effect = Exception(
            "Directory not found"
        )
        
        request = ListCheckpointsRequest()
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar que devuelve error
        self.assertFalse(response.success)
        self.assertEqual(response.count, 0)
        self.assertEqual(len(response.checkpoints), 0)
        self.assertIsNotNone(response.error_message)
        assert response.error_message is not None  # Type narrowing
        self.assertIn("Directory not found", response.error_message)


class TestDeleteCheckpoint(unittest.TestCase):
    """Tests para el caso de uso DeleteCheckpoint."""
    
    def setUp(self):
        """Configuración común para tests."""
        self.simulation_service = Mock(spec=SimulationService)
        self.use_case = DeleteCheckpoint(self.simulation_service)
        
        # Crear directorio temporal para checkpoints
        self.temp_dir = tempfile.mkdtemp()
        self.simulation_service.checkpoint_dir = Path(self.temp_dir)
        
        # Crear archivo de checkpoint de prueba
        self.checkpoint_path = Path(self.temp_dir) / 'test_checkpoint.json'
        self.checkpoint_path.write_text('{"test": "data"}')
    
    def tearDown(self):
        """Limpieza después de tests."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_delete_checkpoint_success(self):
        """Test eliminación exitosa de checkpoint."""
        # Verificar que el archivo existe
        self.assertTrue(self.checkpoint_path.exists())
        
        # Crear request
        request = DeleteCheckpointRequest(checkpoint_path=self.checkpoint_path)
        
        # Ejecutar
        response = self.use_case.execute(request)
        
        # Verificar
        self.assertTrue(response.success)
        self.assertEqual(response.deleted_path, self.checkpoint_path)
        self.assertIsNone(response.error_message)
        
        # Verificar que el archivo fue eliminado
        self.assertFalse(self.checkpoint_path.exists())
    
    def test_delete_checkpoint_fails_if_file_not_exists(self):
        """Test fallo cuando archivo no existe."""
        non_existent_path = Path(self.temp_dir) / 'non_existent.json'
        request = DeleteCheckpointRequest(checkpoint_path=non_existent_path)
        
        with self.assertRaises(ExecutionError) as context:
            self.use_case.execute(request)
        
        self.assertIn("no existe", str(context.exception))
    
    def test_delete_checkpoint_fails_if_outside_checkpoint_dir(self):
        """Test fallo si checkpoint está fuera del directorio permitido."""
        # Crear archivo fuera del directorio de checkpoints
        outside_path = Path(tempfile.gettempdir()) / 'outside_checkpoint.json'
        outside_path.write_text('{"test": "data"}')
        
        try:
            request = DeleteCheckpointRequest(checkpoint_path=outside_path)
            
            with self.assertRaises(ExecutionError) as context:
                self.use_case.execute(request)
            
            self.assertIn("dentro del directorio de checkpoints", str(context.exception))
        
        finally:
            # Limpiar archivo temporal
            if outside_path.exists():
                outside_path.unlink()
    
    def test_delete_checkpoint_handles_permission_error(self):
        """Test manejo de error de permisos."""
        # Crear archivo de checkpoint
        checkpoint_path = Path(self.temp_dir) / 'readonly_checkpoint.json'
        checkpoint_path.write_text('{"test": "data"}')
        
        # Simular error de permisos usando mock
        with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
            request = DeleteCheckpointRequest(checkpoint_path=checkpoint_path)
            
            # Ejecutar
            response = self.use_case.execute(request)
            
            # Verificar que devuelve error
            self.assertFalse(response.success)
            self.assertIsNotNone(response.error_message)
            assert response.error_message is not None  # Type narrowing
            self.assertIn("Permiso denegado", response.error_message)


if __name__ == '__main__':
    unittest.main()
