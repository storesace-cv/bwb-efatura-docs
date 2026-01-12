#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BWB App - Entry point principal.
Orquestrador de mini apps para gestão de dados fiscais.
"""

import argparse
import json
import sys
from pathlib import Path
from orchestrator.runner import AppOrchestrator
from core.logging_setup import setup_logging
import logging

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="BWB App - Orquestrador de Mini Apps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Listar apps disponíveis
  python main.py --list-apps
  
  # Executar uma app específica
  python main.py --app efatura-supplier-docs-download --config config.json
  
  # Executar workflow
  python main.py --workflow workflow.json --config config.json
        """
    )
    
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Diretório base do projeto (default: diretório atual)"
    )
    
    parser.add_argument(
        "--list-apps",
        action="store_true",
        help="Lista todas as mini apps disponíveis e sai"
    )
    
    parser.add_argument(
        "--app",
        help="Nome da mini app a executar"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Ficheiro de configuração JSON"
    )
    
    parser.add_argument(
        "--workflow",
        type=Path,
        help="Ficheiro de workflow JSON"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Logging verboso"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, logger_name="bwb")
    
    # Inicializar orquestrador
    base_dir = args.base_dir.resolve()
    logger.info(f"BWB App iniciado. Base dir: {base_dir}")
    
    try:
        orchestrator = AppOrchestrator(base_dir)
    except Exception as e:
        logger.error(f"Erro ao inicializar orquestrador: {e}", exc_info=True)
        return 1
    
    # Listar apps se solicitado
    if args.list_apps:
        apps = orchestrator.list_apps()
        print("\nMini Apps disponíveis:")
        print("=" * 60)
        for name, info in apps.items():
            print(f"\n{name} v{info['version']}")
            print(f"  Descrição: {info['description']}")
            if info['dependencies']:
                print(f"  Dependências: {', '.join(info['dependencies'])}")
        print("\n" + "=" * 60)
        return 0
    
    # Carregar configuração se especificada
    config_data = {}
    if args.config:
        if not args.config.exists():
            logger.error(f"Ficheiro de configuração não encontrado: {args.config}")
            return 1
        try:
            config_data = json.loads(args.config.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return 1
    
    # Executar workflow
    if args.workflow:
        if not args.workflow.exists():
            logger.error(f"Ficheiro de workflow não encontrado: {args.workflow}")
            return 1
        try:
            workflow_config = json.loads(args.workflow.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Erro ao carregar workflow: {e}")
            return 1
        
        logger.info(f"Executando workflow: {workflow_config.get('name', 'unnamed')}")
        results = orchestrator.run_workflow(workflow_config)
        
        # Resumo
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        print(f"\n{'='*60}")
        print(f"Workflow concluído: {success_count}/{total_count} apps bem-sucedidas")
        print(f"{'='*60}")
        
        for idx, result in enumerate(results, start=1):
            status = "✓" if result.success else "✗"
            print(f"{status} [{idx}] {result.message}")
        
        return 0 if success_count == total_count else 1
    
    # Executar app específica
    if args.app:
        app_config = config_data.get(args.app, {})
        result = orchestrator.run_app(args.app, app_config)
        
        status = "✓" if result.success else "✗"
        print(f"\n{status} {result.message}")
        
        if result.output_files:
            print("\nFicheiros gerados:")
            for f in result.output_files:
                print(f"  - {f}")
        
        return 0 if result.success else 1
    
    # Nenhuma ação especificada
    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Interrompido pelo utilizador.")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Erro fatal: {e}")
        sys.exit(1)
