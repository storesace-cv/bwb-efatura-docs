"""
Mini app: Descarrega facturas de fornecedores do eFatura CV.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Adicionar o diretório app ao path para importar o código existente
_app_dir = Path(__file__).parent.parent.parent / "app"
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

# Importar código existente
from update_supplier_invoices import (
    load_config,
    setup_logging,
    log,
    log_exception,
    EfaturaClient,
    ensure_workbook,
    load_resume_state,
    save_resume_state,
    compute_resume_uid,
    delete_uid_rows,
    extract_uid_from_item,
    extract_efatura_date_from_item,
    backfill_efatura_dates,
    safe_parse_xml,
    parse_invoice_lines,
    append_error_row,
    append_line_rows,
    load_token_json,
    decode_jwt_exp_unverified,
    resolve_or_fail,
    safe_save_workbook,
    dump_text,
    BAD_RESPONSE_DIR,
)

from core.base_app import BaseApp, AppResult
from core.context import AppContext
from core.exceptions import BWBConfigError, BWBExecutionError
import datetime as dt
import time


class EfaturaSupplierDocsDownloadApp(BaseApp):
    """Mini app: Descarrega facturas de fornecedores do eFatura CV."""
    
    @property
    def name(self) -> str:
        return "efatura-supplier-docs-download"
    
    @property
    def description(self) -> str:
        return "Exporta documentos de compras (DFE) do portal eFatura CV para Excel"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Valida configuração da mini app.
        
        Config esperada:
        {
            "config_file": "caminho/para/config.ini",  # obrigatório
            "max_docs": 0,  # opcional, 0 = sem limite
            "rewrite_existing": false,  # opcional
            "save_every_docs": -1,  # opcional, -1 = usar INI
            "save_every_seconds": -1,  # opcional, -1 = usar INI
            "verbose": false  # opcional
        }
        """
        if not isinstance(config, dict):
            return False, "Config deve ser um dicionário"
        
        if "config_file" not in config:
            return False, "Config deve conter 'config_file' com caminho para ficheiro INI"
        
        config_file = Path(config["config_file"])
        if not config_file.exists():
            return False, f"Ficheiro de configuração não encontrado: {config_file}"
        
        return True, None
    
    def run(self, config: Dict[str, Any], context: AppContext) -> AppResult:
        """
        Executa o download de facturas de fornecedores.
        """
        try:
            # 1. Carregar configuração INI
            config_file = Path(config["config_file"]).expanduser().resolve()
            verbose = config.get("verbose", False)
            
            try:
                cfg = load_config(config_file, verbose=verbose)
            except Exception as e:
                return AppResult(
                    success=False,
                    message=f"Erro ao carregar configuração: {e}"
                )
            
            # 2. Ajustar paths relativos ao contexto se necessário
            if not cfg.base_dir.is_absolute():
                cfg.base_dir = context.base_dir / cfg.base_dir
            if not cfg.excel_path.is_absolute():
                cfg.excel_path = context.base_dir / cfg.excel_path
            
            # 3. Setup logging
            if not cfg.log_file.is_absolute():
                cfg.log_file = context.get_or_create_logdir("efatura-supplier-docs") / cfg.log_file.name
            
            setup_logging(cfg.log_file)
            log(f"Log file: {cfg.log_file}")
            
            # 4. Configurar diretórios de dump
            global BAD_RESPONSE_DIR
            BAD_RESPONSE_DIR = context.get_or_create_logdir("bad_responses")
            
            # 5. Ajustar parâmetros de checkpoint se especificados
            if "save_every_docs" in config and config["save_every_docs"] != -1:
                cfg.save_every_docs = max(0, int(config["save_every_docs"]))
            if "save_every_seconds" in config and config["save_every_seconds"] != -1:
                cfg.save_every_seconds = max(0, int(config["save_every_seconds"]))
            
            log(f"Base dir: {cfg.base_dir}")
            log(f"Excel: {cfg.excel_path}")
            
            # 6. DNS preflight
            try:
                ips_services = resolve_or_fail("services.efatura.cv")
                log(f"DNS OK: services.efatura.cv -> {', '.join(ips_services)}")
            except Exception as e:
                return AppResult(
                    success=False,
                    message=f"Erro DNS services.efatura.cv: {e}"
                )
            
            try:
                ips_iam = resolve_or_fail("iam.efatura.cv")
                log(f"DNS OK: iam.efatura.cv -> {', '.join(ips_iam)}")
            except Exception as e:
                log(f"WARNING: {e} (userinfo/refresh may fail)")
            
            # 7. Carregar e validar token
            access_token = load_token_json(cfg.token_json)
            exp = decode_jwt_exp_unverified(access_token)
            if exp:
                exp_dt = dt.datetime.fromtimestamp(exp)
                remaining = exp_dt - dt.datetime.now()
                log(f"Access token: exp={exp_dt} (in {remaining})")
                if remaining.total_seconds() < 60:
                    return AppResult(
                        success=False,
                        message="Access token já expirado ou próximo da expiração. Atualizar token.json."
                    )
            
            # 8. Criar cliente eFatura
            client = EfaturaClient(
                access_token=access_token,
                repo_code=cfg.repo_code,
                timeout_sec=cfg.timeout_sec,
                retries=cfg.retries,
                backoff_sec=cfg.backoff_sec,
                verbose=verbose,
            )
            
            # 9. Validar token com userinfo
            try:
                taxid = client.userinfo_taxid()
                log(f"eFatura userinfo OK: {taxid}")
            except PermissionError:
                return AppResult(
                    success=False,
                    message="TOKEN_EXPIRED_OR_INVALID (userinfo). Atualizar token.json."
                )
            except Exception as e:
                log(f"WARNING: userinfo failed: {e} (continuing)")
            
            # 10. Preparar Excel
            wb, ws, uid_row_map = ensure_workbook(cfg.excel_path)
            existing_uids = set(uid_row_map.keys())
            log(f"Existing UIDs in Excel: {len(existing_uids)}")
            
            # 11. Verificar estado de retoma
            resume_state_path = cfg.excel_path.with_suffix(cfg.excel_path.suffix + ".resume.json")
            resume_state = load_resume_state(resume_state_path)
            resume_uid = compute_resume_uid(resume_state)
            if resume_uid:
                log(f"Resume detected: last started UID={resume_uid} was not marked completed. Will rewrite it.")
            else:
                log("Resume state: clean (no in-progress UID).")
            
            # 12. Listar DFEs
            log(f"Listing DFEs from {cfg.date_start} to {cfg.date_end} (repo={cfg.repo_code}, page_size={cfg.page_size})")
            try:
                records, discovered_date_keys = client.list_dfes(
                    cfg.date_start, 
                    cfg.date_end, 
                    cfg.page_size, 
                    show_fields=False
                )
            except PermissionError:
                return AppResult(
                    success=False,
                    message="TOKEN_EXPIRED_OR_INVALID (listing). Atualizar token.json."
                )
            
            if discovered_date_keys:
                log(f"Discovered possible 'Data eFatura' fields: {', '.join(discovered_date_keys)}")
            
            # 13. Processar UIDs
            uid_to_item: Dict[str, Dict[str, Any]] = {}
            uid_to_efdate: Dict[str, str] = {}
            for it in records:
                uid = extract_uid_from_item(it)
                if not uid:
                    continue
                uid_to_item[uid] = it
                efdate = extract_efatura_date_from_item(it)
                if efdate:
                    uid_to_efdate[uid] = efdate
            
            # Backfill Data eFatura para documentos existentes
            filled = backfill_efatura_dates(ws, uid_row_map, uid_to_efdate)
            if filled:
                log(f"Backfilled 'Data eFatura' for {filled} existing rows.")
            
            uids = sorted(uid_to_item.keys())
            log(f"Total UIDs discovered in date range: {len(uids)}")
            
            # 14. Processar cada documento
            added_docs = 0
            added_rows = 0
            errors = 0
            max_docs = config.get("max_docs", 0)
            rewrite_existing = config.get("rewrite_existing", False)
            
            last_save_ts = time.time()
            docs_since_save = 0
            
            def checkpoint_save(force: bool = False) -> None:
                nonlocal last_save_ts, docs_since_save
                if force:
                    safe_save_workbook(wb, cfg.excel_path)
                    last_save_ts = time.time()
                    docs_since_save = 0
                    log(f"Excel checkpoint saved: {cfg.excel_path}")
                    return
                
                if cfg.save_every_docs == 0 and cfg.save_every_seconds == 0:
                    return
                
                due_by_docs = cfg.save_every_docs > 0 and docs_since_save >= cfg.save_every_docs
                due_by_time = cfg.save_every_seconds > 0 and (time.time() - last_save_ts) >= cfg.save_every_seconds
                if due_by_docs or due_by_time:
                    safe_save_workbook(wb, cfg.excel_path)
                    last_save_ts = time.time()
                    docs_since_save = 0
                    log(f"Excel checkpoint saved: {cfg.excel_path}")
            
            for idx, uid in enumerate(uids, start=1):
                if max_docs and added_docs >= max_docs:
                    log(f"Reached max_docs={max_docs}, stopping.")
                    break
                
                uid_exists = uid in existing_uids
                should_rewrite = rewrite_existing or (resume_uid == uid)
                
                if uid_exists and not should_rewrite:
                    if idx % max(1, cfg.progress_every) == 0:
                        log(f"[{idx}/{len(uids)}] UID={uid} already in Excel -> skip")
                    continue
                
                if uid_exists and should_rewrite:
                    deleted = delete_uid_rows(ws, uid)
                    if deleted:
                        log(f"UID={uid} already existed: deleted {deleted} row(s) to rewrite.")
                
                # Mark started
                resume_state["started_uid"] = uid
                save_resume_state(resume_state_path, resume_state)
                
                log(f"[{idx}/{len(uids)}] UID={uid} fetching document XML...")
                efdate = uid_to_efdate.get(uid, "")
                
                try:
                    inner_xml = client.fetch_dfe_inner_xml(uid)
                    dfe_root = safe_parse_xml(
                        inner_xml, 
                        uid=uid, 
                        stage="inner", 
                        dump_dir=BAD_RESPONSE_DIR
                    )
                    meta, lines = parse_invoice_lines(dfe_root)
                    
                    # Tentar seguir referências se não houver linhas
                    if not lines:
                        ref_uids = meta.get("ref_uids") or ([meta["ref_uid"]] if meta.get("ref_uid") else [])
                        ref_uids = [r for r in ref_uids if r and r != uid]
                        
                        for ref_uid in ref_uids:
                            log(f"UID={uid} has no lines; trying referenced FiscalDocument {ref_uid}...")
                            try:
                                inner2 = client.fetch_dfe_inner_xml(ref_uid)
                                root2 = safe_parse_xml(
                                    inner2, 
                                    uid=ref_uid, 
                                    stage="inner_ref", 
                                    dump_dir=BAD_RESPONSE_DIR
                                )
                                meta2, lines2 = parse_invoice_lines(root2)
                            except Exception as e:
                                log(f"WARNING: referenced fetch/parse failed ref_uid={ref_uid}: {e}")
                                continue
                            
                            if lines2:
                                meta = dict(meta)
                                for k in ("supplier_name", "supplier_taxid", "supplier_address"):
                                    if not meta.get(k):
                                        meta[k] = meta2.get(k, "")
                                lines = lines2
                                break
                    
                    if not lines:
                        # Dump para análise
                        try:
                            nl_dir = context.get_or_create_logdir("no_lines")
                            dump_text(nl_dir / f"{uid}.inner.xml", inner_xml)
                        except Exception as _e:
                            log(f"WARNING: failed to dump no-lines XML: {_e}")
                        
                        doc_kind = meta.get("doc_kind") or ""
                        doc_num = meta.get("document_number") or ""
                        refs = meta.get("ref_uids") or ([meta["ref_uid"]] if meta.get("ref_uid") else [])
                        refs_s = ",".join(refs) if refs else ""
                        
                        append_error_row(
                            ws,
                            uid,
                            f"No Lines found (doc_kind={doc_kind}, doc_number={doc_num}, refs={refs_s})",
                        )
                        errors += 1
                        existing_uids.add(uid)
                        uid_row_map.setdefault(uid, []).append(ws.max_row)
                        log(f"WARNING: UID={uid} has no lines; recorded as error.")
                        
                        resume_state["completed_uid"] = uid
                        save_resume_state(resume_state_path, resume_state)
                        docs_since_save += 1
                        checkpoint_save()
                        continue
                    
                    # Adicionar linhas ao Excel
                    before = ws.max_row
                    rows_added = append_line_rows(ws, uid, efdate, meta, lines)
                    after = ws.max_row
                    added_rows += rows_added
                    added_docs += 1
                    existing_uids.add(uid)
                    uid_row_map[uid] = list(range(before + 1, after + 1))
                    
                    resume_state["completed_uid"] = uid
                    save_resume_state(resume_state_path, resume_state)
                    if resume_uid == uid:
                        resume_uid = None
                    
                    log(f"OK UID={uid} lines={len(lines)} supplier={meta.get('supplier_name','')}")
                    docs_since_save += 1
                    checkpoint_save()
                    
                except PermissionError:
                    log("ERROR: TOKEN_EXPIRED_OR_INVALID while fetching documents. Stop now.")
                    break
                except Exception as e:
                    append_error_row(ws, uid, str(e)[:500])
                    errors += 1
                    existing_uids.add(uid)
                    uid_row_map.setdefault(uid, []).append(ws.max_row)
                    log_exception(f"WARNING: Failed UID={uid}: {e}")
                    
                    resume_state["completed_uid"] = uid
                    save_resume_state(resume_state_path, resume_state)
                    if resume_uid == uid:
                        resume_uid = None
                    docs_since_save += 1
                    checkpoint_save()
                
                if (idx % max(1, cfg.progress_every)) == 0:
                    log(f"Progress: processed={idx}/{len(uids)} added_docs={added_docs} added_rows={added_rows} errors={errors}")
            
            # Guardar final
            checkpoint_save(force=True)
            
            result_message = (
                f"Processados {added_docs} documentos, {added_rows} linhas, {errors} erros. "
                f"Excel guardado: {cfg.excel_path}"
            )
            log(f"DONE. {result_message}")
            
            return AppResult(
                success=True,
                message=result_message,
                data={
                    "docs_added": added_docs,
                    "rows_added": added_rows,
                    "errors": errors,
                    "total_uids": len(uids)
                },
                output_files=[cfg.excel_path]
            )
            
        except Exception as e:
            log_exception(f"Erro inesperado na execução: {e}")
            return AppResult(
                success=False,
                message=f"Erro inesperado: {str(e)}"
            )
