# eFatura CV — Supplier Invoices Exporter

Este repositório contém um script Python (`update_supplier_invoices.py`) para exportar documentos fiscais eletrónicos (DFE) do portal **eFatura Cabo Verde** para um ficheiro **Excel**.

## Objetivo

- Listar DFEs num intervalo de datas (por defeito usando `AuthorizedDateTime` / data eFatura).
- Descarregar o XML de cada documento por **UID**.
- Extrair dados do cabeçalho (fornecedor, NIF, morada, datas, nº documento, tipo de documento).
- Extrair **todas as linhas (items)** do documento.
- Escrever para Excel com a regra:
  - **1 item = 1 linha no Excel**
  - **o UID repete-se** tantas vezes quantos items existirem no documento

## Tipos de documentos (Cabo Verde)

O script suporta a identificação do tipo via `DocumentTypeCode` no XML `<Dfe>` e/ou inferência pelo número do documento.
Códigos comuns em Cabo Verde:

- FTE → Fatura Eletrónica
- FRE → Fatura Recibo Eletrónica
- TVE → Talão de Venda Eletrónico
- RCE → Recibo Eletrónico
- NCE → Nota de Crédito Eletrónica
- NDE → Nota de Débito Eletrónica
- DVE → Nota de Devolução Eletrónica
- DTE → Documento de Transporte Eletrónico
- NLE → Nota de Lançamento Eletrónica

## Requisitos

- Python 3.10+ (recomendado 3.11)
- Dependências:
  - `requests`
  - `openpyxl`

Instalação:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install requests openpyxl
```

## Configuração (INI)

O script é configurado por INI. Exemplo (simplificado):

```ini
[paths]
base_dir = /caminho/para/pasta/onde/ficara/o/excel
excel_path = supplier_invoices.xlsx

[efatura]
token_json = token.json
repo_code = 1
date_start = 2025-09-01
date_end   = 2025-12-31
page_size = 200
timeout_sec = 45
retries = 3
retry_backoff_sec = 1.5

[logging]
progress_every_docs = 10
save_every_docs = 10
save_every_seconds = 60
log_file = /caminho/para/logs/update_supplier_invoices.log
```

Notas:
- `token_json` deve conter `access_token` (e opcionalmente `refresh_token`). **Nunca commits este ficheiro.**
- `base_dir` é a pasta de trabalho onde o Excel e os ficheiros de estado são criados.

## Execução

```bash
python3 update_supplier_invoices.py --config purchases_update_supplier.ini
```

Opções úteis:

- Guardar Excel mais frequentemente (checkpoint):
  - `--save-every-docs 1`
  - `--save-every-seconds 15`
- Reescrever UIDs existentes (cuidado: pesado):
  - `--rewrite-existing`
- Limitar para teste:
  - `--max-docs 50`

## Saída (Excel)

O Excel contém as seguintes colunas (ordem estável, usada como “contrato”):

- UID
- Erro
- Nome Fornecedor / NIF / Morada
- Data eFatura
- Data Documento
- Tipo de Documento
- Numero Documento
- Campos por item (código, descrição, qty, unidade, preços, impostos, etc.)
- last_updated / Exported

## Retoma segura (Opção 2)

O script cria automaticamente um ficheiro ao lado do Excel:

- `supplier_invoices.xlsx.resume.json`

Se houver falha a meio de um documento, na execução seguinte o script:
1) apaga todas as linhas desse UID no Excel
2) reescreve o documento completo (todas as linhas)

## Logs e diagnóstico

- Log principal: `logs/update_supplier_invoices.log` (configurável)
- Dumps de respostas inválidas (parse errors): `logs/bad_responses/`
- Dumps de documentos sem linhas (para análise): `logs/no_lines/`

## Segurança

- `token.json` contém credenciais. Guardar fora do Git e proteger permissões (ex.: `chmod 600 token.json`).
- Não publicar logs/dumps sem remover dados sensíveis.

## Licença

Definir conforme política interna do projeto.
