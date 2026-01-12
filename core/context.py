"""
Contexto partilhado entre mini apps.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class AppContext:
    """Contexto partilhado entre mini apps."""
    
    # Diretórios
    base_dir: Path
    work_dir: Path
    log_dir: Path
    
    # Autenticação (partilhada entre apps que usam eFatura)
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    
    # Metadados
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    start_time: datetime = field(default_factory=datetime.now)
    
    # Dados partilhados entre apps
    shared_data: Dict[str, Any] = field(default_factory=dict)
    
    # Output files gerados pelas apps
    output_files: Dict[str, Path] = field(default_factory=dict)
    
    def get_or_create_workdir(self, subdir: str) -> Path:
        """Cria subdiretório em work_dir se não existir."""
        path = self.work_dir / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_or_create_logdir(self, subdir: str) -> Path:
        """Cria subdiretório em log_dir se não existir."""
        path = self.log_dir / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path
