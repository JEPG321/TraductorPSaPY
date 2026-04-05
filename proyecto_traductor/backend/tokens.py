"""Definiciones de tokens y patrones basicos para PseudoPy."""

TK_SI = "TK_SI"
TK_INICIO = "TK_INICIO"
TK_SINO = "TK_SINO"
TK_ENTONCES = "TK_ENTONCES"
TK_FIN = "TK_FIN"
TK_SEGUN = "TK_SEGUN"
TK_CASO = "TK_CASO"
TK_MIENTRAS = "TK_MIENTRAS"
TK_HACER = "TK_HACER"
TK_PARA = "TK_PARA"
TK_LEER = "TK_LEER"
TK_ESCRIBIR = "TK_ESCRIBIR"
TK_ID = "TK_ID"
TK_NUM = "TK_NUM"
TK_ASIG = "TK_ASIG"
TK_SUMA = "TK_SUMA"
TK_RESTA = "TK_RESTA"
TK_MULT = "TK_MULT"
TK_DIV = "TK_DIV"
TK_IGUAL = "TK_IGUAL"
TK_DIF = "TK_DIF"
TK_MENOR = "TK_MENOR"
TK_MAYOR = "TK_MAYOR"
TK_MENORIGUAL = "TK_MENORIGUAL"
TK_MAYORIGUAL = "TK_MAYORIGUAL"
TK_CADENA = "TK_CADENA"
TK_COMA = "TK_COMA"

RESERVED_WORD_TOKENS = {
    "INICIO": TK_INICIO,
    "SI": TK_SI,
    "SINO": TK_SINO,
    "ENTONCES": TK_ENTONCES,
    "FIN": TK_FIN,
    "SEGUN": TK_SEGUN,
    "CASO": TK_CASO,
    "MIENTRAS": TK_MIENTRAS,
    "HACER": TK_HACER,
    "PARA": TK_PARA,
    "LEER": TK_LEER,
    "ESCRIBIR": TK_ESCRIBIR,
}

TOKEN_REGEX_SPECS = [
    (TK_MENORIGUAL, r"<="),
    (TK_MAYORIGUAL, r">="),
    (TK_IGUAL, r"=="),
    (TK_DIF, r"!="),
    (TK_ASIG, r"="),
    (TK_MENOR, r"<"),
    (TK_MAYOR, r">"),
    (TK_SUMA, r"\+"),
    (TK_RESTA, r"-"),
    (TK_MULT, r"\*"),
    (TK_DIV, r"/"),
    (TK_COMA, r","),
    (TK_INICIO, r"\bINICIO\b"),
    (TK_SI, r"\bSI\b"),
    (TK_SINO, r"\bSINO\b"),
    (TK_ENTONCES, r"\bENTONCES\b"),
    (TK_FIN, r"\bFIN\b"),
    (TK_SEGUN, r"\bSEGUN\b"),
    (TK_CASO, r"\bCASO\b"),
    (TK_MIENTRAS, r"\bMIENTRAS\b"),
    (TK_HACER, r"\bHACER\b"),
    (TK_PARA, r"\bPARA\b"),
    (TK_LEER, r"\bLEER\b"),
    (TK_ESCRIBIR, r"\bESCRIBIR\b"),
    (TK_CADENA, r'"[^"\n]*"'),
    (TK_NUM, r"\b[0-9]+\b"),
    (TK_ID, r"\b[a-zA-Z][a-zA-Z0-9]*\b"),
]
