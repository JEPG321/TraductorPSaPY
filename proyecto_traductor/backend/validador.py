"""Validacion lexica, sintactica y estructural para PseudoPy."""

from __future__ import annotations

import re
from typing import Any

from tokens import TOKEN_REGEX_SPECS

IDENTIFICADOR = r"[a-zA-Z][a-zA-Z0-9]*"
NUMERO = r"[0-9]+"
CADENA = r'"[^"\n]*"'
VALOR = rf"(?:{IDENTIFICADOR}|{NUMERO})"
ITEM_ESCRIBIR = rf"(?:{CADENA}|{IDENTIFICADOR})"
OPERADOR_REL = r"(?:==|!=|<=|>=|<|>)"
EXPRESION_ARITMETICA = rf"{VALOR}(?:\s*[\+\-\*/]\s*{VALOR})*"
EXPRESION_RELACIONAL = rf"{VALOR}\s*{OPERADOR_REL}\s*{VALOR}"

PATRONES = {
    "RESERVADAS": re.compile(
        r"\b(INICIO|SI|SINO|ENTONCES|FIN|SEGUN|CASO|MIENTRAS|HACER|PARA|LEER|ESCRIBIR)\b"
    ),
    "IDENTIFICADOR": re.compile(r"[a-zA-Z][a-zA-Z0-9]*"),
    "NUMERO": re.compile(r"[0-9]+"),
    "CADENA": re.compile(r'"[^"\n]*"'),
    "INICIO": re.compile(r"^\bINICIO\b$"),
    "ASIGNACION": re.compile(
        rf"^(?P<destino>{IDENTIFICADOR})\s*=\s*(?P<expresion>{EXPRESION_ARITMETICA})$"
    ),
    "LEER": re.compile(rf"^\bLEER\b\s+(?P<variable>{IDENTIFICADOR})$"),
    "ESCRIBIR": re.compile(
        rf"^\bESCRIBIR\b\s+(?P<expresion>{ITEM_ESCRIBIR}(?:\s*,\s*{ITEM_ESCRIBIR})*)$"
    ),
    "SI": re.compile(rf"^\bSI\b\s+(?P<condicion>{EXPRESION_RELACIONAL})\s+\bENTONCES\b$"),
    "SINO": re.compile(r"^\bSINO\b$"),
    "SEGUN": re.compile(rf"^\bSEGUN\b\s+(?P<expresion>{VALOR})$"),
    "CASO": re.compile(rf"^\bCASO\b\s+(?P<valor>{NUMERO})$"),
    "MIENTRAS": re.compile(
        rf"^\bMIENTRAS\b\s+(?P<condicion>{EXPRESION_RELACIONAL})(?:\s+\bHACER\b)?$"
    ),
    "PARA": re.compile(
        rf"^\bPARA\b\s+"
        rf"(?P<var_inicial>{IDENTIFICADOR})\s*=\s*(?P<inicio>{NUMERO})\s*;\s*"
        rf"(?P<izquierda>{VALOR})\s*(?P<operador>{OPERADOR_REL})\s*(?P<derecha>{VALOR})\s*;\s*"
        rf"(?P<var_actualizada>{IDENTIFICADOR})\s*=\s*(?P<var_fuente>{IDENTIFICADOR})\s*"
        rf"(?P<signo>[\+\-])\s*(?P<paso>{NUMERO})$"
    ),
    "FIN": re.compile(r"^\bFIN\b$"),
}

ORDEN_INSTRUCCIONES = (
    "SI",
    "INICIO",
    "SINO",
    "SEGUN",
    "CASO",
    "MIENTRAS",
    "PARA",
    "LEER",
    "ESCRIBIR",
    "ASIGNACION",
    "FIN",
)

TOKEN_REGEX = [(tipo, re.compile(patron)) for tipo, patron in TOKEN_REGEX_SPECS]


def clasificar_linea(linea: str) -> dict[str, Any] | None:
    """Devuelve la instruccion reconocida y su match o None si no coincide."""
    for tipo in ORDEN_INSTRUCCIONES:
        coincidencia = PATRONES[tipo].fullmatch(linea)
        if coincidencia:
            return {"tipo": tipo, "match": coincidencia}
    return None


def tokenizar_linea(linea: str, numero_linea: int) -> list[dict[str, Any]]:
    """Tokeniza una linea valida respetando el orden de los operadores."""
    posicion = 0
    tokens: list[dict[str, Any]] = []

    while posicion < len(linea):
        if linea[posicion].isspace():
            posicion += 1
            continue

        coincidencia = None
        for tipo, patron in TOKEN_REGEX:
            coincidencia = patron.match(linea, posicion)
            if coincidencia:
                tokens.append(
                    {
                        "linea": numero_linea,
                        "tipo": tipo,
                        "lexema": coincidencia.group(0),
                    }
                )
                posicion = coincidencia.end()
                break

        if not coincidencia:
            fragmento = linea[posicion:]
            raise ValueError(f"token no reconocido cerca de '{fragmento}'")

    return tokens


def validar_estructura(lineas_validas: list[dict[str, Any]]) -> list[str]:
    """Valida bloques usando una pila para SI, MIENTRAS, SEGUN y PARA."""
    errores: list[str] = []
    pila: list[dict[str, Any]] = []

    if not lineas_validas:
        return ["El programa esta vacio. Debe comenzar con INICIO y terminar con FIN."]

    primera = lineas_validas[0]
    ultima = lineas_validas[-1]

    if primera["tipo"] != "INICIO":
        errores.append(
            f"Linea {primera['numero']}: el programa debe comenzar con INICIO"
        )

    if ultima["tipo"] != "FIN":
        errores.append(
            f"Linea {ultima['numero']}: el programa debe terminar con FIN"
        )

    for info in lineas_validas:
        tipo = info["tipo"]
        numero = info["numero"]

        if tipo == "INICIO":
            if numero != primera["numero"]:
                errores.append(f"Linea {numero}: INICIO solo puede aparecer al comienzo del programa")
            else:
                pila.append({"tipo": "PROGRAMA", "linea": numero})
            continue

        if tipo == "SI":
            pila.append({"tipo": "SI", "linea": numero, "tiene_sino": False})
            continue

        if tipo == "SINO":
            if not pila or pila[-1]["tipo"] != "SI":
                errores.append(f"Linea {numero}: SINO sin un SI abierto y listo para continuar")
                continue

            if pila[-1]["tiene_sino"]:
                errores.append(f"Linea {numero}: el bloque SI ya tiene un SINO")
                continue

            pila[-1]["tiene_sino"] = True
            continue

        if tipo == "SEGUN":
            pila.append({"tipo": "SEGUN", "linea": numero, "casos": 0})
            continue

        if tipo == "CASO":
            if not pila or pila[-1]["tipo"] != "SEGUN":
                errores.append(f"Linea {numero}: CASO fuera de un bloque SEGUN")
                continue

            pila[-1]["casos"] += 1
            continue

        if tipo in {"MIENTRAS", "PARA"}:
            pila.append({"tipo": tipo, "linea": numero})
            continue

        if tipo == "FIN":
            if not pila:
                errores.append(f"Linea {numero}: FIN sin bloque abierto")
                continue

            bloque = pila.pop()
            if bloque["tipo"] == "SEGUN" and bloque["casos"] == 0:
                errores.append(
                    f"Linea {numero}: el bloque SEGUN abierto en la linea {bloque['linea']} no contiene CASO"
                )

    for bloque in reversed(pila):
        if bloque["tipo"] == "PROGRAMA":
            errores.append(
                f"Bloque PROGRAMA abierto en la linea {bloque['linea']} sin FIN correspondiente"
            )
            continue
        errores.append(
            f"Bloque {bloque['tipo']} abierto en la linea {bloque['linea']} sin FIN correspondiente"
        )

    return errores


def analizar_codigo(codigo: str) -> dict[str, Any]:
    """Realiza la validacion completa y devuelve errores y tokens."""
    errores: list[str] = []
    tokens: list[dict[str, Any]] = []
    lineas_validas: list[dict[str, Any]] = []

    for numero, linea_original in enumerate(codigo.splitlines(), start=1):
        linea = linea_original.strip()
        if not linea:
            continue

        info = clasificar_linea(linea)
        if not info:
            errores.append(f"Linea {numero}: instruccion no valida -> '{linea}'")
            continue

        if info["tipo"] == "INICIO" and lineas_validas:
            errores.append(f"Linea {numero}: INICIO solo puede declararse una vez y al principio")
            continue

        try:
            tokens.extend(tokenizar_linea(linea, numero))
        except ValueError as exc:
            errores.append(f"Linea {numero}: {exc}")
            continue

        lineas_validas.append(
            {
                "numero": numero,
                "texto": linea,
                "tipo": info["tipo"],
                "match": info["match"],
            }
        )

    errores.extend(validar_estructura(lineas_validas))

    return {
        "ok": not errores,
        "errores": errores,
        "tokens": tokens if not errores else [],
        "lineas_validas": lineas_validas,
    }
