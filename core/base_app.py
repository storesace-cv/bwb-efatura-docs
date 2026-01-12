"""
Classe base abstrata para todas as mini apps.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from core.context import AppContext
from core.exceptions import BWBConfigError, BWBExecutionError


@dataclass
class AppResult:
    """Resultado da execução de uma mini app."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    output_files: Optional[List[Path]] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []


class BaseApp(ABC):
    """Classe base abstrata para todas as mini apps."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único da mini app (ex: 'efatura-supplier-docs-download')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição da funcionalidade da mini app."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versão da mini app."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Valida a configuração da mini app.
        
        Args:
            config: Configuração a validar
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def run(self, config: Dict[str, Any], context: AppContext) -> AppResult:
        """
        Executa a mini app.
        
        Args:
            config: Configuração específica da mini app
            context: Contexto partilhado entre apps
        
        Returns:
            AppResult com resultado da execução
        """
        pass
    
    def get_dependencies(self) -> List[str]:
        """
        Lista de nomes de outras mini apps que devem ser executadas antes desta.
        Returns lista vazia se não houver dependências.
        """
        return []
    
    def cleanup(self, config: Dict[str, Any], context: AppContext) -> None:
        """
        Cleanup após execução (opcional).
        Útil para fechar conexões, limpar recursos temporários, etc.
        """
        pass
