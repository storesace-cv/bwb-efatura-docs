# Documentação Técnica — update_supplier_invoices.py

## Visão geral de arquitetura

O script implementa um pipeline ETL simples:

1) **Config**: lê INI, resolve caminhos (base_dir, excel_path, log_file).
2) **HTTP Client**: autentica via token bearer (token.json) e comunica com:
   - endpoint de listagem (páginas)
   - endpoint de detalhe (XML do documento por UID)
3) **Parsing**: sanitiza e faz parse do XML (defensivo).
4) **Normalização**:
   - escolhe o documento principal (filho direto de `<Dfe>`)
   - extrai cabeçalho (supplier, datas, doc_number)
   - extrai linhas (items) e normaliza campos
5) **Persistência**: escreve no Excel com checkpoints + retoma segura.

## Contratos e invariantes

### UID e linhas
- UID identifica **o documento**.
- Um documento pode conter N items.
- O Excel armazena **N linhas**, todas com o mesmo UID, uma por item.

### Reescrita determinística (Opção 2)
- Se um UID já existir e precisar de ser reprocessado, o script:
  1) apaga todas as linhas desse UID no Excel (`delete_uid_rows`)
  2) escreve novamente todas as linhas do documento

Isto evita inconsistências quando existe crash a meio da escrita.

## Estratégia de paginação

O portal pode devolver um nº fixo de items por página (p.ex., 287) mesmo quando é pedido um `page_size` diferente, e pode repetir páginas (loop).
Por isso, o script usa detecção de loop por “assinatura”:

- assinatura = (primeiro UID, último UID, count)
- se a assinatura repetir, o script pára a listagem de forma segura.

## Sanitização e parsing XML

Problemas conhecidos:
- XML pode vir tecnicamente inválido (ex.: `&` não escapado em campos textuais)
- podem existir caracteres de controlo ilegais

Abordagem:
- `safe_parse_xml` tenta parse direto
- se falhar, aplica `sanitize_xml_text` e tenta novamente
- se falhar, grava dump para análise e segue para o próximo UID (o UID fica com erro no Excel)

## Seleção do documento principal

Em Cabo Verde, `<Dfe>` contém `DocumentTypeCode` e um único elemento-filho que é o documento principal.
O parser deve:
- localizar o `<Dfe>`
- escolher o **filho direto** como `doc_node`
- evitar escolher referências internas (`FiscalDocument`) como se fossem documento principal

## Documentos sem linhas e referências

Existem documentos que podem não expor linhas de items (ex.: recibos) e referenciam outro documento via `FiscalDocument`.
O script tenta:
- extrair linhas do documento
- se não houver linhas, seguir referências (`_find_reference_uids`) e tentar extrair linhas do documento referenciado

Se mesmo assim não houver linhas, o script:
- grava dump em `logs/no_lines/`
- regista erro controlado no Excel (para auditoria)

## Estrutura de ficheiros gerados

- Excel: `<base_dir>/<excel_path>`
- Resume: `<excel_path>.resume.json`
- Logs:
  - `<log_file>`
  - `<log_file.parent>/bad_responses/`
  - `<log_file.parent>/no_lines/`

## Testes recomendados (manuais)

1) Intervalo pequeno (1-2 dias) para validar schema e tipos
2) Validar um documento com:
   - muitos items
   - supplier com caracteres especiais (ex.: '&')
3) Forçar falha (Ctrl+C) a meio de um UID e validar retoma:
   - o UID deve ser reescrito integralmente na execução seguinte
4) Validar performance em intervalos longos:
   - ajustar `save_every_docs` e `save_every_seconds`

## Extensibilidade

### Novos campos / colunas
- Adicionar no `COLUMNS` e `COLUMNS_DTYPE`
- Atualizar o mapeamento em `append_line_rows` (ou função equivalente)
- Manter a ordem de colunas estável para não quebrar consumidores

### Novos tipos DocumentTypeCode
- Atualizar `DOC_TYPECODE_TO_LABEL` e inferências
- Se necessário, adicionar novos localnames para detetar nós de linhas e cabeçalhos
