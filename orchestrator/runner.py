"""
Orquestrador principal para executar mini apps.
"""

import importlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.base_app import BaseApp, AppResult
from core.context import AppContext
from core.logging_setup import setup_logging
import logging

logger = logging.getLogger(__name__)


class AppOrchestrator:
    """Orquestrador de mini apps."""
    
    def __init__(self, base_dir: Path, context: Optional[AppContext] = None):
        """
        Inicializa o orquestrador.
        
        Args:
            base_dir: Diretório base do projeto
            context: Contexto partilhado (opcional, será criado se None)
        """
        self.base_dir = Path(base_dir).resolve()
        
        if context is None:
            self.context = AppContext(
                base_dir=self.base_dir,
                work_dir=self.base_dir / "work",
                log_dir=self.base_dir / "logs"
            )
        else:
            self.context = context
        
        self.apps: Dict[str, BaseApp] = {}
        self._load_apps()
    
    def _load_apps(self):
        """Carrega dinamicamente todas as mini apps."""
        apps_dir = self.base_dir / "apps"
        
        if not apps_dir.exists():
            logger.warning(f"Diretório apps não encontrado: {apps_dir}")
            return
        
        for app_dir in apps_dir.iterdir():
            if not app_dir.is_dir():
                continue
            
            # Verificar se tem __init__.py
            init_file = app_dir / "__init__.py"
            app_file = app_dir / "app.py"
            
            if not init_file.exists() or not app_file.exists():
                continue
            
            try:
                # Importar módulo
                module_name = f"apps.{app_dir.name}.app"
                module = importlib.import_module(module_name)
                
                # Procurar classe App ou classe que herda de BaseApp
                app_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseApp) and 
                        attr is not BaseApp):
                        app_class = attr
                        break
                
                if app_class:
                    app_instance = app_class()
                    self.apps[app_instance.name] = app_instance
                    logger.info(f"Mini app carregada: {app_instance.name} v{app_instance.version}")
                else:
                    logger.warning(f"Nenhuma classe BaseApp encontrada em {module_name}")
                    
            except Exception as e:
                logger.error(f"Erro ao carregar app {app_dir.name}: {e}", exc_info=True)
    
    def list_apps(self) -> Dict[str, Dict[str, str]]:
        """Lista todas as mini apps disponíveis."""
        return {
            name: {
                "description": app.description,
                "version": app.version,
                "dependencies": app.get_dependencies()
            }
            for name, app in self.apps.items()
        }
    
    def run_app(
        self, 
        app_name: str, 
        config: Dict[str, Any],
        run_dependencies: bool = True
    ) -> AppResult:
        """
        Executa uma mini app específica.
        
        Args:
            app_name: Nome da mini app
            config: Configuração da mini app
            run_dependencies: Se True, executa dependências primeiro
        
        Returns:
            AppResult com resultado da execução
        """
        if app_name not in self.apps:
            return AppResult(
                success=False,
                message=f"App '{app_name}' não encontrada. Apps disponíveis: {', '.join(self.apps.keys())}"
            )
        
        app = self.apps[app_name]
        
        # Validar configuração
        is_valid, error = app.validate_config(config)
        if not is_valid:
            return AppResult(
                success=False, 
                message=f"Config inválida para '{app_name}': {error}"
            )
        
        # Resolver dependências
        if run_dependencies:
            deps = app.get_dependencies()
            for dep_name in deps:
                logger.info(f"Executando dependência '{dep_name}' para '{app_name}'...")
                dep_config = config.get("dependencies", {}).get(dep_name, {})
                dep_result = self.run_app(dep_name, dep_config, run_dependencies=True)
                if not dep_result.success:
                    return AppResult(
                        success=False,
                        message=f"Dependência '{dep_name}' falhou: {dep_result.message}"
                    )
        
        # Executar app
        try:
            logger.info(f"Executando mini app: {app_name}")
            result = app.run(config, self.context)
            
            if result.success:
                logger.info(f"Mini app '{app_name}' executada com sucesso: {result.message}")
            else:
                logger.error(f"Mini app '{app_name}' falhou: {result.message}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Erro ao executar '{app_name}': {e}")
            return AppResult(
                success=False,
                message=f"Erro inesperado: {str(e)}"
            )
        finally:
            # Cleanup
            try:
                app.cleanup(config, self.context)
            except Exception as e:
                logger.warning(f"Erro no cleanup de '{app_name}': {e}")
    
    def run_workflow(self, workflow_config: Dict[str, Any]) -> List[AppResult]:
        """
        Executa uma sequência de apps (workflow).
        
        Args:
            workflow_config: Configuração do workflow
                {
                    "name": "nome_workflow",
                    "continue_on_error": False,
                    "apps": [
                        {"name": "app1", "config": {...}},
                        {"name": "app2", "config": {...}}
                    ]
                }
        
        Returns:
            Lista de resultados de cada app
        """
        results = []
        apps_to_run = workflow_config.get("apps", [])
        continue_on_error = workflow_config.get("continue_on_error", False)
        
        logger.info(f"Iniciando workflow: {workflow_config.get('name', 'unnamed')}")
        
        for idx, app_config in enumerate(apps_to_run, start=1):
            app_name = app_config.get("name")
            if not app_name:
                logger.warning(f"App #{idx} sem nome, ignorando...")
                continue
            
            config = app_config.get("config", {})
            logger.info(f"[{idx}/{len(apps_to_run)}] Executando: {app_name}")
            
            result = self.run_app(app_name, config)
            results.append(result)
            
            # Se uma app falhar e workflow não permitir continuar
            if not result.success and not continue_on_error:
                logger.error(f"Workflow interrompido devido a falha em '{app_name}'")
                break
        
        logger.info(f"Workflow concluído. {sum(1 for r in results if r.success)}/{len(results)} apps bem-sucedidas")
        return results
