# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste ficheiro.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Planeado
- Migração completa de código legado para mini apps
- Testes automatizados
- API REST com FastAPI
- Integração com Supabase
- Refresh token automático
- Novas mini apps

## [0.1.0] - 2025-01-XX

### Adicionado
- Core framework com `BaseApp` abstrata
- Sistema de contexto partilhado (`AppContext`)
- Orquestrador para execução de mini apps (`AppOrchestrator`)
- Sistema de exceções personalizadas
- Setup de logging configurável
- Suporte para dependências entre apps
- Suporte para workflows configuráveis
- CLI (`main.py`) para execução de apps e workflows
- Mini app `efatura-supplier-docs-download`:
  - Download de documentos fiscais do eFatura CV
  - Parse de XML defensivo com sanitização
  - Export para Excel (1 item = 1 linha)
  - Sistema de retoma segura
  - Checkpoints configuráveis
  - Tratamento robusto de erros
  - Suporte para referências entre documentos
- Documentação inicial:
  - README.md principal
  - ARCHITECTURE.md
  - SETUP.md
  - DEVELOPMENT.md
  - API.md
  - ROADMAP.md
  - TROUBLESHOOTING.md
  - CHANGELOG.md (este ficheiro)

### Estrutura Inicial
- Diretório `apps/` para mini apps
- Diretório `core/` para framework base
- Diretório `orchestrator/` para orquestração
- Diretório `config/` para ficheiros de configuração
- Diretório `docs/` para documentação
- Entry point `main.py`

### Características Principais
- Descoberta dinâmica de mini apps
- Validação de configuração antes da execução
- Resolução automática de dependências
- Execução sequencial de apps em workflows
- Suporte para retoma segura de execuções interrompidas
- Checkpoints automáticos para preservar progresso
- Logging detalhado e estruturado

### Notas
- Versão inicial (MVP)
- Código legado ainda em `app/update_supplier_invoices.py` (a migrar)
- Sem testes automatizados (a adicionar)
- Sem API REST (planeado para v0.3.0)
- Sem base de dados (planeado para v0.3.0)

## Tipos de Mudanças

- **Adicionado**: Para novas funcionalidades
- **Alterado**: Para mudanças em funcionalidades existentes
- **Depreciado**: Para funcionalidades que serão removidas
- **Removido**: Para funcionalidades removidas
- **Corrigido**: Para correções de bugs
- **Segurança**: Para vulnerabilidades corrigidas

## Links

- [ROADMAP.md](ROADMAP.md) - Roadmap e plano de desenvolvimento
- [README.md](../README.md) - Documentação principal
