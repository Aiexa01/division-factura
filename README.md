# División de factura

Reparte una factura de EDESA / Aguas del Norte / LUSAL entre dos inquilinos, al centavo exacto.

- `index.html` + `script.js` + `style.css`: página principal. Permite cargar el PDF de la factura y completa los datos sola. Reparte la energía por tramos (cada persona tiene la mitad de los tramos de 70 y 130 kWh).
- `consumo.py`: la misma cuenta por consola.
- `division_factura.html` y `reparto_factura_inquilinos.py`: reparto proporcional a los kWh (el .py lee el PDF; requiere `pip install pypdf`).

Todos los cálculos se hacen en centavos, así la suma de las dos personas da exactamente el total de la factura.
