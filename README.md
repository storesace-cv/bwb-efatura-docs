# BWB App

Sistema modular de gestão de dados fiscais com suporte a múltiplas mini apps e orquestração.

## Estrutura

```
bwb-app/
├── apps/                          # Mini apps
│   └── efatura_supplier_docs_download/
│       ├── __init__.py
│       └── app.py                 # Implementação da mini app
│
├── core/                          # Framework comum
│   ├── base_app.py                # Classe base para mini apps
│   ├── context.py                 # Contexto partilhado
│   ├── exceptions.py              # Exceções personalizadas
│   └── logging_setup.py           # Setup de logging
│
├── orchestrator/                  # Orquestrador
│   └── runner.py                  # Executor principal
│
├── config/                        # Configurações
│   ├── example_config.json
│   └── example_workflow.json
│
├── app/                           # Código legado (será migrado)
│   └── update_supplier_invoices.py
│
├── main.py                        # Entry point principal
└── requirements.txt
```

## Instalação

```bash
# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

1. Copiar `.env.local.example` para `.env.local` e preencher com valores reais
2. Configurar ficheiros INI para cada mini app (ex: `app/purchases_update_supplier.ini`)

## Uso

### Listar mini apps disponíveis

```bash
python main.py --list-apps
```

### Executar uma mini app

```bash
python main.py --app efatura-supplier-docs-download --config config/example_config.json
```

### Executar workflow

```bash
python main.py --workflow config/example_workflow.json --config config/example_config.json
```

## Mini Apps Disponíveis

### efatura-supplier-docs-download

Exporta documentos de compras (DFE) do portal eFatura CV para Excel.

**Configuração:**
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

## Desenvolvimento

### Criar nova mini app

1. Criar diretório em `apps/nome_da_app/`
2. Criar `__init__.py` e `app.py`
3. Implementar classe que herda de `BaseApp`:

```python
from core.base_app import BaseApp, AppResult
from core.context import AppContext

class MinhaApp(BaseApp):
    @property
    def name(self) -> str:
        return "minha-app"
    
    @property
    def description(self) -> str:
        return "Descrição da app"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def validate_config(self, config: dict) -> tuple[bool, Optional[str]]:
        # Validar config
        return True, None
    
    def run(self, config: dict, context: AppContext) -> AppResult:
        # Implementar lógica
        return AppResult(success=True, message="OK")
```

## Licença

[Definir conforme política interna]
