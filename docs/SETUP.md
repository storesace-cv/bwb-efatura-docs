# Guia de Instalação e Configuração

## Pré-requisitos

### Sistema Operativo
- **Linux** (Ubuntu 20.04+, Debian 11+, ou similar)
- **macOS** 10.15+ (Catalina ou superior)
- **Windows** 10/11 (com WSL2 recomendado)

### Software Necessário

#### Python
- **Python 3.10 ou superior** (Python 3.11+ recomendado)
- Verificar versão instalada:
  ```bash
  python3 --version
  ```

Se não tiver Python 3.10+, instalar:
- **Linux**: `sudo apt install python3.10 python3.10-venv python3-pip`
- **macOS**: `brew install python@3.11`
- **Windows**: Download de [python.org](https://www.python.org/downloads/)

#### Git (opcional)
Para clonar o repositório:
```bash
git --version
```

### Conta eFatura CV
- Acesso ao portal [eFatura CV](https://efatura.cv)
- Token de acesso (JWT) obtido via portal
- Credenciais válidas para autenticação

## Instalação

### 1. Obter o Código

Se o código já está na máquina local, pule para o próximo passo.

Se estiver num repositório Git:
```bash
git clone <url-do-repositorio>
cd my-bwb-app
```

### 2. Criar Ambiente Virtual

**Recomendado**: Usar ambiente virtual Python para isolar dependências.

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

Após ativar, o prompt deve mostrar `(.venv)`.

### 3. Atualizar pip

```bash
pip install --upgrade pip
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

Dependências instaladas:
- `requests>=2.31.0` - Cliente HTTP
- `openpyxl>=3.1.2` - Manipulação de Excel

### 5. Verificar Instalação

```bash
# Verificar se as apps são descobertas
python main.py --list-apps
```

Deverá mostrar:
```
Mini Apps disponíveis:
============================================================

efatura-supplier-docs-download v1.0.0
  Descrição: Exporta documentos de compras (DFE) do portal eFatura CV para Excel
  Dependências: 
```

## Configuração

### 1. Obter Token de Acesso

O token JWT deve ser obtido do portal eFatura CV. Normalmente através de:
1. Login no portal
2. Acesso às configurações/API
3. Gerar token de acesso
4. Guardar o token (válido por período limitado)

**Importante**: O token expira. Será necessário renová-lo periodicamente.

### 2. Configurar Token

Criar ficheiro `app/token.json` com o seguinte formato:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "opcional_por_agora"
}
```

**Segurança**: 
- Este ficheiro contém credenciais sensíveis
- **Nunca commitar** para o repositório Git
- Usar permissões restritas: `chmod 600 app/token.json`
- Adicionar `app/token.json` ao `.gitignore`

### 3. Configurar App de Download

Copiar o ficheiro de exemplo:
```bash
cp app/purchases_update_supplier.sample.ini app/purchases_update_supplier.ini
```

Editar `app/purchases_update_supplier.ini`:

```ini
[paths]
# Diretório base onde será criado o Excel
base_dir = /caminho/para/pasta/trabalho
# Nome do ficheiro Excel (relativo a base_dir)
excel_path = supplier_invoices.xlsx

[efatura]
# Caminho para token.json (relativo ou absoluto)
token_json = app/token.json
# Código do repositório (geralmente 1)
repo_code = 1
# Intervalo de datas (formato YYYY-MM-DD)
date_start = 2025-01-01
date_end = 2025-12-31
# Tamanho de página para listagem (recomendado: 200)
page_size = 200
# Timeout para requests HTTP (segundos)
timeout_sec = 45
# Número de tentativas em caso de falha
retries = 3
# Backoff entre tentativas (segundos)
retry_backoff_sec = 1.5

[logging]
# Log a cada N documentos processados
progress_every_docs = 10
# Guardar Excel a cada N documentos
save_every_docs = 100
# Guardar Excel a cada N segundos (0 = desativado)
save_every_seconds = 300
# Caminho para ficheiro de log
log_file = logs/update_supplier_invoices.log
```

### 4. Criar Diretórios Necessários

```bash
# Criar diretório de logs
mkdir -p logs

# Criar diretório de trabalho (se diferente)
mkdir -p /caminho/para/pasta/trabalho
```

### 5. Configuração JSON (Opcional)

Para executar apps via configuração JSON, criar `config/config.json`:

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
- `config_file`: Caminho para ficheiro INI
- `max_docs`: Limite de documentos (0 = sem limite)
- `rewrite_existing`: Reescrever UIDs existentes (false = pular)
- `save_every_docs`: Sobrescrever checkpoints do INI (-1 = usar INI)
- `save_every_seconds`: Sobrescrever checkpoints do INI (-1 = usar INI)
- `verbose`: Logging detalhado (true/false)

## Validação da Configuração

### 1. Verificar DNS

O sistema precisa aceder a:
- `services.efatura.cv` - API principal
- `iam.efatura.cv` - Autenticação

Testar conectividade:
```bash
# Linux/macOS
ping services.efatura.cv
ping iam.efatura.cv

# Verificar resolução DNS
nslookup services.efatura.cv
```

### 2. Testar Token

```bash
# Executar com limite pequeno para teste
python main.py --app efatura-supplier-docs-download \
  --config config/example_config.json \
  --verbose
```

Se o token estiver expirado ou inválido, o sistema avisará:
```
ERROR: TOKEN_EXPIRED_OR_INVALID (userinfo). Atualizar token.json.
```

### 3. Teste com Limite

Executar com apenas alguns documentos:
```json
{
  "efatura-supplier-docs-download": {
    "config_file": "app/purchases_update_supplier.ini",
    "max_docs": 5,
    "verbose": true
  }
}
```

```bash
python main.py --app efatura-supplier-docs-download \
  --config config/config.json \
  --verbose
```

## Configuração de Workflows

Para executar sequências de apps, criar `config/workflow.json`:

```json
{
  "name": "export_completo",
  "description": "Export completo de documentos fiscais",
  "continue_on_error": false,
  "apps": [
    {
      "name": "efatura-supplier-docs-download",
      "config": {
        "config_file": "app/purchases_update_supplier.ini",
        "max_docs": 0,
        "rewrite_existing": false
      }
    }
  ]
}
```

**Parâmetros do workflow**:
- `name`: Nome identificador do workflow
- `description`: Descrição do workflow
- `continue_on_error`: Continuar mesmo se uma app falhar (true/false)
- `apps`: Lista de apps a executar sequencialmente

## Variáveis de Ambiente (Futuro)

Quando a integração com Supabase for adicionada, será necessário configurar:

```bash
# .env (não commitar)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
EFATURA_CLIENT_ID=xxx
EFATURA_CLIENT_SECRET=xxx
```

## Troubleshooting

### Problema: "App não encontrada"

**Solução**: Verificar que:
- O diretório `apps/` existe
- A app tem `__init__.py` e `app.py`
- A classe herda de `BaseApp`

### Problema: "Config inválida"

**Solução**: 
- Verificar sintaxe JSON ou INI
- Verificar que ficheiros referenciados existem
- Verificar paths (absolutos ou relativos)

### Problema: "Token expirado"

**Solução**:
1. Obter novo token do portal eFatura CV
2. Atualizar `app/token.json`
3. Verificar permissões do ficheiro

### Problema: "Erro DNS"

**Solução**:
- Verificar conectividade de rede
- Verificar firewall/proxy
- Verificar DNS resolver

## Próximos Passos

Após configuração bem-sucedida:
1. Ler [DEVELOPMENT.md](DEVELOPMENT.md) para criar novas apps
2. Ler [ROADMAP.md](ROADMAP.md) para ver funcionalidades planeadas
3. Consultar [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para problemas comuns

## Suporte

Para problemas não resolvidos:
1. Consultar logs em `logs/`
2. Verificar [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Verificar issues no repositório (se aplicável)
4. Contactar a equipa de desenvolvimento
