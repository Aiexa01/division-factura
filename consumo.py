from decimal import Decimal, ROUND_HALF_UP


## Cálculo exacto en centavos
##
## Cada importe se redondea al centavo como en la factura y se reparte
## entre las dos personas sin perder ni agregar centavos: lo que no se
## asigna a la persona 1 va a la persona 2, así la suma da justo el total.

CENTAVO = Decimal("0.01")


def pesos(valor):
    return Decimal(valor).quantize(CENTAVO, rounding=ROUND_HALF_UP)


# Cuando un importe no se puede dividir justo (por ejemplo, un importe
# impar al 50/50), el centavo que sobra se alterna entre las personas.
proximo_centavo_persona1 = True


def repartir(importe, fraccion_persona1):
    global proximo_centavo_persona1

    importe = pesos(importe)
    exacto = importe * Decimal(fraccion_persona1)
    persona1 = exacto.quantize(CENTAVO, rounding="ROUND_FLOOR")
    resto = exacto - persona1

    if resto * 2 == CENTAVO:
        if proximo_centavo_persona1:
            persona1 += CENTAVO
        proximo_centavo_persona1 = not proximo_centavo_persona1
    elif resto * 2 > CENTAVO:
        persona1 += CENTAVO

    return persona1, importe - persona1


## Consumo de energía eléctrica EDESA

cargo_fijo_x5_dias = Decimal(input("Ingrese el cargo fijo por 5 días: "))
cargo_fijo_x25_dias = Decimal(input("Ingrese el cargo fijo por 25 días: "))
energia_activa70 = Decimal(input("Ingrese el costo de energía activa de 70kWh: "))
energia_activa130 = Decimal(input("Ingrese el costo de energía activa de 130kWh: "))
energia_activa_excedente219 = Decimal(
    input("Ingrese el costo de energía activa excedente de 219 kWh: ")
)
iva_consumidor_final_edesa = Decimal(
    input("Ingrese el IVA de consumidor final EDESA: ")
)

subtotal_consumidor_final_edesa = (
    cargo_fijo_x5_dias
    + cargo_fijo_x25_dias
    + pesos(energia_activa70 * 70)
    + pesos(energia_activa130 * 130)
    + pesos(energia_activa_excedente219 * 219)
)

total_consumidor_final_edesa = (
    subtotal_consumidor_final_edesa
    + iva_consumidor_final_edesa
)


## Consumo alumbrado público EDESA

alumbrado_publico = Decimal(
    input("Ingrese el costo de alumbrado público: ")
)


## Consumo Aguas del Norte

cargo_fijo_aguas = Decimal(
    input("Ingrese el cargo fijo de Aguas del Norte: ")
)

consumo_equivalente_aguas = Decimal(
    input("Ingrese el consumo equivalente de Aguas del Norte: ")
)

tasa_de_fizcalizacion_y_control = Decimal(
    input(
        "Ingrese el costo de la tasa de fiscalización y control "
        "de Aguas del Norte: "
    )
)

iva_aguas_del_norte = Decimal(
    input("Ingrese el IVA de Aguas del Norte: ")
)

subtotal_aguas_del_norte = (
    cargo_fijo_aguas
    + consumo_equivalente_aguas
    + tasa_de_fizcalizacion_y_control
)

total_aguas_del_norte = (
    subtotal_aguas_del_norte
    + iva_aguas_del_norte
)


## Consumo LUSAL

mantenimiento_alumbrado_publico = Decimal(
    input("Ingrese el costo de mantenimiento LUSAL: ")
)


## Total de KWh consumidos

total_kwh_consumidos = Decimal(
    input("Ingrese el total de KWh consumidos: ")
)

total_persona1 = Decimal(
    input("Ingrese el total de KWh consumidos por la persona 1: ")
)


while total_persona1 < 0 or total_persona1 > total_kwh_consumidos:

    if total_persona1 < 0:
        print(
            "Error: el consumo de la persona 1 no puede ser negativo."
        )

    elif total_persona1 > total_kwh_consumidos:
        print(
            "Error: el consumo de la persona 1 "
            "no puede superar el consumo total."
        )

    total_persona1 = Decimal(
        input(
            "Ingrese el total de KWh consumidos por la persona 1: "
        )
    )


total_persona2 = total_kwh_consumidos - total_persona1


## Porcentaje de consumo

porcentaje_persona1 = (
    total_persona1 / total_kwh_consumidos
) * 100

porcentaje_persona2 = (
    total_persona2 / total_kwh_consumidos
) * 100


## Distribución de KWh por bloques

# Cada persona tiene derecho a la mitad de cada tramo barato
# (35 kWh del de 70 y 65 kWh del de 130). Los kWh se usan en orden:
# primero el tramo de 70, después el de 130 y el resto va al
# excedente. Si una persona no llega a usar su mitad de un tramo,
# lo que le sobra lo usa la otra persona.

def repartir_tramo(capacidad, restante1, restante2):
    tramo1 = min(restante1, Decimal(capacidad) / 2)
    tramo2 = min(restante2, Decimal(capacidad) / 2)
    sobrante = capacidad - tramo1 - tramo2
    extra1 = min(restante1 - tramo1, sobrante)
    tramo1 += extra1
    tramo2 += min(restante2 - tramo2, sobrante - extra1)
    return tramo1, tramo2


kwh_70_persona1, kwh_70_persona2 = repartir_tramo(
    70, total_persona1, total_persona2
)

kwh_130_persona1, kwh_130_persona2 = repartir_tramo(
    130,
    total_persona1 - kwh_70_persona1,
    total_persona2 - kwh_70_persona2,
)

kwh_219_persona1 = (
    total_persona1
    - kwh_70_persona1
    - kwh_130_persona1
)

kwh_219_persona2 = (
    total_persona2
    - kwh_70_persona2
    - kwh_130_persona2
)


## Costo de energía por persona

kwh_70_total = kwh_70_persona1 + kwh_70_persona2

kwh_130_total = kwh_130_persona1 + kwh_130_persona2

kwh_219_total = kwh_219_persona1 + kwh_219_persona2

energia_70_persona1, energia_70_persona2 = repartir(
    pesos(energia_activa70 * 70),
    kwh_70_persona1 / kwh_70_total if kwh_70_total else Decimal("0.5"),
)

energia_130_persona1, energia_130_persona2 = repartir(
    pesos(energia_activa130 * 130),
    kwh_130_persona1 / kwh_130_total if kwh_130_total else Decimal("0.5"),
)

energia_219_persona1, energia_219_persona2 = repartir(
    pesos(energia_activa_excedente219 * 219),
    kwh_219_persona1 / kwh_219_total if kwh_219_total else Decimal("0.5"),
)


energia_persona1 = (
    energia_70_persona1
    + energia_130_persona1
    + energia_219_persona1
)

energia_persona2 = (
    energia_70_persona2
    + energia_130_persona2
    + energia_219_persona2
)


## División de Aguas del Norte

cargo_fijo_agua_persona1, cargo_fijo_agua_persona2 = repartir(
    cargo_fijo_aguas, Decimal("0.5")
)

consumo_equivalente_agua_persona1, consumo_equivalente_agua_persona2 = repartir(
    consumo_equivalente_aguas, Decimal("0.5")
)

tasa_fiscalizacion_agua_persona1, tasa_fiscalizacion_agua_persona2 = repartir(
    tasa_de_fizcalizacion_y_control, Decimal("0.5")
)

iva_agua_persona1, iva_agua_persona2 = repartir(
    iva_aguas_del_norte, Decimal("0.5")
)


## División de EDESA

cargo_fijo_x5_dias_persona1, cargo_fijo_x5_dias_persona2 = repartir(
    cargo_fijo_x5_dias, Decimal("0.5")
)

cargo_fijo_x25_dias_persona1, cargo_fijo_x25_dias_persona2 = repartir(
    cargo_fijo_x25_dias, Decimal("0.5")
)

iva_edesa_persona1, iva_edesa_persona2 = repartir(
    iva_consumidor_final_edesa, Decimal("0.5")
)


## División de alumbrado público

alumbrado_publico_persona1, alumbrado_publico_persona2 = repartir(
    alumbrado_publico, Decimal("0.5")
)


## División de LUSAL

mantenimiento_persona1, mantenimiento_persona2 = repartir(
    mantenimiento_alumbrado_publico, Decimal("0.5")
)


## TOTAL EDESA POR PERSONA

total_edesa_persona1 = (
    energia_persona1
    + cargo_fijo_x5_dias_persona1
    + cargo_fijo_x25_dias_persona1
    + iva_edesa_persona1
)

total_edesa_persona2 = (
    energia_persona2
    + cargo_fijo_x5_dias_persona2
    + cargo_fijo_x25_dias_persona2
    + iva_edesa_persona2
)


## TOTAL AGUAS DEL NORTE POR PERSONA

total_aguas_persona1 = (
    cargo_fijo_agua_persona1
    + consumo_equivalente_agua_persona1
    + tasa_fiscalizacion_agua_persona1
    + iva_agua_persona1
)

total_aguas_persona2 = (
    cargo_fijo_agua_persona2
    + consumo_equivalente_agua_persona2
    + tasa_fiscalizacion_agua_persona2
    + iva_agua_persona2
)


## TOTAL ALUMBRADO Y LUSAL POR PERSONA

total_alumbrado_persona1 = (
    alumbrado_publico_persona1
    + mantenimiento_persona1
)

total_alumbrado_persona2 = (
    alumbrado_publico_persona2
    + mantenimiento_persona2
)


## TOTAL FINAL A PAGAR

total_a_pagar_persona1 = (
    total_edesa_persona1
    + total_aguas_persona1
    + total_alumbrado_persona1
)

total_a_pagar_persona2 = (
    total_edesa_persona2
    + total_aguas_persona2
    + total_alumbrado_persona2
)


## RESULTADOS DEL CONSUMO

print("\n--- CONSUMO DE LOS INQUILINOS ---")

print(
    "KWh persona 1:",
    total_persona1
)

print(
    "KWh persona 2:",
    total_persona2
)


## PORCENTAJE DE CONSUMO

print("\n--- PORCENTAJE DE CONSUMO ---")

print(
    "Porcentaje persona 1:",
    porcentaje_persona1,
    "%"
)

print(
    "Porcentaje persona 2:",
    porcentaje_persona2,
    "%"
)

print(
    "Suma de porcentajes:",
    porcentaje_persona1 + porcentaje_persona2,
    "%"
)


## DISTRIBUCIÓN DE KWh

print("\n--- DISTRIBUCIÓN DE KWh POR BLOQUES ---")

print("Persona 1:")

print(
    "  Bloque 70 kWh:",
    kwh_70_persona1,
    "kWh"
)

print(
    "  Bloque 130 kWh:",
    kwh_130_persona1,
    "kWh"
)

print(
    "  Bloque 219 kWh:",
    kwh_219_persona1,
    "kWh"
)


print("Persona 2:")

print(
    "  Bloque 70 kWh:",
    kwh_70_persona2,
    "kWh"
)

print(
    "  Bloque 130 kWh:",
    kwh_130_persona2,
    "kWh"
)

print(
    "  Bloque 219 kWh:",
    kwh_219_persona2,
    "kWh"
)


## COSTO DE ENERGÍA

print("\n--- COSTO DE ENERGÍA ---")

print("Persona 1:")

print(
    "  Energía bloque 70:",
    energia_70_persona1
)

print(
    "  Energía bloque 130:",
    energia_130_persona1
)

print(
    "  Energía bloque 219:",
    energia_219_persona1
)

print(
    "  Total energía persona 1:",
    energia_persona1
)


print("Persona 2:")

print(
    "  Energía bloque 70:",
    energia_70_persona2
)

print(
    "  Energía bloque 130:",
    energia_130_persona2
)

print(
    "  Energía bloque 219:",
    energia_219_persona2
)

print(
    "  Total energía persona 2:",
    energia_persona2
)


print(
    "Total energía repartida:",
    energia_persona1 + energia_persona2
)


## COMPROBACIÓN DE LA FACTURA

print("\n--- COMPROBACIÓN DE LA FACTURA ---")

print(
    "Energía bloque 70:",
    pesos(energia_activa70 * 70)
)

print(
    "Energía bloque 130:",
    pesos(energia_activa130 * 130)
)

print(
    "Energía bloque 219:",
    pesos(energia_activa_excedente219 * 219)
)

print(
    "Total energía de la factura:",
    pesos(energia_activa70 * 70)
    + pesos(energia_activa130 * 130)
    + pesos(energia_activa_excedente219 * 219)
)

print(
    "Total EDESA:",
    total_consumidor_final_edesa
)

print(
    "Total Aguas del Norte:",
    total_aguas_del_norte
)


## RESULTADOS DEL REPARTO

print("\n--- EDESA POR PERSONA ---")

print(
    "Persona 1:",
    total_edesa_persona1
)

print(
    "Persona 2:",
    total_edesa_persona2
)


print("\n--- AGUAS DEL NORTE POR PERSONA ---")

print(
    "Persona 1:",
    total_aguas_persona1
)

print(
    "Persona 2:",
    total_aguas_persona2
)


print("\n--- ALUMBRADO Y LUSAL POR PERSONA ---")

print(
    "Persona 1:",
    total_alumbrado_persona1
)

print(
    "Persona 2:",
    total_alumbrado_persona2
)


## TOTAL FINAL

print("\n--- TOTAL FINAL A PAGAR ---")

print(
    "Persona 1:",
    total_a_pagar_persona1
)

print(
    "Persona 2:",
    total_a_pagar_persona2
)

print(
    "Total repartido:",
    total_a_pagar_persona1
    + total_a_pagar_persona2
)