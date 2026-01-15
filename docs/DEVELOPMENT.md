# Guia de Desenvolvimento

## Visão Geral

Este guia explica como desenvolver e estender o BWB App, incluindo criação de novas mini apps, modificação de apps existentes, e práticas recomendadas.

## Estrutura do Projeto

```
my-bwb-app/
├── apps/                    # Mini apps (uma por diretório)
│   └── efatura_supplier_docs_download/
│       ├── __init__.py
│       └── app.py
├── core/                    # Framework base
│   ├── base_app.py         # Classe base abstrata
│   ├── context.py          # Contexto partilhado
│   ├── exceptions.py       # Exceções personalizadas
│   └── logging_setup.py    # Setup de logging
├── orchestrator/           # Orquestrador
│   └── runner.py
├── config/                 # Ficheiros de configuração
│   ├── example_config.json
│   └── example_workflow.json
├── app/                    # Código legado (a migrar)
│   └── update_supplier_invoices.py
├── docs/                   # Documentação
├── main.py                 # Entry point CLI
└── requirements.txt        # Dependências Python
```

## Criar Nova Mini App

### 1. Estrutura de Diretórios

Criar novo diretório em `apps/`:

```bash
mkdir -p apps/minha_nova_app
cd apps/minha_nova_app
touch __init__.py app.py
```

### 2. Template Base

Copiar o seguinte template para `app.py`:

```python
"""
Mini app: Descrição da funcionalidade.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from core.base_app import BaseApp, AppResult
from core.context import AppContext
from core.exceptions import BWBConfigError, BWBExecutionError
import logging

logger = logging.getLogger(__name__)


class MinhaNovaApp(BaseApp):
    """Mini app: Descrição da funcionalidade."""
    
    @property
    def name(self) -> str:
        """Nome único da app (usar kebab-case)."""
        return "minha-nova-app"
    
    @property
    def description(self) -> str:
        """Descrição breve da funcionalidade."""
        return "Descrição da funcionalidade da app"
    
    @property
    def version(self) -> str:
        """Versão da app (semver: major.minor.patch)."""
        return "1.0.0"
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida a configuração da app.
        
        Args:
            config: Dicionário com configuração
            
        Returns:
            (is_valid, error_message) - error_message é None se válido
        """
        if not isinstance(config, dict):
            return False, "Config deve ser um dicionário"
        
        # Adicionar validações específicas
        required_fields = ["campo_obrigatorio"]
        for field in required_fields:
            if field not in config:
                return False, f"Campo obrigatório ausente: {field}"
        
        # Validar tipos e valores
        if "campo_obrigatorio" in config:
            if not isinstance(config["campo_obrigatorio"], str):
                return False, "campo_obrigatorio deve ser string"
        
        return True, None
    
    def run(self, config: Dict[str, Any], context: AppContext) -> AppResult:
        """
        Executa a app.
        
        Args:
            config: Configuração validada
            context: Contexto partilhado
            
        Returns:
            AppResult com resultado da execução
        """
        try:
            logger.info(f"Iniciando {self.name} v{self.version}")
            
            # 1. Preparar ambiente
            work_dir = context.get_or_create_workdir(self.name)
            log_dir = context.get_or_create_logdir(self.name)
            
            # 2. Lógica principal
            # ... implementar funcionalidade ...
            
            # 3. Retornar resultado
            return AppResult(
                success=True,
                message=f"{self.name} executada com sucesso",
                data={
                    # Dados adicionais (opcional)
                },
                output_files=[
                    # Lista de ficheiros gerados (opcional)
                ]
            )
            
        except BWBConfigError as e:
            logger.error(f"Erro de configuração: {e}")
            return AppResult(
                success=False,
                message=f"Erro de configuração: {str(e)}"
            )
        except BWBExecutionError as e:
            logger.error(f"Erro de execução: {e}")
            return AppResult(
                success=False,
                message=f"Erro de execução: {str(e)}"
            )
        except Exception as e:
            logger.exception(f"Erro inesperado: {e}")
            return AppResult(
                success=False,
                message=f"Erro inesperado: {str(e)}"
            )
    
    def get_dependencies(self) -> list[str]:
        """
        Lista de apps que devem ser executadas antes desta.
        
        Returns:
            Lista de nomes de apps dependentes
        """
        # Exemplo: depende de outra app
        # return ["efatura-supplier-docs-download"]
        return []
    
    def cleanup(self, config: Dict[str, Any], context: AppContext) -> None:
        """
        Limpeza após execução (opcional).
        
        Útil para:
        - Fechar conexões
        - Limpar recursos temporários
        - Finalizar transações
        """
        # Implementar se necessário
        pass
```

### 3. Verificar Descoberta

Após criar a app, verificar que é descoberta:

```bash
python main.py --list-apps
```

Deverá aparecer na lista:
```
minha-nova-app v1.0.0
  Descrição: Descrição da funcionalidade da app
  Dependências:
```

### 4. Testar Execução

Criar configuração de teste em `config/test_config.json`:

```json
{
  "minha-nova-app": {
    "campo_obrigatorio": "valor_teste"
  }
}
```

Executar:
```bash
python main.py --app minha-nova-app --config config/test_config.json --verbose
```

## Padrões e Boas Práticas

### Nomenclatura

#### Nomes de Apps
- Usar **kebab-case**: `minha-nova-app`
- Ser descritivo mas conciso
- Evitar abreviações obscuras

#### Variáveis e Funções
- Usar **snake_case**: `nome_da_variavel`, `nome_da_funcao`
- Ser descritivo
- Evitar nomes genéricos (`data`, `result`)

#### Classes
- Usar **PascalCase**: `MinhaClasse`
- Nome da classe da app deve terminar em `App`

### Logging

#### Níveis de Log
- `DEBUG`: Informação detalhada para debugging
- `INFO`: Progresso normal da execução
- `WARNING`: Situações atípicas mas não críticas
- `ERROR`: Erros que impedem funcionamento parcial
- `CRITICAL`: Erros que impedem funcionamento total

#### Exemplos

```python
import logging

logger = logging.getLogger(__name__)

# Progresso normal
logger.info(f"Processando {count} documentos")

# Situação atípica
logger.warning(f"Documento {uid} sem linhas, ignorando...")

# Erro recuperável
logger.error(f"Falha ao processar {uid}: {e}")
logger.exception(f"Erro completo:")  # Inclui traceback

# Erro crítico
logger.critical("Sistema de autenticação falhou")
```

### Tratamento de Erros

#### Usar Exceções Específicas

```python
from core.exceptions import BWBConfigError, BWBExecutionError

# Erro de configuração
if not config.get("campo"):
    raise BWBConfigError("Campo obrigatório ausente")

# Erro de execução
try:
    resultado = operacao_perigosa()
except Exception as e:
    raise BWBExecutionError(f"Falha na operação: {e}") from e
```

#### Tratamento Defensivo

```python
def parse_document(xml_content: str) -> dict:
    """Parse com tratamento defensivo."""
    try:
        # Tentativa 1: parse direto
        return xml.etree.ElementTree.fromstring(xml_content)
    except Exception as e:
        logger.warning(f"Parse direto falhou: {e}")
        
        try:
            # Tentativa 2: sanitização
            sanitized = sanitize_xml(xml_content)
            return xml.etree.ElementTree.fromstring(sanitized)
        except Exception as e2:
            logger.error(f"Parse após sanitização falhou: {e2}")
            raise BWBExecutionError("XML não parseável") from e2
```

### Type Hints

Sempre usar type hints:

```python
from typing import Dict, List, Optional, Tuple

def process_documents(
    uids: List[str],
    config: Dict[str, Any],
    context: AppContext
) -> Tuple[int, int]:
    """
    Processa documentos.
    
    Returns:
        (processados, erros)
    """
    ...
```

### Documentação

#### Docstrings

Sempre documentar classes e métodos públicos:

```python
class MinhaApp(BaseApp):
    """
    Mini app para processar documentos fiscais.
    
    Esta app processa documentos do eFatura CV e gera relatórios.
    """
    
    def process_document(self, uid: str) -> dict:
        """
        Processa um documento específico.
        
        Args:
            uid: Identificador único do documento
            
        Returns:
            Dicionário com dados processados
            
        Raises:
            BWBExecutionError: Se o documento não puder ser processado
        """
        ...
```

## Testes

### Testes Manuais

Para testar uma app:

1. **Configuração mínima**: Criar config com valores mínimos válidos
2. **Teste com limite**: Usar `max_docs=1` para teste rápido
3. **Verificar logs**: Consultar logs para erros
4. **Verificar output**: Verificar ficheiros gerados

### Estrutura de Testes (Futuro)

Quando testes automatizados forem adicionados:

```
tests/
├── test_base_app.py
├── test_orchestrator.py
├── apps/
│   └── test_efatura_supplier_docs_download.py
└── conftest.py
```

## Modificar Apps Existentes

### App: efatura-supplier-docs-download

#### Localização
- `apps/efatura_supplier_docs_download/app.py`
- Código legado em `app/update_supplier_invoices.py`

#### Estrutura
- **Wrapper**: A app atual é um wrapper do código legado
- **Migração futura**: Planeado migrar lógica para dentro da app

#### Modificações Comuns

**Adicionar nova coluna ao Excel**:
1. Localizar `COLUMNS` e `COLUMNS_DTYPE` em `update_supplier_invoices.py`
2. Adicionar coluna à lista
3. Atualizar função de escrita (`append_line_rows`)
4. Manter ordem estável (contrato)

**Novo tipo de documento**:
1. Localizar `DOC_TYPECODE_TO_LABEL`
2. Adicionar mapeamento
3. Atualizar função de inferência se necessário

**Ajustar parsing XML**:
1. Localizar `parse_invoice_lines`
2. Modificar extração conforme necessário
3. Manter tratamento defensivo

## Dependências entre Apps

### Definir Dependências

```python
def get_dependencies(self) -> list[str]:
    """Esta app depende de outra app."""
    return ["efatura-supplier-docs-download"]
```

### Configuração de Dependências

Na configuração JSON:

```json
{
  "minha-app": {
    "config": {...},
    "dependencies": {
      "efatura-supplier-docs-download": {
        "config_file": "..."
      }
    }
  }
}
```

O orquestrador executará dependências automaticamente antes da app principal.

## Workflows

### Criar Workflow

Criar ficheiro `config/workflow.json`:

```json
{
  "name": "workflow_completo",
  "description": "Processamento completo de documentos fiscais",
  "continue_on_error": false,
  "apps": [
    {
      "name": "app-1",
      "config": {...}
    },
    {
      "name": "app-2",
      "config": {...}
    }
  ]
}
```

**Parâmetros**:
- `continue_on_error`: Se `true`, continua mesmo se uma app falhar
- `apps`: Lista de apps a executar sequencialmente

### Executar Workflow

```bash
python main.py --workflow config/workflow.json --config config/config.json
```

## Debugging

### Modo Verbose

Ativar logging detalhado:

```bash
python main.py --app minha-app --config config.json --verbose
```

### Logs

Consultar logs em `logs/`:
- Log principal da execução
- Dumps de erros XML em `logs/bad_responses/`
- Documentos sem linhas em `logs/no_lines/`

### Breakpoints (IDE)

Para debugging interativo:
1. Configurar IDE para Python
2. Adicionar breakpoints
3. Executar com `--verbose` para ver progresso

## Performance

### Otimizações Comuns

1. **Checkpoints**: Ajustar `save_every_docs` e `save_every_seconds`
2. **Limites**: Usar `max_docs` para testes
3. **Cache**: Cachear resultados de APIs quando possível
4. **Batch processing**: Processar em lotes quando viável

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Código a analisar
result = app.run(config, context)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 funções
```

## Contribuindo

### Checklist antes de Commit

- [ ] Código segue padrões de nomenclatura
- [ ] Type hints presentes
- [ ] Docstrings documentadas
- [ ] Logging apropriado
- [ ] Tratamento de erros adequado
- [ ] Testado manualmente
- [ ] Sem código comentado desnecessário
- [ ] Formatação consistente (considerar `black` ou similar)

### Mensagens de Commit

Usar formato descritivo:
```
feat: adiciona nova app para export de vendas
fix: corrige parsing de XML com caracteres especiais
docs: atualiza documentação de setup
refactor: extrai lógica de parsing para módulo separado
```

## Recursos Adicionais

- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura do sistema
- [API.md](API.md) - Documentação de APIs e componentes
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Resolução de problemas
