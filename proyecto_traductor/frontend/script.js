const boton = document.getElementById("analizarBtn");
const codigoInput = document.getElementById("codigo");
const erroresBox = document.getElementById("errores");
const tokensBox = document.getElementById("tokens");
const traduccionBox = document.getElementById("traduccion");

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

async function analizarCodigo() {
    const codigo = codigoInput.value.trim();

    boton.disabled = true;
    boton.textContent = "Analizando...";
    tokensBox.textContent = "[]";
    traduccionBox.value = "";
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
codigoInput.addEventListener("keydown", manejarEditorCodigo);
