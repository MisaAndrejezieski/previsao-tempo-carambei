class ClimaException(Exception):
    """Exceção base para o módulo clima"""
    pass

class ApiTimeoutError(ClimaException):
    """Erro de timeout na API"""
    pass

class ApiConnectionError(ClimaException):
    """Erro de conexão com a API"""
    pass

class CidadeNaoEncontradaError(ClimaException):
    """Cidade não encontrada"""
    pass

class DadosInvalidosError(ClimaException):
    """Dados inválidos retornados da API"""
    pass