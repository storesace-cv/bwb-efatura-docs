# Roadmap e Status do Projeto

## Status Atual

### Versão Atual
**v0.1.0** - MVP (Minimum Viable Product)

### Estado
- ✅ **Core Framework**: Implementado e funcional
- ✅ **Orquestrador**: Implementado e funcional
- ✅ **Mini App Base**: efatura-supplier-docs-download implementada
- ✅ **CLI**: Interface de linha de comando funcional
- ⚠️ **Documentação**: Em desenvolvimento (este documento)
- 🔄 **Migração de Código Legado**: Em progresso
- ❌ **API REST**: Não iniciado
- ❌ **Base de Dados**: Não iniciado
- ❌ **Autenticação Automática**: Não iniciado
- ❌ **Testes Automatizados**: Não iniciado

## O que Está Feito ✅

### Core Framework
- [x] Classe base `BaseApp` com interface abstrata
- [x] `AppContext` para contexto partilhado entre apps
- [x] Sistema de exceções personalizadas
- [x] Setup de logging configurável
- [x] Suporte para dependências entre apps

### Orquestrador
- [x] Descoberta dinâmica de mini apps
- [x] Validação de configuração
- [x] Resolução e execução de dependências
- [x] Execução sequencial de apps
- [x] Suporte para workflows configuráveis

### Mini Apps
- [x] **efatura-supplier-docs-download**
  - [x] Download de documentos fiscais do eFatura CV
  - [x] Parse de XML defensivo
  - [x] Export para Excel (1 item = 1 linha)
  - [x] Sistema de retoma segura
  - [x] Checkpoints configuráveis
  - [x] Tratamento de erros robusto

### CLI
- [x] Listagem de apps disponíveis
- [x] Execução de apps individuais
- [x] Execução de workflows
- [x] Suporte para configuração JSON
- [x] Logging verboso opcional

### Documentação
- [x] README.md principal
- [x] ARCHITECTURE.md
- [x] SETUP.md
- [x] DEVELOPMENT.md
- [x] API.md
- [x] ROADMAP.md (este documento)
- [x] TROUBLESHOOTING.md (planeado)
- [x] CHANGELOG.md (planeado)

## O que Está por Fazer 🚧

### Curto Prazo (v0.2.0)

#### Migração de Código Legado
- [ ] Migrar lógica de `app/update_supplier_invoices.py` para dentro da mini app
- [ ] Remover dependências de código legado
- [ ] Limpar código duplicado
- [ ] Refatorar para melhor modularidade

#### Melhorias na Mini App Existente
- [ ] Adicionar suporte para refresh token automático
- [ ] Melhorar tratamento de documentos sem linhas
- [ ] Otimizar performance de parsing XML
- [ ] Adicionar suporte para processamento em lote

#### Testes
- [ ] Adicionar testes unitários para `BaseApp`
- [ ] Adicionar testes unitários para `AppOrchestrator`
- [ ] Adicionar testes de integração para mini apps
- [ ] Adicionar testes de workflows
- [ ] Configurar CI/CD básico

#### Documentação
- [ ] Adicionar exemplos de uso avançado
- [ ] Adicionar diagramas de sequência
- [ ] Documentar estratégias de extensão
- [ ] Adicionar guias de troubleshooting

### Médio Prazo (v0.3.0)

#### Novas Mini Apps
- [ ] **efatura-sales-docs-download**: Download de documentos de vendas
- [ ] **efatura-docs-validator**: Validação de documentos fiscais
- [ ] **efatura-reports-generator**: Geração de relatórios a partir de Excel
- [ ] **efatura-docs-upload**: Upload de documentos para eFatura CV

#### API REST
- [ ] Implementar API REST com FastAPI
- [ ] Endpoints para execução remota de apps
- [ ] Endpoints para gestão de workflows
- [ ] Autenticação JWT para API
- [ ] Documentação OpenAPI/Swagger
- [ ] Webhooks para notificações de conclusão

#### Base de Dados
- [ ] Migração de Excel para Supabase
- [ ] Schema de base de dados para documentos fiscais
- [ ] Suporte para consultas SQL
- [ ] Sincronização incremental
- [ ] Backup e restore

#### Autenticação Automática
- [ ] Integração com sistema de autenticação do eFatura CV
- [ ] Refresh token automático
- [ ] Gestão de sessões
- [ ] Cache de tokens

### Longo Prazo (v1.0.0)

#### Funcionalidades Avançadas
- [ ] Processamento assíncrono (background jobs)
- [ ] Processamento paralelo de documentos
- [ ] Cache de XML e resultados de APIs
- [ ] Suporte para múltiplos repositórios
- [ ] Sincronização bidirecional com eFatura CV

#### Integrações
- [ ] Integração com sistemas de contabilidade
- [ ] Integração com ERPs
- [ ] Export para outros formatos (CSV, JSON, PDF)
- [ ] Integração com ferramentas de BI

#### Interface Web
- [ ] Dashboard web para monitorização
- [ ] Interface para configuração de apps
- [ ] Interface para gestão de workflows
- [ ] Visualização de documentos fiscais
- [ ] Relatórios interativos

#### Performance e Escalabilidade
- [ ] Otimização de queries
- [ ] Suporte para grandes volumes de dados
- [ ] Processamento distribuído
- [ ] Cache distribuído (Redis)

#### Qualidade e Confiabilidade
- [ ] Monitorização e alertas
- [ ] Métricas e analytics
- [ ] Logging estruturado
- [ ] Tracing distribuído
- [ ] Testes de carga

## Prioridades

### Alta Prioridade 🔴
1. **Migração de Código Legado**: Essencial para manutenibilidade
2. **Testes Automatizados**: Garantir qualidade e prevenir regressões
3. **Refresh Token Automático**: Melhorar experiência do utilizador
4. **Documentação de Troubleshooting**: Ajudar utilizadores

### Média Prioridade 🟡
1. **Novas Mini Apps**: Expandir funcionalidades
2. **API REST**: Permitir integração remota
3. **Base de Dados**: Melhorar performance e consultas
4. **Melhorias na Mini App Existente**: Refinamento contínuo

### Baixa Prioridade 🟢
1. **Interface Web**: Melhorar usabilidade
2. **Integrações Externas**: Expandir ecossistema
3. **Funcionalidades Avançadas**: Nice-to-have
4. **Otimizações de Performance**: Melhorias incrementais

## Contribuições

Contribuições são bem-vindas! Por favor:
1. Consultar [DEVELOPMENT.md](DEVELOPMENT.md) para guias de desenvolvimento
2. Seguir padrões de código existentes
3. Adicionar testes para novas funcionalidades
4. Atualizar documentação conforme necessário

## Versões Planeadas

### v0.2.0 - Melhorias e Estabilização
**Data Planeada**: Q2 2025

**Foco**:
- Migração de código legado
- Testes automatizados
- Melhorias na app existente
- Documentação completa

### v0.3.0 - Expansão de Funcionalidades
**Data Planeada**: Q3 2025

**Foco**:
- Novas mini apps
- API REST
- Base de dados
- Autenticação automática

### v1.0.0 - Produção
**Data Planeada**: Q4 2025

**Foco**:
- Funcionalidades avançadas
- Interface web
- Integrações
- Performance e escalabilidade

## Notas

- As datas são estimativas e podem mudar conforme prioridades
- Funcionalidades podem ser adicionadas ou removidas conforme feedback
- Contribuições e sugestões são sempre bem-vindas

## Histórico de Mudanças

Ver [CHANGELOG.md](CHANGELOG.md) para histórico detalhado de versões.
