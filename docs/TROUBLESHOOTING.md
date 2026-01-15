# Guia de Resolução de Problemas

## Problemas Comuns

### Problemas de Instalação

#### Erro: "python3: command not found"

**Causa**: Python 3 não está instalado ou não está no PATH.

**Solução**:
```bash
# Verificar se Python está instalado
python3 --version

# Se não estiver, instalar (exemplo para Ubuntu/Debian)
sudo apt install python3 python3-venv python3-pip

# Ou instalar via Homebrew (macOS)
brew install python@3.11
```

#### Erro: "pip: command not found"

**Causa**: pip não está instalado.

**Solução**:
```bash
# Linux/macOS
python3 -m ensurepip --upgrade

# Ou instalar separadamente
sudo apt install python3-pip  # Ubuntu/Debian
brew install python@3.11       # macOS
```

#### Erro ao criar ambiente virtual

**Causa**: Módulo `venv` não está disponível.

**Solução**:
```bash
# Instalar python3-venv (Ubuntu/Debian)
sudo apt install python3-venv

# Ou usar python3 -m venv diretamente
python3 -m venv .venv
```

### Problemas de Configuração

#### Erro: "App não encontrada"

**Causa**: A mini app não está sendo descoberta pelo orquestrador.

**Solução**:
1. Verificar que o diretório existe em `apps/`
2. Verificar que tem `__init__.py` e `app.py`
3. Verificar que a classe herda de `BaseApp`
4. Verificar sintaxe Python (sem erros de import)

**Verificação**:
```bash
# Listar apps disponíveis
python main.py --list-apps

# Verificar estrutura
ls -la apps/minha-app/
# Deve mostrar: __init__.py app.py
```

#### Erro: "Config inválida"

**Causa**: Configuração JSON ou INI tem erros.

**Solução**:
1. Verificar sintaxe JSON (usar validador JSON online)
2. Verificar sintaxe INI (seções corretas, sem caracteres especiais)
3. Verificar que ficheiros referenciados existem
4. Verificar paths (absolutos ou relativos ao base_dir)

**Validação JSON**:
```bash
# Validar JSON
python -m json.tool config/config.json
```

**Validação INI**:
```python
import configparser
config = configparser.ConfigParser()
config.read('app/config.ini')
```

#### Erro: "Ficheiro de configuração não encontrado"

**Causa**: Caminho do ficheiro está incorreto.

**Solução**:
1. Verificar caminho absoluto ou relativo
2. Verificar que o ficheiro existe
3. Verificar permissões de leitura

**Verificação**:
```bash
# Verificar se ficheiro existe
ls -la app/purchases_update_supplier.ini

# Verificar permissões
chmod 644 app/purchases_update_supplier.ini
```

### Problemas de Autenticação

#### Erro: "TOKEN_EXPIRED_OR_INVALID"

**Causa**: Token JWT expirou ou é inválido.

**Solução**:
1. Obter novo token do portal eFatura CV
2. Atualizar `app/token.json` com novo token
3. Verificar formato do token (JSON válido)

**Verificação**:
```bash
# Verificar formato do token
cat app/token.json | python -m json.tool

# Verificar expiração do token (se possível)
# O sistema mostra automaticamente a expiração no log
```

**Renovação do Token**:
1. Aceder ao portal eFatura CV
2. Gerar novo token de acesso
3. Copiar token para `app/token.json`
4. Formato esperado:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "opcional"
   }
   ```

#### Erro: "token.json não encontrado"

**Causa**: Ficheiro de token não existe.

**Solução**:
1. Criar `app/token.json`
2. Adicionar token válido do eFatura CV
3. Verificar permissões (não deve ser público)

**Criar token.json**:
```bash
# Criar ficheiro
touch app/token.json
chmod 600 app/token.json  # Permissões restritas

# Editar e adicionar token
nano app/token.json
```

#### Erro: "Erro ao carregar token"

**Causa**: Formato do token JSON está incorreto.

**Solução**:
1. Verificar formato JSON válido
2. Verificar que contém `access_token`
3. Verificar que não tem caracteres inválidos

**Validação**:
```bash
python -m json.tool app/token.json
```

### Problemas de Conectividade

#### Erro: "Erro DNS services.efatura.cv"

**Causa**: Não consegue resolver DNS ou não tem conectividade.

**Solução**:
1. Verificar conectividade de rede
2. Verificar firewall/proxy
3. Verificar DNS resolver

**Teste de Conectividade**:
```bash
# Testar DNS
nslookup services.efatura.cv

# Testar conectividade
ping services.efatura.cv

# Testar HTTP
curl -v https://services.efatura.cv
```

#### Erro: "Timeout ao conectar"

**Causa**: Servidor não responde ou timeout muito baixo.

**Solução**:
1. Aumentar `timeout_sec` no INI
2. Verificar conectividade
3. Verificar se servidor está online

**Ajustar Timeout**:
```ini
[efatura]
timeout_sec = 60  # Aumentar de 45 para 60
```

#### Erro: "Connection refused"

**Causa**: Servidor recusa conexão.

**Solução**:
1. Verificar se URL está correta
2. Verificar firewall/proxy
3. Contactar suporte eFatura CV se necessário

### Problemas de Execução

#### Erro: "Erro ao processar documento"

**Causa**: XML malformado ou erro de parsing.

**Solução**:
1. Verificar logs para detalhes
2. Verificar dumps em `logs/bad_responses/`
3. Verificar se é problema conhecido

**Diagnóstico**:
```bash
# Verificar logs
tail -f logs/update_supplier_invoices.log

# Verificar dumps
ls -la logs/bad_responses/
```

#### Erro: "Documento sem linhas"

**Causa**: Documento não tem linhas de itens (ex.: recibo).

**Solução**:
1. Normal para alguns tipos de documentos
2. Sistema regista erro controlado no Excel
3. Verificar dumps em `logs/no_lines/`

**Verificação**:
```bash
# Verificar documentos sem linhas
ls -la logs/no_lines/
```

#### Erro: "Excel não pode ser aberto"

**Causa**: Ficheiro corrompido ou em uso.

**Solução**:
1. Verificar se ficheiro está aberto noutro programa
2. Fechar Excel/outros programas
3. Verificar permissões de escrita
4. Se corrompido, restaurar de backup ou remover e recomeçar

**Verificação**:
```bash
# Verificar se ficheiro está em uso (Linux/macOS)
lsof supplier_invoices.xlsx

# Verificar permissões
ls -la supplier_invoices.xlsx
chmod 644 supplier_invoices.xlsx
```

#### Erro: "Memória insuficiente"

**Causa**: Processamento de muitos documentos simultaneamente.

**Solução**:
1. Processar em lotes menores (`max_docs`)
2. Aumentar checkpoints (`save_every_docs`)
3. Aumentar memória disponível

**Otimização**:
```json
{
  "efatura-supplier-docs-download": {
    "max_docs": 100,  # Processar em lotes
    "save_every_docs": 50  # Checkpoints frequentes
  }
}
```

### Problemas de Performance

#### Lento ao processar documentos

**Causa**: Muitos documentos ou checkpoints muito frequentes.

**Solução**:
1. Reduzir frequência de checkpoints
2. Processar em paralelo (futuro)
3. Otimizar queries de API

**Ajustar Checkpoints**:
```ini
[logging]
save_every_docs = 200  # Reduzir frequência
save_every_seconds = 600  # Aumentar intervalo
```

#### Muitos erros de rede

**Causa**: Instabilidade de rede ou servidor.

**Solução**:
1. Aumentar `retries` e `retry_backoff_sec`
2. Verificar conectividade
3. Executar em horários de menor tráfego

**Ajustar Retries**:
```ini
[efatura]
retries = 5  # Aumentar tentativas
retry_backoff_sec = 2.0  # Aumentar backoff
```

### Problemas Específicos da Mini App

#### efatura-supplier-docs-download

##### UIDs duplicados no Excel

**Causa**: Execução interrompida e retoma incompleta.

**Solução**:
1. Usar `rewrite_existing=true` para reescrever
2. Verificar `resume.json` para UIDs incompletos
3. Limpar Excel e recomeçar se necessário

##### Excel cresce muito

**Causa**: Muitos documentos processados.

**Solução**:
1. Normal para grandes volumes
2. Considerar migração para base de dados (futuro)
3. Arquivar dados antigos

##### Parsing XML falha frequentemente

**Causa**: XML malformado do eFatura CV.

**Solução**:
1. Verificar dumps em `logs/bad_responses/`
2. Reportar problemas ao suporte eFatura CV
3. Sistema continua processamento de outros documentos

## Logs e Diagnóstico

### Localização de Logs

- **Log principal**: `logs/update_supplier_invoices.log` (configurável no INI)
- **Dumps de XML inválido**: `logs/bad_responses/`
- **Documentos sem linhas**: `logs/no_lines/`
- **Logs do orquestrador**: Console ou ficheiro configurável

### Níveis de Log

- **DEBUG**: Informação detalhada (usar com `--verbose`)
- **INFO**: Progresso normal
- **WARNING**: Situações atípicas mas não críticas
- **ERROR**: Erros que impedem funcionamento parcial
- **CRITICAL**: Erros que impedem funcionamento total

### Consultar Logs

```bash
# Ver últimas linhas
tail -f logs/update_supplier_invoices.log

# Procurar erros
grep ERROR logs/update_supplier_invoices.log

# Procurar WARNINGS
grep WARNING logs/update_supplier_invoices.log

# Ver logs de uma execução específica
grep "run_id=20250101_120000" logs/update_supplier_invoices.log
```

## Resolução Passo a Passo

### Problema: App não executa

1. Verificar que app está descoberta: `python main.py --list-apps`
2. Verificar configuração JSON ou INI
3. Verificar que ficheiros referenciados existem
4. Executar com `--verbose` para ver detalhes
5. Consultar logs para erros específicos

### Problema: Token expirado

1. Obter novo token do portal eFatura CV
2. Atualizar `app/token.json`
3. Verificar formato JSON válido
4. Executar novamente

### Problema: Erros de parsing XML

1. Consultar logs para UIDs problemáticos
2. Verificar dumps em `logs/bad_responses/`
3. Se persistente, reportar ao suporte eFatura CV
4. Sistema continua processamento de outros documentos

### Problema: Performance lenta

1. Verificar número de documentos a processar
2. Ajustar checkpoints (`save_every_docs`, `save_every_seconds`)
3. Processar em lotes menores (`max_docs`)
4. Verificar conectividade de rede

## Obter Ajuda

### Antes de Pedir Ajuda

1. Consultar este guia
2. Consultar logs para erros específicos
3. Verificar configuração
4. Reproduzir problema com `--verbose`

### Informações a Fornecer

Ao pedir ajuda, fornecer:
1. Versão do Python: `python3 --version`
2. Versão da app: `python main.py --list-apps`
3. Comando executado (com parâmetros)
4. Mensagens de erro completas
5. Logs relevantes (últimas 50-100 linhas)
6. Configuração (sem credenciais)

### Canais de Suporte

- **Documentação**: Consultar [README.md](../README.md) e outros docs
- **Issues**: Reportar issues no repositório (se aplicável)
- **Equipa de Desenvolvimento**: Contactar diretamente

## Prevenção de Problemas

### Boas Práticas

1. **Backup**: Fazer backup regular de ficheiros importantes
2. **Testes**: Testar com `max_docs` pequeno antes de processar tudo
3. **Verificação**: Verificar configuração antes de executar
4. **Logs**: Monitorizar logs durante execução
5. **Token**: Renovar token antes de expirar

### Checklist Antes de Executar

- [ ] Python 3.10+ instalado e no PATH
- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Token válido em `app/token.json`
- [ ] Configuração INI válida
- [ ] Diretórios criados (logs, work)
- [ ] Conectividade de rede verificada
- [ ] Permissões de escrita verificadas

## Problemas Conhecidos

### XML Malformado

**Status**: Conhecido, mitigado
**Descrição**: Alguns documentos do eFatura CV têm XML malformado
**Mitigação**: Sistema tenta sanitização automática, regista erro se falhar
**Workaround**: Nenhum necessário, sistema continua processamento

### Documentos sem Linhas

**Status**: Comportamento esperado
**Descrição**: Alguns documentos (ex.: recibos) não têm linhas de itens
**Comportamento**: Sistema regista erro controlado, continua processamento
**Nota**: Não é um problema, é comportamento esperado

### Paginação Inconsistente

**Status**: Conhecido, mitigado
**Descrição**: API do eFatura CV pode retornar tamanhos de página inconsistentes
**Mitigação**: Sistema usa detecção de loops para parar paginação
**Workaround**: Nenhum necessário
