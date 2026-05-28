"""Validacion lexica, sintactica y estructural para PseudoPy."""

from __future__ import annotations

import re
from typing import Any

from tokens import TOKEN_REGEX_SPECS

# ============================================================
# DEFINICION DE ELEMENTOS BASICOS DEL LENGUAJE
# ============================================================
# Estas expresiones regulares describen las partes pequenas del
# lenguaje: identificadores, numeros, cadenas, booleanos, operadores
# y expresiones permitidas.

IDENTIFICADOR = r"[a-zA-Z][a-zA-Z0-9]*"
NUMERO_ENTERO = r"[0-9]+"
NUMERO = r"(?:[0-9]+(?:\.[0-9]+)?)"
CADENA = r'"[^"\n]*"'
BOOLEANO = r"(?:VERDADERO|FALSO)"
VALOR_ARITMETICO = rf"(?:{IDENTIFICADOR}|{NUMERO})"
VALOR_GENERAL = rf"(?:{IDENTIFICADOR}|{NUMERO}|{CADENA}|{BOOLEANO})"
OPERADOR_REL = r"(?:==|!=|<=|>=|<|>)"
EXPRESION_ARITMETICA = rf"{VALOR_ARITMETICO}(?:\s*[\+\-\*/]\s*{VALOR_ARITMETICO})*"
ITEM_ESCRIBIR = rf"(?:{CADENA}|{BOOLEANO}|{EXPRESION_ARITMETICA})"
EXPRESION_RELACIONAL = rf"{VALOR_GENERAL}\s*{OPERADOR_REL}\s*{VALOR_GENERAL}"
EXPRESION_ASIGNACION = rf"(?:{EXPRESION_ARITMETICA}|{CADENA}|{BOOLEANO})"

# ============================================================
# PATRONES DE INSTRUCCIONES
# ============================================================
# Cada patron valida la forma correcta de una instruccion completa
# de PseudoPy, por ejemplo INICIO, ASIGNACION, SI, MIENTRAS o PARA.

PATRONES = {
    "RESERVADAS": re.compile(
        r"\b(INICIO|SI|SINO|ENTONCES|FIN|SEGUN|CASO|MIENTRAS|HACER|PARA|LEER|ESCRIBIR)\b"
    ),
    "IDENTIFICADOR": re.compile(r"[a-zA-Z][a-zA-Z0-9]*"),
    "NUMERO": re.compile(r"(?:[0-9]+(?:\.[0-9]+)?)"),
    "CADENA": re.compile(r'"[^"\n]*"'),
    "INICIO": re.compile(r"^\bINICIO\b$"),
    "ASIGNACION": re.compile(
        rf"^(?P<destino>{IDENTIFICADOR})\s*=\s*(?P<expresion>{EXPRESION_ASIGNACION})$"
    ),
    "LEER": re.compile(rf"^\bLEER\b\s+(?P<variable>{IDENTIFICADOR})$"),
    "ESCRIBIR": re.compile(
        rf"^\bESCRIBIR\b\s+(?P<expresion>{ITEM_ESCRIBIR}(?:\s*,\s*{ITEM_ESCRIBIR})*)$"
    ),
    "SI": re.compile(rf"^\bSI\b\s+(?P<condicion>{EXPRESION_RELACIONAL})\s+\bENTONCES\b$"),
    "SINO": re.compile(r"^\bSINO\b$"),
    "SEGUN": re.compile(rf"^\bSEGUN\b\s+(?P<expresion>{VALOR_GENERAL})$"),
    "CASO": re.compile(rf"^\bCASO\b\s+(?P<valor>{NUMERO_ENTERO})$"),
    "MIENTRAS": re.compile(
        rf"^\bMIENTRAS\b\s+(?P<condicion>{EXPRESION_RELACIONAL})(?:\s+\bHACER\b)?$"
    ),
    "PARA": re.compile(
        rf"^\bPARA\b\s+"
        rf"(?P<var_inicial>{IDENTIFICADOR})\s*=\s*(?P<inicio>{NUMERO_ENTERO})\s*;\s*"
        rf"(?P<izquierda>{VALOR_ARITMETICO})\s*(?P<operador>{OPERADOR_REL})\s*(?P<derecha>{VALOR_ARITMETICO})\s*;\s*"
        rf"(?P<var_actualizada>{IDENTIFICADOR})\s*=\s*(?P<var_fuente>{IDENTIFICADOR})\s*"
        rf"(?P<signo>[\+\-])\s*(?P<paso>{NUMERO_ENTERO})$"
    ),
    "FIN": re.compile(r"^\bFIN\b$"),
}

# ============================================================
# ORDEN DE CLASIFICACION DE INSTRUCCIONES
# ============================================================
# Define en que orden se intenta reconocer una linea. Esto evita
# confusiones entre palabras reservadas, identificadores y asignaciones.

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

# ============================================================
# PATRONES PARA TOKENIZACION
# ============================================================
# Convierte las especificaciones de tokens en expresiones regulares
# compiladas para analizar cada linea caracter por caracter.

TOKEN_REGEX = [(tipo, re.compile(patron)) for tipo, patron in TOKEN_REGEX_SPECS]


# ============================================================
# CLASIFICACION DE LINEAS
# ============================================================
# Identifica que tipo de instruccion representa una linea completa.

def clasificar_linea(linea: str) -> dict[str, Any] | None:
    """Devuelve la instruccion reconocida y su match o None si no coincide."""
    for tipo in ORDEN_INSTRUCCIONES:
        coincidencia = PATRONES[tipo].fullmatch(linea)
        if coincidencia:
            return {"tipo": tipo, "match": coincidencia}
    return None


# ============================================================
# TOKENIZACION
# ============================================================
# Separa una linea valida en tokens individuales, indicando el tipo,
# el lexema encontrado y el numero de linea al que pertenece.

def tokenizar_linea(linea: str, numero_linea: int) -> list[dict[str, Any]]:
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


# ============================================================
# VALIDACION ESTRUCTURAL
# ============================================================
# Revisa que el programa empiece con INICIO, termine con FIN y que
# los bloques SI, MIENTRAS, SEGUN y PARA esten bien cerrados.

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


# ============================================================
# UTILIDADES PARA CONSTRUIR EL ARBOL DE DERIVACION
# ============================================================
# Estas funciones crean nodos y separan expresiones para representar
# el programa como una estructura jerarquica.

def _crear_nodo(etiqueta: str, hijos: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"etiqueta": etiqueta, "hijos": hijos or []}


def _partir_lista(texto: str, separador: str) -> list[str]:
    partes: list[str] = []
    actual: list[str] = []
    dentro_de_cadena = False

    for caracter in texto:
        if caracter == '"':
            dentro_de_cadena = not dentro_de_cadena
            actual.append(caracter)
            continue

        if caracter == separador and not dentro_de_cadena:
            partes.append("".join(actual).strip())
            actual = []
            continue

        actual.append(caracter)

    partes.append("".join(actual).strip())
    return partes


def _tokenizar_expresion_aritmetica(expresion: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9]*|\d+(?:\.\d+)?|[+\-*/]", expresion)


def _descomponer_condicion(condicion: str) -> tuple[str, str, str]:
    coincidencia = re.fullmatch(
        rf"\s*(?P<izquierda>{VALOR_GENERAL})\s*(?P<operador>{OPERADOR_REL})\s*(?P<derecha>{VALOR_GENERAL})\s*",
        condicion,
    )
    if not coincidencia:
        return condicion, "", ""

    return (
        coincidencia.group("izquierda"),
        coincidencia.group("operador"),
        coincidencia.group("derecha"),
    )


def _descomponer_condicion_para(condicion: str) -> tuple[str, str, str]:
    coincidencia = re.fullmatch(
        rf"\s*(?P<izquierda>{VALOR_ARITMETICO})\s*(?P<operador>{OPERADOR_REL})\s*(?P<derecha>{VALOR_ARITMETICO})\s*",
        condicion,
    )
    if not coincidencia:
        return condicion, "", ""

    return (
        coincidencia.group("izquierda"),
        coincidencia.group("operador"),
        coincidencia.group("derecha"),
    )


# ============================================================
# CONSTRUCCION DEL ARBOL DE DERIVACION
# ============================================================
# A partir de lineas ya validadas, genera un arbol que muestra como
# se deriva cada instruccion segun la gramatica del lenguaje.

def construir_arbol_derivacion(lineas_validas: list[dict[str, Any]]) -> dict[str, Any]:
    """Construye un arbol estructurado a partir de lineas ya validadas."""
    if not lineas_validas:
        return {}

    indice = 0

    def hoja(etiqueta: str) -> dict[str, Any]:
        return _crear_nodo(etiqueta)

    def expandir_letra(valor: str) -> dict[str, Any]:
        return _crear_nodo("<letra>", [hoja(valor)])

    def expandir_digito(valor: str) -> dict[str, Any]:
        return _crear_nodo("<digito>", [hoja(valor)])

    def expandir_letra_o_digito(valor: str) -> dict[str, Any]:
        if valor.isdigit():
            return _crear_nodo("<letra_o_digito>", [expandir_digito(valor)])
        return _crear_nodo("<letra_o_digito>", [expandir_letra(valor)])

    def expandir_resto_identificador(resto: str) -> dict[str, Any]:
        if not resto:
            return _crear_nodo("<resto_identificador>", [hoja("ε")])

        return _crear_nodo(
            "<resto_identificador>",
            [
                expandir_letra_o_digito(resto[0]),
                expandir_resto_identificador(resto[1:]),
            ],
        )

    def expandir_identificador(valor: str) -> dict[str, Any]:
        hijos = [expandir_letra(valor[0])]
        if len(valor) == 1:
            return _crear_nodo("<identificador>", hijos)

        hijos.append(expandir_resto_identificador(valor[1:]))
        return _crear_nodo("<identificador>", hijos)

    def expandir_numero_entero(valor: str) -> dict[str, Any]:
        if len(valor) == 1:
            return _crear_nodo("<numero_entero>", [expandir_digito(valor)])

        return _crear_nodo(
            "<numero_entero>",
            [
                expandir_digito(valor[0]),
                expandir_numero_entero(valor[1:]),
            ],
        )

    def expandir_numero_decimal(valor: str) -> dict[str, Any]:
        izquierda, derecha = valor.split(".", maxsplit=1)
        return _crear_nodo(
            "<numero_decimal>",
            [
                expandir_numero_entero(izquierda),
                hoja("."),
                expandir_numero_entero(derecha),
            ],
        )

    def expandir_numero(valor: str) -> dict[str, Any]:
        if "." in valor:
            return _crear_nodo("<numero>", [expandir_numero_decimal(valor)])
        return _crear_nodo("<numero>", [expandir_numero_entero(valor)])

    def expandir_booleano(valor: str) -> dict[str, Any]:
        return _crear_nodo("<booleano>", [hoja(valor)])

    def expandir_caracter(valor: str) -> dict[str, Any]:
        if valor.isalpha():
            return _crear_nodo("<caracter>", [expandir_letra(valor)])
        if valor.isdigit():
            return _crear_nodo("<caracter>", [expandir_digito(valor)])
        return _crear_nodo("<caracter>", [hoja(valor)])

    def expandir_contenido_cadena(contenido: str) -> dict[str, Any]:
        if not contenido:
            return _crear_nodo("<contenido_cadena>", [hoja("ε")])

        return _crear_nodo(
            "<contenido_cadena>",
            [
                expandir_caracter(contenido[0]),
                expandir_contenido_cadena(contenido[1:]),
            ],
        )

    def expandir_cadena(valor: str) -> dict[str, Any]:
        contenido = valor[1:-1]
        return _crear_nodo(
            "<cadena>",
            [
                hoja('"'),
                expandir_contenido_cadena(contenido),
                hoja('"'),
            ],
        )

    def expandir_operador_aritmetico(valor: str) -> dict[str, Any]:
        return _crear_nodo("<operador_aritmetico>", [hoja(valor)])

    def expandir_operador_suma_resta(valor: str) -> dict[str, Any]:
        return _crear_nodo("<operador_suma_resta>", [hoja(valor)])

    def expandir_operador_relacional(valor: str) -> dict[str, Any]:
        return _crear_nodo("<operador_relacional>", [hoja(valor)])

    def expandir_valor_aritmetico(valor: str) -> dict[str, Any]:
        valor = valor.strip()
        if re.fullmatch(IDENTIFICADOR, valor):
            return _crear_nodo("<valor_aritmetico>", [expandir_identificador(valor)])
        return _crear_nodo("<valor_aritmetico>", [expandir_numero(valor)])

    def expandir_valor_general(valor: str) -> dict[str, Any]:
        valor = valor.strip()
        if re.fullmatch(BOOLEANO, valor):
            return _crear_nodo("<valor_general>", [expandir_booleano(valor)])
        if re.fullmatch(IDENTIFICADOR, valor):
            return _crear_nodo("<valor_general>", [expandir_identificador(valor)])
        if re.fullmatch(NUMERO, valor):
            return _crear_nodo("<valor_general>", [expandir_numero(valor)])
        if re.fullmatch(CADENA, valor):
            return _crear_nodo("<valor_general>", [expandir_cadena(valor)])
        return _crear_nodo("<valor_general>", [hoja(valor)])

    def expandir_expresion_aritmetica_desde_tokens(tokens: list[str]) -> dict[str, Any]:
        if len(tokens) == 1:
            return _crear_nodo("<expresion_aritmetica>", [expandir_valor_aritmetico(tokens[0])])

        return _crear_nodo(
            "<expresion_aritmetica>",
            [
                expandir_valor_aritmetico(tokens[0]),
                expandir_operador_aritmetico(tokens[1]),
                expandir_expresion_aritmetica_desde_tokens(tokens[2:]),
            ],
        )

    def expandir_expresion_aritmetica(valor: str) -> dict[str, Any]:
        return expandir_expresion_aritmetica_desde_tokens(_tokenizar_expresion_aritmetica(valor))

    def expandir_expresion_asignacion(valor: str) -> dict[str, Any]:
        valor = valor.strip()
        if re.fullmatch(CADENA, valor):
            return _crear_nodo("<expresion_asignacion>", [expandir_cadena(valor)])
        if re.fullmatch(BOOLEANO, valor):
            return _crear_nodo("<expresion_asignacion>", [expandir_booleano(valor)])
        return _crear_nodo("<expresion_asignacion>", [expandir_expresion_aritmetica(valor)])

    def expandir_item_escritura(valor: str) -> dict[str, Any]:
        valor = valor.strip()
        if re.fullmatch(CADENA, valor):
            return _crear_nodo("<item_escritura>", [expandir_cadena(valor)])
        if re.fullmatch(BOOLEANO, valor):
            return _crear_nodo("<item_escritura>", [expandir_booleano(valor)])
        return _crear_nodo("<item_escritura>", [expandir_expresion_aritmetica(valor)])

    def expandir_lista_escritura(items: list[str]) -> dict[str, Any]:
        if len(items) == 1:
            return _crear_nodo("<lista_escritura>", [expandir_item_escritura(items[0])])

        return _crear_nodo(
            "<lista_escritura>",
            [
                expandir_item_escritura(items[0]),
                hoja(","),
                expandir_lista_escritura(items[1:]),
            ],
        )

    def expandir_condicion(valor: str) -> dict[str, Any]:
        izquierda, operador, derecha = _descomponer_condicion(valor)
        return _crear_nodo(
            "<condicion>",
            [
                expandir_valor_general(izquierda),
                expandir_operador_relacional(operador),
                expandir_valor_general(derecha),
            ],
        )

    def expandir_condicion_para(valor: str) -> dict[str, Any]:
        izquierda, operador, derecha = _descomponer_condicion_para(valor)
        return _crear_nodo(
            "<condicion_para>",
            [
                expandir_valor_aritmetico(izquierda),
                expandir_operador_relacional(operador),
                expandir_valor_aritmetico(derecha),
            ],
        )

    def expandir_actualizacion(
        variable_destino: str,
        variable_fuente: str,
        signo: str,
        paso: str,
    ) -> dict[str, Any]:
        return _crear_nodo(
            "<actualizacion>",
            [
                expandir_identificador(variable_destino),
                hoja("="),
                expandir_identificador(variable_fuente),
                expandir_operador_suma_resta(signo),
                expandir_numero_entero(paso),
            ],
        )

    def parsear_programa() -> dict[str, Any]:
        nonlocal indice
        programa = _crear_nodo("<programa>", [hoja("INICIO")])
        indice += 1
        programa["hijos"].append(parsear_lista_instrucciones({"FIN"}))
        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "FIN":
            programa["hijos"].append(hoja("FIN"))
            indice += 1
        return programa

    def parsear_lista_instrucciones(paradas: set[str]) -> dict[str, Any]:
        nonlocal indice
        if indice >= len(lineas_validas) or lineas_validas[indice]["tipo"] in paradas:
            return _crear_nodo("<lista_instrucciones>", [hoja("ε")])

        return _crear_nodo(
            "<lista_instrucciones>",
            [
                _crear_nodo("<instruccion>", [parsear_instruccion()]),
                parsear_lista_instrucciones(paradas),
            ],
        )

    def parsear_instruccion() -> dict[str, Any]:
        tipo = lineas_validas[indice]["tipo"]
        if tipo == "ASIGNACION":
            return parsear_asignacion()
        if tipo == "LEER":
            return parsear_leer()
        if tipo == "ESCRIBIR":
            return parsear_escribir()
        if tipo == "SI":
            return parsear_si()
        if tipo == "MIENTRAS":
            return parsear_mientras()
        if tipo == "PARA":
            return parsear_para()
        if tipo == "SEGUN":
            return parsear_segun()
        return hoja(lineas_validas[indice]["texto"])

    def parsear_asignacion() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1
        return _crear_nodo(
            "<asignacion>",
            [
                expandir_identificador(info["match"].group("destino")),
                hoja("="),
                expandir_expresion_asignacion(info["match"].group("expresion")),
            ],
        )

    def parsear_leer() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1
        return _crear_nodo(
            "<leer>",
            [
                hoja("LEER"),
                expandir_identificador(info["match"].group("variable")),
            ],
        )

    def parsear_escribir() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1
        items = _partir_lista(info["match"].group("expresion"), ",")
        return _crear_nodo(
            "<escribir>",
            [
                hoja("ESCRIBIR"),
                expandir_lista_escritura(items),
            ],
        )

    def parsear_si() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1
        nodo_si = _crear_nodo(
            "<si>",
            [
                hoja("SI"),
                expandir_condicion(info["match"].group("condicion")),
                hoja("ENTONCES"),
                parsear_lista_instrucciones({"SINO", "FIN"}),
            ],
        )

        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "SINO":
            indice += 1
            nodo_si["hijos"].append(hoja("SINO"))
            nodo_si["hijos"].append(parsear_lista_instrucciones({"FIN"}))

        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "FIN":
            nodo_si["hijos"].append(hoja("FIN"))
            indice += 1

        return nodo_si

    def parsear_mientras() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        texto = info["texto"]
        indice += 1

        hijos = [
            hoja("MIENTRAS"),
            expandir_condicion(info["match"].group("condicion")),
        ]
        if texto.endswith(" HACER"):
            hijos.append(hoja("HACER"))

        hijos.append(parsear_lista_instrucciones({"FIN"}))
        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "FIN":
            hijos.append(hoja("FIN"))
            indice += 1

        return _crear_nodo("<mientras>", hijos)

    def parsear_para() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1

        condicion = (
            f"{info['match'].group('izquierda')} "
            f"{info['match'].group('operador')} "
            f"{info['match'].group('derecha')}"
        )

        hijos = [
            hoja("PARA"),
            expandir_identificador(info["match"].group("var_inicial")),
            hoja("="),
            expandir_numero_entero(info["match"].group("inicio")),
            hoja(";"),
            expandir_condicion_para(condicion),
            hoja(";"),
            expandir_actualizacion(
                info["match"].group("var_actualizada"),
                info["match"].group("var_fuente"),
                info["match"].group("signo"),
                info["match"].group("paso"),
            ),
            parsear_lista_instrucciones({"FIN"}),
        ]

        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "FIN":
            hijos.append(hoja("FIN"))
            indice += 1

        return _crear_nodo("<para>", hijos)

    def parsear_segun() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1

        hijos = [
            hoja("SEGUN"),
            expandir_valor_general(info["match"].group("expresion")),
            parsear_lista_casos(),
        ]

        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "FIN":
            hijos.append(hoja("FIN"))
            indice += 1

        return _crear_nodo("<segun>", hijos)

    def parsear_lista_casos() -> dict[str, Any]:
        if indice >= len(lineas_validas) or lineas_validas[indice]["tipo"] != "CASO":
            return _crear_nodo("<lista_casos>", [hoja("ε")])

        caso_actual = parsear_caso()
        if indice < len(lineas_validas) and lineas_validas[indice]["tipo"] == "CASO":
            return _crear_nodo(
                "<lista_casos>",
                [
                    caso_actual,
                    parsear_lista_casos(),
                ],
            )

        return _crear_nodo("<lista_casos>", [caso_actual])

    def parsear_caso() -> dict[str, Any]:
        nonlocal indice
        info = lineas_validas[indice]
        indice += 1
        return _crear_nodo(
            "<caso>",
            [
                hoja("CASO"),
                expandir_numero_entero(info["match"].group("valor")),
                parsear_lista_instrucciones({"CASO", "FIN"}),
            ],
        )

    return parsear_programa()


# ============================================================
# ANALISIS COMPLETO DEL CODIGO
# ============================================================
# Funcion principal del modulo. Clasifica lineas, tokeniza, valida la
# estructura y, si no hay errores, construye el arbol de derivacion.

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

    arbol_derivacion: dict[str, Any] = {}
    if not errores:
        arbol_derivacion = construir_arbol_derivacion(lineas_validas)

    return {
        "ok": not errores,
        "errores": errores,
        "tokens": tokens if not errores else [],
        "lineas_validas": lineas_validas,
        "arbol_derivacion": arbol_derivacion,
    }
