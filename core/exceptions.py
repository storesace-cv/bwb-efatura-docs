"""
Exceções personalizadas do framework BWB.
"""


class BWBAppError(Exception):
    """Exceção base para erros de mini apps."""
    pass


class BWBConfigError(BWBAppError):
    """Erro de configuração."""
    pass


class BWBValidationError(BWBAppError):
    """Erro de validação."""
    pass


class BWBExecutionError(BWBAppError):
    """Erro durante execução de uma mini app."""
    pass
