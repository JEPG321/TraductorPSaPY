const boton = document.getElementById("analizarBtn");
const copiarTraduccionBtn = document.getElementById("copiarTraduccionBtn");
const codigoInput = document.getElementById("codigo");
const erroresBox = document.getElementById("errores");
const tokensBox = document.getElementById("tokens");
const traduccionBox = document.getElementById("traduccion");
const reglasLista = document.getElementById("reglasLista");

const reglasLenguaje = [
    {
        titulo: "Palabras reservadas",
        descripcion: "El lenguaje reconoce como palabras reservadas SI, SINO, ENTONCES, FIN, SEGUN, CASO, MIENTRAS, HACER, PARA, LEER y ESCRIBIR.",
        sintaxis: "SI | SINO | ENTONCES | FIN | SEGUN | CASO | MIENTRAS | HACER | PARA | LEER | ESCRIBIR",
    },
    {
        titulo: "Identificadores",
        descripcion: "Un identificador debe iniciar con una letra y puede continuar con letras o numeros.",
        sintaxis: "resultado\ncontador1\nvalorFinal",
    },
    {
        titulo: "Numeros enteros",
        descripcion: "Un numero entero esta formado por uno o mas digitos numericos consecutivos.",
        sintaxis: "0\n15\n2024",
    },
    {
        titulo: "Operador de asignacion",
        descripcion: "El operador = permite asignar valores a los identificadores.",
        sintaxis: "total = 25",
    },
    {
        titulo: "Operadores aritmeticos",
        descripcion: "El lenguaje permite usar +, -, * y / para realizar operaciones matematicas.",
        sintaxis: "a + b\nx - y\nn * 2\nm / 4",
    },
    {
        titulo: "Operadores relacionales",
        descripcion: "Las condiciones pueden usar ==, !=, <, >, <= y >= para comparar valores.",
        sintaxis: "x == y\nx != y\na < b\nc >= d",
    },
    {
        titulo: "Expresion aritmetica simple",
        descripcion: "Se forma con identificadores o numeros enteros combinados mediante operadores aritmeticos.",
        sintaxis: "a + 5\nx * y - 2\n10 / z",
    },
    {
        titulo: "Expresion relacional",
        descripcion: "Se forma con dos operandos validos separados por un operador relacional.",
        sintaxis: "edad >= 18\ntotal != limite\nx < 100",
    },
    {
        titulo: "Asignacion de variable",
        descripcion: "Una asignacion valida incluye identificador, operador = y una expresion aritmetica valida.",
        sintaxis: "promedio = nota1 + nota2 / 2",
    },
    {
        titulo: "Entrada de datos (LEER)",
        descripcion: "La instruccion inicia con LEER y luego un identificador valido donde se almacena el valor ingresado.",
        sintaxis: "LEER edad",
    },
    {
        titulo: "Salida de datos (ESCRIBIR)",
        descripcion: "La instruccion inicia con ESCRIBIR seguida de un identificador, numero o expresion aritmetica valida.",
        sintaxis: "ESCRIBIR total\nESCRIBIR 25\nESCRIBIR a + b",
    },
    {
        titulo: "Estructura condicional SI",
        descripcion: "Debe iniciar con SI, seguir con una condicion relacional valida y luego la palabra ENTONCES.",
        sintaxis: "SI nota >= 61 ENTONCES",
    },
    {
        titulo: "Estructura opcional SINO",
        descripcion: "SINO puede usarse dentro de una estructura SI para ejecutar instrucciones alternativas.",
        sintaxis: "SI x > 0 ENTONCES\n    ESCRIBIR x\nSINO\n    ESCRIBIR 0\nFIN",
    },
    {
        titulo: "Estructura SEGUN",
        descripcion: "La seleccion multiple inicia con SEGUN seguida de un identificador o numero que sera evaluado.",
        sintaxis: "SEGUN opcion",
    },
    {
        titulo: "Estructura CASO",
        descripcion: "Cada alternativa dentro de SEGUN debe iniciar con CASO y un valor especifico.",
        sintaxis: "CASO 1\nCASO 2",
    },
    {
        titulo: "Estructura MIENTRAS",
        descripcion: "MIENTRAS debe iniciar con una condicion relacional valida y puede incluir opcionalmente la palabra HACER.",
        sintaxis: "MIENTRAS contador < 10 HACER",
    },
    {
        titulo: "Estructura PARA",
        descripcion: "PARA debe incluir variable de control, valor inicial, condicion de terminacion e incremento o decremento.",
        sintaxis: "PARA i = 0; i < 10; i = i + 1",
    },
    {
        titulo: "Cierre de bloque",
        descripcion: "Toda estructura de control debe finalizar obligatoriamente con la palabra reservada FIN.",
        sintaxis: "FIN",
    },
    {
        titulo: "Cadenas de texto",
        descripcion: "Las cadenas de texto se delimitan con comillas dobles y pueden contener letras, numeros y espacios.",
        sintaxis: '"Hola mundo"\n"Usuario 1"\n"Total final"',
    },
];

function renderizarReglas() {
    if (!reglasLista) {
        return;
    }

    reglasLista.innerHTML = reglasLenguaje
        .map(
            (regla, indice) => `
                <details class="regla-card">
                    <summary>
                        <span class="regla-numero">Regla ${indice + 1}</span>
                        <strong>${regla.titulo}</strong>
                    </summary>
                    <p>${regla.descripcion}</p>
                    <pre>${regla.sintaxis}</pre>
                </details>
            `
        )
        .join("");
}

function obtenerInicioLinea(valor, posicion) {
    return valor.lastIndexOf("\n", posicion - 1) + 1;
}

function manejarEditorCodigo(evento) {
    if (evento.key !== "Tab" && evento.key !== "Enter") {
        return;
    }

    evento.preventDefault();

    const inicio = codigoInput.selectionStart;
    const fin = codigoInput.selectionEnd;
    const valor = codigoInput.value;

    if (evento.key === "Enter") {
        const inicioLinea = obtenerInicioLinea(valor, inicio);
        const lineaActual = valor.slice(inicioLinea, inicio);
        const coincidenciaIndentacion = lineaActual.match(/^[\t ]*/);
        const indentacion = coincidenciaIndentacion ? coincidenciaIndentacion[0] : "";
        const nuevoValor = `${valor.slice(0, inicio)}\n${indentacion}${valor.slice(fin)}`;

        codigoInput.value = nuevoValor;
        codigoInput.selectionStart = inicio + 1 + indentacion.length;
        codigoInput.selectionEnd = inicio + 1 + indentacion.length;
        return;
    }

    if (inicio === fin) {
        const nuevoValor = `${valor.slice(0, inicio)}\t${valor.slice(fin)}`;
        codigoInput.value = nuevoValor;
        codigoInput.selectionStart = inicio + 1;
        codigoInput.selectionEnd = inicio + 1;
        return;
    }

    const inicioLinea = obtenerInicioLinea(valor, inicio);
    const finLinea = valor.indexOf("\n", fin);
    const finBloque = finLinea === -1 ? valor.length : finLinea;
    const bloqueSeleccionado = valor.slice(inicioLinea, finBloque);
    const lineas = bloqueSeleccionado.split("\n");

    if (evento.shiftKey) {
        let tabulacionesQuitadas = 0;
        const lineasActualizadas = lineas.map((linea) => {
            if (linea.startsWith("\t")) {
                tabulacionesQuitadas += 1;
                return linea.slice(1);
            }

            if (linea.startsWith("    ")) {
                tabulacionesQuitadas += 1;
                return linea.slice(4);
            }

            return linea;
        });

        codigoInput.value =
            `${valor.slice(0, inicioLinea)}${lineasActualizadas.join("\n")}${valor.slice(finBloque)}`;
        codigoInput.selectionStart = inicio === inicioLinea ? inicio : Math.max(inicioLinea, inicio - 1);
        codigoInput.selectionEnd = Math.max(codigoInput.selectionStart, fin - tabulacionesQuitadas);
        return;
    }

    const bloqueIndentado = lineas.map((linea) => `\t${linea}`).join("\n");
    codigoInput.value = `${valor.slice(0, inicioLinea)}${bloqueIndentado}${valor.slice(finBloque)}`;
    codigoInput.selectionStart = inicio === inicioLinea ? inicio + 1 : inicio + 1;
    codigoInput.selectionEnd = fin + lineas.length;
}

function mostrarErrores(mensajes, tipo = "error") {
    erroresBox.className = `errores ${tipo}`;
    if (!mensajes.length) {
        erroresBox.textContent = "Sin mensajes.";
        return;
    }

    erroresBox.innerHTML = mensajes.map((mensaje) => `<div>${mensaje}</div>`).join("");
}

async function copiarTraduccion() {
    const texto = traduccionBox.value.trim();

    if (!texto) {
        const textoOriginal = copiarTraduccionBtn.textContent;
        copiarTraduccionBtn.textContent = "Sin texto";
        setTimeout(() => {
            copiarTraduccionBtn.textContent = textoOriginal;
        }, 1200);
        return;
    }

    const textoOriginal = copiarTraduccionBtn.textContent;

    try {
        await navigator.clipboard.writeText(texto);
        copiarTraduccionBtn.textContent = "Copiado";
    } catch (error) {
        copiarTraduccionBtn.textContent = "No se pudo";
    }

    setTimeout(() => {
        copiarTraduccionBtn.textContent = textoOriginal;
    }, 1200);
}

async function analizarCodigo() {
    const codigo = codigoInput.value.trim();

    boton.disabled = true;
    boton.textContent = "Analizando...";
    tokensBox.textContent = "[]";
    traduccionBox.value = "";
    mostrarErrores(["Enviando codigo al backend..."], "vacío");

    try {
        const respuesta = await fetch("http://localhost:5000/analizar", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ codigo }),
        });

        const datos = await respuesta.json();

        if (!respuesta.ok || !datos.ok) {
            mostrarErrores(datos.errores || ["Ocurrio un error al procesar la solicitud."], "error");
            tokensBox.textContent = "[]";
            traduccionBox.value = "";
            return;
        }

        mostrarErrores(["Analisis completado sin errores."], "exito");
        tokensBox.textContent = JSON.stringify(datos.tokens, null, 2);
        traduccionBox.value = datos.traduccion || "";
    } catch (error) {
        mostrarErrores(
            [
                "No fue posible conectar con el backend en http://localhost:5000.",
                "Asegurate de haber iniciado Flask antes de usar la interfaz.",
            ],
            "error"
        );
        tokensBox.textContent = "[]";
        traduccionBox.value = "";
    } finally {
        boton.disabled = false;
        boton.textContent = "Analizar y traducir";
    }
}

boton.addEventListener("click", analizarCodigo);
copiarTraduccionBtn.addEventListener("click", copiarTraduccion);
codigoInput.addEventListener("keydown", manejarEditorCodigo);
renderizarReglas();
