"""Traduccion de PseudoPy a Python."""

from __future__ import annotations

from typing import Any

from validador import clasificar_linea


def _indentacion(nivel: int) -> str:
    return "    " * max(nivel, 0)


def _traducir_booleanos(fragmento: str) -> str:
    """Convierte VERDADERO/FALSO a True/False sin tocar el texto entre comillas."""
    resultado: list[str] = []
    dentro_de_cadena = False
    i = 0

    while i < len(fragmento):
        caracter = fragmento[i]
        if caracter == '"':
            dentro_de_cadena = not dentro_de_cadena
            resultado.append(caracter)
            i += 1
            continue

        if not dentro_de_cadena and fragmento.startswith("VERDADERO", i):
            fin = i + len("VERDADERO")
            antes = i == 0 or not fragmento[i - 1].isalnum()
            despues = fin >= len(fragmento) or not fragmento[fin].isalnum()
            if antes and despues:
                resultado.append("True")
                i = fin
                continue

        if not dentro_de_cadena and fragmento.startswith("FALSO", i):
            fin = i + len("FALSO")
            antes = i == 0 or not fragmento[i - 1].isalnum()
            despues = fin >= len(fragmento) or not fragmento[fin].isalnum()
            if antes and despues:
                resultado.append("False")
                i = fin
                continue

        resultado.append(caracter)
        i += 1

    return "".join(resultado)


def _construir_range(componentes: dict[str, str]) -> str | None:
    """Trata de convertir un PARA clasico a range(...)."""
    variable = componentes["var_inicial"]
    izquierda = componentes["izquierda"]
    operador = componentes["operador"]
    derecha = componentes["derecha"]
    var_actualizada = componentes["var_actualizada"]
    var_fuente = componentes["var_fuente"]
    signo = componentes["signo"]
    paso = int(componentes["paso"])
    inicio = componentes["inicio"]

    variables_compatibles = (
        izquierda == variable
        and var_actualizada == variable
        and var_fuente == variable
    )
    if not variables_compatibles:
        return None

    if signo == "+" and operador in {"<", "<="}:
        if operador == "<":
            return f"range({inicio}, {derecha}, {paso})"
        return f"range({inicio}, ({derecha}) + 1, {paso})"

    if signo == "-" and operador in {">", ">="}:
        paso_negativo = -paso
        if operador == ">":
            return f"range({inicio}, {derecha}, {paso_negativo})"
        return f"range({inicio}, ({derecha}) - 1, {paso_negativo})"

    return None


def traducir_codigo(codigo: str) -> str:
    """Convierte el pseudocodigo valido a Python con indentacion."""
    lineas_python: list[str] = []
    nivel_indentacion = 0
    pila_bloques: list[dict[str, Any]] = []

    for linea_original in codigo.splitlines():
        linea = linea_original.strip()
        if not linea:
            continue

        info = clasificar_linea(linea)
        if not info:
            continue

        tipo = info["tipo"]
        match = info["match"]

        if tipo == "ASIGNACION":
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}{match.group('destino')} = {_traducir_booleanos(match.group('expresion'))}"
            )
            continue

        if tipo == "INICIO":
            continue

        if tipo == "LEER":
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}{match.group('variable')} = float(input())"
            )
            continue

        if tipo == "ESCRIBIR":
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}print({_traducir_booleanos(match.group('expresion'))})"
            )
            continue

        if tipo == "SI":
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}if {_traducir_booleanos(match.group('condicion'))}:"
            )
            pila_bloques.append({"tipo": "SI"})
            nivel_indentacion += 1
            continue

        if tipo == "SINO":
            nivel_indentacion = max(nivel_indentacion - 1, 0)
            lineas_python.append(f"{_indentacion(nivel_indentacion)}else:")
            nivel_indentacion += 1
            continue

        if tipo == "MIENTRAS":
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}while {_traducir_booleanos(match.group('condicion'))}:"
            )
            pila_bloques.append({"tipo": "MIENTRAS"})
            nivel_indentacion += 1
            continue

        if tipo == "SEGUN":
            pila_bloques.append(
                {
                    "tipo": "SEGUN",
                    "expresion": _traducir_booleanos(match.group("expresion")),
                    "casos": 0,
                    "caso_abierto": False,
                }
            )
            continue

        if tipo == "CASO":
            bloque = pila_bloques[-1]
            if bloque["caso_abierto"]:
                nivel_indentacion = max(nivel_indentacion - 1, 0)

            prefijo = "if" if bloque["casos"] == 0 else "elif"
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}{prefijo} {bloque['expresion']} == {match.group('valor')}:"
            )
            bloque["casos"] += 1
            bloque["caso_abierto"] = True
            nivel_indentacion += 1
            continue

        if tipo == "PARA":
            componentes = match.groupdict()
            rango = _construir_range(componentes)
            variable = componentes["var_inicial"]
            inicio = componentes["inicio"]

            if rango:
                lineas_python.append(f"{_indentacion(nivel_indentacion)}for {variable} in {rango}:")
                pila_bloques.append({"tipo": "PARA", "modo": "for"})
                nivel_indentacion += 1
                continue

            condicion = (
                f"{componentes['izquierda']} {componentes['operador']} {componentes['derecha']}"
            )
            actualizacion = (
                f"{componentes['var_actualizada']} = {componentes['var_fuente']} "
                f"{componentes['signo']} {componentes['paso']}"
            )
            lineas_python.append(f"{_indentacion(nivel_indentacion)}{variable} = {inicio}")
            lineas_python.append(
                f"{_indentacion(nivel_indentacion)}while {_traducir_booleanos(condicion)}:"
            )
            pila_bloques.append(
                {"tipo": "PARA", "modo": "while", "actualizacion": actualizacion}
            )
            nivel_indentacion += 1
            continue

        if tipo == "FIN":
            if not pila_bloques:
                nivel_indentacion = 0
                continue

            bloque = pila_bloques.pop()
            if bloque["tipo"] == "SEGUN":
                if bloque["caso_abierto"]:
                    nivel_indentacion = max(nivel_indentacion - 1, 0)
                continue

            if bloque["tipo"] == "PARA" and bloque.get("modo") == "while":
                lineas_python.append(
                    f"{_indentacion(nivel_indentacion)}{bloque['actualizacion']}"
                )

            nivel_indentacion = max(nivel_indentacion - 1, 0)

    return "\n".join(lineas_python)
