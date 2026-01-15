# Arquitetura do Sistema

## Visão Geral

O **BWB App** é um sistema modular de gestão de dados fiscais desenvolvido para interagir com o portal **eFatura Cabo Verde**. O sistema é baseado numa arquitetura de **mini apps orquestradas**, permitindo a execução modular e independente de diferentes funcionalidades.

## Princípios de Design

### 1. Modularidade
- Cada funcionalidade é implementada como uma **mini app** independente
- Mini apps podem ser executadas isoladamente ou em conjunto via workflows
- Fácil adição de novas funcionalidades sem modificar código existente

### 2. Orquestração
- **Orquestrador central** (`AppOrchestrator`) gerencia execução de apps
- Suporte para **dependências** entre apps
- Execução sequencial ou em workflows configuráveis

### 3. Contexto Partilhado
- `AppContext` fornece contexto comum entre apps
- Partilha de diretórios, autenticação e dados entre execuções
- Isolamento de dados por execução via `run_id`

### 4. Resiliência
- Tratamento robusto de erros XML malformados
- Retoma segura de execuções interrompidas
- Checkpoints automáticos para preservar progresso

## Componentes Principais

### Core Framework

```
core/
├── base_app.py          # Classe base abstrata BaseApp
├── context.py           # AppContext - contexto partilhado
├── exceptions.py        # Exceções personalizadas
└── logging_setup.py     # Configuração de logging
```

#### BaseApp
Interface abstrata que todas as mini apps devem implementar:

- `name`: Nome único da app
- `description`: Descrição da funcionalidade
- `version`: Versão da app
- `validate_config()`: Validação de configuração
- `run()`: Execução principal
- `get_dependencies()`: Lista de apps dependentes
- `cleanup()`: Limpeza de recursos (opcional)

#### AppContext
Contexto partilhado entre apps contendo:
- Diretórios de trabalho (`base_dir`, `work_dir`, `log_dir`)
- Autenticação partilhada (`access_token`, `token_expiry`)
- Metadados de execução (`run_id`, `start_time`)
- Dados partilhados (`shared_data`, `output_files`)

### Orchestrator

```
orchestrator/
└── runner.py            # AppOrchestrator
```

#### AppOrchestrator
Responsabilidades:
- **Descoberta dinâmica** de mini apps na pasta `apps/`
- **Validação** de configuração antes da execução
- **Resolução de dependências** (executa apps dependentes primeiro)
- **Execução sequencial** de apps individuais
- **Execução de workflows** (sequências configuráveis de apps)

### Mini Apps

```
apps/
└── efatura_supplier_docs_download/
    ├── __init__.py
    └── app.py           # Implementação da app
```

Cada mini app:
- Herda de `BaseApp`
- Define sua própria configuração
- Pode depender de outras apps
- Retorna `AppResult` com resultado da execução

### Entry Point

```
main.py                  # CLI principal
```

Interface de linha de comando que:
- Lista apps disponíveis
- Executa apps individuais
- Executa workflows
- Gerencia configuração e logging

## Fluxo de Execução

### Execução de App Individual

```
1. main.py recebe comando --app <nome>
2. Carrega configuração JSON
3. Cria AppOrchestrator
4. Orquestrador valida configuração da app
5. Resolve e executa dependências (se houver)
6. Executa app principal
7. Retorna AppResult
```

### Execução de Workflow

```
1. main.py recebe comando --workflow <arquivo>
2. Carrega configuração de workflow JSON
3. Para cada app no workflow:
   a. Valida configuração
   b. Resolve dependências
   c. Executa app
   d. Continua ou para em caso de erro (conforme config)
4. Retorna lista de AppResult
```

## Integração com eFatura CV

### Autenticação
- Token Bearer JWT armazenado em `token.json`
- Validação de expiração antes da execução
- Suporte para refresh token (futuro)

### APIs Utilizadas

#### Listagem de Documentos
- Endpoint: `services.efatura.cv/api/v1/dfe/list`
- Método: GET com paginação
- Retorna: Lista de UIDs de documentos fiscais

#### Download de Documento
- Endpoint: `services.efatura.cv/api/v1/dfe/{uid}/inner`
- Método: GET
- Retorna: XML do documento fiscal

#### UserInfo
- Endpoint: `iam.efatura.cv/userinfo`
- Método: GET
- Uso: Validação de token

## Estrutura de Dados

### Excel Output (efatura-supplier-docs-download)

Estrutura de colunas:
- **Identificação**: UID, Erro
- **Fornecedor**: Nome, NIF, Morada
- **Documento**: Data eFatura, Data Documento, Tipo, Número
- **Itens**: Código, Descrição, Quantidade, Unidade, Preços, Impostos
- **Metadados**: last_updated, Exported

**Regra de negócio**: 1 item = 1 linha no Excel (UID repetido)

### Retoma Segura

Sistema de retoma usando `resume.json`:
- Rastreia último UID iniciado mas não completado
- Na próxima execução, reescreve o UID completo
- Garante consistência mesmo após crashes

## Padrões de Código

### Tratamento de Erros
- Exceções específicas: `BWBConfigError`, `BWBExecutionError`
- Logging detalhado de erros
- Continuidade de execução quando possível (apps seguintes)

### Parsing XML Defensivo
1. Tentativa de parse direto
2. Se falhar: sanitização de caracteres problemáticos
3. Se falhar: dump do XML para análise
4. Registra erro no Excel e continua processamento

### Paginação Resiliente
- Não confia em `page_size` do servidor
- Detecção de loops (páginas repetidas)
- Assinatura baseada em (primeiro_UID, último_UID, count)

## Extensibilidade

### Adicionar Nova Mini App

1. Criar diretório em `apps/nome_da_app/`
2. Implementar classe herdando de `BaseApp`
3. Definir propriedades: `name`, `description`, `version`
4. Implementar `validate_config()` e `run()`
5. Opcionalmente definir `get_dependencies()` e `cleanup()`

### Adicionar Novos Campos ao Excel

1. Adicionar coluna em `COLUMNS`
2. Definir tipo em `COLUMNS_DTYPE`
3. Atualizar mapeamento em função de escrita
4. Manter ordem estável (contrato com consumidores)

## Tecnologias e Dependências

### Linguagem e Runtime
- **Python 3.10+** (recomendado 3.11+)
- Suporte para type hints

### Bibliotecas Principais
- `requests`: Cliente HTTP para APIs do eFatura
- `openpyxl`: Manipulação de ficheiros Excel
- Biblioteca padrão: `pathlib`, `dataclasses`, `abc`, `logging`

### Futuras Integrações (Planeadas)
- **FastAPI**: API REST para execução remota
- **Supabase**: Base de dados e autenticação
- **python-dotenv**: Gestão de variáveis de ambiente

## Segurança

### Credenciais
- `token.json` contém JWT - **nunca commitar**
- Usar `.gitignore` para ficheiros sensíveis
- Permissões restritas recomendadas (`chmod 600`)

### Validação de Input
- Validação de configuração antes da execução
- Sanitização de XML antes do parsing
- Validação de paths e ficheiros

### Logging
- Logs não devem conter credenciais
- Dumps de XML podem conter dados sensíveis
- Proteger diretórios de logs

## Performance

### Otimizações
- Checkpoints configuráveis (`save_every_docs`, `save_every_seconds`)
- Processamento assíncrono futuro (planeado)
- Cache de UIDs já processados

### Limitações Conhecidas
- Execução sequencial de apps (sem paralelismo)
- Processamento de documentos um a um
- Sem cache de XML entre execuções

## Diagrama de Componentes

```
┌─────────────────────────────────────────┐
│           main.py (CLI)                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      AppOrchestrator                    │
│  - Descobre apps                        │
│  - Resolve dependências                 │
│  - Executa apps/workflows               │
└──────┬──────────────────┬───────────────┘
       │                  │
       ▼                  ▼
┌─────────────┐    ┌──────────────────────┐
│   BaseApp   │    │    AppContext        │
│  (Abstract) │◄───│  - Diretórios        │
└──────┬──────┘    │  - Autenticação      │
       │           │  - Dados partilhados │
       │           └──────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Mini Apps                              │
│  - efatura-supplier-docs-download       │
│  - (futuras apps...)                    │
└─────────────────────────────────────────┘
```

## Decisões Arquiteturais

### Por que Mini Apps?
- **Isolamento**: Bugs numa app não afetam outras
- **Reutilização**: Apps podem ser combinadas em workflows
- **Testabilidade**: Cada app pode ser testada isoladamente
- **Extensibilidade**: Fácil adicionar novas funcionalidades

### Por que Orquestrador?
- **Centralização**: Ponto único de controlo
- **Dependências**: Gestão automática de ordem de execução
- **Consistência**: Mesma interface para todas as apps
- **Observabilidade**: Logging e métricas centralizados

### Por que Excel?
- **Compatibilidade**: Formato universalmente aceite
- **Facilidade**: Não requer base de dados
- **Portabilidade**: Ficheiro único contém todos os dados
- **Migração futura**: Fácil converter para base de dados

## Próximos Passos Arquiteturais

1. **API REST**: FastAPI para execução remota
2. **Base de Dados**: Migração de Excel para Supabase
3. **Processamento Assíncrono**: Suporte para execução paralela
4. **Cache**: Cache de XML e resultados de APIs
5. **Autenticação Automática**: Refresh token automático
6. **Webhooks**: Notificações de conclusão de execuções
