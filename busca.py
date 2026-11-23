from unicodedata import normalize


def normalizar(texto):
    return ''.join(
        caractere for caractere in normalize('NFD', texto.casefold())
        if not ('\u0300' <= caractere <= '\u036f')
    )


def buscar_pacientes(pacientes, termo):
    """Busca linear por trecho do nome, ignorando caixa e acentos."""
    if not termo.strip():
        return pacientes

    termo = normalizar(termo.strip())
    encontrados = []
    for paciente in pacientes:
        if termo in normalizar(paciente['nome']):
            encontrados.append(paciente)
    return encontrados
