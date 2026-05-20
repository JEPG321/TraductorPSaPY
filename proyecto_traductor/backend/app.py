"""Servidor Flask para analizar y traducir codigo PseudoPy."""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

from traductor import traducir_codigo
from validador import analizar_codigo

app = Flask(__name__)
CORS(app)


@app.post("/analizar")
def analizar() -> tuple:
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or "codigo" not in datos:
        return (
            jsonify(
                {
                    "ok": False,
                    "errores": ["El cuerpo de la solicitud debe ser JSON e incluir la clave 'codigo'."],
                    "tokens": [],
                    "traduccion": "",
                    "arbol_derivacion": "",
                }
            ),
            400,
        )

    codigo = str(datos.get("codigo", ""))
    resultado = analizar_codigo(codigo)

    if not resultado["ok"]:
        return jsonify(
            {
                "ok": False,
                "errores": resultado["errores"],
                "tokens": [],
                "traduccion": "",
                "arbol_derivacion": "",
            }
        )

    traduccion = traducir_codigo(codigo)
    return jsonify(
        {
            "ok": True,
            "errores": [],
            "tokens": resultado["tokens"],
            "traduccion": traduccion,
            "arbol_derivacion": resultado.get("arbol_derivacion", ""),
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
