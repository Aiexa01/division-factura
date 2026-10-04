
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Repartidor de facturas EDESA / Aguas del Norte entre 2 inquilinos.

V1:
- Lee una factura PDF de EDESA.
- Extrae los principales importes y los bloques de energía de la factura.
- Recibe los kWh consumidos por cada inquilino.
- Reparte:
    * cargo fijo EDESA: 50/50
    * energía EDESA: según kWh, aplicando los tramos/tarifas de la factura
    * IVA EDESA: proporcional al subtotal EDESA antes de IVA
    * alumbrado público: 50/50
    * Aguas del Norte: 50/50 (configurable)
    * mantenimiento de alumbrado: 50/50
- Comprueba que los kWh de los inquilinos coincidan con el consumo total de la factura.

Uso:
    python reparto_factura_inquilinos.py factura.pdf 198.6 220.4

Dependencia:
    pip install pypdf
"""

import re
import sys
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Falta la dependencia pypdf. Instalá con: pip install pypdf")
    raise SystemExit(1)

# El OCR es opcional: sólo se usa si el texto del PDF viene incompleto.
try:
    import fitz
    import pytesseract
    from PIL import Image
except ImportError:
    fitz = None

CENT = Decimal("0.01")


def D(value):
    """Decimal seguro para cálculos monetarios."""
    return Decimal(str(value))


def money(value):
    return D(value).quantize(CENT, rounding=ROUND_HALF_UP)


class Repartidor:
    """
    Reparte importes entre A y B en centavos exactos: lo que no recibe A
    lo recibe B, así la suma siempre da el importe de la factura.

    Si sobra medio centavo (por ejemplo, un importe impar al 50/50),
    el centavo se alterna entre los inquilinos.
    """

    def __init__(self):
        self.proximo_centavo_a = True

    def __call__(self, importe, fraccion_a):
        importe = money(importe)
        exacto = importe * D(fraccion_a)
        a = exacto.quantize(CENT, rounding=ROUND_FLOOR)
        resto = exacto - a
        if resto * 2 == CENT:
            if self.proximo_centavo_a:
                a += CENT
            self.proximo_centavo_a = not self.proximo_centavo_a
        elif resto * 2 > CENT:
            a += CENT
        return a, importe - a


def parse_ar_number(s):
    """
    Convierte números argentinos:
      188.558,98 -> Decimal('188558.98')
      419        -> Decimal('419')
      187,0918   -> Decimal('187.0918')
    """
    s = s.strip().replace("$", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(".", "")
    return D(s)


def read_pdf(path):
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def first_decimal(pattern, text, flags=re.I):
    m = re.search(pattern, text, flags)
    if not m:
        return None
    return parse_ar_number(m.group(1))


def extract_invoice(text):
    # Valores específicos de la estructura de esta factura.
    total = first_decimal(r"\bT o t a l:\s*([\d\.,]+)", text)
    edesa = first_decimal(r"Subtotal EDESA SA\s+([\d\.,]+)", text)
    alumbrado = first_decimal(
        r"Subtotal Incidencia Alumbrado Público\s+([\d\.,]+)", text
    )
    aguas = first_decimal(r"Subtotal Aguas del Norte\s+([\d\.,]+)", text)
    mantenimiento = first_decimal(
        r"Subtotal p/cuenta y orden de LUSAL UTE\s+([\d\.,]+)", text
    )

    consumo = first_decimal(r"Activa\s+\d+\s+\d+\s+[\d\.,]+\s+([\d\.,]+)", text)

    iva = first_decimal(
        r"IVA Consumidor Final\s+21,00%\s+([\d\.,]+)", text
    )

    # Cargo fijo: en esta factura aparece en dos períodos.
    cargos_fijos = [
        parse_ar_number(x)
        for x in re.findall(
            r"Cargo Fijo Mensual\s+\([^)]*\)\s+([\d\.,]+)", text, re.I
        )
    ]

    # Bloques de energía:
    # Energia activa (70 kWh * 187,0918 $ / kWh) 13.096,43
    # Energia activa (130 kWh * 179,5144 $ / kWh) 23.336,87
    # Energia activa excedente (219 kWh * 301,8821 $ / kWh) 66.112,18
    energy_blocks = []
    pattern = (
        r"Energia\s+activa(?:\s+excedente)?\s*"
        r"\(([\d\.,]+)\s*kWh\s*\*\s*([\d\.,]+)\s*\$\s*/\s*kWh\)"
        r"\s+([\d\.,]+)"
    )
    for m in re.finditer(pattern, text, re.I):
        energy_blocks.append({
            "kwh": parse_ar_number(m.group(1)),
            "rate": parse_ar_number(m.group(2)),
            "amount": parse_ar_number(m.group(3)),
        })

    # Algunos PDFs de EDESA tienen texto extraíble incompleto por el diseño
    # de la factura. Si faltan bloques, hacemos OCR de la página y tomamos
    # únicamente los bloques de energía desde allí.
    if len(energy_blocks) < 3 and fitz is not None:
        try:
            pdf_path = getattr(extract_invoice, "_pdf_path", None)
            if pdf_path:
                doc = fitz.open(str(pdf_path))
                ocr_text = ""
                for page in doc:
                    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text += "\n" + pytesseract.image_to_string(
                        img, lang="spa", config="--psm 6"
                    )
                ocr_blocks = []
                for m in re.finditer(pattern, ocr_text, re.I):
                    block = {
                        "kwh": parse_ar_number(m.group(1)),
                        "rate": parse_ar_number(m.group(2)),
                        "amount": parse_ar_number(m.group(3)),
                    }
                    if block not in ocr_blocks:
                        ocr_blocks.append(block)
                if len(ocr_blocks) >= len(energy_blocks):
                    energy_blocks = ocr_blocks
        except Exception:
            pass

    if not energy_blocks:
        raise ValueError("No pude encontrar los bloques de energía de EDESA.")

    required = {
        "total": total,
        "edesa": edesa,
        "alumbrado": alumbrado,
        "aguas": aguas,
        "mantenimiento": mantenimiento,
        "consumo": consumo,
        "iva": iva,
    }
    missing = [k for k, v in required.items() if v is None]
    if missing:
        raise ValueError(
            "No pude extraer de la factura: " + ", ".join(missing)
        )

    return {
        **required,
        "cargo_fijo": sum(cargos_fijos, Decimal("0")),
        "energy_blocks": energy_blocks,
    }


def split_invoice(invoice, tenant_a_kwh, tenant_b_kwh):
    a = D(tenant_a_kwh)
    b = D(tenant_b_kwh)
    total_kwh = invoice["consumo"]

    if a < 0 or b < 0:
        raise ValueError("Los consumos no pueden ser negativos.")

    if abs((a + b) - total_kwh) > D("0.01"):
        raise ValueError(
            f"Los consumos no coinciden con la factura: "
            f"{a} + {b} = {a+b}, pero la factura indica {total_kwh} kWh."
        )

    repartir = Repartidor()
    share_a = a / (a + b) if a + b else D("0.5")

    # Energía variable: cada bloque de la factura se reparte según la
    # participación de kWh de cada inquilino.
    #
    # Importante: los tramos tarifarios se aplican al medidor conjunto.
    # No se reinicia la escala de precios para cada inquilino, porque eso
    # duplicaría los primeros tramos y no cerraría contra la factura.
    detail_a = []
    detail_b = []
    for block in invoice["energy_blocks"]:
        amount_a, amount_b = repartir(block["amount"], share_a)
        detail_a.append({
            "kwh": block["kwh"] * share_a,
            "rate": block["rate"],
            "amount": amount_a,
        })
        detail_b.append({
            "kwh": block["kwh"] * (1 - share_a),
            "rate": block["rate"],
            "amount": amount_b,
        })
    energy_a = sum((x["amount"] for x in detail_a), Decimal("0"))
    energy_b = sum((x["amount"] for x in detail_b), Decimal("0"))

    # Cargo fijo 50/50.
    fixed_a, fixed_b = repartir(invoice["cargo_fijo"], D("0.5"))

    # IVA EDESA: proporcional al subtotal antes de IVA.
    # Base = cargo fijo + energía. La factura permite verificar que 21%
    # coincide con el IVA informado.
    base_a = fixed_a + energy_a
    base_total = base_a + fixed_b + energy_b

    iva_a, iva_b = repartir(
        invoice["iva"], base_a / base_total if base_total else D("0.5")
    )

    # Otros conceptos: 50/50 por ahora. Se dejan configurables.
    alum_a, alum_b = repartir(invoice["alumbrado"], D("0.5"))

    agua_a, agua_b = repartir(invoice["aguas"], D("0.5"))

    mant_a, mant_b = repartir(invoice["mantenimiento"], D("0.5"))

    result = {
        "A": {
            "kwh": a,
            "energia": energy_a,
            "cargo_fijo": fixed_a,
            "iva": iva_a,
            "alumbrado": alum_a,
            "agua": agua_a,
            "mantenimiento": mant_a,
        },
        "B": {
            "kwh": b,
            "energia": energy_b,
            "cargo_fijo": fixed_b,
            "iva": iva_b,
            "alumbrado": alum_b,
            "agua": agua_b,
            "mantenimiento": mant_b,
        },
        "_detail": {"A": detail_a, "B": detail_b},
    }

    for person in ("A", "B"):
        r = result[person]
        r["total"] = sum(r[k] for k in ("energia", "cargo_fijo", "iva", "alumbrado", "agua", "mantenimiento"))

    return result


def print_report(invoice, result):
    print("\n========== REPARTO DE FACTURA ==========")
    print(f"Consumo factura: {invoice['consumo']} kWh")
    print(f"Total factura:   ${money(invoice['total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print()

    for name in ("A", "B"):
        r = result[name]
        print(f"INQUILINO {name} — {r['kwh']} kWh")
        print(f"  Energía:              ${money(r['energia']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print(f"  Cargo fijo:           ${money(r['cargo_fijo']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print(f"  IVA:                  ${money(r['iva']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print(f"  Alumbrado público:    ${money(r['alumbrado']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print(f"  Aguas del Norte:      ${money(r['agua']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print(f"  Mantenimiento:        ${money(r['mantenimiento']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print(f"  -------------------------------")
        print(f"  TOTAL:                ${money(r['total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        print()

    suma = result["A"]["total"] + result["B"]["total"]
    print(f"Control suma inquilinos: ${money(suma):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    print(f"Diferencia vs factura:   ${money(suma - invoice['total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    print("\nDetalle de energía por tramos:")
    for name in ("A", "B"):
        print(f"  Inquilino {name}:")
        for d in result["_detail"][name]:
            print(
                f"    {d['kwh']} kWh × ${d['rate']} = "
                f"${money(d['amount']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        print("Ejemplo:")
        print("  python reparto_factura_inquilinos.py factura.pdf 198.6 220.4")
        raise SystemExit(2)

    pdf = Path(sys.argv[1])
    if not pdf.exists():
        raise SystemExit(f"No existe el archivo: {pdf}")

    invoice_text = read_pdf(pdf)
    extract_invoice._pdf_path = pdf
    invoice = extract_invoice(invoice_text)
    result = split_invoice(invoice, sys.argv[2], sys.argv[3])
    print_report(invoice, result)


if __name__ == "__main__":
    main()
