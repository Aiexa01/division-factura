function calcular() {

    const error = document.getElementById("error");

    error.textContent = "";


    // =========================
    // DATOS EDESA
    // =========================

    const cargoFijo5 =
        Number(document.getElementById("cargoFijo5").value);

    const cargoFijo25 =
        Number(document.getElementById("cargoFijo25").value);

    const energia70 =
        Number(document.getElementById("energia70").value);

    const energia130 =
        Number(document.getElementById("energia130").value);

    const energia219 =
        Number(document.getElementById("energia219").value);

    const ivaEdesa =
        Number(document.getElementById("ivaEdesa").value);


    // =========================
    // ALUMBRADO
    // =========================

    const alumbradoPublico =
        Number(document.getElementById("alumbradoPublico").value);


    // =========================
    // AGUAS
    // =========================

    const cargoFijoAguas =
        Number(document.getElementById("cargoFijoAguas").value);

    const consumoAguas =
        Number(document.getElementById("consumoAguas").value);

    const tasaAguas =
        Number(document.getElementById("tasaAguas").value);

    const ivaAguas =
        Number(document.getElementById("ivaAguas").value);


    // =========================
    // LUSAL
    // =========================

    const mantenimientoLusal =
        Number(document.getElementById("mantenimientoLusal").value);


    // =========================
    // CONSUMO
    // =========================

    const totalKwh =
        Number(document.getElementById("totalKwh").value);

    const persona1Kwh =
        Number(document.getElementById("persona1Kwh").value);


    // =========================
    // VALIDACIONES
    // =========================

    if (totalKwh <= 0) {

        error.textContent =
            "El consumo total debe ser mayor que cero.";

        return;
    }


    if (
        persona1Kwh < 0 ||
        persona1Kwh > totalKwh
    ) {

        error.textContent =
            "El consumo de la persona 1 no puede ser negativo ni superar el consumo total.";

        return;
    }


    // =========================
    // PERSONA 2
    // =========================

    const persona2Kwh =
        totalKwh - persona1Kwh;


    // =========================
    // PORCENTAJES
    // =========================

    const porcentajePersona1 =
        (persona1Kwh / totalKwh) * 100;

    const porcentajePersona2 =
        (persona2Kwh / totalKwh) * 100;


    // =========================
    // BLOQUES DE KWh
    // =========================

    // Cada persona tiene derecho a la mitad de cada tramo barato
    // (35 kWh del de 70 y 65 kWh del de 130). Los kWh se usan en orden:
    // primero el tramo de 70, después el de 130 y el resto va al
    // excedente. Si una persona no llega a usar su mitad de un tramo,
    // lo que le sobra lo usa la otra persona.

    function repartirTramo(capacidad, restante1, restante2) {

        let tramo1 = Math.min(restante1, capacidad / 2);

        let tramo2 = Math.min(restante2, capacidad / 2);

        const sobrante = capacidad - tramo1 - tramo2;

        const extra1 = Math.min(restante1 - tramo1, sobrante);

        tramo1 += extra1;

        tramo2 += Math.min(restante2 - tramo2, sobrante - extra1);

        return [tramo1, tramo2];
    }


    const [kwh70Persona1, kwh70Persona2] =
        repartirTramo(70, persona1Kwh, persona2Kwh);


    const [kwh130Persona1, kwh130Persona2] =
        repartirTramo(
            130,
            persona1Kwh - kwh70Persona1,
            persona2Kwh - kwh70Persona2
        );


    const kwh219Persona1 =
        persona1Kwh - kwh70Persona1 - kwh130Persona1;


    const kwh219Persona2 =
        persona2Kwh - kwh70Persona2 - kwh130Persona2;


    const kwh70Total =
        kwh70Persona1 + kwh70Persona2;

    const kwh130Total =
        kwh130Persona1 + kwh130Persona2;

    const kwh219Total =
        kwh219Persona1 + kwh219Persona2;


    // =========================
    // CENTAVOS
    // =========================

    // Todo se calcula en centavos enteros para que la suma de las dos
    // personas dé exactamente el total de la factura. Cada renglón se toma
    // tal como figura en la factura (redondeado al centavo) y se reparte
    // entre las dos personas sin perder ni agregar centavos.

    function centavos(valor) {

        return Math.round(
            (valor + Number.EPSILON * Math.max(1, Math.abs(valor))) * 100
        );
    }


    // Cuando un renglón no se puede dividir justo (por ejemplo, un importe
    // impar al 50/50), el centavo que sobra se alterna entre las personas.
    let proximoCentavoPersona1 = true;

    function repartir(importeCentavos, fraccionPersona1) {

        const exacto = importeCentavos * fraccionPersona1;

        let persona1 = Math.floor(exacto);

        const resto = exacto - persona1;

        if (Math.abs(resto - 0.5) < 1e-9) {

            if (proximoCentavoPersona1) {
                persona1 += 1;
            }

            proximoCentavoPersona1 = !proximoCentavoPersona1;

        } else if (resto > 0.5) {

            persona1 += 1;
        }

        return [persona1, importeCentavos - persona1];
    }


    // =========================
    // COSTO DE ENERGÍA
    // =========================

    const lineaEnergia70 = centavos(kwh70Total * energia70);

    const lineaEnergia130 = centavos(kwh130Total * energia130);

    const lineaEnergia219 = centavos(kwh219Total * energia219);


    const [energia70Persona1, energia70Persona2] =
        repartir(
            lineaEnergia70,
            kwh70Total === 0 ? 0.5 : kwh70Persona1 / kwh70Total
        );

    const [energia130Persona1, energia130Persona2] =
        repartir(
            lineaEnergia130,
            kwh130Total === 0 ? 0.5 : kwh130Persona1 / kwh130Total
        );

    const [energia219Persona1, energia219Persona2] =
        repartir(
            lineaEnergia219,
            kwh219Total === 0 ? 0.5 : kwh219Persona1 / kwh219Total
        );


    const energiaPersona1 =
        energia70Persona1 +
        energia130Persona1 +
        energia219Persona1;


    const energiaPersona2 =
        energia70Persona2 +
        energia130Persona2 +
        energia219Persona2;


    // =========================
    // EDESA 50/50
    // =========================

    const [cargoFijo5Persona1, cargoFijo5Persona2] =
        repartir(centavos(cargoFijo5), 0.5);

    const [cargoFijo25Persona1, cargoFijo25Persona2] =
        repartir(centavos(cargoFijo25), 0.5);

    const [ivaEdesaPersona1, ivaEdesaPersona2] =
        repartir(centavos(ivaEdesa), 0.5);


    const totalEdesaPersona1 =
        energiaPersona1 +
        cargoFijo5Persona1 +
        cargoFijo25Persona1 +
        ivaEdesaPersona1;


    const totalEdesaPersona2 =
        energiaPersona2 +
        cargoFijo5Persona2 +
        cargoFijo25Persona2 +
        ivaEdesaPersona2;


    // =========================
    // AGUAS 50/50
    // =========================

    const [cargoFijoAguaPersona1, cargoFijoAguaPersona2] =
        repartir(centavos(cargoFijoAguas), 0.5);

    const [consumoAguaPersona1, consumoAguaPersona2] =
        repartir(centavos(consumoAguas), 0.5);

    const [tasaAguaPersona1, tasaAguaPersona2] =
        repartir(centavos(tasaAguas), 0.5);

    const [ivaAguaPersona1, ivaAguaPersona2] =
        repartir(centavos(ivaAguas), 0.5);


    const totalAguasPersona1 =
        cargoFijoAguaPersona1 +
        consumoAguaPersona1 +
        tasaAguaPersona1 +
        ivaAguaPersona1;


    const totalAguasPersona2 =
        cargoFijoAguaPersona2 +
        consumoAguaPersona2 +
        tasaAguaPersona2 +
        ivaAguaPersona2;


    // =========================
    // ALUMBRADO + LUSAL
    // =========================

    const [alumbradoPersona1, alumbradoPersona2] =
        repartir(centavos(alumbradoPublico), 0.5);

    const [mantenimientoPersona1, mantenimientoPersona2] =
        repartir(centavos(mantenimientoLusal), 0.5);


    const totalAlumbradoPersona1 =
        alumbradoPersona1 +
        mantenimientoPersona1;


    const totalAlumbradoPersona2 =
        alumbradoPersona2 +
        mantenimientoPersona2;


    // =========================
    // TOTAL FINAL
    // =========================

    const totalAPagarPersona1 =
        totalEdesaPersona1 +
        totalAguasPersona1 +
        totalAlumbradoPersona1;


    const totalAPagarPersona2 =
        totalEdesaPersona2 +
        totalAguasPersona2 +
        totalAlumbradoPersona2;


    const totalRepartido =
        totalAPagarPersona1 +
        totalAPagarPersona2;


    // =========================
    // FORMATO
    // =========================

    function dinero(valorCentavos) {

        return (valorCentavos / 100).toFixed(2);
    }


    function numero(valor) {

        return valor.toFixed(2);
    }


    // =========================
    // CONSUMO
    // =========================

    document.getElementById(
        "resultadoKwh1"
    ).textContent =
        numero(persona1Kwh);


    document.getElementById(
        "resultadoKwh2"
    ).textContent =
        numero(persona2Kwh);


    document.getElementById(
        "resultadoPorcentaje1"
    ).textContent =
        porcentajePersona1.toFixed(2) + "%";


    document.getElementById(
        "resultadoPorcentaje2"
    ).textContent =
        porcentajePersona2.toFixed(2) + "%";


    // =========================
    // BLOQUES
    // =========================

    document.getElementById(
        "bloque70Persona1"
    ).textContent =
        numero(kwh70Persona1);


    document.getElementById(
        "bloque130Persona1"
    ).textContent =
        numero(kwh130Persona1);


    document.getElementById(
        "bloque219Persona1"
    ).textContent =
        numero(kwh219Persona1);


    document.getElementById(
        "bloque70Persona2"
    ).textContent =
        numero(kwh70Persona2);


    document.getElementById(
        "bloque130Persona2"
    ).textContent =
        numero(kwh130Persona2);


    document.getElementById(
        "bloque219Persona2"
    ).textContent =
        numero(kwh219Persona2);


    // =========================
    // ENERGÍA
    // =========================

    document.getElementById(
        "energia70Persona1"
    ).textContent =
        dinero(energia70Persona1);


    document.getElementById(
        "energia130Persona1"
    ).textContent =
        dinero(energia130Persona1);


    document.getElementById(
        "energia219Persona1"
    ).textContent =
        dinero(energia219Persona1);


    document.getElementById(
        "energiaTotalPersona1"
    ).textContent =
        dinero(energiaPersona1);


    document.getElementById(
        "energia70Persona2"
    ).textContent =
        dinero(energia70Persona2);


    document.getElementById(
        "energia130Persona2"
    ).textContent =
        dinero(energia130Persona2);


    document.getElementById(
        "energia219Persona2"
    ).textContent =
        dinero(energia219Persona2);


    document.getElementById(
        "energiaTotalPersona2"
    ).textContent =
        dinero(energiaPersona2);


    // =========================
    // REPARTO
    // =========================

    document.getElementById(
        "edesaPersona1"
    ).textContent =
        dinero(totalEdesaPersona1);


    document.getElementById(
        "edesaPersona2"
    ).textContent =
        dinero(totalEdesaPersona2);


    document.getElementById(
        "aguasPersona1"
    ).textContent =
        dinero(totalAguasPersona1);


    document.getElementById(
        "aguasPersona2"
    ).textContent =
        dinero(totalAguasPersona2);


    document.getElementById(
        "alumbradoPersona1"
    ).textContent =
        dinero(totalAlumbradoPersona1);


    document.getElementById(
        "alumbradoPersona2"
    ).textContent =
        dinero(totalAlumbradoPersona2);


    // =========================
    // TOTAL FINAL
    // =========================

    document.getElementById(
        "totalPersona1"
    ).textContent =
        dinero(totalAPagarPersona1);


    document.getElementById(
        "totalPersona2"
    ).textContent =
        dinero(totalAPagarPersona2);


    document.getElementById(
        "totalRepartido"
    ).textContent =
        dinero(totalRepartido);


    // =========================
    // MOSTRAR RESULTADOS
    // =========================

    document.getElementById(
        "resultados"
    ).classList.remove("hidden");
}


document
    .getElementById("calcularBtn")
    .addEventListener("click", calcular);


// =========================
// CARGAR FACTURA PDF
// =========================

// Lee el PDF de EDESA en el navegador y completa los campos con los
// importes de la factura. El archivo no se sube a ningún lado.

function numeroArgentino(texto) {

    return Number(
        texto.replace(/\./g, "").replace(",", ".")
    );
}


async function leerTextoPdf(archivo) {

    pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

    const datos = new Uint8Array(await archivo.arrayBuffer());

    const pdf = await pdfjsLib.getDocument({ data: datos }).promise;

    const lineas = [];

    for (let numero = 1; numero <= pdf.numPages; numero++) {

        const pagina = await pdf.getPage(numero);

        const contenido = await pagina.getTextContent();

        // Agrupa los textos que están a la misma altura en una línea.
        const filas = [];

        for (const item of contenido.items) {

            if (!item.str.trim()) continue;

            const x = item.transform[4];
            const y = item.transform[5];

            let fila = filas.find(f => Math.abs(f.y - y) < 2);

            if (!fila) {
                fila = { y, items: [] };
                filas.push(fila);
            }

            fila.items.push({ x, texto: item.str });
        }

        filas.sort((a, b) => b.y - a.y);

        for (const fila of filas) {

            fila.items.sort((a, b) => a.x - b.x);

            lineas.push(
                fila.items.map(i => i.texto).join(" ").replace(/\s+/g, " ")
            );
        }
    }

    return lineas.join("\n");
}


function buscarImporte(texto, patron) {

    const encontrado = texto.match(patron);

    return encontrado ? numeroArgentino(encontrado[1]) : null;
}


function extraerFactura(texto) {

    const importe = "(\\d{1,3}(?:\\.\\d{3})*,\\d{2})";

    const cargosFijos = [
        ...texto.matchAll(
            new RegExp("Cargo Fijo Mensual \\([^)]*\\) " + importe, "gi")
        )
    ].map(m => numeroArgentino(m[1]));

    const tramos = {};

    for (const m of texto.matchAll(
        /Energia activa(?: excedente)? \(([\d.,]+) kWh \* ([\d.,]+) \$ \/ kWh\)/gi
    )) {
        tramos[numeroArgentino(m[1])] = numeroArgentino(m[2]);
    }

    const consumo = texto.match(/Activa (\d+) (\d+) [\d,]+ (\d+)/);

    return {
        cargoFijo5: cargosFijos[0],
        cargoFijo25: cargosFijos[1],
        energia70: tramos[70],
        energia130: tramos[130],
        energia219: Object.entries(tramos)
            .filter(([kwh]) => Number(kwh) !== 70 && Number(kwh) !== 130)
            .map(([, precio]) => precio)[0],
        ivaEdesa: buscarImporte(
            texto, new RegExp("IVA Consumidor Final 21,00% " + importe, "i")
        ),
        alumbradoPublico: buscarImporte(
            texto, new RegExp("Incidencia Energia Alumb\\. Pub\\. \\([^)]*\\) " + importe, "i")
        ),
        cargoFijoAguas: buscarImporte(
            texto, new RegExp("Cargo Fijo " + importe)
        ),
        consumoAguas: buscarImporte(
            texto, new RegExp("Consumo Equivalente " + importe, "i")
        ),
        tasaAguas: buscarImporte(
            texto, new RegExp("Tasa de Fiscalizaci[oó]n y Control [\\d,]+% " + importe, "i")
        ),
        ivaAguas: buscarImporte(
            texto, new RegExp("IVA Consumidor Final 21% " + importe, "i")
        ),
        mantenimientoLusal: buscarImporte(
            texto, new RegExp("Mantenimiento de Alumbrado Publico - Tarifa \\w+ " + importe, "i")
        ),
        totalKwh: consumo ? Number(consumo[3]) : null,
        total: buscarImporte(
            texto, new RegExp("T o t a l: " + importe)
        )
    };
}


async function cargarFactura(evento) {

    const estado = document.getElementById("estadoFactura");

    const archivo = evento.target.files[0];

    if (!archivo) return;

    estado.style.color = "var(--text-secondary)";

    estado.textContent = "Leyendo la factura...";

    try {

        if (typeof pdfjsLib === "undefined") {
            throw new Error(
                "No se pudo cargar el lector de PDF. Revisá la conexión a internet."
            );
        }

        const factura = extraerFactura(await leerTextoPdf(archivo));

        const faltan = [];

        for (const [id, valor] of Object.entries(factura)) {

            if (id === "total") continue;

            if (valor === null || valor === undefined || Number.isNaN(valor)) {
                faltan.push(id);
                continue;
            }

            document.getElementById(id).value = valor;
        }

        if (faltan.length) {

            estado.style.color = "";

            estado.textContent =
                "No pude leer algunos datos de la factura (" +
                faltan.join(", ") +
                "). Completalos a mano.";

        } else {

            estado.textContent =
                "Factura cargada. Total de la factura: $" +
                (factura.total ?? 0).toFixed(2) +
                ". Completá el consumo de la persona 1 y calculá.";
        }

    } catch (e) {

        estado.style.color = "";

        estado.textContent =
            "No pude leer la factura: " + e.message;
    }
}


document
    .getElementById("facturaPdf")
    .addEventListener("change", cargarFactura);
