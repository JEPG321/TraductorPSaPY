# Proyecto Traductor PseudoPy

Aplicacion web local para escribir pseudocodigo estructurado en espanol, validarlo con reglas de PseudoPy y traducirlo a Python.

## Estructura

```text
proyecto_traductor/
|
+-- backend/
|   +-- app.py
|   +-- traductor.py
|   +-- validador.py
|   +-- tokens.py
|   +-- requirements.txt
|
+-- frontend/
|   +-- index.html
|   +-- styles.css
|   +-- script.js
|
+-- README.md
```

## Requisitos

- Python 3.10 o superior
- Navegador web moderno

## Crear entorno virtual

En Windows PowerShell:

```powershell
cd proyecto_traductor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
cd proyecto_traductor
python3 -m venv .venv
source .venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r backend/requirements.txt
```

## Ejecutar el backend

```bash
cd backend
python app.py
```

El servidor queda disponible en:

```text
http://localhost:5000
```

## Abrir el frontend

Abre el archivo `frontend/index.html` directamente en tu navegador o sirvelo con un servidor estatico simple.

Ejemplo con Python:

```bash
cd frontend
python -m http.server 5500
```

Luego abre:

```text
http://localhost:5500
```

## Endpoint de la API

### POST `/analizar`

Solicitud:

```json
{
  "codigo": "INICIO\nSI x > 5 ENTONCES\nESCRIBIR \"Resultado:\", x\nFIN\nFIN"
}
```

Respuesta exitosa:

```json
{
  "ok": true,
  "errores": [],
  "tokens": [
    { "linea": 1, "tipo": "TK_INICIO", "lexema": "INICIO" }
  ],
  "traduccion": "if x > 5:\n    print(\"Resultado:\", x)"
}
```

Respuesta con errores:

```json
{
  "ok": false,
  "errores": [
    "Linea 3: FIN sin bloque abierto"
  ],
  "tokens": [],
  "traduccion": ""
}
```

## Reglas implementadas

El backend valida:

- Palabras reservadas
- Identificadores
- Numeros enteros
- Cadenas de texto entre comillas dobles
- Asignacion
- Operadores aritmeticos
- Operadores relacionales
- Expresiones aritmeticas simples
- Expresiones relacionales
- LEER
- ESCRIBIR con textos y variables separados por comas
- INICIO como apertura obligatoria del programa
- SI ... ENTONCES
- SINO
- SEGUN
- CASO
- MIENTRAS
- PARA
- FIN

Ademas realiza validacion estructural global con una pila para detectar:

- `SINO` fuera de `SI`
- `CASO` fuera de `SEGUN`
- `FIN` sobrantes
- Bloques abiertos sin cerrar
- Orden de cierre incorrecto
- Falta de `INICIO` al principio
- Falta de `FIN` final del programa

## Ejemplo completo

Entrada PseudoPy:

```text
INICIO
LEER x
SI x > 5 ENTONCES
ESCRIBIR "Resultado:", x
SINO
ESCRIBIR "Hola"
FIN
FIN
```

Salida Python:

```python
x = input()
if x > 5:
    print("Resultado:", x)
else:
    print("Hola")
```

## Archivos principales

- `backend/app.py`: API Flask con CORS y endpoint `POST /analizar`
- `backend/validador.py`: regex compiladas, tokenizacion y validacion estructural
- `backend/traductor.py`: traduccion a Python con manejo de indentacion
- `backend/tokens.py`: definicion central de tokens
- `frontend/index.html`: interfaz principal
- `frontend/script.js`: consumo del backend con `fetch`
- `frontend/styles.css`: estilos de la pagina
