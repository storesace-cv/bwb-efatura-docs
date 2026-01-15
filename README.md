# BWB App

Sistema modular de gestão de dados fiscais com suporte a múltiplas mini apps e orquestração.

## Índice

- [Sobre](#sobre)
- [Características](#características)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Mini Apps Disponíveis](#mini-apps-disponíveis)
- [Desenvolvimento](#desenvolvimento)
- [Documentação](#documentação)
- [Roadmap](#roadmap)
- [Licença](#licença)

## Sobre

O **BWB App** é um sistema modular desenvolvido para gestão de dados fiscais, especificamente para interagir com o portal **eFatura Cabo Verde**. O sistema baseia-se numa arquitetura de **mini apps orquestradas**, permitindo a execução modular e independente de diferentes funcionalidades.

### Características Principais

- 🧩 **Arquitetura Modular**: Cada funcionalidade é uma mini app independente
- 🎯 **Orquestração**: Execução automática de apps com dependências
- 🔄 **Workflows**: Sequências configuráveis de apps
- 🛡️ **Resiliência**: Tratamento robusto de erros e retoma segura
- 📊 **Export para Excel**: Saída estruturada e compatível
- 🔐 **Autenticação**: Integração com eFatura CV via JWT

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

1. **Token de Acesso**: Criar `app/token.json` com token JWT do portal eFatura CV:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "opcional"
   }
   ```
   ⚠️ **Importante**: Este ficheiro contém credenciais sensíveis. Nunca commitar para Git.

2. **Configuração INI**: Configurar ficheiro INI para cada mini app (ex: `app/purchases_update_supplier.ini`)

Para mais detalhes, consulte [SETUP.md](docs/SETUP.md).

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

Consulte [DEVELOPMENT.md](docs/DEVELOPMENT.md) para guia completo de desenvolvimento.

**Quick Start**:

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

4. Verificar descoberta: `python main.py --list-apps`

## Documentação

A documentação completa está disponível na pasta [docs/](docs/):

- 📐 [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura do sistema
- 🔧 [SETUP.md](docs/SETUP.md) - Guia de instalação e configuração
- 💻 [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Guia para desenvolvedores
- 📚 [API.md](docs/API.md) - Documentação de APIs e componentes
- 🗺️ [ROADMAP.md](docs/ROADMAP.md) - Roadmap e status do projeto
- 🔍 [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Resolução de problemas
- 📝 [CHANGELOG.md](docs/CHANGELOG.md) - Histórico de mudanças

## Roadmap

Ver [ROADMAP.md](docs/ROADMAP.md) para detalhes completos.

### Próximas Versões

- **v0.2.0**: Migração de código legado, testes automatizados
- **v0.3.0**: API REST, base de dados, novas mini apps
- **v1.0.0**: Interface web, integrações avançadas

## Licença

[Definir conforme política interna]
