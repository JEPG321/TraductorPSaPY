const boton = document.getElementById("analizarBtn");
const codigoInput = document.getElementById("codigo");
const erroresBox = document.getElementById("errores");
const tokensBox = document.getElementById("tokens");
const traduccionBox = document.getElementById("traduccion");

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
