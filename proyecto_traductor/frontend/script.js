const boton = document.getElementById("analizarBtn");
const copiarTraduccionBtn = document.getElementById("copiarTraduccionBtn");
const toggleTokensBtn = document.getElementById("toggleTokensBtn");
const toggleArbolBtn = document.getElementById("toggleArbolBtn");
const exportarArbolBtn = document.getElementById("exportarArbolBtn");
const codigoInput = document.getElementById("codigo");
const erroresBox = document.getElementById("errores");
const tokensBox = document.getElementById("tokens");
const traduccionBox = document.getElementById("traduccion");
const arbolDerivacionBox = document.getElementById("arbolDerivacion");
const reglasLista = document.getElementById("reglasLista");
let arbolDisponible = false;
let arbolActual = null;

const reglasLenguaje = [
    {
        titulo: "Palabras reservadas",
        descripcion: "El lenguaje reconoce INICIO, SI, SINO, ENTONCES, FIN, SEGUN, CASO, MIENTRAS, HACER, PARA, LEER y ESCRIBIR.",
        sintaxis: "INICIO | SI | SINO | ENTONCES | FIN | SEGUN | CASO | MIENTRAS | HACER | PARA | LEER | ESCRIBIR",
    },
    {
        titulo: "Identificadores",
        descripcion: "Un identificador debe iniciar con una letra y continuar solo con letras o digitos.",
        sintaxis: "resultado\ncontador1\nvalorFinal",
    },
    {
        titulo: "Numeros",
        descripcion: "La app acepta enteros y decimales positivos. El PARA inicia siempre con un numero entero.",
        sintaxis: "0\n15\n3.14",
    },
    {
        titulo: "Cadenas",
        descripcion: "Las cadenas usan comillas dobles y pueden contener cualquier caracter excepto salto de linea y comillas dobles sin escapar.",
        sintaxis: "\"Hola mundo\"\n\"Total: 25\"\n\"Caso A\"",
    },
    {
        titulo: "Asignacion",
        descripcion: "Una asignacion valida usa identificador, = y una expresion aritmetica, cadena o booleano.",
        sintaxis: "total = 25\nmensaje = \"Hola\"\nactivo = VERDADERO",
    },
    {
        titulo: "Expresion aritmetica",
        descripcion: "Una expresion aritmetica concatena valores aritmeticos con +, -, * o /.",
        sintaxis: "a + 5\nx * y - 2\n10 / z",
    },
    {
        titulo: "Condicion relacional",
        descripcion: "Las condiciones comparan dos valores generales usando ==, !=, <, >, <= o >=",
        sintaxis: "edad >= 18\ntotal != limite\nx < \"z\"",
    },
    {
        titulo: "LEER y ESCRIBIR",
        descripcion: "LEER recibe un identificador. ESCRIBIR acepta cadenas, booleanos y expresiones aritmeticas separadas por comas.",
        sintaxis: "LEER edad\nESCRIBIR \"Resultado:\", total\nESCRIBIR activo\nESCRIBIR a + b",
    },
    {
        titulo: "Bloque SI",
        descripcion: "SI debe incluir una condicion, la palabra ENTONCES y cerrar con FIN. SINO es opcional.",
        sintaxis: "SI nota >= 61 ENTONCES\n    ESCRIBIR \"Aprobado\"\nSINO\n    ESCRIBIR \"Reprobado\"\nFIN",
    },
    {
        titulo: "Bloque MIENTRAS",
        descripcion: "MIENTRAS acepta una condicion relacional y puede llevar HACER de forma opcional.",
        sintaxis: "MIENTRAS contador < 10 HACER\n    ESCRIBIR contador\nFIN",
    },
    {
        titulo: "Bloque PARA",
        descripcion: "PARA usa inicializacion entera, condicion relacional entre valores aritmeticos y actualizacion con suma o resta.",
        sintaxis: "PARA i = 0; i < 10; i = i + 1\n    ESCRIBIR i\nFIN",
    },
    {
        titulo: "Bloque SEGUN",
        descripcion: "SEGUN recibe un valor general. Cada CASO actual de la app se define con un numero entero y el bloque debe tener al menos un CASO.",
        sintaxis: "SEGUN opcion\nCASO 1\n    ESCRIBIR \"Uno\"\nCASO 2\n    ESCRIBIR \"Dos\"\nFIN",
    },
    {
        titulo: "BNF corregida",
        descripcion: "Esta version esta alineada con lo que valida actualmente el backend.",
        sintaxis:
`<programa> ::= INICIO <lista_instrucciones> FIN
<lista_instrucciones> ::= <instruccion> <lista_instrucciones> | epsilon
<instruccion> ::= <asignacion> | <leer> | <escribir> | <si> | <mientras> | <para> | <segun>
<asignacion> ::= <identificador> "=" <expresion_asignacion>
<leer> ::= LEER <identificador>
<escribir> ::= ESCRIBIR <lista_escritura>
<lista_escritura> ::= <item_escritura> | <item_escritura> "," <lista_escritura>
<si> ::= SI <condicion> ENTONCES <lista_instrucciones> FIN
       | SI <condicion> ENTONCES <lista_instrucciones> SINO <lista_instrucciones> FIN
<mientras> ::= MIENTRAS <condicion> <lista_instrucciones> FIN
             | MIENTRAS <condicion> HACER <lista_instrucciones> FIN
<para> ::= PARA <identificador> "=" <numero_entero> ";" <condicion_para> ";" <actualizacion> <lista_instrucciones> FIN
<condicion_para> ::= <valor_aritmetico> <operador_relacional> <valor_aritmetico>
<actualizacion> ::= <identificador> "=" <identificador> <operador_suma_resta> <numero_entero>
<segun> ::= SEGUN <valor_general> <lista_casos> FIN
<lista_casos> ::= <caso> <lista_casos> | <caso>
<caso> ::= CASO <numero_entero> <lista_instrucciones>
<condicion> ::= <valor_general> <operador_relacional> <valor_general>
<expresion_asignacion> ::= <expresion_aritmetica> | <cadena> | <booleano>
<expresion_aritmetica> ::= <valor_aritmetico> | <valor_aritmetico> <operador_aritmetico> <expresion_aritmetica>
<item_escritura> ::= <cadena> | <booleano> | <expresion_aritmetica>`,
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
    codigoInput.selectionStart = inicio + 1;
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

function limpiarResultados() {
    tokensBox.textContent = "[]";
    tokensBox.hidden = true;
    tokensBox.classList.add("oculto");
    toggleTokensBtn.textContent = "Mostrar";
    toggleTokensBtn.setAttribute("aria-expanded", "false");
    traduccionBox.value = "";
    arbolDisponible = false;
    arbolActual = null;
    exportarArbolBtn.disabled = true;
    arbolDerivacionBox.className = "arbol-panel vacio";
    arbolDerivacionBox.textContent = "El arbol aparecera cuando el programa sea valido.";
    arbolDerivacionBox.hidden = true;
    arbolDerivacionBox.classList.add("oculto");
    toggleArbolBtn.textContent = "Mostrar";
    toggleArbolBtn.setAttribute("aria-expanded", "false");
}

function escaparHtml(valor) {
    return String(valor)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll("\"", "&quot;")
        .replaceAll("'", "&#39;");
}

function renderizarNodoArbol(nodo) {
    if (!nodo || typeof nodo !== "object") {
        return "";
    }

    const etiqueta = escaparHtml(nodo.etiqueta || "");
    const hijos = Array.isArray(nodo.hijos) ? nodo.hijos : [];

    if (!hijos.length) {
        return `
            <div class="tree-node tree-leaf">
                <div class="tree-label">${etiqueta}</div>
            </div>
        `;
    }

    return `
        <div class="tree-node">
            <div class="tree-label">${etiqueta}</div>
            <div class="tree-children">
                ${hijos.map((hijo) => `<div class="tree-child">${renderizarNodoArbol(hijo)}</div>`).join("")}
            </div>
        </div>
    `;
}

function mostrarArbolDerivacion(arbol) {
    if (!arbol || typeof arbol !== "object" || !arbol.etiqueta) {
        arbolDisponible = false;
        arbolActual = null;
        exportarArbolBtn.disabled = true;
        arbolDerivacionBox.className = "arbol-panel vacio";
        arbolDerivacionBox.textContent = "No se pudo construir el arbol de derivacion.";
        return;
    }

    arbolDisponible = true;
    arbolActual = arbol;
    exportarArbolBtn.disabled = false;
    arbolDerivacionBox.className = "arbol-panel";
    arbolDerivacionBox.innerHTML = `<div class="tree-root">${renderizarNodoArbol(arbol)}</div>`;
}

function alternarSeccion(contenedor, botonControl) {
    const estaOculto = contenedor.hidden;
    contenedor.hidden = !estaOculto;
    contenedor.classList.toggle("oculto", !estaOculto);
    botonControl.textContent = estaOculto ? "Ocultar" : "Mostrar";
    botonControl.setAttribute("aria-expanded", estaOculto ? "true" : "false");
}

function medirTexto(contexto, texto) {
    return Math.ceil(contexto.measureText(texto).width);
}

function construirLayoutArbol(nodo, contexto) {
    const hijos = Array.isArray(nodo.hijos) ? nodo.hijos : [];
    const paddingX = 12;
    const paddingY = 8;
    const gapHorizontal = 24;
    const gapVertical = 48;
    const texto = String(nodo.etiqueta || "");
    const anchoNodo = Math.max(48, medirTexto(contexto, texto) + paddingX * 2);
    const altoNodo = 34;

    if (!hijos.length) {
        return {
            etiqueta: texto,
            width: anchoNodo,
            height: altoNodo,
            boxWidth: anchoNodo,
            boxHeight: altoNodo,
            children: [],
            childGapVertical: gapVertical,
        };
    }

    const layoutsHijos = hijos.map((hijo) => construirLayoutArbol(hijo, contexto));
    const anchoHijos = layoutsHijos.reduce((total, layout, index) => {
        return total + layout.width + (index > 0 ? gapHorizontal : 0);
    }, 0);

    return {
        etiqueta: texto,
        width: Math.max(anchoNodo, anchoHijos),
        height: altoNodo + gapVertical + Math.max(...layoutsHijos.map((layout) => layout.height)),
        boxWidth: anchoNodo,
        boxHeight: altoNodo,
        children: layoutsHijos,
        childGapVertical: gapVertical,
    };
}

function dibujarRectRedondeado(contexto, x, y, width, height, radius) {
    contexto.beginPath();
    contexto.moveTo(x + radius, y);
    contexto.lineTo(x + width - radius, y);
    contexto.quadraticCurveTo(x + width, y, x + width, y + radius);
    contexto.lineTo(x + width, y + height - radius);
    contexto.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    contexto.lineTo(x + radius, y + height);
    contexto.quadraticCurveTo(x, y + height, x, y + height - radius);
    contexto.lineTo(x, y + radius);
    contexto.quadraticCurveTo(x, y, x + radius, y);
    contexto.closePath();
}

function dibujarLayoutArbol(contexto, layout, x, y) {
    const boxX = x + (layout.width - layout.boxWidth) / 2;
    const boxY = y;
    const centerX = boxX + layout.boxWidth / 2;
    const centerY = boxY + layout.boxHeight / 2;
    const esHoja = layout.children.length === 0;

    dibujarRectRedondeado(contexto, boxX, boxY, layout.boxWidth, layout.boxHeight, 10);
    contexto.fillStyle = esHoja ? "#f7f0e5" : "#fffdf9";
    contexto.fill();
    contexto.strokeStyle = "#d9ccb9";
    contexto.lineWidth = 1.5;
    contexto.stroke();

    contexto.fillStyle = "#1b1a17";
    contexto.textAlign = "center";
    contexto.textBaseline = "middle";
    contexto.fillText(layout.etiqueta, centerX, centerY);

    if (!layout.children.length) {
        return;
    }

    const totalChildrenWidth = layout.children.reduce((total, child, index) => {
        return total + child.width + (index > 0 ? 24 : 0);
    }, 0);
    let childX = x + (layout.width - totalChildrenWidth) / 2;
    const childY = y + layout.boxHeight + layout.childGapVertical;
    const parentBottomY = boxY + layout.boxHeight;
    const horizontalY = y + layout.boxHeight + layout.childGapVertical / 2;

    contexto.strokeStyle = "#d9ccb9";
    contexto.lineWidth = 2;
    contexto.beginPath();
    contexto.moveTo(centerX, parentBottomY);
    contexto.lineTo(centerX, horizontalY);
    contexto.stroke();

    const centrosHijos = [];
    for (const child of layout.children) {
        const childCenterX = childX + child.width / 2;
        centrosHijos.push({ x: childCenterX, layout: child, left: childX });
        childX += child.width + 24;
    }

    if (centrosHijos.length > 1) {
        contexto.beginPath();
        contexto.moveTo(centrosHijos[0].x, horizontalY);
        contexto.lineTo(centrosHijos[centrosHijos.length - 1].x, horizontalY);
        contexto.stroke();
    }

    for (const hijo of centrosHijos) {
        contexto.beginPath();
        contexto.moveTo(hijo.x, horizontalY);
        contexto.lineTo(hijo.x, childY);
        contexto.stroke();
        dibujarLayoutArbol(contexto, hijo.layout, hijo.left, childY);
    }
}

async function exportarArbolComoPng() {
    if (!arbolDisponible || !arbolActual) {
        return;
    }

    const textoOriginal = exportarArbolBtn.textContent;
    exportarArbolBtn.disabled = true;
    exportarArbolBtn.textContent = "Exportando...";

    try {
        const canvas = document.createElement("canvas");
        const contexto = canvas.getContext("2d");
        contexto.font = '16px Consolas, "Courier New", monospace';

        const padding = 24;
        const escala = 2;
        const layout = construirLayoutArbol(arbolActual, contexto);
        const ancho = Math.ceil(layout.width + padding * 2);
        const alto = Math.ceil(layout.height + padding * 2);

        canvas.width = ancho * escala;
        canvas.height = alto * escala;
        contexto.scale(escala, escala);
        contexto.fillStyle = "#fffaf3";
        contexto.fillRect(0, 0, ancho, alto);
        contexto.font = '16px Consolas, "Courier New", monospace';
        dibujarLayoutArbol(contexto, layout, padding, padding);

        const enlace = document.createElement("a");
        enlace.href = canvas.toDataURL("image/png");
        enlace.download = "arbol-derivacion.png";
        enlace.click();
        exportarArbolBtn.textContent = "Exportado";
    } catch (error) {
        exportarArbolBtn.textContent = "No se pudo";
    }

    setTimeout(() => {
        exportarArbolBtn.textContent = textoOriginal;
        exportarArbolBtn.disabled = !arbolDisponible;
    }, 1200);
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
    limpiarResultados();
    mostrarErrores(["Enviando codigo al backend..."], "vacio");

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
            limpiarResultados();
            return;
        }

        mostrarErrores(["Analisis completado sin errores."], "exito");
        tokensBox.textContent = JSON.stringify(datos.tokens, null, 2);
        traduccionBox.value = datos.traduccion || "";
        mostrarArbolDerivacion(datos.arbol_derivacion);
    } catch (error) {
        mostrarErrores(
            [
                "No fue posible conectar con el backend en http://localhost:5000.",
                "Asegurate de haber iniciado Flask antes de usar la interfaz.",
            ],
            "error"
        );
        limpiarResultados();
    } finally {
        boton.disabled = false;
        boton.textContent = "Analizar y traducir";
    }
}

boton.addEventListener("click", analizarCodigo);
copiarTraduccionBtn.addEventListener("click", copiarTraduccion);
toggleTokensBtn.addEventListener("click", () => alternarSeccion(tokensBox, toggleTokensBtn));
toggleArbolBtn.addEventListener("click", () => alternarSeccion(arbolDerivacionBox, toggleArbolBtn));
exportarArbolBtn.addEventListener("click", exportarArbolComoPng);
codigoInput.addEventListener("keydown", manejarEditorCodigo);
renderizarReglas();
limpiarResultados();
