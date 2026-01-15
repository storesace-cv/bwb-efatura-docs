# Documentação de API e Componentes

## Core Framework

### BaseApp

Classe base abstrata para todas as mini apps.

```python
from core.base_app import BaseApp, AppResult
from core.context import AppContext

class BaseApp(ABC):
    """Classe base abstrata para todas as mini apps."""
```

#### Propriedades

##### name: str
Nome único da mini app (kebab-case).

```python
@property
@abstractmethod
def name(self) -> str:
    """Nome único da mini app."""
    pass
```

**Exemplo**: `"efatura-supplier-docs-download"`

##### description: str
Descrição breve da funcionalidade.

```python
@property
@abstractmethod
def description(self) -> str:
    """Descrição da funcionalidade."""
    pass
```

##### version: str
Versão da mini app (semver: major.minor.patch).

```python
@property
@abstractmethod
def version(self) -> str:
    """Versão da mini app."""
    pass
```

**Exemplo**: `"1.0.0"`

#### Métodos

##### validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]

Valida a configuração da mini app.

**Parâmetros**:
- `config`: Dicionário com configuração

**Retorna**:
- `(is_valid, error_message)`: `error_message` é `None` se válido

**Exemplo**:
```python
def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    if "campo_obrigatorio" not in config:
        return False, "Campo obrigatório ausente"
    return True, None
```

##### run(config: Dict[str, Any], context: AppContext) -> AppResult

Executa a mini app.

**Parâmetros**:
- `config`: Configuração validada
- `context`: Contexto partilhado

**Retorna**:
- `AppResult`: Resultado da execução

**Exemplo**:
```python
def run(self, config: Dict[str, Any], context: AppContext) -> AppResult:
    # Lógica da app
    return AppResult(
        success=True,
        message="Executado com sucesso",
        data={"docs": 10},
        output_files=[Path("output.xlsx")]
    )
```

##### get_dependencies() -> List[str]

Lista de nomes de outras mini apps que devem ser executadas antes desta.

**Retorna**:
- `List[str]`: Lista de nomes de apps dependentes (vazia se não houver)

**Exemplo**:
```python
def get_dependencies(self) -> List[str]:
    return ["efatura-supplier-docs-download"]
```

##### cleanup(config: Dict[str, Any], context: AppContext) -> None

Cleanup após execução (opcional).

**Parâmetros**:
- `config`: Configuração usada
- `context`: Contexto partilhado

**Uso**: Fechar conexões, limpar recursos temporários, etc.

### AppResult

Dataclass que representa o resultado da execução de uma mini app.

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List

@dataclass
class AppResult:
    """Resultado da execução de uma mini app."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    output_files: Optional[List[Path]] = None
```

#### Campos

- `success` (bool): Se a execução foi bem-sucedida
- `message` (str): Mensagem descritiva do resultado
- `data` (Optional[Dict]): Dados adicionais (opcional)
- `output_files` (Optional[List[Path]]): Lista de ficheiros gerados (opcional)

### AppContext

Contexto partilhado entre mini apps.

```python
from core.context import AppContext
from pathlib import Path
from datetime import datetime

@dataclass
class AppContext:
    """Contexto partilhado entre mini apps."""
    base_dir: Path
    work_dir: Path
    log_dir: Path
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None
    run_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    start_time: datetime = field(default_factory=datetime.now)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    output_files: Dict[str, Path] = field(default_factory=dict)
```

#### Campos

- `base_dir` (Path): Diretório base do projeto
- `work_dir` (Path): Diretório de trabalho
- `log_dir` (Path): Diretório de logs
- `access_token` (Optional[str]): Token de acesso partilhado
- `token_expiry` (Optional[datetime]): Expiração do token
- `run_id` (str): Identificador único da execução
- `start_time` (datetime): Timestamp de início
- `shared_data` (Dict): Dados partilhados entre apps
- `output_files` (Dict): Ficheiros gerados por app

#### Métodos

##### get_or_create_workdir(subdir: str) -> Path

Cria subdiretório em `work_dir` se não existir.

**Parâmetros**:
- `subdir`: Nome do subdiretório

**Retorna**:
- `Path`: Caminho do diretório criado

**Exemplo**:
```python
work_dir = context.get_or_create_workdir("minha-app")
```

##### get_or_create_logdir(subdir: str) -> Path

Cria subdiretório em `log_dir` se não existir.

**Parâmetros**:
- `subdir`: Nome do subdiretório

**Retorna**:
- `Path`: Caminho do diretório criado

**Exemplo**:
```python
log_dir = context.get_or_create_logdir("minha-app")
```

## Orchestrator

### AppOrchestrator

Orquestrador principal para executar mini apps.

```python
from orchestrator.runner import AppOrchestrator
from pathlib import Path

orchestrator = AppOrchestrator(base_dir=Path.cwd())
```

#### Métodos

##### __init__(base_dir: Path, context: Optional[AppContext] = None)

Inicializa o orquestrador.

**Parâmetros**:
- `base_dir`: Diretório base do projeto
- `context`: Contexto partilhado (opcional, será criado se None)

##### list_apps() -> Dict[str, Dict[str, str]]

Lista todas as mini apps disponíveis.

**Retorna**:
- `Dict[str, Dict]`: Dicionário com nome da app como chave e informações como valor
  - `description`: Descrição da app
  - `version`: Versão da app
  - `dependencies`: Lista de dependências

**Exemplo**:
```python
apps = orchestrator.list_apps()
# {
#   "efatura-supplier-docs-download": {
#     "description": "...",
#     "version": "1.0.0",
#     "dependencies": []
#   }
# }
```

##### run_app(app_name: str, config: Dict[str, Any], run_dependencies: bool = True) -> AppResult

Executa uma mini app específica.

**Parâmetros**:
- `app_name`: Nome da mini app
- `config`: Configuração da mini app
- `run_dependencies`: Se `True`, executa dependências primeiro

**Retorna**:
- `AppResult`: Resultado da execução

**Exemplo**:
```python
result = orchestrator.run_app(
    "efatura-supplier-docs-download",
    {"config_file": "app/config.ini"}
)
```

##### run_workflow(workflow_config: Dict[str, Any]) -> List[AppResult]

Executa uma sequência de apps (workflow).

**Parâmetros**:
- `workflow_config`: Configuração do workflow
  ```python
  {
      "name": "nome_workflow",
      "continue_on_error": False,
      "apps": [
          {"name": "app1", "config": {...}},
          {"name": "app2", "config": {...}}
      ]
  }
  ```

**Retorna**:
- `List[AppResult]`: Lista de resultados de cada app

**Exemplo**:
```python
workflow_config = {
    "name": "export_completo",
    "continue_on_error": False,
    "apps": [
        {
            "name": "efatura-supplier-docs-download",
            "config": {"config_file": "app/config.ini"}
        }
    ]
}
results = orchestrator.run_workflow(workflow_config)
```

## Exceções

### BWBAppError

Exceção base para erros de mini apps.

```python
from core.exceptions import BWBAppError

class BWBAppError(Exception):
    """Exceção base para erros de mini apps."""
    pass
```

### BWBConfigError

Erro de configuração.

```python
from core.exceptions import BWBConfigError

raise BWBConfigError("Campo obrigatório ausente")
```

### BWBValidationError

Erro de validação.

```python
from core.exceptions import BWBValidationError

raise BWBValidationError("Valor inválido para campo X")
```

### BWBExecutionError

Erro durante execução de uma mini app.

```python
from core.exceptions import BWBExecutionError

raise BWBExecutionError("Falha ao processar documento")
```

## Logging

### setup_logging

Configura logging para console e ficheiro.

```python
from core.logging_setup import setup_logging
from pathlib import Path
import logging

logger = setup_logging(
    log_file=Path("logs/app.log"),
    level=logging.INFO,
    logger_name="bwb"
)
```

**Parâmetros**:
- `log_file` (Optional[Path]): Caminho para ficheiro de log (opcional)
- `level` (int): Nível de logging (default: `logging.INFO`)
- `logger_name` (str): Nome do logger (default: `"bwb"`)

**Retorna**:
- `logging.Logger`: Logger configurado

**Uso**:
```python
logger = setup_logging(Path("logs/app.log"))
logger.info("Mensagem de info")
logger.error("Mensagem de erro")
logger.exception("Erro com traceback")
```

## Mini Apps Existentes

### efatura-supplier-docs-download

Mini app que exporta documentos de compras (DFE) do portal eFatura CV para Excel.

#### Configuração

```json
{
  "efatura-supplier-docs-download": {
    "config_file": "app/purchases_update_supplier.ini",
    "max_docs": 0,
    "rewrite_existing": false,
    "save_every_docs": -1,
    "save_every_seconds": -1,
    "verbose": false
  }
}
```

**Parâmetros**:
- `config_file` (str, obrigatório): Caminho para ficheiro INI de configuração
- `max_docs` (int): Limite de documentos (0 = sem limite)
- `rewrite_existing` (bool): Reescrever UIDs existentes (default: false)
- `save_every_docs` (int): Guardar Excel a cada N documentos (-1 = usar INI)
- `save_every_seconds` (int): Guardar Excel a cada N segundos (-1 = usar INI)
- `verbose` (bool): Logging detalhado (default: false)

#### Ficheiro INI

```ini
[paths]
base_dir = /caminho/base
excel_path = supplier_invoices.xlsx

[efatura]
token_json = app/token.json
repo_code = 1
date_start = 2025-01-01
date_end = 2025-12-31
page_size = 200
timeout_sec = 45
retries = 3
retry_backoff_sec = 1.5

[logging]
progress_every_docs = 10
save_every_docs = 100
save_every_seconds = 300
log_file = logs/update_supplier_invoices.log
```

#### Retorno

```python
AppResult(
    success=True,
    message="Processados 10 documentos, 25 linhas, 0 erros...",
    data={
        "docs_added": 10,
        "rows_added": 25,
        "errors": 0,
        "total_uids": 10
    },
    output_files=[Path("supplier_invoices.xlsx")]
)
```

## CLI (Command Line Interface)

### main.py

Entry point principal do sistema.

#### Argumentos

##### --base-dir DIR

Diretório base do projeto (default: diretório atual).

```bash
python main.py --base-dir /caminho/projeto
```

##### --list-apps

Lista todas as mini apps disponíveis e sai.

```bash
python main.py --list-apps
```

##### --app NAME

Nome da mini app a executar.

```bash
python main.py --app efatura-supplier-docs-download
```

##### --config FILE

Ficheiro de configuração JSON.

```bash
python main.py --app minha-app --config config.json
```

##### --workflow FILE

Ficheiro de workflow JSON.

```bash
python main.py --workflow workflow.json --config config.json
```

##### --verbose

Logging verboso.

```bash
python main.py --app minha-app --config config.json --verbose
```

#### Exemplos de Uso

**Listar apps**:
```bash
python main.py --list-apps
```

**Executar app**:
```bash
python main.py \
  --app efatura-supplier-docs-download \
  --config config/example_config.json \
  --verbose
```

**Executar workflow**:
```bash
python main.py \
  --workflow config/example_workflow.json \
  --config config/example_config.json
```

## Estruturas de Dados

### Workflow Config

```json
{
  "name": "nome_workflow",
  "description": "Descrição do workflow",
  "continue_on_error": false,
  "apps": [
    {
      "name": "app1",
      "config": {
        "campo": "valor"
      }
    },
    {
      "name": "app2",
      "config": {
        "campo": "valor"
      }
    }
  ]
}
```

### App Config

```json
{
  "app-name": {
    "campo1": "valor1",
    "campo2": 123,
    "campo3": true
  }
}
```

## Extensibilidade

### Criar Nova App

Ver [DEVELOPMENT.md](DEVELOPMENT.md) para guia completo de criação de novas apps.

### Adicionar Novas Funcionalidades

1. Implementar na classe da app
2. Adicionar validação em `validate_config`
3. Documentar em docstrings
4. Atualizar este documento
