# Índice da Documentação

Bem-vindo à documentação do **BWB App**! Este índice ajuda-o a navegar pelos documentos disponíveis.

## Documentação Principal

### [README.md](../README.md)
Visão geral do projeto, instalação rápida e links para documentação detalhada.

## Guias de Início

### [SETUP.md](SETUP.md)
Guia completo de instalação e configuração:
- Pré-requisitos
- Instalação passo a passo
- Configuração de token e credenciais
- Validação da instalação
- Configuração de workflows

### [ARCHITECTURE.md](ARCHITECTURE.md)
Documentação de arquitetura do sistema:
- Visão geral da arquitetura
- Componentes principais
- Fluxo de execução
- Padrões de código
- Extensibilidade
- Decisões arquiteturais

## Desenvolvimento

### [DEVELOPMENT.md](DEVELOPMENT.md)
Guia para desenvolvedores:
- Criar novas mini apps
- Padrões e boas práticas
- Modificar apps existentes
- Dependências entre apps
- Workflows
- Debugging
- Performance

### [API.md](API.md)
Documentação de APIs e componentes:
- Core Framework (BaseApp, AppContext, AppResult)
- Orquestrador (AppOrchestrator)
- Exceções
- Logging
- Mini Apps existentes
- CLI (Command Line Interface)
- Estruturas de dados

## Referência e Suporte

### [ROADMAP.md](ROADMAP.md)
Roadmap e status do projeto:
- O que está feito
- O que está por fazer
- Prioridades
- Versões planeadas

### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
Guia de resolução de problemas:
- Problemas comuns
- Logs e diagnóstico
- Resolução passo a passo
- Obter ajuda

### [CHANGELOG.md](CHANGELOG.md)
Histórico de mudanças do projeto:
- Versões e mudanças
- Tipos de mudanças

## Documentação Técnica

### [TECHNICAL_DOC.md](TECHNICAL_DOC.md)
Documentação técnica detalhada (legado):
- Visão geral de arquitetura
- Contratos e invariantes
- Estratégia de paginação
- Sanitização e parsing XML

### [AI_MAINTENANCE.md](AI_MAINTENANCE.md)
Guia de manutenção para AI (legado):
- Invariantes
- Pontos de extensão
- Como validar alterações

## Documentação eFatura

### [efatura/](../efatura/)
Documentação relacionada com eFatura Cabo Verde:
- Manual técnico
- XSD schemas
- Exemplos XML

## Início Rápido

### Para Utilizadores
1. Ler [README.md](../README.md) para visão geral
2. Seguir [SETUP.md](SETUP.md) para instalação
3. Consultar [TROUBLESHOOTING.md](TROUBLESHOOTING.md) se tiver problemas

### Para Desenvolvedores
1. Ler [ARCHITECTURE.md](ARCHITECTURE.md) para entender o sistema
2. Seguir [DEVELOPMENT.md](DEVELOPMENT.md) para criar apps
3. Consultar [API.md](API.md) para referência de APIs
4. Ver [ROADMAP.md](ROADMAP.md) para ver o que está por fazer

## Estrutura da Documentação

```
docs/
├── INDEX.md              # Este ficheiro
├── README.md             # Visão geral
├── ARCHITECTURE.md       # Arquitetura
├── SETUP.md              # Instalação
├── DEVELOPMENT.md        # Desenvolvimento
├── API.md                # Documentação de API
├── ROADMAP.md            # Roadmap
├── TROUBLESHOOTING.md    # Resolução de problemas
├── CHANGELOG.md          # Histórico
├── TECHNICAL_DOC.md      # Documentação técnica (legado)
└── AI_MAINTENANCE.md     # Guia de manutenção (legado)
```

## Contribuir

Se encontrar problemas na documentação ou quiser contribuir:
1. Consultar [DEVELOPMENT.md](DEVELOPMENT.md)
2. Seguir padrões de documentação existentes
3. Manter documentação atualizada com mudanças no código
