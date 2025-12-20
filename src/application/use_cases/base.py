"""
Base Use Case Classes
======================

Abstract base classes and common patterns for use cases following Clean Architecture principles.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from dataclasses import dataclass
from datetime import datetime


TRequest = TypeVar('TRequest')
TResponse = TypeVar('TResponse')


class UseCaseError(Exception):
    """Base exception for use case errors."""
    pass


class ValidationError(UseCaseError):
    """Raised when request validation fails."""
    pass


class ExecutionError(UseCaseError):
    """Raised when use case execution fails."""
    pass


@dataclass
class BaseResponse:
    """
    Base response class with standard fields.
    
    All use case responses should include these fields for consistency.
    """
    success: bool
    error: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class UseCase(ABC, Generic[TRequest, TResponse]):
    """
    Abstract base class for all use cases.
    
    Implements the Template Method pattern:
    1. Validate request
    2. Execute business logic
    3. Handle errors gracefully
    
    Subclasses must implement:
    - validate_request(): Validate input parameters
    - _execute(): Core business logic
    """
    
    def execute(self, request: TRequest) -> TResponse:
        """
        Execute the use case with error handling.
        
        Args:
            request: Input parameters for the use case
            
        Returns:
            Response with result or error information
            
        Raises:
            ValidationError: If request validation fails
            ExecutionError: If execution fails
        """
        try:
            # Step 1: Validate
            self.validate_request(request)
            
            # Step 2: Execute
            start_time = datetime.now()
            response = self._execute(request)
            end_time = datetime.now()
            
            # Step 3: Add metadata if response is BaseResponse
            if isinstance(response, BaseResponse):
                response.execution_time_seconds = (end_time - start_time).total_seconds()
            
            return response
            
        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            raise ExecutionError(f"Use case execution failed: {str(e)}") from e
    
    @abstractmethod
    def validate_request(self, request: TRequest) -> None:
        """
        Validate request parameters.
        
        Args:
            request: Input parameters to validate
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def _execute(self, request: TRequest) -> TResponse:
        """
        Execute the core use case logic.
        
        Args:
            request: Validated input parameters
            
        Returns:
            Response with operation result
            
        Raises:
            ExecutionError: If execution fails
        """
        pass
