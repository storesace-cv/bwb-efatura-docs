# AI Maintenance Guide — invariantes e pontos de extensão

Este ficheiro existe para que um assistente AI (ou um programador) consiga alterar o script sem regressões.

## Invariantes (NÃO quebrar)

1) **1 item = 1 linha no Excel**
   - Não deduplicar linhas por UID.
   - O UID repete-se por item.

2) **Opção 2 (reescrita determinística)**
   - Em retoma ou quando for necessário reprocessar um UID: apagar todas as linhas do UID e reescrever.

3) **Resiliência do XML**
   - O eFatura pode devolver XML inválido (caracteres e entidades).
   - O script deve continuar a processar os restantes UIDs mesmo quando um UID falha.

4) **Paginação defensiva**
   - Não confiar que `len(items) < page_size` termina paginação.
   - Manter detecção de página repetida.

## Onde mexer (com segurança)

- Schema Excel:
  - `COLUMNS`, `COLUMNS_DTYPE`, `ensure_workbook`
- Reescrita por UID:
  - `delete_uid_rows`, `uid_row_map`, estado resume
- Parsing XML:
  - `sanitize_xml_text`, `safe_parse_xml`, `_localname`, `_find_*`
- Tipos de documento:
  - `DOC_TYPECODE_TO_LABEL` e `infer_tipo_documento`
- Extração de linhas:
  - função que localiza `Lines/Line` ou equivalentes por localname

## Como validar alterações

- Rodar com `--max-docs 20` e comparar:
  - número de UIDs vs número total de linhas no Excel
  - repetição de UID por item
- Forçar interrupção (Ctrl+C) e garantir que o UID em progresso é reescrito na próxima execução
- Validar que logs/dumps são criados quando necessário
